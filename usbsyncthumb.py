

import logging
import os, time, sys, glob, re
import threading
import datetime as dt

import RPi.GPIO as GPIO

import ftplib
import ftptool

from subprocess import check_output

time_now = dt.datetime.now()
### Log file name
log_file_name = time_now.strftime("%Y-%m-%d") + ".txt"
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=log_file_name)

logging.info("Script started")

UsbMountPath = '/home/pi/usbthumb.d'
UsbImagePath = '/home/pi/usbthumb.img'

def checkInternet():
	print ' '
	wifi_ip = check_output(['hostname', '-I'])
	if wifi_ip is not None:
		print 'Current IP ' + wifi_ip
		return True
	print 'No Connection'
	return False

class ThumbSync(threading.Thread):

	def __init__(self, interval=30): # interval : uint sec
		threading.Thread.__init__(self)
		self.currEvent = threading.Event()
		self.interval = interval
		self.lasttime = dt.datetime.now() - dt.timedelta(seconds=self.interval)
		return 

	def run(self):
		while not self.currEvent.isSet():
			if((dt.datetime.now() - self.lasttime).seconds >= self.interval):
				self.lasttime = dt.datetime.now()
				### Check Wifi connection Status
				if(checkInternet() == True):
					print 'Wifi Okay'
					logging.info('It is connected to Internet.')
					self.ftpSyncProc()
				else:
					logging.info('It is not connected to Internet.')

					# turn off wifi
					command = "sudo ifdown 'wlan0'"
					os.system(command)
					time.sleep(5)

					# turn on Wifi
					command = "sudo ifup --force 'wlan0'"
					os.system(command)
					logging.info('I have turned on again Wifi Interface.')

			time.sleep(2)
		return

	def ftpSyncProc(self):
		try:
			ftphost = ftptool.FTPHost.connect("192.168.2.126", user="admin", password="admin", timeout=3)
			
			# Checking whether contents of USB Drive are changed.
			command = 'sudo umount ' + UsbMountPath
			os.system(command)
			time.sleep(2)
			command = 'sudo mount -o loop,rw, -t vfat ' + UsbImagePath + ' ' + UsbMountPath
			os.system(command)
			
			### FTP sync
			ftphost.sync_to_remote('/home/pi/usbthumb.d', '/')
			logging.info('I have syncronized with FTP server!')
			print 'done.'
            
		except ftplib.all_errors, e:
			errorcode_string = str(e).split(None, 1)
			logging.error(errorcode_string)		
		return

if __name__ == '__main__':

	CheckInterval = 120 # unit sec
	
	print 'RPI Zero Network enabled USB Thumb Drive'

	### thread Instance
	thumbProc = ThumbSync(CheckInterval)
	thumbProc.start()

	try:
		while True:
			time.sleep(3)

	except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
		thumbProc.currEvent.set()
		print 'Exiting program!'

	finally:
		time.sleep(3)
