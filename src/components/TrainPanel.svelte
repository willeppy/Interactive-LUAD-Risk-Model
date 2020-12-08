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

    // console.log(m.metrics)
</script>

<style type="text/scss">
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

    /* Loading animation */

    .load-wrapper {
        width: 100%;
        height: 100vh;
        display: flex;
        justify-content: center;
        // align-items: center;
        padding-top: 5rem;

        .loading {
            width: 80px;
            height: 50px;
            position: relative;

            p {
                top: 0;
                padding: 0;
                margin: 0;
                color: #5389a6;
                animation: text 3.5s ease both infinite;
                font-size: 12px;
                letter-spacing: 1px;

                @keyframes text {
                    0% {
                        letter-spacing: 1px;
                        transform: translateX(0px);
                    }

                    40% {
                        letter-spacing: 2px;
                        transform: translateX(26px);
                    }

                    80% {
                        letter-spacing: 1px;
                        transform: translateX(32px);
                    }

                    90% {
                        letter-spacing: 2px;
                        transform: translateX(0px);
                    }

                    100% {
                        letter-spacing: 1px;
                        transform: translateX(0px);
                    }
                }
            }
            span {
                background-color: #5389a6;
                border-radius: 50px;
                display: block;
                height: 16px;
                width: 16px;
                bottom: 0;
                position: absolute;
                transform: translateX(64px);
                animation: loading 3.5s ease both infinite;

                &:before {
                    position: absolute;
                    content: "";
                    width: 100%;
                    height: 100%;
                    background-color: #a6dcee;
                    border-radius: inherit;
                    animation: loading2 3.5s ease both infinite;
                }

                @keyframes loading {
                    0% {
                        width: 16px;
                        transform: translateX(0px);
                    }

                    40% {
                        width: 100%;
                        transform: translateX(0px);
                    }

                    80% {
                        width: 16px;
                        transform: translateX(64px);
                    }

                    90% {
                        width: 100%;
                        transform: translateX(0px);
                    }

                    100% {
                        width: 16px;
                        transform: translateX(0px);
                    }
                }
                @keyframes loading2 {
                    0% {
                        transform: translateX(0px);
                        width: 16px;
                    }

                    40% {
                        transform: translateX(0%);
                        width: 80%;
                    }

                    80% {
                        width: 100%;
                        transform: translateX(0px);
                    }

                    90% {
                        width: 80%;
                        transform: translateX(15px);
                    }
                    100% {
                        transform: translateX(0px);
                        width: 16px;
                    }
                }
            }
        }
    }
</style>

<div id="feat-selector">
    <h1>Risk Model</h1>

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
        <div class="load-wrapper">
            <div class="loading">
                <p>Running...</p>
                <span />
            </div>
        </div>
    {:then respObj}
        {#if respObj != undefined}
            <ResultsGraphs input_data={JSON.parse(respObj)} />
        {/if}
    {:catch error}
        <p style="color: red">{error.message}</p>
    {/await}
</div>
