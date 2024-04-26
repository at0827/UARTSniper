#We would like to credit GUIDO DIEPEN at 
#https://www.guidodiepen.nl/2017/02/detecting-and-tracking-a-face-with-python-and-opencv/
#for providing much of the inspiration for using facial recognition in python.


#Import the OpenCV, dlib, and serial libraries
import cv2
import dlib
import serial



class AutoTurret:

    def __init__(self) -> None:
        
        #Initialize the trackers list for potential targets.
        self.trackers = {}
        #Set the targetting box color
        self.targettingBoxColor = (100,0,0)
        #Pick and create the kind of classifier desired to identify targets
        self.faceClassifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")#"haarcascade_frontalface_default.xml")haarcascade_upperbody.xml
        
        #Initialize the frame counter and face ids.
        self.frameCounter = 0
        self.currentFaceID = 0


    #target aquisition function that handles finding targets to shoot.
    def target_aquisition(self, baseImage):
        """
        Target acquisition function that identifies potential targets in the input image.

        Arguments:
        - self: The object instance of the class containing this method.
        - baseImage (numpy.ndarray): The base image containing the scene to analyze for targets.
        """

        #Copy the image to a result image which will be annotated with targetting information.
        resultImage = baseImage.copy()
        trackerIDsToDelete = []
        
        #The DLIB library has a notion of tracking quality. Here we check if 
        #the targets we are tracking with the dlib library has a low tracking
        #quality and if so we remove them from the list of viable targets
        #as they may no longer represent viable targets or acurrately reflect
        #the position of the desired target.
        for trackerID in self.trackers.keys():
            trackingQuality = self.trackers[trackerID].update(baseImage)

            #If the tracking quality is bad, delete the tracker.
            if trackingQuality < 4:
                trackerIDsToDelete.append(trackerID)

        for trackerID in trackerIDsToDelete:
            self.trackers.pop(trackerID , None )


        #Every 10 frames, we will have to determine which faces
        #are present in the frame. We do this so that the program regularly
        #scans the image for new targets / updates its knowledge of existing targets
        #if dlib is preforming poorly (ie has low tracking quality and is loosing targets).
        #These targets can be reaquired in this step. However, the reason we only do it
        #every 10 frames is to save computational power. We don't need to do this
        #every iteration of the program so by doing it evey x number of frames we
        #save power and achieve program speedup.
        trackerIDsWithFace = []
        if (self.frameCounter % 10) == 0:

            #We convert the imaage to grayscale so we can do facial detection on it.
            gray = cv2.cvtColor(baseImage, cv2.COLOR_BGR2GRAY)
            #Now use the haar cascade detector to find all faces
            #in the image
            targets = self.faceClassifier.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=4, minSize=(20, 20))

            #loop over the data in each aquired target from the classifier
            for (_x,_y,_w,_h) in targets:
                torso_x = int(_x)
                torso_y = int(_y)
                torso_width = int(_w)
                torso_height = int(_h)

                cv2.rectangle(resultImage, (torso_x, torso_y),
                                    (torso_x + torso_width , torso_y + torso_height),
                                    (100, 100,100) ,2)


                #rectangle centerpoint
                torso_x_center = torso_x + 0.5 * torso_width
                torso_y_center = torso_y + 0.5 * torso_height

                #Used to check if we found a face that's already tracked by us.
                foundtrackerID = None

                #Check all trackers to see if the current new target is already
                #a face we track.
                for trackerID in self.trackers.keys():
                    tracked_position =  self.trackers[trackerID].get_position()

                    tracker_x = int(tracked_position.left())
                    tracker_y = int(tracked_position.top())
                    tracker_width = int(tracked_position.width())
                    tracker_height = int(tracked_position.height())


                    #centerpoint of the tracked face
                    tracker_x_center = tracker_x + 0.5 * tracker_width
                    tracker_y_center = tracker_y + 0.5 * tracker_height


                    #if the centerpoint of the new face is in the 
                    #rectangle spanning the currently considered tracked face
                    #and the centerpoint of the tracked face is in the rectlangle
                    #spanning the new face, then we consider these two faces to
                    #be the same.

                    if (( tracker_x <= torso_x_center   <= (tracker_x + tracker_width)) and 
                            ( tracker_y <= torso_y_center   <= (tracker_y + tracker_height)) and 
                            ( torso_x   <= tracker_x_center <= (torso_x   + torso_width  )) and 
                            ( torso_y   <= tracker_y_center <= (torso_y   + torso_height  ))):
                      foundtrackerID = trackerID

                #If there isn't a match then we have a new face so we create a 
                #new tracker and add it to the list.
                if foundtrackerID is None:

                  
                    #Create and store the tracker 
                    tracker = dlib.correlation_tracker()
                    
                    rectangle = dlib.rectangle((torso_x + torso_width // 4), (torso_y + torso_width//4), (torso_x + 3*torso_width//4), (torso_y + 3*torso_height//4))
                    tracker.start_track(baseImage, rectangle)

                    self.trackers[self.currentFaceID] = tracker

                    #Increase the currentFaceID counter
                    self.currentFaceID += 1

                #See which boxes still have faces in them. We use this information
                #to forceably clear any artifacts such as boxes with no faces in them in case
                #our checks with dlib earlier (the quality checks) do not get them.
                trackerIDsWithFace.append(foundtrackerID)
            
        #Get rid of artifacts
        if (self.frameCounter % 1000) == 0:
            #get rid of trackers with no faces
            trackerIDsToDelete = []
            for trackerID in self.trackers.keys():
                if not trackerID in trackerIDsWithFace:
                    trackerIDsToDelete.append(trackerID)
            for trackerID in trackerIDsToDelete:

                self.trackers.pop(trackerID , None)


        #Draw a rectangle around the face of each target being tracked and
        #label these targets
        for trackerID in self.trackers.keys():
            
            #Get coordinates
            tracked_position = self.trackers[trackerID].get_position()
            tracker_x = int(tracked_position.left())
            tracker_y = int(tracked_position.top())
            tracker_width = int(tracked_position.width())
            tracker_height = int(tracked_position.height())
            
            #Draw rectangle
            cv2.rectangle(resultImage, (tracker_x, tracker_y),
                                    (tracker_x + tracker_width , tracker_y + tracker_height),
                                    self.targettingBoxColor ,2)

            #Label targets
            if trackerID in self.trackers.keys():
                cv2.putText(resultImage, "Target"+str(trackerID) , 
                            (int(tracker_x + tracker_width/2), int(tracker_y)), 
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (255, 255, 255), 2)
            else:
                cv2.putText(resultImage, "Aquiring Target..." , 
                            (int(tracker_x + tracker_width/2), int(tracker_y)), 
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (255, 255, 255), 2)

        #For testing purposes, write the image to a file location
        #or display it for testing on a machien with a GUI
        #cv2.imshow("base-image", baseImage)
        cv2.imwrite("Frame.jpg", resultImage) 

    def select_target(self):
        
      """
      Function selects the oldest target in the targets list to shoot.

      Arguments:
      - self: The object instance of the class containing this method.

      Returns:
      List[coords]: A list of coordinates, [x_center, y_center], which represents the center of a target.
      """

      selected_target_id = sorted(self.trackers.keys()).pop(0)
      target_position = self.trackers[selected_target_id].get_position()

      x_coordinate = int(target_position.left())
      y_coordinate = int(target_position.top())
      target_position_width = int(target_position.width())
      target_position_height = int(target_position.height())

      x_center = x_coordinate + target_position_width / 2
      y_center = y_coordinate + target_position_height / 2

      #Make sure to remove the selected target from the tracked targets.
      self.trackers.pop(selected_target_id)

      return [x_center, y_center]
    
    #Sends the firing solution to the MSP
    def send_firing_solution(self, firing_solution):
      """
      Function sends the firing solution to the msp430s.

      Arguments:
      - self: The object instance of the class containing this method.
      - firing_solution list: A list of coordinates, [x_center, y_center], which represents the center of a target.

      """
     
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
      
      # close the serial communications.
      ser_x.close()
      ser_y.close()
        
        
    def main(self):
      """
      Main functionality of the AutoTurret Class. Controls the interface with
      the camera and handles calling the target aquisition and send firing
      solution functions.

      Arguments:
      - self: The object instance of the class containing this method.
      """
        
        
        
      #Turn the camera on so we can deterct targets and see what they're shooting at.
      capture = cv2.VideoCapture(0)

      #This is the main while loop where we execure all of our logic.
      #We aquire targets, send targetting data to the msp who kills the targets.
      #and continute to update targetting lists.
      while True:
          

      #Target aquisition

        #Open the first webcame device
          ret, frame = capture.read()

          #Downsample because we're poor and the pi can't handle high res
          #images
          working_image = cv2.resize(frame, (240, 180))


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
    
    
#Create an instance of the autoturret class and call the main function.
turret = AutoTurret()
turret.main()
