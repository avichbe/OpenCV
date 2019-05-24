import cv2
import numpy as np
import os

filename = 'video.avi'
frames_per_second = 24.0
res = '720p'


# Set resolution for the video capture
def change_res(cap, width, height):
    cap.set(3, width)
    cap.set(4, height)


# Standard Video Dimensions Sizes
STD_DIMENSIONS =  {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
}


# grab resolution dimensions and set video capture to it.
def get_dims(cap, res='1080p'):
    width, height = STD_DIMENSIONS["480p"]
    if res in STD_DIMENSIONS:
        width,height = STD_DIMENSIONS[res]
    ## change the current caputre device
    ## to the resulting resolution
    change_res(cap, width, height)
    return width, height


# Video Encoding, might require additional installs
# Types of Codes: http://www.fourcc.org/codecs.php
VIDEO_TYPE = {
    'avi': cv2.VideoWriter_fourcc(*'XVID')
    }


def get_video_type(filename):
    filename, ext = os.path.splitext(filename)
    if ext in VIDEO_TYPE:
        return VIDEO_TYPE[ext]
    return VIDEO_TYPE['avi']


cap = cv2.VideoCapture(0)
out = cv2.VideoWriter(filename, get_video_type(filename),
     frames_per_second, get_dims(cap, res))
ret1, frame1 = cap.read()
ret2, frame2 = cap.read()

while True:
    #convert the frame to gray 
    frame1_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    frame2_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    #convert the frame to blur for reduce the noises
    frame1_blur = cv2.GaussianBlur(frame1_gray, (21, 21), 0)
    frame2_blur = cv2.GaussianBlur(frame2_gray, (21, 21), 0)
    #compare the frame and return the abs diffrecne - if != 0 - there is a movment
    diff = cv2.absdiff(frame1_blur, frame2_blur)
    #thresing and dialting the diffrence helps to reduce mistakes
    thresh = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)[1]
    dilated = cv2.dilate(thresh, None, iterations=2)
    masked = cv2.bitwise_and(frame1, frame1, mask=thresh)

    #count the number of white pixels in the thresholded image
    white_pixels = np.sum(thresh) / 255
    rows, cols = thresh.shape
    total = rows * cols
    #after some tests i decide about 0.0001 is the best result.
    if white_pixels > 0.0001 * total:
        out.write(frame1)
        #split the screen and open new window when motion detected.
        cv2.imshow("rec", diff)

    out.release()
    #main screen with live video
    cv2.imshow("Main", frame1)
    frame1 = frame2
    ret, frame2 = cap.read()
    if not ret:
        break
    #close when ESC press
    key = cv2.waitKey(10)
    if key == 27:
        break

cv2.destroyAllWindows()
