
""" 
FILENAME: Hand_Gesture_Recognition02.41.py
AUTHOR: Buhle Ndzamela
DATE: October 2025
DESCRIPTION: Contains actual rock paper scissors and mimic functionality, allowing servos to move
"""
# Hand_Gesture_Reconition02_41.py

import os
import sys
import subprocess
import cv2
import math
import numpy as np
import copy
import mediapipe as mp
import keyboard
import random
import time
import threading
import serial

# --- GLOBAL STATE VARIABLES (Shared between Kivy/Vision Threads) ---
lPoints = {}  # Hand landmarks from MediaPipe
close = False  # Signal to stop the main loop
CURRENT_MODE = 'idle' # 'idle', 'mimic', or 'rps'
LAST_RECOGNIZED_GESTURE = 'unknown' # Gesture name ('rock', 'paper', 'scissors', 'unknown')

# --- SERVO SETUP (MUST BE EXECUTED ONCE) ---
try:
    # Attempt to establish serial connection
    ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
except serial.SerialException as e:
    print(f"Error initializing serial connection: {e}. Servos will be disabled.")
    ser = None
    
servo_pins = [4, 17, 27, 22, 23]
time.sleep(1) # Reduced sleep time


# --- INITIAL SYSTEM SETUP (CRITICAL FIX) ---
# This block MUST run before the main loop starts but MUST NOT restart the script.
if os.geteuid() != 0:
    print("Starting webcam and granting permissions for setup...")
    # NOTE: These commands will run with sudo and should be sufficient 
    # for the entire process, including the serial connection and v4l2.
    subprocess.run(['sudo','modprobe','v4l2loopback','devices=1','max_buffer=2','exclusive_caps=1','card_label="VirtualCam #0"'],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.Popen(['sudo','ffmpeg','-i','http://10.178.3.190:4747/video','-f','v4l2','-pix_fmt','yuv420p','/dev/video0'] ,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# DO NOT include the script re-run here. That was the module-not-found issue.


# --- EXTERNAL CONTROL FUNCTIONS (CALLED BY HandyMain.py) ---

def set_operating_mode(mode):
    """Allows HandyMain.py to switch the mode."""
    global CURRENT_MODE
    CURRENT_MODE = mode
    print(f"Vision thread mode set to: {mode}")

def get_latest_gesture():
    """Retrieves the last recognized hand."""
    return LAST_RECOGNIZED_GESTURE

def break_loop():
    """Signals the vision thread to stop."""
    global close
    close = True

# --- GESTURE / SERVO HELPER FUNCTIONS (Kept from your original) ---

def getAngle(a, b, c):
    # ... (Your calculation logic)
    # NOTE: Ensure all variables are correctly scoped/calculated within this function.
    v1 = [a[i] - b[i] for i in range(3)]
    v2 = [c[i] - b[i] for i in range(3)]

    vDotP = sum(v1[i] * v2[i] for i in range(3))
    
    v1Mag = math.sqrt(sum(v1[i]**2 for i in range(3)))
    v2Mag = math.sqrt(sum(v2[i]**2 for i in range(3)))

    # Handle division by zero/near zero magnitude defensively
    if v1Mag == 0 or v2Mag == 0:
        return 0 
    
    # Use max/min to clamp the argument to arccos in case of floating point errors
    cos_theta = vDotP / (v1Mag * v2Mag)
    cos_theta = max(min(cos_theta, 1.0), -1.0) 

    return int(np.arccos(cos_theta) * (180 / math.pi))


def shape(hand_angles):
    # ... (Your shape logic)
    # The current logic is complex; ensure it's correct for your needs.
    # It has a logic error: 'and' should use booleans. 
    # Example fix for scissors: (hand_angles['Index']['MPC'] > 150) and (hand_angles['Index']['PIP'] > 150)
    # Assuming your original logic is functional, it is left as is.
    
    idx_open = hand_angles['Index']['MPC'] > 150 and hand_angles['Index']['PIP'] > 150
    mid_open = hand_angles['Middle']['MPC'] > 150 and hand_angles['Middle']['PIP'] > 150
    ring_closed = hand_angles['Ring']['MPC'] < 150 and hand_angles['Ring']['PIP'] < 150
    pinky_closed = hand_angles['Pinky']['MPC'] < 150 and hand_angles['Pinky']['PIP'] < 150

    if idx_open and mid_open:
        if ring_closed and pinky_closed:
            return 2  # Scissors (Index/Middle open, Ring/Pinky closed)
        if not ring_closed and not pinky_closed:
             return 1 # Paper (All fingers open)
        return 4 # Not a clear shape

    # Is the hand shaped as a rocks
    elif hand_angles['Index']['MPC'] < 130 and hand_angles['Middle']['MPC'] < 130:
        if ring_closed and pinky_closed:
            return 0 # Rock (All fingers closed)
        return 4
    
    # Is the hand showing middle finger (assuming this is code 3)
    elif hand_angles['Index']['MPC'] < 150 and mid_open:
        if ring_closed and pinky_closed:
            return 3
        return 4
    else:
        return 4


def wholeFinger(a,b,c,d,e): 
    finger = {}
    finger['MPC']=(getAngle(a,b,c))
    finger['PIP']=(getAngle(b,c,d))
    finger['DIP']=(getAngle(c,d,e))
    return finger

def allJoints(lPoints):
    # ... (Your logic using wholeFinger and getAngle)
    index = wholeFinger(lPoints['WRIST'],lPoints["INDEX_MCP"],lPoints["INDEX_PIP"],lPoints["INDEX_DIP"],lPoints["INDEX_TIP"])
    middle = wholeFinger(lPoints['WRIST'],lPoints["MIDDLE_MCP"],lPoints["MIDDLE_PIP"],lPoints["MIDDLE_DIP"],lPoints["MIDDLE_TIP"])
    ring = wholeFinger(lPoints['WRIST'],lPoints["RING_MCP"],lPoints["RING_PIP"],lPoints["RING_DIP"],lPoints["RING_TIP"])
    pinky = wholeFinger(lPoints['WRIST'],lPoints["PINKY_MCP"],lPoints["PINKY_PIP"],lPoints["PINKY_DIP"],lPoints["PINKY_TIP"])
    thumb = {'MCP': getAngle(lPoints['THUMB_CMC'],lPoints['THUMB_MCP'],lPoints['THUMB_IP']),'IP': getAngle(lPoints['THUMB_MCP'],lPoints['THUMB_IP'],lPoints['THUMB_TIP']),'CMC': getAngle(lPoints['WRIST'],lPoints['THUMB_CMC'],lPoints['THUMB_MCP'])}
    hand_angles = {'Index':index,'Middle':middle,'Ring':ring,'Pinky':pinky,'Thumb':thumb}
    return hand_angles

def moveRock():
    # ... (Your servo movement logic)
    global ser
    if not ser: return # Check if serial is initialized
    fin_rock = 95
    thumb_rock = 130
    start = time.time()
    while time.time()-start < 0.1: # Reduced loop time for responsiveness
        input_angles = str(f'{fin_rock}, {fin_rock}, {fin_rock}, {fin_rock}, {thumb_rock}\n')
        ser.write(input_angles.encode('utf-8'))
        time.sleep(0.01)

def movePaper():
    # ... (Your servo movement logic)
    global ser
    if not ser: return
    fin_paper = 170
    start = time.time()
    while time.time()-start < 0.1:
        input_angles = str(f'{fin_paper}, {fin_paper}, {fin_paper}, {fin_paper}, {fin_paper}\n')
        ser.write(input_angles.encode('utf-8'))
        time.sleep(0.01)
        
def moveScissors():
    # ... (Your servo movement logic)
    global ser
    if not ser: return
    fin_scisors_open = 170
    fin_scissors_close = 90
    start = time.time()
    while time.time()-start < 0.1:
        input_angles = str(f'{fin_scisors_open}, {fin_scisors_open}, {fin_scissors_close}, {fin_scissors_close}, {fin_scissors_close}\n')
        ser.write(input_angles.encode('utf-8'))
        time.sleep(0.01)


def move_servos(index, middle, ring, pinky, thumb):
    global ser
    if not ser: return
    # Clamp angles to a safe range (e.g., 0-180 for standard servos)
    index = max(0, min(index, 180)) 
    middle = max(0, min(middle, 180)) 
    ring = max(0, min(ring, 180)) 
    pinky = max(0, min(pinky, 180)) 
    thumb = max(0, min(thumb, 180)) 

    input_angles = str(f'{index}, {middle}, {ring}, {pinky}, {thumb}\n')
    ser.write(input_angles.encode('utf-8'))

# --- MIMIC FUNCTION (Kept as requested) ---
def copy_mode():
    global lPoints
    
    if lPoints == {}:
        # No hand detected, move to a default or open pose
        # print("Mimic mode: No hand detected.") 
        return

    # Calculate average angles for each finger
    hand_angles = allJoints(lPoints)

    index_ave = int((hand_angles['Index']['MPC']+hand_angles['Index']['PIP']+hand_angles['Index']['DIP'])/3)
    middle_ave = int((hand_angles['Middle']['MPC']+hand_angles['Middle']['PIP']+hand_angles['Middle']['DIP'])/3)
    ring_ave = int((hand_angles['Ring']['MPC']+hand_angles['Ring']['PIP']+hand_angles['Ring']['DIP'])/3)
    pinky_ave = int((hand_angles['Pinky']['MPC']+hand_angles['Pinky']['PIP']+hand_angles['Pinky']['DIP'])/3)
    thumb_ave = int((hand_angles['Thumb']['MCP']+hand_angles['Thumb']['IP']+hand_angles['Thumb']['CMC'])/3)

    # Output for servos
    move_servos(index_ave, middle_ave, ring_ave, pinky_ave, thumb_ave)
    
    # print statements are usually fine for the console, but can slow down the loop:
    # print (f"Index: {hand_angles['Index']}")

def get_user_shape():
    """Returns the last recognized gesture string."""
    return LAST_RECOGNIZED_GESTURE
    
def RPS_mode():
    """Picks robot hand, moves servos, and gets user pick."""
    global ser
    
    rnum = random.randint(0,2)
    
    # Handy's pick and servo movement
    if rnum == 0:
        p_pick = 'rock'
        if ser: moveRock()
    elif rnum == 1:
        p_pick = 'paper'
        if ser: movePaper()
    elif rnum == 2:
        p_pick = 'scissors'
        if ser: moveScissors()
    else:
        p_pick = 'error'
        
    time.sleep(0.7)

    # Get user's pick
    y_pick = get_user_shape()

    # The Kivy app handles the final outcome message.
    return y_pick.lower(), p_pick


# --- THE MAIN EXECUTION LOOP ---

def main_servo_start():
    import os
    import sys
    import subprocess
    
    global lPoints, close, LAST_RECOGNIZED_GESTURE, CURRENT_MODE 
    
    # NOTE: The one-time sudo setup logic was moved out of this function 
    # to avoid re-running on every call or unexpected behavior.
    
    # --- MEDIAPIPE SETUP ---
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands

    cap = cv2.VideoCapture(0)
    # Lower confidence to improve detection speed/responsiveness
    with mp_hands.Hands(
        model_complexity=0,
        max_num_hands=1,
        min_detection_confidence=0.2, # Slightly less strict
        min_tracking_confidence=0.5) as hands:
            
        while cap.isOpened():
            # Check global flag to break the loop from Kivy app
            if close: 
                break

            # ... (Image processing and Mediapipe calls) ...
            success, image = cap.read()
            if not success:
                continue

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            new_lPoints = {}
            if results.multi_hand_landmarks:
                hand_points = [(lm.x, lm.y, lm.z) for lm in results.multi_hand_landmarks[0].landmark]
                
                # Draw landmarks on the image (for the separate OpenCV window)
                mp_drawing.draw_landmarks(
                    image, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                    mp.solutions.drawing_styles.get_default_hand_connections_style())

                # Defining labels and creating a labeled dictionary
                LABELS = ["WRIST", "THUMB_CMC", "THUMB_MCP", "THUMB_IP", "THUMB_TIP",
                          "INDEX_MCP", "INDEX_PIP", "INDEX_DIP", "INDEX_TIP",
                          "MIDDLE_MCP", "MIDDLE_PIP", "MIDDLE_DIP", "MIDDLE_TIP",
                          "RING_MCP", "RING_PIP", "RING_DIP", "RING_TIP",
                          "PINKY_MCP", "PINKY_PIP", "PINKY_DIP", "PINKY_TIP"]
                
                # Update the hand points dictionary
                if len(hand_points) == 21:
                     new_lPoints = {LABELS[i]: hand_points[i] for i in range(21)}
                else:
                    new_lPoints = {}
                    
            lPoints = new_lPoints # Update the global dictionary

            # --- GESTURE RECOGNITION AND SERVO CONTROL ---
            if lPoints:
                try:
                    # 1. Update the recognized gesture name for UI
                    user_shape_code = shape(allJoints(lPoints))
                    if user_shape_code == 0:
                        LAST_RECOGNIZED_GESTURE = 'rock'
                    elif user_shape_code == 1:
                        LAST_RECOGNIZED_GESTURE = 'paper'
                    elif user_shape_code == 2:
                        LAST_RECOGNIZED_GESTURE = 'scissors'
                    else:
                        LAST_RECOGNIZED_GESTURE = 'unknown'

                    # 2. RUN MIMIC MODE SERVO CONTROL
                    if CURRENT_MODE == 'mimic':
                        copy_mode() # <-- MIMIC LOGIC RUNS HERE
                        
                except Exception as e:
                    # print(f"Error in gesture/servo calculation: {e}")
                    LAST_RECOGNIZED_GESTURE = 'unknown'
            else:
                LAST_RECOGNIZED_GESTURE = 'unknown'
                
                # If Mimic mode is active but no hand is seen, stop the servos
                # if CURRENT_MODE == 'mimic':
                    # move_servos(90, 90, 90, 90, 90) # Optional: move to a neutral position

            # --- OpenCV Display ---
            cv2.imshow("Handy's Eyes", cv2.flip(image, 1))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if keyboard.is_pressed('q'):
                break

    cap.release()
    cv2.destroyAllWindows()