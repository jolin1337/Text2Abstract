<template>
	<span class="keyword" v-bind:style="{borderColor: valueToRGBcolor(keyword.probability)}">
		{{keyword.label}}
		<span v-if="editable" class="remove" @click="remove">X</span>
		<div class="probability">
			{{keyword.probability < 0 ? "Manuell" : Math.round(keyword.probability * 100 * 1000) / 1000 + ' %'}}
		</div>
	</span>
</template>
<script>

export default {
	name: 'text-chip',
	props: {
		keyword: { type: Object, required: true },
		editable: Boolean
	},
	methods: {
		valueToRGBcolor: function(value) {
			var alpha = 0.7;
			if(value < 0 || value > 1) return "rgba(100, 100, 100, " + alpha + ")";
			// value = Math.max(Math.min(value, 1), 0); // make the interval [0, 1]
			var redAmount = Math.min(2 * (1 - value), 1);
			var greenAmount = Math.min(value * 2, 1);
			var res = "rgba(" + parseInt(redAmount * 200) + ", " + parseInt(greenAmount * 255) + ", 0, " + alpha + ")";
			return res;
		},
		remove: function () {
			console.log("destroy");
			this.$emit('remove-chip', this.keyword);
			// this.show = false;
			// this.$destroy(true);
		}
	}
}
</script>

<style>

.keyword {
	position: relative;
	border: 6px double transparent;
	box-shadow: 0 0 15px rgba(0,0,0,0.4);
	border-radius: 25px;
	padding: 10px;
	margin: 5px;
	display: inline-block;
	text-align: center;
}
.keyword .remove {
	cursor: pointer;
	border: 1px solid #ccc;
	width: 15px;
	height: 15px;
	overflow: hidden;
	border-radius: 8px;
	display: inline-block;
}
.keyword .probability {
	position: absolute;
	bottom: -60px;
	left: 0;
	width: 100%;
	height: 0;
	padding: 0;
	margin: 0;
	opacity: 0;
	overflow: hidden;
	z-index: 10;
	background-color: white;

	transition: opacity 0.4s;
	-webkit-transition: opacity 0.4s;
	-moz-transition: opacity 0.4s;
	-o-transition: opacity 0.4s;

	transition-delay: 0.4s;
	-webkit-transition-delay: 0.4s;
	-moz-transition-delay: 0.4s;
	-o-transition-delay: 0.4s;
	visibility: visible;
}
.keyword:hover .probability {
	height: auto;
	opacity: 1;
	padding: 10px; 
	border: 1px solid #999;
}
</style>