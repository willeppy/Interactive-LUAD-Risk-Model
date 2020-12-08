<script>
    import embed from "vega-embed";

    export let input_data;

    console.log("INPUT PRED TYPE:", input_data.prediction_type)

    // SPECS
    let feat_imp_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
        "width": "container",
        "height": "container",
        "title": "Ranked Features (top 20)",
        "data": { "values": input_data.feat_importance },
        "selection": {
            "highlight": {"type": "single", "empty": "none", "on": "mouseover"}
        },
        "transform": [
            {
            "window": [{"op": "rank", "as": "rank"}],
            "sort": [{"field": "imp", "order": "descending"}]
            },
            {"filter": "datum.rank <= 20"}
        ],
        "mark": {"type": "bar", "tooltip": true},
        "encoding": {
            "x": {"field": "imp", "type": "quantitative", "title": "Importance Value"},
            "y": {
                "field": "feat",
                "sort": "-x",
                "title": "Feature Name",
                "axis": {"labelOverlap": "greedy"}
            },
            "fillOpacity": {
                "condition": {"selection": "highlight", "value": 0.7},
                "value": 1
            },
            "color": {"value": "#085"}
        }
    };

    let model_dist_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
        "data": {"values": input_data.predictions},
        "selection": {
            "highlight": {"type": "single", "empty": "none", "on": "mouseover"}
        },
        "width": "container",
        "height": "container",
        "title": "Model Output Distribution",
        "mark": {"type": "bar", "tooltip": true},
        "encoding": {
            "x": {
                "field": "data",
                "type": "ordinal",
                "title": "Predicted Class",
                "axis": {"labelAngle": 0}
            },
            "y": {
                "aggregate": "count",
                "field": "data",
                "title": "Count"
            },
            "color": {"field": "data", "type": "nominal"},
            "fillOpacity": {
                "condition": {"selection": "highlight", "value": 0.7},
                "value": 1
            }
        }
    };

    let km_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
        "width": "container",
        "height": "container",
        "title": "Kaplan Meier Estimate",
        "data": { "values": input_data.km_curve.data},
        "encoding": {
            "x": {
            "field": "day",
            "type": "quantitative",
            "title": "Time (days)",
            "axis": {"labelOverlap": true}
            },
            "tooltip": [
            {"field": "day", "type": "quantitative"},
            {"field": "gp_0", "type": "quantitative"},
            {"field": "gp_1", "type": "quantitative"}
            ]
        },
        "layer": [
            {
            "mark": {"type": "line", "interpolate": "step-after"},
            "encoding": {
                "y": {
                "field": "gp_0",
                "type": "quantitative",
                "title": "Survival Probability"
                },
                "color": {"datum": "gp_0", "type": "nominal"}
            }
            },
            {
            "mark": {"type": "line", "interpolate": "step-after"},
            "encoding": {
                "y": {
                "field": "gp_1",
                "type": "quantitative",
                "title": "Survival Probability"
                },
                "color": {"datum": "gp_1", "type": "nominal"}
            }
            },
            {
            "mark": "rule",
            "selection": {
                "hover": {
                "type": "single",
                "on": "mouseover",
                "empty": "none",
                "nearest": true
                }
            },
            "encoding": {
                "color": {
                "condition": {"selection": {"not": "hover"}, "value": "transparent"}
                }
            }
            }
        ]
    }

    // Testing: print out 
    console.log("Feature Importance Spec:")
    console.log(JSON.stringify(feat_imp_spec))

    console.log("Model Dist Spec:")
    console.log(JSON.stringify(model_dist_spec))

    console.log("KM Spec:")
    console.log(JSON.stringify(km_spec))


    // embed charts
    embed("#feat-importance-bar", feat_imp_spec, { renderer: "svg", actions: false });
    embed("#model-dist-bar", model_dist_spec, { renderer: "svg" , actions: false});
    embed("#km-curve-line", km_spec, { renderer: "svg" , actions: false});

</script>

<style>
    #results-graphs-wrapper {
        /* border: 1px solid rgb(87, 130, 209); */
        padding: 1rem 1rem 1rem 0;
    }

    #model-dist-bar, #feat-importance-bar, #km-curve-line {
        height: 500px;
        width: 500px;
    }

    /* table styles generated from  https://divtable.com/table-styler/ */

    table.simple-table {
        border: 1px solid #ebebeb;
        width: 100%;
        text-align: center;
        /* border-collapse: collapse; */
        border-radius: 6px;
    }
    table.simple-table td {
        padding: 3px 4px;
    }
    table.simple-table tbody td {
        font-size: 1rem;
    }
    /* table.simple-table tr:nth-child(odd) {
        background: #ebebeb;
    } */
    table.simple-table thead th {
        font-size: 15px;
        font-weight: bold;
        color: #333333;
        text-align: center;
        padding: 10px 4px;
    }

    .blockDiv {
        display: inline-block;
    }

    .key {
        border: 2px solid #ebebeb;
        border-radius: 6px;
        display: inline-block;
        padding: .5rem;
        font-weight: 600;
    }
</style>

<div id="results-graphs-wrapper">
    <h1>Model Training Results</h1>
    <p>
        This model was trained to predict <strong><em>{input_data.prediction_type}</em></strong>.    
    </p>
    {#if input_data.prediction_type == "normal_vs_tumor"}
        <div class="key">
            0 = Healthy Tissue
        </div>
        <div class="key">
            1 = Cancer Tissue
        </div>
    {/if}
    {#if input_data.prediction_type == "lowrisk_vs_highrisk"}
        <div class="key">
            0 = Low Risk
        </div>
        <div class="key">
            1 = High Risk
        </div>
    {/if}

    
    <div class="">
        <h3>Model Performance Metrics</h3>
        <table class="simple-table">
            <thead>
                <th>Metric</th>
                <th>Score</th>
            </thead>
            <tbody>
                {#each input_data.metrics as item}
                    <tr>
                        <td>{item.metric}</td>
                        <td>{item.value.toFixed(4)}</td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>

    <div class="blockDiv">
        <h3>Predicted Class Distribution</h3>
        <div id="model-dist-bar" />
    </div>

    <div class="blockDiv">
        <h3>Feature Importance</h3>
        <div id="feat-importance-bar" />
    </div>

    <div class="blockDiv">
        <h3>Kaplan Meier Curve</h3>
        <p>Log-odds p-value that curves are significantly different: {input_data.km_curve.p_val.toFixed(4)}</p>
        <div id="km-curve-line" />
    </div>
</div>
