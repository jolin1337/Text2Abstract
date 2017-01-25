
var http = require('http');
var path = require('path');
var express = require('express');
var bodyParser = require('body-parser');
var async = require('async');
var crypto = require('crypto');

var router = express();
var server = http.createServer(router);

router.use(express.static(path.resolve(__dirname, 'client')));

const child_process = require('child_process');
const network = require('request');

router.post('/text2abstract/:algorithm', bodyParser.urlencoded({ extended: false }), function (request, response) {
	if (!request.body || !request.body.text) return response.sendStatus(400);
	var algorithm = request.params.algorithm;
	var text = request.body.text.replace(/\n/gm, ' ');
	var current_date = (new Date()).valueOf().toString();
	var random = Math.random().toString();
	var textId = crypto.createHash('sha1').update(text/*current_date + random*/).digest('hex');
	// var textId = new Date().getTime();
	//return response.end(JSON.stringify({"keywords": [{"label": 'Sport', "probability":0.9992}], "abstract": text}));
	async.parallel([
		function(callback) {
			var item = {
				textId: textId,
				originalText: text,
				type: 'original'
			};
			network({
				uri: (process.env.PRED_URI || 'http://localhost:3000') + '/text', 
				method: 'POST',
				form: item
			}, function(response) {
				// console.log(response); // Should be {success: true}
			});
			callback(false, {original: text});
		},
		function(callback) {
			if(algorithm == 'k-means')
				var classifier = child_process.spawn('../gensim/kmeans', ['../gensim/centroid.txt']);
			else
				var classifier = child_process.spawn('../fastText/fasttext', ['predict-prob', '../fastText/sv_model/all_model.bin', '-', '14'])
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
				if(certainKeywords.length == 0)
					certainKeywords = [keywords[0]];
				var item = {
					type: "keywords",
					textId: textId,
					keywords: certainKeywords
				};
				network.post({
					uri: (process.env.PRED_URI || 'http://localhost:3000') + '/text', 
					method: 'POST',
					form: item
				}, function(response) {
					// console.log(response); // Should be {success: true}
				});
				callback(false, {keywords: certainKeywords});
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

				var item = {
					type: "summary",
					textId: textId,
					text: newText
				};
				network.post({
					uri: (process.env.PRED_URI || 'http://localhost:3000') + '/text', 
					method: 'POST',
					form: item
				}, function(response) {
					// console.log(response); // Should be {success: true}
				});
				callback(false, {abstract: newText});
			})
		}
	], function(err, result) {
		response.end(JSON.stringify(Object.assign({}, result[1], result[2])));
	});
});

server.listen(process.env.DEMO_PORT || 8080, process.env.DEMO_IP || "0.0.0.0", function(){
	var addr = server.address();
	console.log("Server listening at", addr.address + ":" + addr.port);
});
