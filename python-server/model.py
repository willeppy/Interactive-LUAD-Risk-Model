import numpy as np
import pandas as pd
import seaborn as sns
import json
import math

from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV

from lifelines.statistics import logrank_test
import shap


# gridsearchCV throws lots of warnings so supress bc not critical
import warnings

def warn(*args, **kwargs):
    pass
warnings.warn = warn

'''
data_df has [bcr_patient_barcode, death_days_to, y_is_tumor, GENES...]

NOTE: death_days_to = 1_000_000 means they are censored and didnt die in data

'''
def prepare_data(data_df, genelist, prediction_type, day_threshold=600):
    X = data_df[genelist]
    X = (X - X.mean()) / X.std()

    if prediction_type == 'normal_vs_tumor': # 0 = normal, 1 = tumor
        y = data_df["y_is_tumor"] 

    if prediction_type == 'lowrisk_vs_highrisk': # 0 is low risk, 1 = high risk
        y = (data_df["death_days_to"] < day_threshold).astype(int)
        
    return X, y

'''
TODO: add class_weight to hyperparameter search 

'''
def train_model(X, y, classifier_name, scoring=["f1_weighted", "balanced_accuracy"]):
        
    if classifier_name == 'RF':
        clf = RandomForestClassifier()
    if classifier_name == 'NN':
        clf = MLPClassifier()
    if classifier_name == 'DT':
        clf = DecisionTreeClassifier()
    if classifier_name == 'LR':
        clf = LogisticRegression()
    if classifier_name == "SVM":
        clf = SVC()
        
    params = {
        "RF": {"n_estimators": [10, 100], "criterion": ["gini", "entropy"]},
        "NN": {"hidden_layer_sizes": [(100), (50, 25), (100, 50)], "learning_rate_init": [.01, .001], "max_iter": [100]},
        "DT": {"max_depth": [None, 10]},
        "LR": {"penalty": ["l1", "l2", "elasticnet"], "solver": ["lbfgs", "saga"], "l1_ratio":[.5], "max_iter":[200]},
        "SVM": {"kernel": ["linear", "poly", "rbf",]}
    }
    
    # evaluates with both scoring metrics but selects the best_model with the first
    cv = GridSearchCV(clf, params[classifier_name], scoring=scoring, refit=scoring[0], cv=5)
    cv.fit(X, y)
    
    # best estimator
    best_clf = cv.best_estimator_
    
    # get average metrics
    metric_df = pd.DataFrame(cv.cv_results_)
    metrics = []
    
    for m in scoring:
        _val = metric_df[metric_df[f"rank_test_{scoring[0]}"] == 1][f"mean_test_{m}"].values[0]
        metrics.append({"metric":m, "value":_val})
        
    return best_clf, metrics


'''
If using LR, then take the model coefficients.
Otherwise, compute SHAP values.

SHAP: https://shap.readthedocs.io/en/latest/api.html

'''
def get_feature_importance(classifier_name, clf, X):
   
    if classifier_name == 'LR':
        ### taks abs val of coefficients of linear model
        feat_imps = abs(clf.coef_.flatten()).tolist() 
    
    elif classifier_name in ["RF", "DT"]:
        ### TreeExplainer is super fast for tree methods
        
        background = shap.maskers.Independent(X, max_samples=500)
        explainer = shap.TreeExplainer(clf, masker=background)
        shap_vals = explainer(X)
        
        feat_imps = shap_vals.abs.values.mean(axis=0)[:,0].tolist()
    
    else: # ["NN", "SVM"]
        
        ### generic method -- super slow!!
        # background = shap.maskers.Independent(X, max_samples=100)
        # explainer = shap.Explainer(clf, background)
        # shap_vals = explainer(X)
        # feat_imps = shap_vals.abs.values.mean(axis=0).tolist()
        
        ### Kernel Explainer is a bit faster
        med = np.median(X, axis=0).reshape(1, -1)
        explainer = shap.KernelExplainer(clf.predict, med)
        shap_vals = explainer.shap_values(X)
        feat_imps = abs(shap_vals.mean(axis=0)).tolist()
    
    # d = dict(zip(X.columns.tolist(), feat_imps))
    d = []

    for f, imp in zip(X.columns.tolist(), feat_imps):
        d.append({"feat": f, "imp": imp})
    
    return d


