<script>
    import {
        selected_model,
        selected_genes,
        prediction_type,
    } from "../stores.js";
    import ResultsGraphs from "./ResultsGraphs.svelte";

    // base URL of server
    const url_base = "http://127.0.0.1:8000";

    async function postAPI(r_data) {
        // check inputs
        if (!r_data.genelist.length) {
            throw new Error(
                "Uh oh! Please select at least 1 gene to train a model."
            );
        }

        // stringify
        let processed_data = JSON.stringify(r_data);
        console.log(processed_data);

        // send to server
        const res = await self.fetch(url_base + "/model", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(r_data),
        });

        if (res.ok) {
            return res.json();
        } else {
            throw new Error(res);
        }
    }

    let promise = Promise.resolve(undefined); // trick the dum dum computer

    function handleClick() {
        let request_data = {
            classifier_name: $selected_model.value,
            genelist: $selected_genes,
            prediction_type: $prediction_type.value,
            day_thresh: $prediction_type.day_thresh,
        };

        promise = postAPI(request_data);
    }

    // TEMP
    // let m = {"metrics": [{"metric": "f1_weighted", "value": 0.8409703504043128}, {"metric": "fskl", "value": 0.408}]}

    // console.log(m.metrics)
</script>

<style>
    #feat-selector {
        /* border: 1px solid rgb(87, 130, 209); */
        padding: 1rem;
    }

    /* Table stuff */
    table.simple-table {
        /* border: 1px solid #ebebeb; */
        width: 60%;
        text-align: left;
        border-radius: 6px;
    }
    table.simple-table td {
        padding: 3px 4px;
    }
    td.emph {
        font-style: italic;
    }

    
</style>

<div id="feat-selector">
    <h1>Train Model:</h1>

    <h3>Model Meta-data:</h3>
    <table class="simple-table">
        <tbody>
            <tr>
                <td class="emph">Model Type:</td>
                <td>{$selected_model.label}</td>
            </tr>
            <tr>
                <td class="emph"># Features Selected:</td>
                <td>{$selected_genes.length}</td>
            </tr>
            <tr>
                <td class="emph">Target Class:</td>
                <td>
                    {$prediction_type.label}
                    {#if $prediction_type.value == 'lowrisk_vs_highrisk'}
                        with threshold set to
                        <strong>{$prediction_type.day_thresh} </strong>
                    {/if}
                </td>
            </tr>
        </tbody>
    </table>
    <br />
    <br />

    <button on:click={handleClick}>Train Model!</button>

    {#await promise}
        <!-- <p>...Running...</p> -->

        <div class="load-wrapper">
            <div class="loading">
                <p>Running...</p>
                <span />
            </div>
        </div>
    {:then respObj}
        <!-- <p>The response is {JSON.stringify(respObj)}</p> -->
        {#if respObj != undefined}
            <ResultsGraphs input_data={JSON.parse(respObj)} />
        {/if}
    {:catch error}
        <p style="color: red">{error.message}</p>
    {/await}
</div>
