function summary(item) {
	var thisItemType = summary.ItemType;
	if(item.type == thisItemType || (item.type instanceof Array && item.type.indexOf(thisItemType) > -1))
		return {
			type: thisItemType,
			textId: item.textId,
			text: item.text
		};
	return false;
}
summary.ItemType ="summary";

module.exports = summary;