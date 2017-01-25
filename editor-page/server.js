var original = require("./server/original");
var summaries = require("./server/summaries");
var keywords = require("./server/keywords");
var dataManager = require('./server/data-manager');

var config = require("./webpack.config");
var webpack = require("webpack");
var path = require("path");
var WebpackDevServer = require("webpack-dev-server");
// config.entry.src.unshift("webpack-dev-server/client?http://localhost:3000/", "webpack/hot/dev-server");
var compiler = webpack(config);
var server = new WebpackDevServer(compiler, {
    contentBase: path.resolve(__dirname, './build/'),
    stats: { colors: true },
	hot: true
});

var dm = new dataManager({}, original, summaries, keywords);
var bp = require('body-parser');
server.app.use(bp.urlencoded({ extended: true }), bp.json());
server.app.get('/texts', function (request, response) {
	// TODO: implement a slice array function to remove all items before the from parameter in request.query
	var from = request.query.from || 0; 
	var count = request.query.count || 0; 
	dm.retrieve({from: from, count: count}).then(function(items) {
		items.sort((a, b) => { return a.textId < b.textId; });
		response.end(JSON.stringify({ items: items }));
	}).catch(function(e) {
		response.status(401).end(JSON.stringify({ error: true, about: e }));
	});
});
server.app.get('/text', function (request, response) {
	// TODO: implement a slice array function to remove all items before the from parameter in request.query
	var textId = request.query.textId;
	var textOld = request.query.old;
	dm.retrieve({old: textOld, where: {textId: textId}}).then(function(items) {
		// items.sort((a, b) => { return a.textId < b.textId; });
		response.end(JSON.stringify({items: items}));
	}).catch(function(e) {
		response.status(401).end(JSON.stringify({ error: true, about: e }));
	});
});
server.app.post('/save', function (request, response) {
	dm.save(request.body.items).then(function(items) {
		items.sort((a, b) => { return a.textId < b.textId; });
		response.end(JSON.stringify({ items: items }));
	}).catch(function(e) {
		response.end(JSON.stringify({ error: false, about: e }));
	});
});

server.app.post('/text', function(request, response) {
	var item = request.body;
	if(typeof item == "object")
		dm.add(item);
	response.end('{"success": true}');
});

server.listen(process.env.PRED_PORT || 3000);