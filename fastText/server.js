
var http = require('http');
var path = require('path');
var express = require('express');
var bodyParser = require('body-parser');
var async = require('async');

var router = express();
var server = http.createServer(router);

router.use(express.static(path.resolve(__dirname, 'client')));

const child_process = require('child_process');


router.post('/fetch_categories', bodyParser.urlencoded({ extended: false }), function (request, response) {
	if (!request.body || !request.body.text) return response.sendStatus(400);
	var text = request.body.text.replace(/\n/gm, ' ');
	//return response.end(JSON.stringify({"keywords": [{"label": 'Sport', "probability":0.9992}], "abstract": text}));
	async.parallel([function(callback) {
		const classifier = child_process.spawn('./fasttext', ['predict-prob', 'sv_model/all_model.bin', '-', '14'])
		//classifier.on("error", function(e) {console.log(":(");callback(true, {});});
		classifier.stdin.setEncoding('utf-8');
		classifier.stdin.write(text + "\n");
		classifier.stdin.end();
		var predictions = '';
		classifier.stdout.on('data', (prediction) => {
			predictions += prediction; //'__label__Sport 0.33213 __label__Ekonomi 0.5432123 __label__Hästar 0.343232';
		});
		classifier.on('exit', function() {
			var keywords = predictions.split('__label__');
			keywords.shift();
			keywords = keywords.map(function(prediction) {
				var predSplit = prediction.split(' ');
				return {
					label: predSplit[0],
					probability: parseFloat(predSplit[1])
				}
			}).sort(function(a, b) {return b.probability - a.probability});
			var certainKeywords = keywords.filter(function(prediction) {
				return prediction.probability > 1/keywords.length;
			})
			if(certainKeywords.length > 0)
				callback(false, {keywords: certainKeywords});
			else
				callback(false, {keywords: [keywords[0]]});
		});
	}, function(callback) {
		//callback(false, {abstract: text});
		//return "";
		const abstracter = child_process.spawn('python', ['../gensim/abstract.py', '-'])
		abstracter.stdin.setEncoding('utf-8');
		abstracter.stdin.write(text + "\n");
		var newText = "";
		abstracter.stdout.on('data', (moreText) => {
			newText += moreText;
		});
		abstracter.on('exit', function () {
			callback(false, {abstract: newText});
		})
	}], function(err, result) {
		console.log(result);
		response.end(JSON.stringify(Object.assign({}, result[0], result[1])));
	});
});

server.listen(process.env.PORT || 3000, process.env.IP || "0.0.0.0", function(){
	var addr = server.address();
	console.log("Server listening at", addr.address + ":" + addr.port);
});
