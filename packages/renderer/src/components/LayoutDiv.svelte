<script>
    export let id = window.getID()
    // export let active=false;
</script>

<div {id} class="main_content__div">
    <div class="header_content"><slot name="header_content__slot" /></div>
    <div class="main_content"><slot name="main_content__slot" /></div>

    <div class="footer_content">
        <div class="left align"><slot name="left_footer_content__slot" /></div>
        <div class="right align"><slot name="footer_content__slot" /></div>
    </div>
</div>

<style lang="scss">
    .main_content__div {
        display: grid;
        max-height: 100%;
        grid-template-rows: auto 1fr auto;
        height: 100%;
        gap: 1em;
        padding: 0;
        overflow-y: auto;
        .header_content {
            display: grid;
            grid-row-gap: 1em;
        }

        .main_content {
            overflow-y: scroll;
        }

        .footer_content {
            display: flex;
            gap: 1em;
            justify-content: flex-end;
            align-items: center;
            border-top: solid 1px;
            padding: 0.5rem;
            background-color: #8965c982;
            .right {
                justify-content: flex-end;
                flex-wrap: nowrap;
            }
        }
    }
</style>