def get_survival_curve(df, model_output):
    
    _dftrim = df[["bcr_patient_barcode", "death_days_to"]]
        
    idx = np.sort(_dftrim["death_days_to"].astype(int).unique())[:-1] # ignore the max because is 1_000_000

    group_0 = _dftrim[model_output==0]
    group_1 = _dftrim[model_output==1]
    
    # build event table
    event_table_0 = build_event_table(group_0, idx)
    event_table_1 = build_event_table(group_1, idx)
    
    # log rank test 
    group_0["obs"] = (group_0["death_days_to"] != 1000000).astype(int)
    group_1["obs"] = (group_1["death_days_to"] != 1000000).astype(int)
    
    stat_test = logrank_test(group_0["death_days_to"], 
                             group_1["death_days_to"], 
                             event_observed_A=group_0["obs"], 
                             event_observed_B=group_1["obs"])
    
    # change types of outputs
    p_val = float(stat_test.p_value)
    if math.isnan(p_val):
        p_val = 100.0 # this only happens when one of the groups is empty
    
    days = idx.tolist()
    events_group_0 = event_table_0.p.values.tolist()
    events_group_1 = event_table_1.p.values.tolist()

    # format data 
    resp = {"data": [], "p_val": p_val}

    for i in range(len(days)):
        _item = {"day": days[i], "gp_0": events_group_0[i], "gp_1": events_group_1[i]}
        resp["data"].append(_item)

    return resp


def build_event_table(group_data, idx):
    event_table = pd.DataFrame(data=np.zeros((len(idx), 3)), index=idx, columns=['event','at_risk','p'])
    event_table.index.name = 'days'
    
    vc = group_data["death_days_to"].value_counts()
    
    for i, day in enumerate(event_table.index):
        if i == 0:
            at_risk = len(group_data)
            p_prev = 1
        else:
            at_risk = event_table.iloc[i - 1]["at_risk"] - event_table.iloc[i - 1]["event"]
            p_prev = event_table.iloc[i - 1]["p"]
            
        event_num = vc.get(day, default=0)
        
        # save metrics
        event_table.loc[day]["event"] = event_num
        event_table.loc[day]["at_risk"] = at_risk
        if not at_risk: 
            at_risk = 1 # to prevent divide by zero
        event_table.loc[day]["p"] = p_prev * (1 - (event_num/at_risk))
        
    return event_table

'''
classifier_name: 'Random_Forest', 'Logistic_Regression' and 'SVM'
prediction_type: 'normal_vs_tumor' or 'lowrisk_vs_highrisk'
genelist: list of gene names, e.g. ['AAAS','ERAS','MPO','BTBD2','MYG1']

'''
def run_model_creation(data_df, classifier_name, prediction_type, genelist, day_thresh):
    # print("In create model.")
    # print("\tModel Type: ", classifier_name)
    # print("\tOutput variable: ", prediction_type)
    # print("\tGenes: ", genelist)
    # print("\tData looks like: ", data_df.shape)

    # normlize X and select right y 
    X, y = prepare_data(data_df, genelist, prediction_type, day_threshold=day_thresh)

    # scoring = ["f1_weighted", "balanced_accuracy"]
    best_clf, metrics_dict = train_model(X, y, classifier_name)

    predictions = best_clf.predict(X)

    km_curve = get_survival_curve(data_df, predictions)

    feat_importance = get_feature_importance(classifier_name, best_clf, X)

    response = {"metrics": metrics_dict,  
                "predictions": predictions.tolist(), 
                "y": y.tolist(), 
                "km_curve": km_curve,
                "feat_importance": feat_importance,
                "prediction_type": prediction_type}

    json_res = json.dumps(response)
    # print(json_res)
    return json_res

