import cv2
import numpy as np
import os
from matplotlib import pyplot as plt
import time
import mediapipe as mp
from tensorflow.keras.layers import BatchNormalization,Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Masking,Bidirectional,Input
import tensorflow as tf

mp_holistic = mp.solutions.holistic # Holistic model
mp_drawing = mp.solutions.drawing_utils # Drawing utilities


def mediapipe_detection(image, model):
    
    """
        Converts image to RGB, processes it with the given model.
        
        Parameters:
        - image: The input image in BGR format.
        - model: The Mediapipe model used for prediction.
        
        Returns:
        - image: The processed image in RGB format.
        - results: The results from the model prediction.
    """
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # COLOR CONVERSION BGR 2 RGB
    image.flags.writeable = False                  # Image is no longer writeable
    results = model.process(image)                 # Make prediction
    image.flags.writeable = True                   # Image is now writeable 
    #image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # COLOR COVERSION RGB 2 BGR
    return image, results


def draw_landmarks(image, results):
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS) # Draw face connections
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS) # Draw pose connections
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS) # Draw left hand connections
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS) # Draw right hand connections
    
    
def draw_styled_landmarks(image, results):
    
    """
        Draws landmarks on the image for both hands using Mediapipe drawing utilities.
        
        Parameters:
        - image: The input image to draw landmarks on.
        - results: The landmarks data from the Mediapipe model.
        
        Returns:
        - None: The function modifies the image in place.
    """

    # Draw left hand connections
    mp_drawing.draw_landmarks(
        image, results.left_hand_landmarks, mp.solutions.holistic.HAND_CONNECTIONS,
        #mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4),
        #mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2)
    )
    # Draw right hand connections  
    mp_drawing.draw_landmarks(
        image, results.right_hand_landmarks, mp.solutions.holistic.HAND_CONNECTIONS,
        #mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4),
       # mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
    )




def extract_keypoints(results):
    
    """
    Extracts and flattens keypoints for both hands from Mediapipe results.

    Parameters:
    - results: The landmarks data from the Mediapipe model.

    Returns:
    - A numpy array containing the flattened keypoints for the left and right hands.
      If landmarks are missing, zeros are used as placeholders.
      
    """
    
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([lh, rh])


colors = [(245,117,16), (117,245,16), (16,117,245)]
def prob_viz(res, actions, input_frame, colors):
    output_frame = input_frame.copy()
    for num, prob in enumerate(res):
        cv2.rectangle(output_frame, (0,60+num*40), (int(prob*100), 90+num*40), colors[num], -1)
        cv2.putText(output_frame, actions[num], (0, 85+num*40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)





# trained words list
actions = np.array(['bathroom', 'cost', 'deaf', 'drink', 'eat', 'fine', 'go', 'good',
                    'goodbye', 'hamburger', 'hello', 'home', 'how', 'israel', 'learn',
                    'live', 'me', 'morning', 'no', 'please', 'thank you', 'want',
                    'water', 'what', 'when', 'where', 'work', 'yes', 'you', 'your'])

# minimum threshold for success prediction
threshold = 1 / actions.size

model = Sequential()
model.add(Input(shape=(119, 126)))  # Define the input shape using Input layer
# Add BatchNormalization after each LSTM layer
model.add(LSTM(32, return_sequences=True, activation='relu'))
model.add(BatchNormalization())
model.add(LSTM(32, return_sequences=True, activation='relu'))
model.add(BatchNormalization())
model.add(LSTM(16, return_sequences=False, activation='relu'))
model.add(BatchNormalization())
model.add(Dense(64, activation='relu'))
model.add(BatchNormalization())  # Add BatchNormalization after Dense layer
model.add(Dense(32, activation='relu'))
model.add(BatchNormalization())  # Add BatchNormalization after Dense layer

model.add(Dense(actions.shape[0], activation='softmax'))

# Create the optimizer with the specified learning rate
optimizer = Adam(clipnorm=1.0)  # or clipvalue=0.5

# Compile the model
model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])


# loading the weights to the model
try:
    loaded_model = tf.keras.models.load_model('model/new_action2.keras')
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
