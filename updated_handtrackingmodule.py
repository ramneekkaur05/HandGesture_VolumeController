import cv2 as cv
import mediapipe as mp
import time
import math

class handDetector():
    def __init__(self,mode=False,maxHands=2, detectionCon=0.5, trackCon=0.5):
        '''static_image_mode = False,
        max_num_hands = 2,
        min_detection_confidence = 0.5,
        min_tracking_confidence = 0.5'''
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = float(detectionCon)
        self.trackCon = float(trackCon)
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode= self.mode,max_num_hands= self.maxHands, min_detection_confidence= self.detectionCon, min_tracking_confidence = self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4,8,12,16,20]

    def findHands(self,img,draw=True):
        imgRGB = cv.cvtColor(img,cv.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        
        if self.results.multi_hand_landmarks:
            for handlms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img,handlms,
                    self.mpHands.HAND_CONNECTIONS)
        
        return img


    def findPosition(self, img, handNo=0, draw=True):
        self.lmList = []
        xList = []
        yList = []
        bbox = []

        if self.results.multi_hand_landmarks:
            myhand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myhand.landmark):
                h,w,c = img.shape
                cx,cy = int(lm.x*w), int(lm.y*h)
                xList.append(cx)
                yList.append(cy)
                #print(id,cx,cy)
                self.lmList.append([id,cx,cy])
                if draw:
                    cv.circle(img,(cx,cy),4,(255,0,255),cv.FILLED)

            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin,xmax,ymin,ymax

            if draw:
                cv.rectangle(img,(xmin-20,ymin-20),
                                  (xmax+20,ymax+20),(0,255,0), 2)

        return self.lmList, bbox
           

    def fingersUp(self):
        fingers = []
        # Thumb
        if self.lmList[self.tipIds[0]][1] < self.lmList[self.tipIds[0]-1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        # 4 fingers
        for id in range(1,5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id]-2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers
    
    def findDistance(self,p1,p2,img,draw=True):
        x1,y1 = self.lmList[p1][1], self.lmList[p1][2]
        x2,y2 = self.lmList[p2][1], self.lmList[p2][2]
        cx,cy = (x1+x2)//2 ,(y1+y2)//2

        if draw:
            cv.circle(img, (x1,y1), 9, (255,0,255), cv.FILLED)
            cv.circle(img, (x2,y2), 9, (255,0,255), cv.FILLED)
            cv.line(img, (x1,y1), (x2,y2), (255,0,255), 3)
            cv.circle(img, (cx,cy), 9, (255,0,255), cv.FILLED)

        length = math.hypot(x2-x1, y2-y1)
        return length,img, [x1,y1,x2,y2,cx,cy]

def main():
    cap = cv.VideoCapture(0)
    pTime = 0
    cTime = 0
    detector = handDetector()
    while True:
         success, img = cap.read()
         img = detector.findHands(img)
         lmList = detector.findPosition(img)
         if len(lmList)!=0:
             print(lmList[4])

         cTime = time.time()
         fps = 1/(cTime-pTime)
         pTime= cTime
         
         cv.putText(img, str(int(fps)), (10,70), cv.FONT_HERSHEY_PLAIN, 3, (255,0,255),3)
         cv.imshow("Image", img)
         cv.waitKey(1)
        

if __name__ == "__main__":
    main()