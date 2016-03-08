"""
Author: Ellie Ansell
Project name: Raspi Rendering 
This script renders the scene using input parameters of time, light intensity and temperature. It
renders the image and saves it as a .png file, to be sent to the raspi and displayed.
"""
import maya.mel
import maya.cmds as cm
import xml.etree.ElementTree as ET
import math
import urllib2




class Render:
    """
    Initialises and sets variables by reading the XML file that was output from the raspi.
    Attributes:
        time (int): Time of day when data was recorded
        lightIntensity (int): LDR value
        temperature (int): Temperature of the room 
    """
    
    def __init__(self): 
            
        url = urllib2.urlopen('http://elliespi.ddns.net/xml.xml') #fetches data from website
        root = ET.parse(url)
        for i in root.findall('data'):
            self.time = i.find('time').text
            self.lightIntensity = i.find('lightIntensity').text
            self.temperatureC = i.find('temperatureC').text
            self.temperatureF = i.find('temperatureF').text
            print "At ", self.time, '\nLight Intensity: ', self.lightIntensity, '\nTemperature C: ', self.temperatureC, '\nTemperature F: ', self.temperatureF
        
        self.timeHr = int(self.time[11:13])
        self.timeMin = int(self.time[14:16])
        self.timeFrame = math.floor((self.timeHr*30)+(float(self.timeMin)/float(60))*30)
        self.temperatureC = int(self.temperatureC[0:2])
        self.lightIntensity = int(self.lightIntensity)
        
        decimalMin = float(self.timeMin)/float(60)
        if self.timeHr>12:
            self.niceTime = (self.timeHr-12) + decimalMin     
        else: 
            self.niceTime = self.timeHr + decimalMin       
            
                
        print "Hr: ", self.timeHr, "  Min: ", self.timeMin, "Nice time: %.2f" % (self.niceTime), "  Frame", self.timeFrame, self.temperatureC





    """
    Changes the sun's intensity by changing the colour value.
    Attributes: 
        niceTime (int): converts time to a nicer format
    """    
    def changeTemperature(self):
        '''
	Changes temperature dial and sets the sun's temperature colour.
	'''
        print "Temperature:", self.temperatureC*1000
        lightTimeTemperature = (-100*(self.timeHr+float(self.timeMin)/float(60)-12)**2)+5500 #equation for sun's temperature value 
        print "Sun temperature: ", lightTimeTemperature
        if lightTimeTemperature<0:
            lightTimeTemperature = 10000
            print "It's night time, the moon is up!"
            
        cm.setAttr("SUNSPHEREShape.temperature", lightTimeTemperature) #for vray
        cm.setAttr("SUNSPHEREShape.intensityMult", (50+(self.lightIntensity/5))) 
        tempRotate = (float(self.temperatureC)*float(3))*-1
        cm.rotate(0,0,0, 'thermometerDial', os=True, a=True) 
        cm.rotate(0, 0, float(tempRotate), 'thermometerDial', os=True, a=True) 
        
    def changeTimeFrame(self):
       '''
	Changes the clock's time
	'''
	 hourHandRotZ=(30*self.niceTime)*-1
        minHandRotZ=(self.timeMin*6)*-1
        cm.rotate(0, 0, 0, 'hourHand', os=True, a=True) 
        cm.rotate(0, 0, 0, 'minuteHand', os=True, a=True) 
        cm.rotate(0, 0, hourHandRotZ, 'hourHand')
        cm.rotate(0, 0, minHandRotZ, 'minuteHand')
        cm.currentTime(self.timeFrame)
        
    def setScene(self):
         '''
	Changes the scene depending on temperature and time of day.
	'''	    
        if self.timeHr>=6 and self.timeHr<10:
            maya.mel.eval('setAttr "hot_chocolate_SCENE.visibility" 0;')
            maya.mel.eval('setAttr "Tropical_Hot_SCENE.visibility" 0;')  ##Displays scene depending on time
            cm.move(float(2.1), float(1.2), float(8.909), 'RENDER_CAM', os=True, a=True)
            cm.rotate(0, 0, 0, 'RENDER_CAM', os=True, a=True)
            maya.mel.eval('setAttr "Breakfast_SCENE.visibility" 1;')
        else:
            if self.temperatureC>18: 
                maya.mel.eval('setAttr "Tropical_Hot_SCENE.visibility" 1;')
                maya.mel.eval('setAttr "hot_chocolate_SCENE.visibility" 0;')
                cm.move(float(2.052), float(2.336), float(25.185), 'RENDER_CAM', os=True, a=True)
                cm.rotate(0, 0, 0, 'RENDER_CAM', os=True, a=True)
            else: 
                maya.mel.eval('setAttr "hot_chocolate_SCENE.visibility" 1;')
                maya.mel.eval('setAttr "Tropical_Hot_SCENE.visibility" 0;')
                cm.move(float(2.389), float(3.368), float(19.504), 'RENDER_CAM', os=True, a=True)
                cm.rotate(0, 0, 0, 'RENDER_CAM', os=True, a=True)
            pass
        
render = Render()
render.changeTemperature()
render.changeTimeFrame()
render.setScene()

import maya.cmds as cmds
import maya.mel as mel

startFrom = 300
renderTill = 500

mel.eval('currentTime %s ;'%(startFrom))
maya.mel.eval('$frame = 1;')
while(startFrom < renderTill):
    render = Render()
    render.changeTemperature()
    render.changeTimeFrame()
    render.setScene()
    mel.eval('renderWindowRender redoPreviousRender renderView;')
    #startFrom += 1
    #mel.eval('currentTime %s ;'%(startFrom))
    maya.mel.eval('$frame +=1;')
    maya.mel.eval('renderWindowSaveImageCallback "renderView" (`workspace -q -sn` + "/home/i7685565/Documents/Innovations/RENDERS" + "getDataRender" + "." + $frame ) "image";')
	print "frame saved in /home/i7685565/Documents/Innovations/RENDERS"
