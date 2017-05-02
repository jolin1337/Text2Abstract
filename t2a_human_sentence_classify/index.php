<?php 
define('EOL', "\n");

class SentenceData {
	private $sentenceFile = "data/lead-language.sv";
	private $configFile = "data/config.txt";
	private $classifyFile = "data/classifies.txt";
	
	private $currentSentence = 0;
	private $fileIterations = 0;
	private $totalSentences = 0;
	private $reversedOrder = 0;
	
	function __construct() {
		$configData = file_get_contents($this->configFile);
		if($configData !== false) {
			$configData = explode(EOL, $configData);
			foreach($configData as $param) {
				$param = explode('=', $param);
				if(count($param) < 2) continue;
				if($param[0] == 'totalSentences')
					$this->totalSentences = (int)$param[1];
				else if($param[0] == 'fileIterations')
					$this->fileIterations = (int)$param[1];
				else if($param[0] == 'currentSentence')
					$this->currentSentence = (int)$param[1];
				else if($param[0] == 'reversedOrder')
					$this->reversedOrder = (int)$param[1];
			}
			if($this->totalSentences == 0) {
				$this->updateSentenceCount();
			}
		}
	}
	
	function close() {
		$configData = "";
		$configData .= "totalSentences=" . $this->totalSentences . EOL;
		$configData .= "fileIterations=" . $this->fileIterations . EOL;
		$configData .= "currentSentence=" . $this->currentSentence . EOL;
		//file_put_contents($this->configFile, $configData, FILE_APPEND | LOCK_EX);
		
		file_put_contents($this->configFile, $configData, LOCK_EX);
	}
   
	public function getNewSentence($goToNextSentence=true) {
		$encodedSentences = explode(EOL, file_get_contents($this->sentenceFile));
		$decodedSentences = explode(EOL, file_get_contents($this->sentenceFile . '.decoded'));
		if ($goToNextSentence) {
			$this->currentSentence = ($this->getCurrentSentence() + 1) % $this->getTotalNumberOfSentences();
			if ($this->currentSentence == 0) $this->fileIterations++;
		}
		foreach ($encodedSentences as $key => $value) {
			if ($key >= $this->getCurrentSentence()+1) break;
		}
		return (object)array(
			'totalSentences' => $this->getTotalNumberOfSentences(),
			'currentSentence' => $this->getCurrentSentence(),
			'fileIterations' => $this->getFileIterations(),
			'name_default' 	=> $encodedSentences[$key],
			'name_predict' 	=> $decodedSentences[$key],
			'id'	=> $this->currentSentence
		);
	}
	
	public function updateSentenceCount() {
		$sentences = explode(EOL, file_get_contents($this->sentenceFile));
		$this->totalSentences = count($sentences);
		return $this->totalSentences;
	}
	public function classifySentence($id, $classify) {
		$sentences = explode(EOL, file_get_contents($this->classifyFile));
		$found = False;
		foreach ($sentences as $key => $value) {
			$value = explode('"§§"', substr($value, 1, -1));
			if ($key === 0) {
				$headings = array();
				foreach ($value as $index => $attr) {
					$headings[$attr] = $index;
				}
			}
			if ($key === $id || $value[$headings['uuid']] === $id) {
				$value[$headings['class']] = ($value[$headings['class']] ? $value[$headings['class']] . ';' : '') . $classify;
				$sentences[$key] = '"' . implode('"§§"', $value) . '"';
				$found = True;
			}
		}
		if (!$found) {
			$newValue = array();
			$newValue[$headings['uuid']] = $id;
			$newValue[$headings['class']] = $classify;
			$sentences[] = '"' . implode('"§§"', $newValue) . '"';
		}
		file_put_contents($this->classifyFile, implode(EOL, $sentences));
	}
	
	public function getTotalNumberOfSentences() {
		return $this->totalSentences;
	}
	public function getCurrentSentence() {
		return $this->currentSentence;
	}
	public function getFileIterations() {
		return $this->fileIterations;
	}
}

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
$sentenceData = new SentenceData();
if(isset($_POST['sentence_id'], $_POST['sentence_class'])) {
	$sentenceData->classifySentence($_POST['sentence_id'], $_POST['sentence_class']);
	
	//if(isset($_POST['first']) && $_POST['first'] == '1')
	//	$sentenceData->getNewSentence(true);
	$sentence = $sentenceData->getNewSentence(true);
	echo json_encode($sentence);
}
else {
	$sentence = $sentenceData->getNewSentence(false);
	include ('index-page.php');
}
$sentenceData->close();

 ?>