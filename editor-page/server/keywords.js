
function keywords(item) {
	var thisItemType = keywords.ItemType;
	if(item.type == thisItemType || (item.type instanceof Array && item.type.indexOf(thisItemType) > -1))
		return {
			type: thisItemType,
			textId: item.textId,
			keywords: item.keywords
		};
	return false;
}
keywords.ItemType ="keywords";
module.exports = keywords;