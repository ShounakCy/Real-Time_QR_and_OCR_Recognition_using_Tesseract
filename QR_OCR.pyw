# -*- coding: utf-8 -*-
import cv2
import cv2.cv as cv
import numpy
import zbar
import time
import iothub_client
import os
from iothub_client import *
#from iothub_client_args import *
import sys
import time
import datetime
from time import gmtime, strftime
import Tkinter
import threading
from PIL import Image
import pytesseract
import argparse
import numpy as np


message_timeout = 10000
 
receive_context = 0
message_count = 5
received_count = 0
 
# global counters
receive_callbacks = 0
send_callbacks = 0
blob_callbacks = 0
 
# chose HTTP, AMQP or MQTT as transport protocol
protocol = IoTHubTransportProvider.AMQP
connection_string ="HostName=*******;DeviceId=QrReader_Pi3;SharedAccessKey=************"
 
def iothub_client_init():
        # prepare iothub client
        iotHubClient = IoTHubClient(connection_string, protocol)
        if iotHubClient.protocol == IoTHubTransportProvider.HTTP:
            iotHubClient.set_option("timeout", timeout)
            iotHubClient.set_option("MinimumPollingTime", minimum_polling_time)
        # set the time until a message times out
        iotHubClient.set_option("messageTimeout", message_timeout)
        # some embedded platforms need certificate information
        # set_certificates(iotHubClient)
        # to enable MQTT logging set to 1
        if iotHubClient.protocol == IoTHubTransportProvider.MQTT:
            iotHubClient.set_option("logtrace", 0)
        iotHubClient.set_message_callback(
            receive_message_callback, receive_context)
        return iotHubClient

def receive_message_callback(message, counter):
        global receive_callbacks
        buffer = message.get_bytearray()
        size = len(buffer)
        print("Received Message [%d]:" % counter)
        print("    Data: <<<%s>>> & Size=%d" % (buffer[:size].decode('utf-8'), size))
        map_properties = message.properties()
        key_value_pair = map_properties.get_internals()
        print("    Properties: %s" % key_value_pair)
        counter += 1
        receive_callbacks += 1
        print("    Total calls received: %d" % receive_callbacks)
        return IoTHubMessageDispositionResult.ACCEPTED    

def send_confirmation_callback(message, result, user_context):
        global send_callbacks
        # print("Confirmation[%d] received for message with result = %s" %(user_context, result))
        map_properties = message.properties()
        # print("    message_id: %s" % message.message_id)
        # print("    correlation_id: %s" % message.correlation_id)
        key_value_pair = map_properties.get_internals()
        # print("    Properties: %s" % key_value_pair)
        send_callbacks += 1
        # print("    Total calls confirmed: %d" % send_callbacks)


 
