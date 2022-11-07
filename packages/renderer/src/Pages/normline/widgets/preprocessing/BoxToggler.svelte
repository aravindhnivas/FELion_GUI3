<div class="top-nav">
    <div class="control felix animate__animated animate__bounce" />
    <div class="control opo animate__animated animate__bounce" class:hide={!$opoMode} />
    <div class="control theory animate__animated animate__bounce" class:hide={!$theoryRow} />
</div>

<style lang="scss">
    .top-nav {
        display: flex;
        flex-direction: column;
        gap: 1em;
        padding: 3px;
        width: 25px;
        height: 110px;
        border: 1px solid;
        position: absolute;
        top: 5rem;
        left: 19em;
        z-index: 99;
        border-radius: 20px;
        place-content: center;
        place-items: center;
        .control {
            display: flex;
            place-content: center;
            cursor: pointer;
            width: 20px;
            height: 20px;
            border-radius: 1em;
            position: relative;
        }

        .felix {
            background-color: rgba(98 73 165);
        }
        .opo {
            background-color: rgba(255, 169, 77, 0.4);
        }
        .theory {
            background-color: rgba(119, 186, 248, 0.5);
        }
    }
</style>
