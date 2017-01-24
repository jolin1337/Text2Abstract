<template>
	<div class="text-section">
		<div class="text-edit" v-if="editable">
			<textarea v-model="textItem.text"></textarea>
		</div>
		<div class="text-preview" v-else>{{textItem.text}}</div>
	</div>
</template>
<script>
	
export default {
	name: 'text-summary',
	props: {
		textItem: {
			type: Object,
			required: true
		},
		editable: Boolean
	}
}
</script>

<style>
.text-section {
	padding: 10px;
	box-sizing: border-box;
}
.text-section textarea {
	width: 100%;
	max-width: 100%;
	min-width: 100%;
	font-style: italic;
}
</style>