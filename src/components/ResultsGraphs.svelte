<script>
    import embed from "vega-embed";

    export let input_data;

    console.log(input_data.km_curve)

    // SPECS
    let feat_imp_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
        "width": "container",
        "height": "container",
        "title": "Ranked Features",
        "data": { "values": input_data.feat_importance },
        "mark": "bar",
        "encoding": {
            "x": {
                "field": "imp",
                "type": "quantitative",
                "title": "Importance Value",
            },
            "y": { "field": "feat", "sort": "-x", "title": "Feature Name" },
        },
    };

    let model_dist_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
        "data": {"values": input_data.predictions},
        "width": "container",
        "height": "container",
        "title": "Model Output Distribution",
        "mark": "bar",
        "encoding": {
            "x": {
            "field": "data",
            "type": "ordinal",
            "title": "Predicted Class"
            },
            "y": {
            "aggregate": "count",
            "field": "data",
            "title": "Count"
            },
            "color": {"value": "darkred"}
        }
    };

    let km_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
        "width": "container",
        "height": "container",
        "title": "Kaplan Meier Estimate",
        "data": { "values": input_data.km_curve.data},
        "repeat": {"layer": ["gp_0", "gp_1"]},
        "spec": {
            "mark": {"type": "line", "interpolate": "step-after"},
            "encoding": {
            "x": {"field": "day", "type": "ordinal", "title":"Time (days)", "axis": {"labelOverlap": "greedy"}},
            "y": {
                "field": {"repeat": "layer"},
                "type": "quantitative",
                "title": "Survival Probability"
            },
            "stroke": {"datum": {"repeat": "layer"}, "type": "nominal"}
            }
        }
    }


    // embed charts
    embed("#feat-importance-bar", feat_imp_spec, { renderer: "svg", actions: false });
    embed("#model-dist-bar", model_dist_spec, { renderer: "svg" , actions: false});
    embed("#km-curve-line", km_spec, { renderer: "svg" , actions: false});

</script>

<style>
    #results-graphs-wrapper {
        /* border: 1px solid rgb(87, 130, 209); */
        padding: 1rem;
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
</style>

<div id="results-graphs-wrapper">
    
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
        <p>Log-odds significance value for different curves: {input_data.km_curve.p_val.toFixed(4)}</p>
        <div id="km-curve-line" />
    </div>
</div>
