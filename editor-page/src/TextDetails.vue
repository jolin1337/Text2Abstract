<template>
	<div class="detail-container">
		<div v-if="textItem">
			<h2><a :href="'#' + textItem.textId">{{textItem.title || textItem.textId}}</a></h2>
			<text-summary v-if="isSummary" :text-item="textItem" :editable="editable"></text-summary>
			<hr v-if="isSummary && isKeywords" />
			<div class="keyword-section">
				<input type="text" name="keyword" @keydown="addNewCategory" placeholder="Lägg till en ny saknad kategori" class="new-category">
				<text-chip v-if="isKeywords" v-for="keyword in textItem.keywords" :editable="editable" :keyword="keyword" @remove-chip="removeKeyword">
				</text-chip>
			</div>
			<hr v-if="isSummary || isKeywords" />
		</div>
	</div>
</template>

<script>
import TextSummary from './TextSummary.vue'
import TextChip from './TextChip.vue'

export default {
	name: 'detail',
	components: {
		"text-summary": h => h(TextSummary),
		"text-chip": h => h(TextChip)
	},
	props: {
		textItem: {
			type: Object,
			default: null
		},
		editable: Boolean
	},
	computed: {
		isSummary: function() {
			console.log(this.textItem);
			return this.textItem.type.indexOf('summary') > -1;
		},
		isKeywords: function() {
			return this.textItem.type.indexOf('keywords') > -1;
		}
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
		removeKeyword: function(keyword) {
			var index = this.textItem.keywords.indexOf(keyword);
			this.textItem.keywords.splice(index, 1);
		},
		addNewCategory: function (event) {
			if(event.key === "Enter" && typeof event.target.value !== "undefined" && event.target.value.length > 0) {
				var newKeyword = {label: event.target.value, probability: -1};
				var matchingKeywords = this.textItem.keywords.filter(function(keyword) {
					return keyword.label === newKeyword.label;
				});
				if(matchingKeywords.length == 0) {
					event.target.value = "";
					this.textItem.keywords.push(newKeyword);
				}
			}
		}
	}
}
</script>

<style>
h2:hover a {
	position: relative;
	text-decoration: none;
	display: block;
}
h2:hover a:before {
	content: '#';
	position: absolute;
	left: -15px;
}
.detail-container {
	margin: 20px 10%;
	box-sizing: border-box;
}
.detail-container .keyword-section {
	padding: 10px;
}

.detail-container .new-category {
	width: 100%;
	padding: 10px;
	box-sizing: border-box;
	margin-bottom: 10px;
}
</style>