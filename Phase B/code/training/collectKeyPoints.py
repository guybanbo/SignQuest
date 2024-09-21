import cv2
import numpy as np
import os
from matplotlib import pyplot as plt
import time
import mediapipe as mp

from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense


mp_holistic = mp.solutions.holistic # Holistic model
mp_drawing = mp.solutions.drawing_utils # Drawing utilities


def getVideosCountPerWord():
    
    # Initialize the dictionary to hold folder names and video counts
    actions_dict = {}

    # Path to the 'videos' directory
    VIDEOS_PATH = os.path.join('videos')

    # Loop through each folder in the 'videos' directory
    for folder_name in os.listdir(VIDEOS_PATH):
        folder_path = os.path.join(VIDEOS_PATH, folder_name)
        if os.path.isdir(folder_path):
            # Count the number of video files in the folder
            video_count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
            # Add to the dictionary
            actions_dict[folder_name] = video_count
    
    return actions_dict


def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # COLOR CONVERSION BGR 2 RGB
    image.flags.writeable = False                  # Image is no longer writeable
    results = model.process(image)                 # Make prediction
    image.flags.writeable = True                   # Image is now writeable 
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # COLOR COVERSION RGB 2 BGR
    return image, results


def extract_keypoints(results):

    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([lh, rh])
    



DATA_PATH = os.path.join('MP_Data')
VIDEOS_PATH = os.path.join('videos')

# Thirty videos worth of data
no_sequences = 30

# Videos are going to be 30 frames in length
sequence_length = 30


# Get the dictionary of actions and their respective video counts
actions_dict = getVideosCountPerWord()

# Set mediapipe model
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    # Loop through actions
    for action, video_count in actions_dict.items():
        action_path = os.path.join(VIDEOS_PATH, action)
        video_files = [f for f in os.listdir(action_path) if os.path.isfile(os.path.join(action_path, f))]
        
        # Loop through sequences aka videos
        for sequence, video_file in enumerate(video_files):
            video_path = os.path.join(action_path, video_file)
            cap = cv2.VideoCapture(video_path)
            frame_num = 0
            
            # Print message to console for each video
            print('STARTING COLLECTION')
            print(f'Collecting frames for {action} Video Number {sequence}')
            print()
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                image_height, image_width, _ = frame.shape

                # Make detections
                _, results = mediapipe_detection(frame, holistic)

                # Export keypoints
                keypoints = extract_keypoints(results)
                
                npy_path = os.path.join(DATA_PATH, action, str(sequence), str(frame_num))
                os.makedirs(os.path.dirname(npy_path), exist_ok=True)
                np.save(npy_path, keypoints)
                
           


                frame_num += 1
                
                # Break gracefully
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break

            cap.release()
    cv2.destroyAllWindows()