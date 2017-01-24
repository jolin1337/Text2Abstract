function original(item) {
	var thisItemType = original.ItemType;
	if(item.type == thisItemType || (item.type instanceof Array && item.type.indexOf(thisItemType) > -1))
		return {
			type: thisItemType,
			textId: item.textId,
			originalText: item.originalText,
			color: item.color
		};
	return false;
}
original.ItemType ="original";

module.exports = original;