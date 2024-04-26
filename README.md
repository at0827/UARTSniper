# UARTSniper
## ELEC 327 Final Project

This repository contains the source code for an automated turret tracking system designed to point a light (LED) towards a detected face using a camera system. The system utilizes a Raspberry Pi for face detection and two MSP430 microcontrollers to control servo motors for accurate positioning in both x and y axes.

# System Architecture

## Hardware Components
- Raspberry Pi 4: Runs the facial detection software and communicates coordinates to two MSP430 microcontrollers.
- Two MSP430 LaunchPads: Each controls one axis of a servo motor system. One MSP430 is dedicated to the x-coordinate, and the other to the y-coordinate.
- Two Servo Motors: Control the movement of the turret system along the specified coordinates.
- Camera Module: Connected to the Raspberry Pi to capture real-time video for face detection.
- LED: Attached to the turret and pointed in the direction determined by the servo's position.

## Software Components
- Python Script (turretMain.py): Implements the face detection using OpenCV and sends the coordinates of the detected face to the MSP430s via serial communication.
- MSP430 Firmware (main.c): Receives coordinates from the Raspberry Pi, calculates the PWM values using a mapping function to adjust the servo positions, and controls the servo motors accordingly.
  
## Power Considerations
- Using a 5V power pack such as a standard 5V phone charging power brick can cause the servos to shudder uncontrollably on startup.
- Potential fixes to this problem are to use a more robust power source, ie. using a brick that pulls power directly from a
- wall outlet and supports high current draw or to use multiple power bricks as well as wire a capacitor in parallel with each
- servo to offset current draw issues. Altenatively using any standard laptop as a power source also works likely due to the
- laptops more sophisticated protocal for figuring out how much power needs to be supplied to the connected system.

## System Diagram
[insert system diagram here]

![image](https://github.com/at0827/UARTSniper/assets/31556111/e1f7bf1e-00a4-4349-ae52-352497148f03)



# Setup and Installation

## Raspberry Pi Setup:
1. Install Python 3 and OpenCV.
2. Clone the repository and install required Python packages.
3. Connect the camera and configure it for facial recognition.

## MSP430 Setup:
1. Flash the main.c code to the respective MSP430 devices.
2. Connect each MSP430 to a servo motor as per the wiring diagrams.

Hardware Assembly:
Assemble the turret structure with servo motors and mount the camera and LED.

# Usage

To run the system:

1. Power up the Raspberry Pi and MSP430s.
2. Execute the Python script to start the face detection and tracking:

```
python turretMain.py
```

3. Adjust the parameters in the script for detection sensitivity and motor responsiveness as needed.
