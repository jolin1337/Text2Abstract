var Promise = require('promise');

var data = {
	items: [{
		textId: "aaa",
		text: "Default red Test 1",
		type: "summary",
		color: "#00f"
	},{
		textId: "bbb",
		text: "Default green Test 2",
		type: "summary",
		color: "#0f0"
	}, {
		textId: "aaa",
		type: "keywords",
		keywords: [{label: "Hästar", probability: 1.0}, {label: "Sport", probability: 0.5}, {label: "Ekonomi", probability: 0.0}]
	}, {
		textId: "bbb",
		type: "keywords",
		keywords: [{label: "Testing", probability: 0.5}]
	}]
};
var oldData = {items: []};
for(var i in data.items) 
	oldData.items.push(data.items[i]);

function dm(options) {
	var opt = Object.assign({
		// Default values
	}, options);
	var objects = Object.keys(arguments);
	for(var i in arguments) 
		objects[parseInt(i)] = arguments[i];
	// objects = objects.map(function (key, index) { return arguments[index]; });

	function updateItem(item) {
		var newItems = [];
		objects.forEach(function (object) {
			if(typeof object !== "function") return;
			var singleItem = object(item);
			if(typeof singleItem == "object" )
				newItems.push(singleItem);
		});
		if(newItems.length > 0) {
			var itemIds = newItems.map(function(item) {return item.textId});
			data.items = data.items.filter(function(item) {
				return itemIds.indexOf(item.textId) == -1;
			});
			data.items.unshift.apply(data.items, newItems);
		}
		else {
			// Clear them?
			data.items.splice(0, data.items.length);
		}
	}
	/** Returns true if the item mathes the given the conditions **/
	function filterConditions(conditions) {
		return function(item) {
			var isPresent = true;
			for(var i in conditions)
				if(conditions[i] !== item[i])
					isPresent = false;
			return isPresent;
		}
	}

	/**
	 * Save the data in the resource
	 */
	this.save = function(newdata) {
		if(newdata instanceof Array) {
			return new Promise(function(done, reject) {
				try {
					newdata.forEach(updateItem);
					// TODO Save to data source
					return done(data.items);
				} catch(e) {return reject(e);}
			});
		}
		else {
			updateItem(newdata);
			return new Promise(function(done, reject) {
				// TODO Save to data source
				return done(data.items);
			});
		}
	};
	/**
	 * Fetch determined amount of data items
	 */
	this.retrieve = function (query) {
		var old = query.old;
		var sourceData = (old ? oldData : data);
		var index = query.from || 0;
		var count = query.count || sourceData.items.length;
		var conditions = query.where;
		if(typeof conditions != "object") conditions = {};
		if(typeof from == "object") {
			index = sourceData.items.indexOf(from);
		}
		index = parseInt(index);
		return new Promise(function(done, reject) {
			if(isNaN(index)) return reject({invalidIndex: index});
			return done(sourceData.items.slice(index, index + count)
								  .filter(filterConditions(conditions))
						);
		});
	};
	this.add = function (item) {
		// TODO: verify item somehow maybe with objects (original, summary or keywords)
		data.items.push(item);
		oldData.items.push(item);
	};
}
module.exports = dm;