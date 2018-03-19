import sys
import os
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import cv2
import pyttsx
import time
import tensorflow as tf
from r305 import R305
import MySQLdb
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
#--------------------------------------------------------GLOBAL DECLARATIONS-------------------------------------------------------------------------------
global userid
#--------------------------------------------------------DATA BASE CONNECTION------------------------------------------------------------------------------

def updatedb(str): # FOR DML OPERATIONS
    # Open database connection
    db = MySQLdb.connect("localhost","root","root","Bank")
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    try:
        # Execute the SQL command
        cursor.execute(str)
        # Commit  changes in the database
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()
        # disconnect from server
        db.close()

def resultdb(str):
    #try:
        # Open database connection
        db = MySQLdb.connect("localhost","root","root","Bank")
        # prepare a cursor object using cursor() method
        cursor = db.cursor()
        # execute SQL query using execute() method.
        cursor.execute(str)
        # Fetch a single row using fetchone() method.
        data = cursor.fetchall()
        return data
    #except:
        speak('DATA FETCHING FAILED!, CHECK DATABASE CONNECTION')
        return 'error'    
    # disconnect from server
        db.close() 
    
#--------------------------------------------------------TEXT TO SPEECH------------------------------------------------------------------------------------
def speak(str):
    engine = pyttsx.init()
    engine.say(str)
    engine.runAndWait()


#---------------------------------------------------------BIOMETRIC SEARCH----------------------------------------------------------------------------------
device   = "/dev/ttyUSB0"
baudrate = 57600 # the default baudrate for this module is 57600    
dev = R305(device, baudrate)


#---------------------------------------------------------GESTURE PREDICTION--------------------------------------------------------------------------------
def predict(image_data):
    predictions = sess.run(softmax_tensor, \
             {'DecodeJpeg/contents:0': image_data})
    # Sort to show labels of first prediction in order of confidence
    top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
    max_score = 0.0
    res = ''
    for node_id in top_k:
        human_string = label_lines[node_id]
        score = predictions[0][node_id]
        if score > max_score:
            max_score = score
            res = human_string
    return res, max_score


#---------------------------------------------------------Loads label file, strips off carriage return------------------------------------------------------
label_lines = [line.rstrip() for line
                   in tf.gfile.GFile("logs/trained_labels.txt")]

#----------------------------------------------------------Unpersists graph from file------------------------------------------------------------------------
with tf.gfile.FastGFile("logs/trained_graph.pb", 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')

#---------------------------------------------------------IMAGE CAPTURE AND RECOGNITION --------------------------------------------------------------------
def rec():
    c = 0
    cap = cv2.VideoCapture(0)
    res, score = '', 0.0
    i = 0
    mem = ''
    consecutive = 0
    sequence = ''
    while True:
        ret,img = cap.read()
        ret = True
        img = cv2.flip(img, 1)
        if ret:
            x1, y1, x2, y2 = 100, 100, 600, 550
            img_cropped = img[y1:y2, x1:x2]
            c += 1
            image_data = cv2.imencode('.jpg', img_cropped)[1].tostring()
            a = cv2.waitKey(33)
            if i == 4:
                res_tmp, score = predict(image_data)
                res = res_tmp
                i = 0
                if mem == res:
                    consecutive += 1
                else:
                    consecutive = 0

                if consecutive == 3 :                    
                    speak("YOU HAVE SHOWN "+res.upper())    
                    return res
            i += 1
            cv2.putText(img, '%s' % (res.upper()), (100,400), cv2.FONT_HERSHEY_SIMPLEX, 4, (255,255,255), 4)
            cv2.putText(img, '(score = %.5f)' % (float(score)), (100,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
            mem = res
            cv2.rectangle(img, (x1, y1), (x2, y2), (255,0,0), 2)
            cv2.imshow("img", img)
            
        else:
            speak("PLEASE CHECK CAMERA OR RESTART SYSTEM")
            print ("PLEASE CHECK CAMERA OR RESTART SYSTEM")
            


#------------------------------------------------------------------------MAIN----------------------------------------------------------------------------




while(1):

    while(1):
        result = dev.SearchFingerPrint()
        if(result == "no finger on the sensor"):
            speak("PLEASE PUT YOUR FINGER ON THE FINGERPRINT READER")
        elif(result == 'fail to find the matching finger'):
            speak("NO MACHING USERNAME FOUND! PLEASE TRY AGAIN")
        elif(result == 'Checksum Error'):
            speak("PLEASE REMOVE AND PLACE YOUR FINGER AGAIN")
        else:
            userid= result['matchstore']
            print(userid)
            for row in resultdb("SELECT * FROM Bank.acc_dtl where userid = "+int(userid)):        
                break;

    
pin = ''
temp = ''
with tf.Session() as sess:
    # Feed the image_data as input to the graph and get first prediction
    softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
    while True:
        speak("Please Show the First number")
        time.sleep(3) 
        temp=rec()
        speak("Remove Your Hand to Confirm")
        time.sleep(3)
        if(rec()=='none'):
            speak(temp+" confirmed")
            pin += temp
            break;4
       
    while True:
        speak("Please Show the Second number")
        time.sleep(3)
        temp=rec()
        speak("Remove Your Hand to Confirm")
        time.sleep(3)
        if(rec()=='none'):
            speak(temp+" confirmed")
            pin += temp
            break;
    while True:
        speak("Please Show the Third number")
        time.sleep(3)
        temp=rec()
        speak("Remove Your Hand to Confirm")
        time.sleep(3)
        if(rec()=='none'):
            speak(temp+" confirmed")
            pin += temp
            break;
    while True:
        speak("Please Show the Fourth number")
        time.sleep(3)
        temp=rec()
        speak("Remove Your Hand to Confirm")
        time.sleep(3)
        if(rec()=='none'):
            speak(temp+" confirmed")
            pin += temp
            break;
        
    
    
# Following line should appear but is not working with opencv-python package
# cv2.destroyAllWindows() 
cv2.VideoCapture(0).release()




