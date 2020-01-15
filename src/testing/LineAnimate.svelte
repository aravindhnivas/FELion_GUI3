<script>
  import LinearProgress from '@smui/linear-progress';
  // import someAsyncAction from './someAsyncAction.js';

  let closed = true;

  // someAsyncAction(() => {
  //   closed = true;
  // });
</script>

<div class="line" style=""><LinearProgress indeterminate {closed} /></div>