<script>
    // @ts-nocheck
    const filetype = getContext('filetype')
    $: console.warn(getContext('filetype'))
    onMount(async () => {
        const el = document.getElementById(`${filetype}-chrome-tabs`)
        const chromeTabs = new ChromeTabs()
        chromeTabs.init(el)
        console.warn(chromeTabs)
        chromeTabs.addTab()
    })
</script>

<div
    id="{filetype}-chrome-tabs"
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
                // background-image: url(/assets/svgs/close.svg);
                &:hover {
                    background-color: var(--color-danger);
                }
            }
        }
    }
</style>
