
<script>
    import {onMount} from "svelte";
    export let id="report", reportEditor;
    
    onMount(()=>{
        reportEditor = new Quill(`#${id}-editor-container`, {
        
            modules: {
                formula: true,
                syntax: true,
                toolbar: `#${id}-toolbar-container`
            
            },

            // placeholder: 'Compose an epic...',
        
            theme: 'snow'
        
        });
    })

</script>

<style global>

    .editor-container * { color: black; }

    .text-container {height: 30rem; width: 100%;}
    .ql-tooltip.ql-editing.ql-flip {
        left: -7.5px;
        top: 20.5px;
    }

    .ql-snow .ql-editor pre.ql-syntax {
        background-color: #4a4a4ae6;

        color: #fafafa;
    
    }
    
    .hljs-symbol, .hljs-attribute {color: #fafafa;}


    .toolbar-container {width: 100%;}
</style>



<div id="{id}-standalone-container" class="align editor-container" style="background-color: #fafafa; width: 75%;">
  <div id="{id}-toolbar-container" class="toolbar-container">
    <span class="ql-formats">
      <select class="ql-font"></select>
      <select class="ql-size"></select>
    </span>
    <span class="ql-formats">
      <button class="ql-bold"></button>
      <button class="ql-italic"></button>
      <button class="ql-underline"></button>
      <button class="ql-strike"></button>
    </span>
    <span class="ql-formats">
      <select class="ql-color"></select>
      <select class="ql-background"></select>
    </span>
    <span class="ql-formats">
      <button class="ql-script" value="sub"></button>
      <button class="ql-script" value="super"></button>
    </span>
    <span class="ql-formats">
      <button class="ql-header" value="1"></button>
      <button class="ql-header" value="2"></button>
      <button class="ql-blockquote"></button>
      <button class="ql-code-block"></button>
    </span>
    <span class="ql-formats">
      <button class="ql-list" value="ordered"></button>
      <button class="ql-list" value="bullet"></button>
      <button class="ql-indent" value="-1"></button>
      <button class="ql-indent" value="+1"></button>
    </span>
    <span class="ql-formats">
      <button class="ql-direction" value="rtl"></button>
      <select class="ql-align"></select>
    </span>
    <span class="ql-formats">
      <button class="ql-link"></button>
      <button class="ql-image"></button>
      <button class="ql-video"></button>
      <button class="ql-formula"></button>
    </span>
    <span class="ql-formats">
      <button class="ql-clean"></button>
      
    </span>
  </div>
  <div id="{id}-editor-container" class="text-container"></div>

</div>