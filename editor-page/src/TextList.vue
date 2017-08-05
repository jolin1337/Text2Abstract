<template>
	<ul>
	<text-item v-for="item in items" :item="item" :color="item.color" v-on:focus="focusTextItem">
	</text-item>
	</ul>
</template>
<script>    
import TextItem from './TextItem.vue'
import request from './libs/request.js'

var sources = {};
var currentSource = "tmp";


export default {
	name: 'text-list',
  components: {
		"text-item": h => h(TextItem)
  },
	props: {
		src: String,
		query: String,
	},
	events: {
		setSource: function(src) {
			this.setSource(src || currentSource);
		}
	},
  methods: {
		focusTextItem: function (item) {
			this.$emit('focus', item);
		},
		setSource: function(src) {
			var self = this;
			// The "from" flag is there to tell the server to load all items/texts from a specific text index
			return request.get(location.origin + '/texts?from=0', function (texts) {
				currentSource = src;
				sources[src] = texts.items;
				// this.src = src;
				self.items = self.updateSource(texts);
			});
		},
		resetItem: function(item) {
			var self = this;
			return request.get(location.origin + '/text?textId=' + item.textId, function (texts) {
				var oldItem = self.updateSource(texts);
				for(var i in oldItem[0]) {
					item[i] = oldItem[0][i];
				}
			});
		},
		saveItems: function() {
			var self = this;
			return request.post(location.origin + '/save', { items: this.items }, function (texts) {
				sources[currentSource] = texts.items;
				// this.src = src;
				var items = self.updateSource(texts);
				self.items.splice(0, self.items.length);
				self.items.push.apply(self.items, items);
			});
		},
		updateSource: function(data) {
			var hashStr = location.hash.substr(1);
			var res = {items: []};
			for(var i in data.items) {
				var item = data.items[i];
				if(typeof item == "undefined") continue;

				if(hashStr == item.textId)
					hashStr = item;

				if(typeof item.textId != "undefined") {
					for(var j in data.items) {
						if(typeof data.items[j] == "undefined") continue;
						if(item.textId == data.items[j].textId) {
							var itemType = item.type;
							var otherItemType = data.items[j].type;
							item = Object.assign(item, data.items[j]); 

							if(itemType instanceof Array) {
								itemType.push(otherItemType);
							} else itemType = [itemType];

							item.type = itemType;
							data.items[j] = undefined;
						}
					}
				}
				res.items.push(item);
			}
			if(typeof hashStr !== "string") {
				this.$emit('focus', hashStr);
			} else if(res.items.length > 0) {
				this.$emit('focus', res.items[0]);
			}
			return res.items;
		}
  },
	data: function() {
		var items = {};
		if(typeof sources[currentSource] !== "undefined") {
			items = this.updateSource(sources[currentSource]);
		} else {
			items = [];
			this.setSource(currentSource);
		}
		return {
			items: items
		};
		// return this.setSource("");
	}
}
</script>

<style>
	
ul {
	list-style-type: none;
	padding: 0;
	margin: 0;
}

li {
	display: block;
	padding: 10px;
	margin-bottom: 6px;
}
</style>