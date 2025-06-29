#!/usr/bin/env python

import cv2
import os
import sys, getopt
import signal
import time
from edge_impulse_linux.image import ImageImpulseRunner
import pyrebase
import json
import time

# Tilo_Count = 0
# Oreo_Count = 0
# Coca_Cola_Count=6
# Bread_Count = 4
# Pringles_Count = 3
# Diary_Milk_Count = 6

BabyPowder_Count = 0
BoxDrink_Count = 0
CannedGood_Count=0
Deo_Count = 0
Soap_Count = 0
Wipes_Count = 0

flag = 0


# count_data = {"soap" : Tilo_Count,"Oreo":Oreo_Count, "Coca-Cola":Coca_Cola_Count,"Bread":Bread_Count,"Pringles":Pringles_Count, "Diary-Milk":Diary_Milk_Count,}

count_data = {"BabyPowder" : BabyPowder_Count,"BoxDrink":BoxDrink_Count, "CannedGood":CannedGood_Count,"Deo":Deo_Count,"Soap":Soap_Count, "Wipes":Wipes_Count,}


runner = None
# if you don't want to see a camera preview, set this to False
show_camera = True

if (sys.platform == 'linux' and not os.environ.get('DISPLAY')):
    show_camera = False

def now():
    b = round(time.time() * 1000)
    print("NOW", b)
    return b

def get_webcams():
    port_ids = []
    for port in range(5):
        print("Looking for a camera in port %s:" %port)
        camera = cv2.VideoCapture(port)
        if camera.isOpened():
            ret = camera.read()[0]
            if ret:
                backendName =camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print("Camera %s (%s x %s) found in port %s " %(backendName,h,w, port))
                port_ids.append(port)
            camera.release()
    return port_ids

def sigint_handler(sig, frame):
    print('Interrupted')
    if (runner):
        runner.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def help():
    print('python classify.py <path_to_model.eim> <Camera port ID, only required when more than 1 camera is present>')

def main(argv):
    # global Tilo_Count, Oreo_Count,flag
    global BabyPowder_Count, BoxDrink_Count, CannedGood_Count, Deo_Count, Soap_Count, Wipes_Count, flag
    if flag == 0:
        firebaseConfig = {
            "apiKey": "AIzaSyC0N-ADc0kZ8XqcbpVKP7C2B4kb_c5LDYc",
            "authDomain": "inventorymanagementdb.firebaseapp.com",
            "databaseURL": "https://inventorymanagementdb-default-rtdb.asia-southeast1.firebasedatabase.app",
            "projectId": "inventorymanagementdb",
            "storageBucket": "inventorymanagementdb.firebasestorage.app",
            "messagingSenderId": "511046986981",
            "appId": "1:511046986981:web:958eaab4690f6bfb9f780c"
            }
        firebase = pyrebase.initialize_app(firebaseConfig)
        db = firebase.database()
        db.child("count").set(count_data)
        flag = 1

    try:
        opts, args = getopt.getopt(argv, "h", ["--help"])
    except getopt.GetoptError:
        help()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help()
            sys.exit()

    if len(args) == 0:
        help()
        sys.exit(2)

    model = args[0]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, model)

    print('MODEL: ' + modelfile)

    with ImageImpulseRunner(modelfile) as runner:
        try:
            model_info = runner.init()
            print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
            labels = model_info['model_parameters']['labels']
            if len(args)>= 2:
                videoCaptureDeviceId = int(args[1])
            else:
                port_ids = get_webcams()
                if len(port_ids) == 0:
                    raise Exception('Cannot find any webcams')
                if len(args)<= 1 and len(port_ids)> 1:
                    raise Exception("Multiple cameras found. Add the camera port ID as a second argument to use to this script")
                videoCaptureDeviceId = int(port_ids[0])

            camera = cv2.VideoCapture(videoCaptureDeviceId)
            ret = camera.read()[0]
            if ret:
                backendName = camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print("Camera %s (%s x %s) in port %s selected." %(backendName,h,w, videoCaptureDeviceId))
                camera.release()
            else:
                raise Exception("Couldn't initialize selected camera.")

            next_frame = 0 # limit to ~10 fps here

            for res, img in runner.classifier(videoCaptureDeviceId):               

                if "bounding_boxes" in res["result"].keys():
                    print('Found %d bounding boxes (%d ms.)' % (len(res["result"]["bounding_boxes"]), res['timing']['dsp'] + res['timing']['classification']))
                    count = len(res["result"]["bounding_boxes"])

                    for bb in res["result"]["bounding_boxes"]:
                        img = cv2.rectangle(img, (bb['x'], bb['y']), (bb['x'] + bb['width'], bb['y'] + bb['height']), (255, 0, 0), 1)
                        Label  = bb['label']
                        score  = bb['value']
                        print(Label, score)
                        if score > 0.70 :
                          if Label == "Powder":
                             BabyPowder_Count+=1
                          elif Label == "Drink":
                             BoxDrink_Count+=1
                          elif Label == "canned good":
                             CannedGood_Count+=1
                          elif Label == "deo":
                             Deo_Count+=1
                          elif Label == "soap":
                             Soap_Count+=1
                          elif Label == "wipes":
                             Wipes_Count+=1
                    db.child("count").update({"BabyPowder" : BabyPowder_Count,"BoxDrink":BoxDrink_Count,"CannedGood":CannedGood_Count,"Deo":Deo_Count,"Soap":Soap_Count,"Wipes":Wipes_Count,})
                    BabyPowder_Count,BoxDrink_Count,CannedGood_Count,Deo_Count,Soap_Count,Wipes_Count  = 0,0,0,0,0,0
                if (show_camera):
                    cv2.imshow('edgeimpulse', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                    if cv2.waitKey(1) == ord('q'):
                        break

                next_frame = now() + 10
        finally:
            if (runner):
                runner.stop()

if __name__ == "__main__":
   main(sys.argv[1:])