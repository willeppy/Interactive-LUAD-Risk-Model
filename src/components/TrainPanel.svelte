<script>

    import { selected_model, selected_genes, prediction_type } from "../stores.js";
    import ResultsGraphs from "./ResultsGraphs.svelte"

    // base URL of server
    const url_base = "http://127.0.0.1:8000"

    async function postAPI(r_data) {

        // check inputs
        if (!r_data.genelist.length){
            throw new Error("Uh oh! Please select at least 1 gene to train a model.");
        }

        // stringify
        let processed_data = JSON.stringify(r_data);
        console.log(processed_data)

        // send to server
        const res = await self.fetch(url_base + "/model", {
            method: "POST",
            headers: { 'Content-Type': 'application/json'},
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
        "classifier_name": $selected_model.value,
        "genelist": $selected_genes,
        "prediction_type": $prediction_type.value,
        "day_thresh": $prediction_type.day_thresh
        }

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
</style>

<div id="feat-selector">
    <h1>Train Model:</h1>
    <p>Model type: {$selected_model.label}</p>
    <p>Num Features: {$selected_genes.length}</p>
    <p>Features: {$selected_genes}</p>

    <p>Pred type: {JSON.stringify($prediction_type)}</p>

    

    <button on:click={handleClick}> hit API</button>

    {#await promise}
        <p>...waiting...</p>
    {:then respObj}
        <!-- <p>The response is {JSON.stringify(respObj)}</p> -->
        {#if respObj != undefined}
            <ResultsGraphs input_data={JSON.parse(respObj)} />
        {/if}
    {:catch error}
        <p style="color: red">{error.message}</p>
    {/await}
</div>
