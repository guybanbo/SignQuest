from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
import cv2
import numpy as np
import os
from matplotlib import pyplot as plt
import time
import mediapipe as mp
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.optimizers import Adam


from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Masking, Dropout,Conv1D , Bidirectional,Input
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import tensorflow as tf
from tensorflow.keras.regularizers import l2
import keras_tuner as kt
import os
import shutil
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report, ConfusionMatrixDisplay
from concurrent.futures import ThreadPoolExecutor
from tensorflow.keras.callbacks import Callback


# Define the directory path
directory_path = 'my_dir/intro_to_kt'

# Remove the directory if it exists
if os.path.exists(directory_path):
    shutil.rmtree(directory_path)

# Create the directory structure
os.makedirs(directory_path)




DATA_PATH = os.path.join('MP_Data2/MP_Data')
VIDEOS_PATH = os.path.join('videos')


# Determine the actions (folder names)
actions = np.array([folder for folder in os.listdir(DATA_PATH) if os.path.isdir(os.path.join(DATA_PATH, folder))])

#actions = np.array(['hello','goodbye','deaf','what'])

# Create the label map
label_map = {label: num for num, label in enumerate(actions)}


def custom_pad_sequences(sequences, maxlen):
    padded_sequences = []
    for seq in sequences:
        seq_len = len(seq)
        if seq_len < maxlen:
            repeat_len = maxlen - seq_len
            repeat_values = np.tile(seq[:1], (repeat_len, 1))  # Repeat the first frame
            padded_seq = np.concatenate([seq, repeat_values], axis=0)
        else:
            padded_seq = seq[:maxlen]
        padded_sequences.append(padded_seq)
    return np.array(padded_sequences)



def load_sequence(sequence_path, sequence_length):
    window = []
    for frame_num in range(sequence_length):
        res = np.load(os.path.join(sequence_path, "{}.npy".format(frame_num)))
        window.append(res)
    return window

'''
def load_data(videos_path, actions, label_map):
    sequences, labels = [], []

    with ThreadPoolExecutor() as executor:
        futures = []
        for action in actions:
            action_path = os.path.join(videos_path, action)
            no_sequences = len([folder for folder in os.listdir(action_path) if os.path.isdir(os.path.join(action_path, folder))])

            for sequence in range(no_sequences):
                sequence_path = os.path.join(action_path, str(sequence))
                sequence_length = len([file for file in os.listdir(sequence_path) if file.endswith('.npy')])
                
                if sequence_length <= 152:
                    futures.append(executor.submit(load_sequence, sequence_path, sequence_length))
                    labels.append(label_map[action])

        for future in futures:
            sequences.append(future.result())

    return sequences, labels
'''

def load_data(videos_path,actions,label_map):

    sequences, labels = [], []

    # Loop through each action (folder)
    for action in actions:
        action_path = os.path.join(videos_path, action)
        
        # Determine the number of sequences (subfolders)
        no_sequences = len([folder for folder in os.listdir(action_path) if os.path.isdir(os.path.join(action_path, folder))])
        
        # Loop through each sequence (subfolder)
        for sequence in range(no_sequences):
            sequence_path = os.path.join(action_path, str(sequence))
            
            # Determine the number of frames (npy files) in the sequence folder
            sequence_length = len([file for file in os.listdir(sequence_path) if file.endswith('.npy')])
            
            if sequence_length <= 119:
            
                window = []
                # Loop through each frame number in the sequence
                for frame_num in range(sequence_length):
                    res = np.load(os.path.join(sequence_path, "{}.npy".format(frame_num)))
                    window.append(res)
                
                sequences.append(window)
                labels.append(label_map[action])

    return sequences, labels


# Load the data
sequences, labels = load_data(DATA_PATH,actions,label_map)


maxlen = max(len(seq) for seq in sequences)

print(len(sequences[0]))

# Pad sequences to the same length
padded_sequences = pad_sequences(sequences, padding='post', dtype='float64')

#padded_sequences = custom_pad_sequences(sequences, maxlen)

