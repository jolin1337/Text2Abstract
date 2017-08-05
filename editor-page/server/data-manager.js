const Promise = require('promise');
const fs = require('fs');

const DATA_FILE = 'data.json';
const ORIGINAL_DATA_FILE = 'orignal-data.json';
let data = JSON.parse(fs.readFileSync(DATA_FILE).toString());
let originalData = JSON.parse(fs.readFileSync(ORIGINAL_DATA_FILE).toString());

 // Perhaps an action as a parameter could tell this method what to save instead of saving everything
 // And make this function async
function storeDM() {
  fs.writeFileSync(DATA_FILE, data);
  fs.writeFileSync(ORIGINAL_DATA_FILE, originalData);
}

function dm() {
  const objects = Object.keys(arguments);
  for(let i in arguments) 
    objects[parseInt(i)] = arguments[i];
  // objects = objects.map(function (key, index) { return arguments[index]; });

  function updateItem(item) {
    const newItems = objects.map(function (object) {
      if(typeof object !== "function") return false;
      const singleItem = object(item);
      if(typeof singleItem === "object" )
        return singleItem;
      return false;
    }).filter((o) => false !== o);

    if(newItems.length > 0) {
      const itemIds = newItems.map(function(item) { return item.textId; });
      data.items = data.items.filter(function(item) {
        return itemIds.indexOf(item.textId) === -1;
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
      let isPresent = true;
      for(let i in conditions)
        if(conditions[i] !== item[i])
          isPresent = false;
      return isPresent;
    }
  }

  /**
   * Save the data in the resource, when a modification has been made from the orignal data
   */
  this.save = function(newdata) {
    if(!(newdata instanceof Array)) newdata = [newdata];
    return new Promise(function(done, reject) {
      try {
        newdata.forEach(updateItem);
        storeDM();
        return done(data.items);
      } catch(e) {return reject(e);}
    });
  };
  /**
   * Fetch determined amount of data items
   */
  this.retrieve = function (query) {
    const old = query.old;
    const sourceData = (old ? originalData : data);
    let index = query.from || 0;
    const count = query.count || sourceData.items.length;
    let conditions = query.where;
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
    originalData.items.push(item);
    storeDM();
  };
}
module.exports = dm;