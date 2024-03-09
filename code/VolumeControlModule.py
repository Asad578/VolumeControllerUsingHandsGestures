import cv2
import numpy as np
import HandTrackingModule as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# set camera width and height
wCam, hCam = 840, 680

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.HandDetector(detectionCon=0.7, maxHands=2)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

vol = 0
volBar = 400
volPer = 0
area = 0
colorVol = (208, 96, 255)

while True:
    success, img = cap.read()

    # Find Hand
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=True)
    if len(lmList) != 0:

        # Filter based on size
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100

        # print(area)
        if 200 < area < 900:

            # Find Distance between index and Thumb
            length, img, lineInfo = detector.findDistance(4, 8, img)

            # Convert Volume
            volBar = np.interp(length, [50, 200], [400, 150])
            volPer = np.interp(length, [50, 200], [0, 100])

            # Reduce Resolution to make it smoother
            smoothness = 5
            volPer = smoothness * round(volPer / smoothness)

            # Check fingers up
            fingers = detector.fingersUp()

            # If pinky is down then set volume
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 7, (0, 0, 0), cv2.FILLED)
                colorVol = (0, 0, 0)
            else:
                colorVol = (208, 96, 255)

    # Drawings
    cv2.rectangle(img, (30, 150), (65, 400), (0, 0, 0), 2)
    cv2.rectangle(img, (32, int(volBar)), (63, 398), (208, 96, 255), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (25, 430), cv2.FONT_HERSHEY_COMPLEX,
                0.8, (208, 96, 255), 2)
    cVol = int(volume.GetMasterVolumeLevelScalar() * 100)
    cv2.putText(img, f'Volume set at: {int(cVol)}', (20, 40), cv2.FONT_HERSHEY_COMPLEX,
                1.2, colorVol, 2)

    cv2.imshow("Img", img)
    cv2.waitKey(1)
