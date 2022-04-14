<script>
	import {running_processes} from "../svelteWritable";
	import DataTable, { Head, Body, Row, Cell } from '@smui/data-table';
	import { toast } from '@zerodevx/svelte-toast'
	export let toastId=""
</script>

<DataTable table$aria-label="current processes list" style="width: 100%;">
	<Head>
		<Row>
			<Cell>PID</Cell>
			<Cell>pyfile</Cell>
			<Cell></Cell>
		</Row>

	</Head>
	<Body>
		{#each $running_processes as process}
			<Row>
				<Cell>{process.pid}</Cell>
				<Cell>{process.pyfile}</Cell>
				<Cell><button class="button is-danger" style:background="#ff3860" on:click="{()=>process.kill()}">X</button></Cell>
			</Row>
		{/each}
		
	</Body>
</DataTable>
<br>
<button class="button is-link" on:click={()=>{toast.pop(toastId)}} style="background: #ff3860; float: right;" >Close</button>
