#!/usr/bin/python

from time import sleep
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
import os
import re

MAXCHARS = 16

def centerLine(msg, fillChar = ' '):
  if len(msg) < MAXCHARS - 1:
    return fillChar*(int((MAXCHARS - len(msg))/2)) + msg + fillChar*(MAXCHARS - len(msg) - int((MAXCHARS - len(msg))/2))
  else: 
    return msg

def centerHighlight(msg):
  if len(msg) < (MAXCHARS - 4):
    newMsg = '< ' + msg + ' >'
    return centerLine(newMsg, '-')
  else:
    return msg

def clear():
  global lcd
  global lastMessage
  lcd.clear()
  lastMessage = ""
  sleep (0.01)

def moveOutLeft():
  """ Animation, move text out to the left """
  for dx in range(1,MAXCHARS):
    dt = max(dx * dx * 2, 6)
    lcd.scrollDisplayLeft()
    sleep(max(1.0/dt, 0.01))
  clear()

def moveOutRight():
  """ Animation, move text out to the right """
  for dx in range(1,MAXCHARS):
    dt = max(dx * dx * 2, 6)
    lcd.scrollDisplayRight()
    sleep(max(1.0/dt, 0.01))
  clear()

def getRadioInfo():
  """ Get station name and song title from radio stream """
  global isplaying
  txt = os.popen("mpc current")
  string = ""
  station = ""
  song    = ""
  for line in txt.readlines():
    string += line
  
  matchObj = re.search ( r'(.*):(.*)', string, re.M|re.I)

  if matchObj:
    station = matchObj.group(1)
    song    = matchObj.group(2)
    isplaying = True
    return [station, song]
  else:
    return ["", ""]

def getWlanIP():
  """ get network IP from wlan0 """
  txt = os.popen("ifconfig wlan0 | grep 'inet addr' | awk -F: '{print $2}' | awk '{print $1}'")
  string = ""
  for line in txt.readlines():
    string += line
  return string

def bufferedMessage(msg):
  global lcd
  global lastMessage
  if lastMessage != msg:
    clear()
    lcd.message(msg)
    lastMessage = msg
    sleep(0.01)
  
# Initialize the LCD plate.  Should auto-detect correct I2C bus.  If not,
# pass '0' for early 256 MB Model B boards or '1' for all later versions
lcd = Adafruit_CharLCDPlate(0)
isplaying   = False
lastplaying = True
lastMessage = ""
lastInfo    = ["-", "-"]
counter     = 0

# Poll buttons, display message & set backlight accordingly
btn = (lcd.LEFT,lcd.UP,lcd.DOWN,lcd.RIGHT,lcd.SELECT)
pressed = -1
bufferedMessage(centerLine("iRadio by Dave") + '\n' + centerLine("Have a nice Day"))
sleep(1)
moveOutLeft()

while True:
  sleep(0.05)
  counter += 1
  if isplaying and (counter % 100 == 0):
    lastInfo = ["-", "-"]

  if pressed == -1:
    prev = -1
  pressed = -1
  for b in btn:
    if lcd.buttonPressed(b):
      pressed = b
  if pressed is not prev:
    prev = pressed
    if pressed == lcd.SELECT:
      bufferedMessage(centerLine('my IP is') + '\n' + centerLine(getWlanIP()))
      sleep(2)
    if pressed == lcd.LEFT:
      if isplaying:
        os.system("mpc stop")
        isplaying = False
      else:
        os.system("mpc play")
        isplaying = True
      lastInfo = ['-','-']
    elif pressed == lcd.UP:
      os.system("mpc next")
      sleep(0.3)
      os.system("mpc play")
      moveOutRight()
      lastInfo = ['-','-']
    elif pressed == lcd.DOWN:
      os.system("mpc prev")
      sleep(0.3)
      os.system("mpc play")
      moveOutLeft()
      lastInfo = ['-','-']
    elif pressed == lcd.RIGHT:
      # bufferedMessage("Play")
      os.system("mpc play")
      lastInfo = ['-','-']
  else:
    stationInfo = getRadioInfo()
    if (stationInfo[0] != lastInfo[0]) or (stationInfo[1] != lastInfo[1]) or (lastplaying != isplaying):
      if not isplaying or stationInfo[0] == "":
        lastMessage = "-"
        lcd.message(centerLine('iRadio') + "\n" + centerHighlight('PAUSED'))
      elif stationInfo[0] != lastInfo[0]:
        # station change 
        if len(stationInfo[0]) < 16:
          bufferedMessage(centerLine('iRadio') + '\n' +  centerHighlight(stationInfo[0][:16].strip()))
        else:
          message = stationInfo[1][:16].lstrip() + '\n' + stationInfo[1][16:32].lstrip()
          bufferedMessage(message)
        stationInfo[1] = ""
        sleep(1.5)
      elif stationInfo[1] != lastInfo[1]:
        # song changed
        message = stationInfo[1][:16] + '\n' + stationInfo[1][16:32]
        bufferedMessage(message)
      #sleep
      lastInfo = stationInfo
      lastplaying = isplaying