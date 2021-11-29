<script>
    import Moveable from "svelte-moveable";
    export let target;

    const onResizeStart = (details) => console.log(details)
    const onResize = (details) => console.log(details)
    const onResizeEnd = (details) => console.log(details)
</script>

<Moveable
  target={target}
  origin={true}
  edge={false}

  keepRatio={false}
  renderDirections={["nw", "ne", "sw", "se", "n", "w", "s", "e"]}

  resizable={true}
  throttleResize={0}
  on:resizeStart={({ detail }) => onResizeStart(detail)}
  on:resize={({ detail }) => onResize(detail)}
  on:resizeEnd={({ detail }) => onResizeEnd(detail)}

/>