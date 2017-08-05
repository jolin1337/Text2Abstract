import psutil
import subprocess

class ProcessTimer:
	def __init__(self,command):
		self.command = command
		self.execution_state = False

	def execute(self):
		self.max_vms_memory = 0
		self.max_rss_memory = 0

		self.t1 = None
		try:
			self.t0 = time.time()
			self.p = subprocess.Popen(self.command,shell=False)
		except Exception as e:
			print e, self.command
		self.execution_state = True

	def poll(self):
		if not self.check_execution_state():
			return False

		self.t1 = time.time()

		try:
			pp = psutil.Process(self.p.pid)

			#obtain a list of the subprocess and all its descendants
			descendants = list(pp.children(recursive=True))
			descendants = descendants + [pp]

			rss_memory = 0
			vms_memory = 0

			#calculate and sum up the memory of the subprocess and all its descendants 
			for descendant in descendants:
				try:
					mem_info = descendant.memory_info()

					rss_memory += mem_info[0]
					vms_memory += mem_info[1]
				except psutil.NoSuchProcess:
					#sometimes a subprocess descendant will have terminated between the time
					# we obtain a list of descendants, and the time we actually poll this
					# descendant's memory usage.
					pass
			self.max_vms_memory = max(self.max_vms_memory,vms_memory)
			self.max_rss_memory = max(self.max_rss_memory,rss_memory)

		except psutil.NoSuchProcess:
			return self.check_execution_state()


		return self.check_execution_state()


	def is_running(self):
		return psutil.pid_exists(self.p.pid) and self.p.poll() == None
	def check_execution_state(self):
		if not self.execution_state:
			return False
		if self.is_running():
			return True
		self.executation_state = False
		self.t1 = time.time()
		return False

	def close(self,kill=False):

		try:
			pp = psutil.Process(self.p.pid)
			if kill:
				pp.kill()
			else:
				pp.terminate()
		except psutil.NoSuchProcess:
			pass

from subprocess import Popen
import datetime
import time

paramsValues = [
	"--learning_rate", [0.5],
	"--learning_rate_decay_factor", [0.99],
	"--max_gradient_norm", [5.0],
	"--batch_size", [8, 16, 32, 64],
	"--size", [64, 128, 256],
	"--num_layers", [1, 2, 3, 4],
	"--from_vocab_size", [20000, 30000, 40000, 50000, 60000],
	"--to_vocab_size", [20000, 30000, 40000, 50000, 60000],
	"--data_dir", ["../../../../trained-sources/"],
	"--train_dir", ["../../../../trained-sources/"],
	"--from_train_data", ["../../../../trained-sources/body-language.sv"],
	"--to_train_data", ["../../../../trained-sources/lead-language.sv"],
	"--from_dev_data", ["../../../../trained-sources/body-language.sv"],
	"--to_dev_data", ["../../../../trained-sources/lead-language.sv"],
	"--max_train_data_size", [1000000, 1500000, 2000000],
	"--steps_per_checkpoint", [100],
	"--decode", [False],
	"--self_test", [False],
	"--use_fp16", [False]
]

def oneParamConvert(param):
	if isinstance(param, list):
		return param[0]
	return param

def runTest(params):
	ptimer = ProcessTimer(['python', 'translate.py'] + [str(param) for param in params])
	try:
		prevTimestamp = time.time()
		ptimer.execute()
		#poll as often as possible; otherwise the subprocess might 
		# "sneak" in some extra memory usage while you aren't looking
		while ptimer.poll():
			time.sleep(.5)
			if prevTimestamp + 10 < time.time():
				prevTimestamp = time.time()
				print prevTimestamp, ptimer.max_vms_memory >> 20, ptimer.max_rss_memory >> 20, ptimer.max_vms_memory + ptimer.max_rss_memory >> 20
	finally:
		#make sure that we don't leave the process dangling?
		ptimer.close()

for i in range(0, len(paramsValues)/2, 1):
	currentParams = [oneParamConvert(param) for param in paramsValues]
	for j, paramValue in enumerate(paramsValues[i * 2 + 1]):
		if i != 0 and j == 0: continue
		currentParams[i * 2 + 1] = paramValue
		runTest(currentParams)
	# p = Popen(['python', 'tensorflow-models/tutorials/rnn/translate/translate.py'] + currentParams)
	# myProc.read() # Read standard-out
	# startTime = time.time() # Get start time in secounds
	# p.terminate() # Terminate/close the application process