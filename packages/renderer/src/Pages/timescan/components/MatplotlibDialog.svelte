
<script>
    import HelperText from '@smui/textfield/helper-text';
    import Dialog, { Title, Content, Actions } from '@smui/dialog';
    import Button, { Label } from '@smui/button';
    import Textfield from '@smui/textfield';
    export let open = false;
    export let value;
</script>

<Dialog
    bind:open
    aria-labelledby="kinetics_plot_adjust_title"
    aria-describedby="kinetics_plot_adjust_content"
    surface$style='background: #8361bf; padding: 0.5rem;'
    >
    <Title style='color: #fff;' id="kinetics_plot_adjust_title">matplotlib</Title>
    <Content style='padding: 1rem;' id="kinetics_plot_adjust_content">
    <Textfield 
        style='min-height: 200px; width: 100%; max-height: 300px; max-width: 300px;' textarea bind:value label="Adjust plot"
    >
        <HelperText slot="helper">matplotlib subplot_adjust configs</HelperText>
    </Textfield>
    <Actions>
        <Button action="close">
            <Label>close</Label>
        </Button>
    </Actions>
    </Content>
</Dialog>