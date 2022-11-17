<script>
    // @ts-nocheck
    export let id = window.getID()

    onMount(async () => {
        const el = document.getElementById(`${id}-chrome-tabs`)
        const chromeTabs = new ChromeTabs()
        chromeTabs.init(el)
        // console.warn(chromeTabs)
        chromeTabs.addTab()
    })
</script>

<div
    id="{id}-chrome-tabs"
    class="chrome-tabs"
    style="--tab-content-margin: 9px"
    on:activeTabChange
    on:tabAdd
    on:tabRemove
>
    <div class="chrome-tabs-content" />
</div>

<style lang="scss" global>
    .chrome-tabs {
        background: var(--color-primary-light);
        border-radius: 0;
        .chrome-tab {
            .chrome-tab-title {
                color: white;
            }
            &[active] {
                .chrome-tab-title {
                    color: black;
                }
            }

            .chrome-tab-close {
                &:hover {
                    background-color: var(--color-danger);
                }
            }
        }
    }
</style>
