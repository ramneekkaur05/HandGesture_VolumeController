import cv2 as cv
import mediapipe as mp
import time

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
        lmList = []

        if self.results.multi_hand_landmarks:
            myhand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myhand.landmark):
                h,w,c = img.shape
                cx,cy = int(lm.x*w), int(lm.y*h)
                #print(id,cx,cy)
                lmList.append([id,cx,cy])
                if draw:
                    cv.circle(img,(cx,cy),10,(255,0,255),cv.FILLED)

        return lmList
           

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