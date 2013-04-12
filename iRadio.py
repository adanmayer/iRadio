#!/usr/bin/python

from time import sleep
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
import os
import re

class IRadio():
  MAXCHARS = 16
  # Initialize the LCD plate.  Should auto-detect correct I2C bus.  If not,
  # pass '0' for early 256 MB Model B boards or '1' for all later versions
  lcd          = Adafruit_CharLCDPlate(0)
  isplaying    = False
  isdisplaying = TRUE
  lastMessage  = ""
  BTNS         = (lcd.LEFT,lcd.UP,lcd.DOWN,lcd.RIGHT,lcd.SELECT)

  def centerLine(self, msg, fillChar = ' '):
    if len(msg) < self.MAXCHARS - 1:
      return fillChar*(int((self.MAXCHARS - len(msg))/2)) + msg + fillChar*(self.MAXCHARS - len(msg) - int((self.MAXCHARS - len(msg))/2))
    else: 
      return msg

  def centerHighlight(self, msg):
    if len(msg) < (self.MAXCHARS - 4):
      newMsg = '< ' + msg + ' >'
      return centerLine(newMsg, '-')
    else:
      return msg

  def clear(self):
    self.lcd.clear()
    self.lastMessage = ""
    sleep (0.01)

  def moveOutLeft(self):
    """ Animation, move text out to the left """
    for dx in range(1,MAXCHARS):
      dt = max(dx * dx * 2, 6)
      self.lcd.scrollDisplayLeft()
      sleep(max(1.0/dt, 0.01))
    self.clear()

  def moveOutRight(self):
    """ Animation, move text out to the right """
    for dx in range(1,MAXCHARS):
      dt = max(dx * dx * 2, 6)
      self.lcd.scrollDisplayRight()
      sleep(max(1.0/dt, 0.01))
    self.clear()

  def getRadioInfo(self):
    """ Get station name and song title from radio stream """
    txt = os.popen("mpc current")
    string = ""
    station = ""
    song    = ""
    for line in txt.readlines():
      string += line
    
    matchObj = re.search (r'\s*(.*)\s*:\s*(.*)', string, re.M|re.I)

    if matchObj:
      station = matchObj.group(1)
      song    = matchObj.group(2)
      self.isplaying = True
      return [station, song]
    else:
      return ["", ""]

  def getWlanIP(self):
    """ get network IP from wlan0 """
    txt = os.popen("ifconfig wlan0 | grep 'inet addr' | awk -F: '{print $2}' | awk '{print $1}'")
    string = ""
    for line in txt.readlines():
      string += line
    return string

  def bufferedMessage(self, msg):
    if self.lastMessage != msg:
      self.clear()
      self.lcd.message(msg)
      self.lastMessage = msg
      sleep(0.01)

  def toggleDisplay(self):
    if self.isdisplaying:
      self.lcd.noDisplay()
    else:
      self.lcd.display()
    self.isdisplaying = not self.isdisplaying
   
  def toggleStopPlay(self):
    if self.isplaying:
      os.system("mpc stop")
    else:
      os.system("mpc play")
    self.isplaying = not self.isplaying

iRadio = IRadio()
iRadio.bufferedMessage(iRadio.centerLine("iRadio by Dave") + '\n' + iRadio.centerLine("Have a nice Day"))
sleep(1)
iRadio.moveOutLeft()


# Poll buttons, display message & set backlight accordingly
pressed      = -1
counter      = 0
lastplaying  = True
lastInfo     = ["-", "-"]

while True:
  sleep(0.05)
  counter += 1
  if iRadio.isplaying and (counter % 200 == 0):
    lastInfo = ["-", "-"]

  if iRadio.pressed == -1:
    prev = -1
  pressed = -1
  for b in iRadio.BTNS:
    if iRadio.lcd.buttonPressed(b):
      pressed = b
  if pressed is not prev:
    prev = pressed
    if pressed == lcd.SELECT:
      iRadio.bufferedMessage(iRadio.centerLine('my IP is') + '\n' + iRadio.centerLine(getWlanIP()))
      sleep(2)
    if pressed == iRadio.lcd.LEFT:
      iRadio.toggleStopPlay()
      lastInfo = ['-','-']
    elif pressed == iRadio.lcd.UP:
      os.system("mpc next")
      sleep(0.3)
      os.system("mpc play")
      iRadio.moveOutRight()
      lastInfo = ['-','-']
    elif pressed == iRadio.lcd.DOWN:
      os.system("mpc prev")
      sleep(0.3)
      os.system("mpc play")
      iRadio.moveOutLeft()
      lastInfo = ['-','-']
    elif pressed == iRadio.lcd.RIGHT:
      # bufferedMessage("Play")
      os.system("mpc play")
      lastInfo = ['-','-']
  else:
    stationInfo = getRadioInfo()
    if (stationInfo[0] != lastInfo[0]) or (stationInfo[1] != lastInfo[1]) or (lastplaying != iRadio.isplaying):
      if not iRadio.isplaying or stationInfo[0] == "":
        iRadio.lastMessage = "-"
        iRadio.clear()
        iRadio.lcd.message(iRadio.centerLine('iRadio') + "\n" + iRadio.centerHighlight('PAUSED'))
      elif stationInfo[0] != lastInfo[0]:
        # station change 
        if len(stationInfo[0]) < 16:
          iRadio.bufferedMessage(iRadio.centerLine('iRadio') + '\n' +  iRadio.centerHighlight(stationInfo[0][:16].strip()))
        else:
          message = stationInfo[1][:16].lstrip() + '\n' + stationInfo[1][16:32].lstrip()
          iRadio.bufferedMessage(message)
        stationInfo[1] = ""
        sleep(1.5)
      elif stationInfo[1] != lastInfo[1]:
        # song changed
        message = stationInfo[1][:16] + '\n' + stationInfo[1][16:32]
        iRadio.bufferedMessage(message)
      #sleep
      lastInfo = stationInfo
      lastplaying = isplaying