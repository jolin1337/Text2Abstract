<!DOCTYPE html>
<html>
<head>
	<meta charset="utf8">
	<title>Klassificera meningar - av Michelle Ludovici</title>
	<link rel="stylesheet" type="text/css" href="styles.css">
</head>
<body>
<div id="background">
	<img src="wordcloud.svg" />
</div>
<div id="main">
	<div id="about">
		<p>Mitt namn är Johannes Lindén och jag är en master student på Mittuniversitetet i årskurs 5.
		</p>
		<p>Jag undersöker hur Long Short Term Memory (LSTM) algorithmen presterar i uppgiften att skriva om små texter med andra ord men samma betydelse. För att se hur bra programmet fungerar, så vill jag gärna jämföra med hur bra ni (en oberoende part) tycker att denna algoritm fungerar. Var vänlig och betygsätt meningarna genom att välja på skalan och sen trycka på knappen 'Betygsätt'.
		</p>
		<p>OBS! Det går tyvärr inte att ångra sig i efterhand. Jag uppskattar att ni betygsätter så många meningar som möjligt. Meningarna är hämtade från lokaltidningar i sverige.
		</p>
		<p>Ni får gärna kontakta mig angående studien genom att skriva till <a href="mailto:joli1230@student.miun.se">joli1230@student.miun.se</a>.
		</p>
		<p>Tack så mycket!</p>
	</div>
	<div id="polarity">
		<!-- Väldigt Negativt - Negativt - Neutralt - Positivt - Väldigt positivt -->
		<canvas class="sentence"></canvas>
	</div>
	<div id="applySentenceForm">
		<div id="sentence_field" class="sentence">
			<?php echo $sentence->name_default; ?>
			<hr/>
			<?php echo $sentence->name_predict; ?>
		</div>
		<button onclick="submit()">Betygsätt</button>
		Itereringar av alla texter <span id="fileIterations"><?php echo $sentenceData->getFileIterations(); ?></span><br/>
		Vänligen betygsätt text <span id="status"><?php echo ($sentenceData->getCurrentSentence()+1) . ' av ' . $sentenceData->getTotalNumberOfSentences(); ?></span>
	</div>
</div>
<script type="text/javascript">
var sentenceData = {
	name: document.getElementById("sentence_field").innerHTML,
	id: <?php echo $sentence->id; ?>,
	firstTime: 1
}
var elStatus = document.getElementById('status');
var statusSentences = elStatus.innerText.split("/");
var fileIterations = document.getElementById('fileIterations').innerHTML;
function processNewSentence() {
	console.log(this.responseText)
	var newSentence = JSON.parse(this.responseText);
	sentenceData.name = newSentence.name_default + "<hr/>" + newSentence.name_predict;
	sentenceData.id = newSentence.id;
	sentenceData.firstTime = 0;
	document.getElementById("sentence_field").innerHTML = sentenceData.name;
	
	// statusSentences[0] = parseInt(statusSentences[0]) + 1;
	// if(statusSentences[0] > parseInt(statusSentences[1])) {
	// 	fileIterations = parseInt(fileIterations) + 1;
	// 	statusSentences[0] = 1;
	// }
	// console.log(typeof statusSentences);
	document.getElementById('fileIterations').innerHTML = newSentence.fileIterations;//"" + fileIterations;
	document.getElementById('status').innerHTML = (newSentence.currentSentence+1) + " / " + newSentence.totalSentences;//statusSentences[0] + "/" + statusSentences[1];
}
function submit () {
	var params = "sentence_id=" + sentenceData.id 
					+ "&sentence_class=" + targetPolarity 
					+ "&first=" + sentenceData.firstTime;
	var request = new XMLHttpRequest();
	request.addEventListener("load", processNewSentence);
	request.open("POST", location.href);
	request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	// request.setRequestHeader("Content-length", params.length);
	// request.setRequestHeader("Connection", "close");
	request.send(params);
}
</script>
<script type="text/javascript" src="http://localhost/t2a_human_sentence_classify/script.js"></script>
</body>
</html>