print(np.array(sequences,dtype=object).shape)


#np.array(sequences).shape
#np.array(labels).shape
        
X = np.array(padded_sequences,dtype='float64')

#print(X.shape)

#print(actions.shape[0])

y = to_categorical(labels).astype(int)
 

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.10)


early_stopping = EarlyStopping(monitor='val_loss', patience=10)
model_checkpoint = ModelCheckpoint('new_action.keras', save_best_only=True, monitor='val_loss')
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=5, min_lr=1e-6, verbose=1)


target_accuracy = 0.80
target_loss = 0.4

# EarlyStopping for accuracy
early_stopping_accuracy = EarlyStopping(
    monitor='val_categorical_accuracy', 
    min_delta=0.001, # Minimum change to qualify as an improvement
    mode='max', 
    patience=80, # Number of epochs with no improvement after which training will be stopped
    verbose=1,
    baseline=target_accuracy
)

# EarlyStopping for loss
early_stopping_loss = EarlyStopping(
    monitor='val_loss',
    min_delta=0.001,
    mode='min',
    patience=150,
    verbose=1,
    baseline=target_loss
)


class StopAtGoalLoss(Callback):
    def __init__(self, goal_loss):
        super(StopAtGoalLoss, self).__init__()
        self.goal_loss = goal_loss

    def on_epoch_end(self, epoch, logs=None):
        # Get the current loss from logs
        current_loss = logs.get('loss')  # You can also use 'val_loss' for validation loss
        if current_loss is not None and current_loss <= self.goal_loss:
            print(f"\nReached goal loss of {self.goal_loss} at epoch {epoch + 1}, stopping training.")
            self.model.stop_training = True


goal_loss = 0.03

stop_at_goal_loss = StopAtGoalLoss(goal_loss=goal_loss)

callbacks = [early_stopping_loss]





#log_dir = os.path.join('Logs')
#tb_callback = TensorBoard(log_dir=log_dir)
"""
model = Sequential()
model.add(Input(shape=(119, 84)))  # Define the input shape using Input layer
model.add(Masking(mask_value=0))
#model.add(Bidirectional(LSTM(16, return_sequences=True, activation='relu')))
model.add(LSTM(32, return_sequences=True, activation='relu'))
#model.add(Dropout(0.2))
model.add(LSTM(32, return_sequences=True, activation='relu'))
#model.add(Dropout(0.2))
model.add(LSTM(64, return_sequences=False, activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(32, activation='relu'))


#model.add(Dense(16, activation='relu'))

# Working model
'''
model = Sequential()
model.add(Masking(mask_value=0, input_shape=(None, 126)))
#model.add(Bidirectional(LSTM(16, return_sequences=True, activation='relu')))
model.add(LSTM(16, return_sequences=True, activation='relu'))
model.add(LSTM(32, return_sequences=True, activation='relu'))
model.add(LSTM(16, return_sequences=False, activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(actions.shape[0], activation='softmax'))
'''


model.add(Dense(actions.shape[0], activation='softmax'))
#clip_value = 1.0
#optimizer = tf.keras.optimizers.Adam(clipnorm=clip_value)
model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])
"""
#l2_factor = 0.001
model = Sequential()
model.add(Input(shape=(119, 126)))  # Define the input shape using Input layer
model.add(Masking(mask_value=0))

# Add BatchNormalization after each LSTM layer
model.add(LSTM(32, return_sequences=True, activation='relu'))
model.add(BatchNormalization())
#model.add(Dropout(0.3))
model.add(LSTM(32, return_sequences=True, activation='relu'))
model.add(BatchNormalization())
#model.add(Dropout(0.3))
model.add(LSTM(16, return_sequences=False, activation='relu'))
model.add(BatchNormalization())

model.add(Dense(64, activation='relu'))
model.add(BatchNormalization())  # Add BatchNormalization after Dense layer
#model.add(Dropout(0.2))  # Retain Dropout for regularization
model.add(Dense(32, activation='relu'))
model.add(BatchNormalization())  # Add BatchNormalization after Dense layer

