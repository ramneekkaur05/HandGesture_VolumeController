import cv2 as cv
import time
import numpy as np
import handtrackingmodule as htm
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 700,480

cap= cv.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)
pTime=0 

detector = htm.handDetector(detectionCon = 0.8, maxHands=1)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
area = 0
colorV= ()

while True:
    success , img  = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img,draw=True)
    if(len(lmList)!=0):
    
        #print bbox
        area = (bbox[2]-bbox[0]) * (bbox[3]-bbox[1]) // 100
        #print(area)
        
        #Find Distance between thumb and index finger
        length, img, lineInfo = detector.findDistance(4,8,img)
        print(length)

        # Convert Volume
        
        volBar = np.interp(length, [40,200], [400,150])
        volPer = np.interp(length, [40,200], [0,100])

    
        # Reduce Resolution to make it smoother
        smoothness = 10
        volPer = smoothness* (round(volPer/smoothness))

        # Check Fingers up
        fingers = detector.fingersUp()
        print(fingers)

        # If pinky is down set volume
        if not fingers[4]:
            volume.SetMasterVolumeLevelScalar(volPer/100, None)
            cv.circle(img, (lineInfo[4],lineInfo[5]), 9, (0,255,0), cv.FILLED)
            colorV = (0,255,0)
        else:
            colorV = (255,0,0)

    # Drawings
    cv.rectangle(img, (50,150), (85,400), (0,0,0), 3 )
    cv.rectangle(img, (50,int(volBar)), (85,400), (0,255,255), cv.FILLED )
    cv.putText(img, f'{int(volPer)} %', (40,450), cv.FONT_HERSHEY_PLAIN, 
            2,(0,0,0), 3 )
    cVol = int(volume.GetMasterVolumeLevelScalar()*100)
    cv.putText(img, f'{int(cVol)} %', (400,50), cv.FONT_HERSHEY_PLAIN, 
    2,colorV, 3 )
    
        

    # Frame Rate
    cTime = time.time()
    fps= 1/(cTime-pTime)
    pTime = cTime

    cv.putText(img, f'FPS: {int(fps)}', (10,50), cv.FONT_HERSHEY_PLAIN, 
               2,(255,0,0), 3 )

    cv.imshow("Img",img)
    cv.waitKey(1)