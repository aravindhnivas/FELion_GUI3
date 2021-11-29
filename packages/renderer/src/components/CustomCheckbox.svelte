
<script>
  import Checkbox from '@smui/checkbox';
  import FormField from '@smui/form-field';

  export let selected = false, label="Check me", style=""
</script>

<FormField {style}>
  <Checkbox bind:checked={selected} />
  <span slot="label">{label}</span>
</FormField>