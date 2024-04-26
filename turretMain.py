# import cv2
# import AutoTurret

# ser_x = serial.Serial()
# ser_x.port = '/dev/ttyACM2'
# ser_x.baudrate = 19200
# ser_x.open()

# # # Send the x-coordinate
# x_coordinate = 120
# ser_x.write(x_coordinate.to_bytes(1, byteorder='big'))  # Convert integer to one byte

# # y_coordinate = 
# # ser_x.write(x_coordinate.to_bytes(1, byteorder='big'))  # Convert integer to one byte

# # Read x-coordinate from first MSP430
# #reply = ser_x.read(1)
# #reply = int.from_bytes(reply, byteorder='big')
# #print(f"Received x-coordinate: {reply}")

# # Read y-coordinate from second MSP430
# # y_coordinate = ser_y.read(1)
# # y_coordinate = int.from_bytes(y_coordinate, byteorder='big')
# # print(f"Received y-coordinate: {y_coordinate}")

# # Close serial ports
# ser_x.close()



















#Import the OpenCV and dlib libraries
import cv2
import dlib
import serial
import time


#The deisred output width and height
OUTPUT_SIZE_WIDTH = 500
OUTPUT_SIZE_HEIGHT = 400



class AutoTurret:

    def __init__(self) -> None:
        self.trackers = {}
        self.targettingBoxColor = (100,0,0)
        self.torsoClassifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")#"haarcascade_frontalface_default.xml")haarcascade_upperbody.xml
        self.frameCounter = 0
        self.currentFaceID = 0
        #Can get rid of these once testing is done.
        self.OUTPUT_SIZE_WIDTH = 775
        self.OUTPUT_SIZE_HEIGHT = 600


    #target aquisition function that handles finding targets to shoot.
    def target_aquisition(self, baseImage):
        resultImage = baseImage.copy()
        trackerIDsToDelete = []
                    
        for trackerID in self.trackers.keys():
            trackingQuality = self.trackers[trackerID].update(baseImage)

            #If the tracking quality is good enough, we must delete
            #this tracker
            if trackingQuality < 4:
                trackerIDsToDelete.append(trackerID)

        for trackerID in trackerIDsToDelete:
            # print("Removing trackerID " + str(trackerID) + " from list of trackers")
            self.trackers.pop(trackerID , None )


        #Every 10 frames, we will have to determine which faces
        #are present in the frame
        trackerIDsWithFace = []
        if (self.frameCounter % 10) == 0:

            #For the face detection, we need to make use of a gray
            #colored image so we will convert the baseImage to a
            #gray-based image
            gray = cv2.cvtColor(baseImage, cv2.COLOR_BGR2GRAY)
            #Now use the haar cascade detector to find all faces
            #in the image
            targets = self.torsoClassifier.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=4, minSize=(20, 20))



            #Loop over all faces and check if the area for this
            #face is the largest so far
            #We need to convert it to int here because of the
            #requirement of the dlib tracker. If we omit the cast to
            #int here, you will get cast errors since the detector
            #returns numpy.int32 and the tracker requires an int
            
            for (_x,_y,_w,_h) in targets:
                torso_x = int(_x)
                torso_y = int(_y)
                torso_width = int(_w)
                torso_height = int(_h)

                cv2.rectangle(resultImage, (torso_x, torso_y),
                                    (torso_x + torso_width , torso_y + torso_height),
                                    (100, 100,100) ,2)


                #calculate the centerpoint
                torso_x_center = torso_x + 0.5 * torso_width
                torso_y_center = torso_y + 0.5 * torso_height

                #Variable holding information which faceid we 
                #matched with
                foundtrackerID = None

                #Now loop over all the trackers and check if the 
                #centerpoint of the face is within the box of a 
                #tracker
                for trackerID in self.trackers.keys():
                    tracked_position =  self.trackers[trackerID].get_position()

                    tracker_x = int(tracked_position.left())
                    tracker_y = int(tracked_position.top())
                    tracker_width = int(tracked_position.width())
                    tracker_height = int(tracked_position.height())


                    #calculate the centerpoint
                    tracker_x_center = tracker_x + 0.5 * tracker_width
                    tracker_y_center = tracker_y + 0.5 * tracker_height

                    #check if the centerpoint of the face is within the 
                    #rectangleof a tracker region. Also, the centerpoint
                    #of the tracker region must be within the region 
                    #detected as a face. If both of these conditions hold
                    #we have a match

                    #Check if the centerpoint of the face is inside the rectangle
                    #for a tracker region and check if the centerpoint of 
                    #tracker is inside the region bounded fr the face.

                    if (( tracker_x <= torso_x_center   <= (tracker_x + tracker_width)) and 
                            ( tracker_y <= torso_y_center   <= (tracker_y + tracker_height)) and 
                            ( torso_x   <= tracker_x_center <= (torso_x   + torso_width  )) and 
                            ( torso_y   <= tracker_y_center <= (torso_y   + torso_height  ))):
                      foundtrackerID = trackerID
                      #print("FOUND", foundtrackerID)

                #If no matched fid, then we have to create a new tracker
                if foundtrackerID is None:

                    # print("Creating new tracker " + str(self.currentFaceID))
                    #Create and store the tracker 
                    tracker = dlib.correlation_tracker()
                    # print("coord", (torso_x, torso_y, torso_width, torso_height))
                    
                    rectangle = dlib.rectangle((torso_x + torso_width // 4), (torso_y + torso_width//4), (torso_x + 3*torso_width//4), (torso_y + 3*torso_height//4))

                    #print(rectangle)
                    # print("made it")
                    tracker.start_track(baseImage, rectangle)

                    self.trackers[self.currentFaceID] = tracker

                    #Increase the currentFaceID counter
                    self.currentFaceID += 1
                trackerIDsWithFace.append(foundtrackerID) #See which boxes still have faces in them
            
        #Get rid of artifacts
        if (self.frameCounter % 1000) == 0:
            #get rid of trackers with no faces
            trackerIDsToDelete = []
            for trackerID in self.trackers.keys():
                if not trackerID in trackerIDsWithFace:
                    trackerIDsToDelete.append(trackerID)
            for trackerID in trackerIDsToDelete:
                #print("Fids to delete", trackerID)
                #print("Removing fid " + str(trackerID) + " from list of trackers")
                self.trackers.pop(trackerID , None)


        #Now loop over all the trackers we have and draw the rectangle
        #around the detected faces. If we 'know' the name for this person
        #(i.e. the recognition thread is finished), we print the name
        #of the person, otherwise the message indicating we are detecting
        #the name of the person
        for trackerID in self.trackers.keys():
            tracked_position = self.trackers[trackerID].get_position()

            tracker_x = int(tracked_position.left())
            tracker_y = int(tracked_position.top())
            tracker_width = int(tracked_position.width())
            tracker_height = int(tracked_position.height())

            cv2.rectangle(resultImage, (tracker_x, tracker_y),
                                    (tracker_x + tracker_width , tracker_y + tracker_height),
                                    self.targettingBoxColor ,2)


            if trackerID in self.trackers.keys():
                cv2.putText(resultImage, "Target"+str(trackerID) , 
                            (int(tracker_x + tracker_width/2), int(tracker_y)), 
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (255, 255, 255), 2)
            else:
                cv2.putText(resultImage, "Detecting..." , 
                            (int(tracker_x + tracker_width/2), int(tracker_y)), 
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (255, 255, 255), 2)

        #Since we want to show something larger on the screen than the
        #original 320x240, we resize the image again
        #
        #Note that it would also be possible to keep the large version
        #of the baseimage and make the result image a copy of this large
        #base image and use the scaling factor to draw the rectangle
        #at the right coordinates.
        largeResult = cv2.resize(resultImage,
                                    (OUTPUT_SIZE_WIDTH,OUTPUT_SIZE_HEIGHT))

        #Finally, we want to show the images on the screen
        #cv2.imshow("base-image", baseImage)
        cv2.imwrite("Frame.jpg", largeResult) 

    def select_target(self):
        selected_target_id = sorted(self.trackers.keys()).pop(0)
        target_position = self.trackers[selected_target_id].get_position()

        x_coordinate = int(target_position.left())
        y_coordinate = int(target_position.top())
        target_position_width = int(target_position.width())
        target_position_height = int(target_position.height())

        x_center = x_coordinate + target_position_width / 2
        y_center = y_coordinate + target_position_height / 2

        #Make sure to remove the selected target from the tracked targets.
        #self.trackers.pop(selected_target_id)

        return [x_center, y_center]
    
    #Sends the firing solution to the MSP
    def send_firing_solution(self, firing_solution):
      
      #Send the y coordinate to MSP2
      ser_y = serial.Serial()
      ser_y.port = '/dev/ttyACM3'
      ser_y.baudrate = 19200
      ser_y.open()
      ser_y.write(int (firing_solution[1]).to_bytes(1, byteorder='big'))  # Convert integer to one byte
      
      #Send the x coordinate to MSP1     
      ser_x = serial.Serial()
      ser_x.port = '/dev/ttyACM1'
      ser_x.baudrate = 19200
      ser_x.open()
      ser_x.write(int (firing_solution[0]).to_bytes(1, byteorder='big'))  # Convert integer to one byte
      
      #reply = ser_x.read(1)
      #reply = int.from_bytes(reply, byteorder='big')
      #print(f"Received x-coordinate: {reply}")

      

      #TODO Get rid of this debugging stuff for final ver.
      #Reading for debugging
      # reply = ser_x.read(1)
      # reply = int.from_bytes(reply, byteorder='big')
      # print(f"Received x-coordinate: {reply}")

      # close that hoe
      ser_x.close()
      ser_y.close()
        
        
    def main(self):
        
        #Turn the camera on so we can deterct targets and see what they're shooting at.
        capture = cv2.VideoCapture(0)

        #TODO In the future I would like to do facial regognition to know if a
        # target is dead and recognize dead targets. The current omplementation
        #of our firing scheme doesn't do this. It works in fids which are
        #related to tracking frames and have nothing to do with unique faces.

        #This is the main while loop where we execure all of our logic.
        #Here we aquire targets, send targetting data to the msp who lills the targets.
        #and continute to update targetting lists.
        while True:
            
        #do any setup here

        #Target aquisition

         #Open the first webcame device
            ret, frame = capture.read()

            #Downsample because we're poor and the pi can't handle high res
            #images
            working_image = cv2.resize(frame, (240, 180))

            #TODO get rid of this once testing is done bc it's not
            #doing anything useful.
            #Check if a key was pressed and if it was Q, then break
            #from the infinite loop
            pressedKey = cv2.waitKey(2)
            if pressedKey == ord('Q'):
                break

            #Result image is the image we will show the user, which is a
            #combination of the original image from the webcam and the
            #overlayed rectangle for the largest face
            self.frameCounter+=1
            self.target_aquisition(working_image)


            #If there are aquired targets. Engage the targets.
            if ((len(self.trackers) != 0) and (self.frameCounter % 10 == 0)):
                # Select a target and send the corresponding firing solution
                # to the msps to move the servos to hit the target.
                firing_solution = self.select_target()
                #print("firing Solution", firing_solution)
                self.send_firing_solution(firing_solution)
            #Update all the trackers and remove the ones for which the update
            #indicated the quality was not good enough
            
   
    #Destroy any OpenCV windows and exit the application
    cv2.destroyAllWindows()
    
    

turret = AutoTurret()
turret.main()