model.add(Dense(actions.shape[0], activation='softmax'))

# Compile the model
#model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])


# Create the optimizer with the specified learning rate
optimizer = Adam(clipnorm=1.0)  # or clipvalue=0.5

# Compile the model with the optimizer
model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['categorical_accuracy'])


#history = model.fit(X_train, y_train, epochs=150,validation_data=(X_test, y_test),batch_size=32,callbacks=[stop_at_goal_loss])
history = model.fit(X_train, y_train, epochs=150,validation_data=(X_test, y_test),batch_size=32)

model.summary()




'''
def build_model(hp):
    model = Sequential()
    model.add(Masking(mask_value=0, input_shape=(119, 84)))
    model.add(Bidirectional(LSTM(hp.Int('units_1', min_value=32, max_value=128, step=32), return_sequences=True, activation='relu')))
    model.add(LSTM(hp.Int('units_2', min_value=64, max_value=256, step=64), return_sequences=True, activation='relu'))
    model.add(LSTM(hp.Int('units_3', min_value=32, max_value=128, step=32), return_sequences=False, activation='relu'))
    model.add(Dense(hp.Int('dense_units_1', min_value=32, max_value=128, step=32), activation='relu'))
    model.add(Dense(hp.Int('dense_units_2', min_value=16, max_value=64, step=16), activation='relu'))
    model.add(Dense(actions.shape[0], activation='softmax'))
    model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])
    return model

tuner = kt.Hyperband(build_model, objective='val_loss', max_epochs=20, factor=3, directory='D:\\', project_name='intro_to_kt')

tuner.search(X_train, y_train, epochs=50, validation_data=(X_test, y_test), callbacks=[early_stopping, model_checkpoint, reduce_lr])

model = tuner.get_best_models(num_models=1)[0]
model.summary()

best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]

# Retrieve the best hyperparameters for each part of the model
best_units_1 = best_hps.get('units_1')
best_units_2 = best_hps.get('units_2')
best_units_3 = best_hps.get('units_3')
best_dense_units_1 = best_hps.get('dense_units_1')
best_dense_units_2 = best_hps.get('dense_units_2')

# Print the best hyperparameters
print('Best units for LSTM layer 1:', best_units_1)
print('Best units for LSTM layer 2:', best_units_2)
print('Best units for LSTM layer 3:', best_units_3)
print('Best units for dense layer 1:', best_dense_units_1)
print('Best units for dense layer 2:', best_dense_units_2)
res = model.predict(X_test)

'''
tf.keras.models.save_model(model, 'new_action2.keras')
#model.load_weights('new_action1.h5')

model.load_weights('new_action2.keras')

# Evaluate the model on test data
test_loss, test_accuracy = model.evaluate(X_test, y_test)

print(f'Test Loss: {test_loss}')
print(f'Test Accuracy: {test_accuracy}')


# Plot training & validation loss values
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

# Plot training & validation accuracy values
plt.subplot(1, 2, 2)
plt.plot(history.history['categorical_accuracy'], label='Training Accuracy')
plt.plot(history.history['val_categorical_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

plt.tight_layout()
plt.show()


# Assuming your y_test and model predictions are one-hot encoded, convert them to class labels
y_test_labels = np.argmax(y_test, axis=1)
y_pred = np.argmax(model.predict(X_test), axis=1)

# Confusion Matrix
cm = confusion_matrix(y_test_labels, y_pred)

# Display the Confusion Matrix with adjusted figure size and spacing
plt.figure(figsize=(10, 8))  # Increase figure size for better spacing

disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=actions)
disp.plot(cmap=plt.cm.Blues, ax=plt.gca())

# Adjust the layout to add spacing
plt.subplots_adjust(bottom=0.2)  # Adjust bottom margin to make space for x-axis labels

plt.title('Confusion Matrix')
plt.show()

# Classification Report
print("Classification Report:\n")
print(classification_report(y_test_labels, y_pred, target_names=actions))
