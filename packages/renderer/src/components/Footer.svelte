<script>
	import {running_processes} from "../svelteWritable";
	import RunningProcess from "./RunningProcess.svelte";
	import { toast } from '@zerodevx/svelte-toast'
	const show_process = () => {

		toast.push({
			component: {
				src: RunningProcess, // where `src` is a Svelte component
				// props: {},
				sendIdTo: 'toastId' // send toast id to `toastId` prop
			},

			dismissable: false,
			initial: 0,
			theme: {
				'--toastPadding': '0',
				'--toastMsgPadding': '0',
				'--toastWidth': '40rem',
				'--toastContainerLeft': 'auto',
				'--toastContainerRight': '1rem',
			}
		})
	}

	$: console.log({$running_processes});
</script>

<nav class="navbar is-fixed-bottom animated fadeInUp" id="footer">
	
	<div class="navbar-menu">
	
		<div class="navbar-start">
			<div class="navbar-item"><p>Developed at Dr.Br&uuml;nken's group FELion@FELIX</p></div>
		</div>
	
		<div class="navbar-end">
			{#if $running_processes.length}
				<div class="navbar-item" on:click={show_process} style="cursor: pointer;">
					<p>Running {$running_processes.length} {$running_processes.length > 1 ? 'processes': 'process'}</p>
				</div>
			{/if}
			<div class="navbar-item"><p>2019-{new Date().getFullYear()} &copy; AN Marimuthu</p></div>

		</div>
	</div>

</nav>