if __name__ == '__main__':
        #Initate the IoT hub
        iotHubClient = iothub_client_init()
        #(connection_string, protocol) = get_iothub_opt(sys.argv[1:], connection_string, protocol)
        # Main execution of program
        cv2.namedWindow("QR READER")
        cap = cv2.VideoCapture(0)

        scanner = zbar.ImageScanner()
        scanner.parse_config('enable')

        p=1
        a=None
        c=0
        valid=0
        invalid=0
        count=0
        q=1
    # Capture frames from the camera4
        cap.set(3,300)
        cap.set(4,400)

        while True:
             ret, output = cap.read()
             if not ret:
                continue
             gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY, dstCn=0)
             pil = Image.fromarray(gray)
             width, height = pil.size
             raw = pil.tobytes()
             image = zbar.Image(width, height, 'Y800', raw)
             scanner.scan(image)
            
             for symbol in image:
               
                root = Tkinter.Tk()
                root.title("QR READER")
                
                root.configure(background ='#e1d8b9')
                w = 1500 # width for the Tk root
                h = 400 # height for the Tk root

                # get screen width and height
                ws = root.winfo_screenwidth() # width of the screen
                hs = root.winfo_screenheight() # height of the screen

                # calculate x and y coordinates for the Tk root window
                x = (ws/2) - (w/2)
                y = (hs/2) - (h/2)

                # set the dimensions of the screen 
                # and where it is placed
                root.geometry('%dx%d+%d+%d' % (w, h, x, y))

                time.sleep(.5)
                if p==1:
                 
                 a=str(symbol.data)   
                 p=2
                c=str(symbol.data)
                   
                if c==a:
                    
                 while(True):
                     
                     ret,frame= cap.read()            
                     
                     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                     
                     cv2.imshow('frame', rgb)
                     
                     #cv2.destroyWindow('frame')
                     
                     #if cv2.waitKey(1) & 0xFF == ord('q'):
                     out = cv2.imwrite('capture.png', frame)
                     
                     break
                 
                 ou1= frame[10:200,10:280]
                 cv2.imwrite("capture.png",ou1)
                 
                 image = cv2.imread("capture.png")
                 img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                 
                 cv2.imwrite("thres.png", img)
                 
                 pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract'
                 text = pytesseract.image_to_string(Image.open('thres.png'))
                    
                 text=text.encode('utf-8')
                 
                 try:
                                
                        
                        if str(newstr) in str(text):
                          
                          label1=Tkinter.Label(root,text="\nVALID BOX",font=('Helvetica 12 bold',50),fg='green')
                          label1.pack()
                          root.after(500, lambda:root.destroy())
                          root.mainloop()

                          count = valid + invalid + 1
                          valid = valid + 1

                          
                          #msg_txt_formatted_1= str(self.valid)
                          msg_txt_formatted = "{\"DeviceId\":\"PRpackageQR\",\"ValidCount\":"+ str(valid) +",\"InvalidCount\":"+ str(invalid) +",\"TotalCount\":"+ str(count) +"}"
                          # print("JSON payload = " + msg_txt_formatted)

                          message = IoTHubMessage(msg_txt_formatted)

                          i = 1  #1 message per exe so static 1

                          message.message_id = "message_%d" % i
                          message.correlation_id = "correlation_%d" % i
                          iotHubClient.send_event_async(message, send_confirmation_callback,i)
                          t_end=time.time()+10
                          break
                           
                        elif str(text)=='':
                            
                          label1 = Tkinter.Label(root,text="\nTRY AGAIN" ,font=('Helvetica 12 bold',50),fg='blue')
                          label1.pack()
                          root.after(500, lambda:root.destroy())
                          root.mainloop()
                          break
                        
                        else:
                         if q==1:

                          label1 = Tkinter.Label(root,text="\nTRY AGAIN" ,font=('Helvetica 12 bold',50),fg='blue')
                          label1.pack()
                          root.after(500, lambda:root.destroy())
                          root.mainloop()
                          q=2
                          break

                         elif q==2:  
                          label1=Tkinter.Label(root,text="\nINVALID BOX",font=('Helvetica 12 bold',50),fg='red')
                          label1.pack()
                          label2=Tkinter.Label(root,text=" X ",font=('Helvetica 12 bold',70),fg='red')
                          label2.pack()
                          root.after(500, lambda:root.destroy())
                          root.mainloop()
                          q=1

                          count  = valid + invalid + 1
                          invalid=invalid + 1
                          msg_txt_formatted = "{\"DeviceId\":\"PRpackageQR\",\"ValidCount\":"+ str(valid) +",\"InvalidCount\":"+ str(invalid) +",\"TotalCount\":"+ str(count) +"}"
                          # print("JSON payload = " + msg_txt_formatted)
                          message = IoTHubMessage(msg_txt_formatted)

                          i = 1  #1 message per exe so static 1

                          message.message_id = "message_%d" % i
                          message.correlation_id = "correlation_%d" % i
                          iotHubClient.send_event_async(message, send_confirmation_callback,i)
                          t_end=time.time()+10
                          break
                 except:
                        
                          label1 = Tkinter.Label(root,text="\n\n\nTRY AGAIN" ,font=('Helvetica 12 bold',50),fg='blue')
                          label1.pack()
                          root.after(500, lambda:root.destroy())
                          root.mainloop()
                          continue
                            
                if c!=a:
                          label=Tkinter.Label(root,text="\nINVALID QR CODE",font=('Helvetica 12 bold',50),fg='red')
                          label.pack()
                          label1=Tkinter.Label(root,text=" X ",font=('Helvetica 12 bold',70),fg='red')
                          label1.pack()
                          root.after(500, lambda:root.destroy())
                          root.mainloop()

                          count= invalid + valid + 1
                          invalid = invalid + 1
                          msg_txt_formatted = "{\"DeviceId\":\"PRpackageQR\",\"ValidCount\":"+ str(valid) +",\"InvalidCount\":"+ str(invalid) +",\"TotalCount\":"+ str(count) +"}"
                      # print("JSON payload = " + msg_txt_formatted)

                          message = IoTHubMessage(msg_txt_formatted)

                          i = 1  #1 message per exe so static 1

                          message.message_id = "message_%d" % i
                          message.correlation_id = "correlation_%d" % i
                          iotHubClient.send_event_async(message, send_confirmation_callback,i)
                          t_end=time.time()+10  
                          break
                   
             cv2.imshow("QR READER", output)
             #time.sleep(1)
            # Wait for the magic key
             keypress = cv2.waitKey(1) & 0xFF
             if keypress == ord('q'):
                 break

    # When everything is done, release the capture
        cap.release()
        cv2.destroyAllWindows()
