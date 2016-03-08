'''

This script gets the data from the rapberry pi by using temperature and light sensors. It then sends the data to
an xml file.
Author: Ellie Ansell
Credit: Modmypi.com
Date: 06/03/16
'''
#!/usr/bin/env python
import os
import datetime
import time
import glob #temperature
import RPi.GPIO as GPIO
import lxml.etree as ET

'''Initialises the temperature device'''
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

GPIO.setwarnings(False) ##turns off warnings
DEBUG = 1
GPIO.setmode(GPIO.BCM)
 
def RCtime (RCpin):
        '''
        Gets the light intensity reading
        '''
        reading = 0
        GPIO.setup(RCpin, GPIO.OUT)
        GPIO.output(RCpin, GPIO.LOW)
        time.sleep(.1)
 
        GPIO.setup(RCpin, GPIO.IN)
        # This takes about 1 millisecond per loop cycle
        while (GPIO.input(RCpin) == GPIO.LOW):
                reading += 1
        print "Light Intensity", reading
        return reading

def read_temp_raw():
    '''
    Gets the temperature in raw format.
    '''
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_tempC():
    '''
    Converts the temperature to centigrade.
    '''
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        print "Temperature degrees centigrade:", temp_c
        return temp_c

def read_tempF():
    '''
    Converts the temperature to fahrenheit.
    '''
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        print "Temperature fahrenheit:", temp_f
        return temp_f

while True:
    '''
    Writes the data to an XML file, which can be seen at elliespi.ddns.net/xml.xml
    '''
		GetDateTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print "At ", GetDateTime
                
                tree = ET.parse('/var/www/html/xml.xml')
                root = tree.getroot()
                container = tree.findall('data')
                tree.find('.//lightIntensity').text = str(RCtime(3))
                tree.find('.//time').text = str(GetDateTime)
                tree.find('.//temperatureC').text = str(read_tempC())
                tree.find('.//temperatureF').text = str(read_tempF())
                tree.write("/var/www/html/xml.xml")

		time.sleep(10)





