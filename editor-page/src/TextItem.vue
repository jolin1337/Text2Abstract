<template>
	<li v-bind:style="{borderRightColor: color}" @click="focusTextItem">
		<span v-if="item.text">{{shortedText(item.text)}}</span>
		<span v-else>{{item.textId}}</span>
	</li>
</template>

<script>
	export default {
		name: 'TextItem',
		props: {
			color: {
				type: String,
				default: '#aaa'
			},
			item: {
				type: Object,
				default: function() {
					return {text: "non text item"};
				}
			}
		},
		methods: {
			shortedText: function(text) {
				var shorted = text.substring(0, 30);
				return shorted + (shorted != text ? "..." : "");
			},
			focusTextItem: function() {
				this.$emit('focus', this.item);
			}
		}
	}
	// ref-397 (987)
</script>

<style>
	li {
		border-right: 3px solid #aaa;
		transition: border 0.6s, background-color 0.3s;
		-webkit-transition: border 0.6s, background-color 0.3s;
		-moz-transition: border 0.6s, background-color 0.3s;
		-o-transition: border 0.6s, background-color 0.3s;
		cursor: pointer;
	}
	li:hover {
		background-color: #ddd;
		border-right-width: 10px;
	}
</style>
