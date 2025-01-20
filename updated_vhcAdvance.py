import cv2 as cv
import mediapipe as mp
import numpy as np
import math
import time
import handtrackingmodule as htm
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 700,480

cap = cv.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)
pTime = 0
vol = 0
volBar = 400
volPer = 0
area = 0
colorV =()

detector = htm.handDetector(detectionCon=0.8, maxHands=1)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

while True:
    success,img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    if(len(lmList)!=0):

        # Find distance between thumb and index finger
        length, img, lineInfo = detector.findDistance(4,8,img)
        if length<30:
            cv.circle(img, (lineInfo[4],lineInfo[5]),9, (0,255,0),cv.FILLED)
        #print(length)

        # Convert Volume
        volBar = np.interp(length,[40,200],[400,150])  # linear interpolation
        volPer = np.interp(length, [40,200],[0,100])

        # Reduce Resoltuion to make it more smoother
        smoothness = 10
        volPer = smoothness*(round(volPer/smoothness))

        # Check Fingers up or down
        fingers = detector.fingersUp()
        print(fingers)

        # If Ring Finger is down , set volume
        if(fingers[3]==0):
            volume.SetMasterVolumeLevelScalar(volPer/100,None)
            cv.circle(img,(lineInfo[4],lineInfo[5]),9,(0,255,0),cv.FILLED)
            
    #Drawings
    cv.rectangle(img,(50,150),(85,400),(0,0,0),3)
    cv.rectangle(img,(50,int(volBar)),(85,400),(0,255,255),cv.FILLED)
    cVol = int(volume.GetMasterVolumeLevelScalar()*100)
    cv.putText(img, (f'{int(volPer)}%'),(40,450),cv.FONT_HERSHEY_PLAIN,2,(0,0,0),3)
    cv.putText(img, (f'{int(cVol)}%'), (400,50),cv.FONT_HERSHEY_PLAIN, 2 , (255,0,0),3)

    #Frames
    cTime =time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv.putText(img,(f'FPS : {int(fps)}'), (10,40), cv.FONT_HERSHEY_PLAIN, 2, (255,0,0), 3)   
    cv.imshow("Image",img)
    cv.waitKey(1)