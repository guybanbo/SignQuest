import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
from model.model import *
from tkinter import messagebox

# class for the frame "Setence Gesture" exercise, when the user need to perform a sequence of gesture that creating a sentence
class SentenceGesture(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        self.correct_answer = "Answer 1"
        self.video_url = ""
        self.buttons = []  # To keep track of the created buttons
        self.cap = None  # Video capture for the user's camera
        self.frame_count = 0
        self.predicted = []
        self.current_word = 0
        self.buttons = {}
        self.waitFrames = 90

        # Loading and converting the loading icon
        loading_image_path = "images/loading.png"  # Replace with the path to your image
        loading_image = Image.open(loading_image_path)
        loading_image = loading_image.resize((20, 20), Image.ANTIALIAS)  # Resize the image if necessary
        self.loading_icon = ImageTk.PhotoImage(loading_image,master=self.controller)  # Keep a reference to the image
        
        # Loading and converting the checkmark icon
        checkmark_image_path = "images/checked.png"  # Replace with the path to your image
        checkmark_image = Image.open(checkmark_image_path)
        checkmark_image = checkmark_image.resize((20, 20), Image.ANTIALIAS)  # Resize the image if necessary
        self.checkmark = ImageTk.PhotoImage(checkmark_image,master=self.controller)  # Keep a reference to the image

        image_path = "images/left-arrow.png"  # Replace with the path to your image
        image = Image.open(image_path)
        image = image.resize((25, 25), Image.ANTIALIAS)  # Resize the image if necessary
        self.image_tk = ImageTk.PhotoImage(image,master=self.controller)  # Keep a reference to the image


        self.title_container = ctk.CTkFrame(self, fg_color="#E6F3FF")
        self.title_container.grid(row=0, column=0, columnspan=2, pady=5,sticky="nsew")
        
        self.title_container.grid_columnconfigure(1, weight=1)

        # Now place the label on top of this background frame
        self.back_button = ctk.CTkLabel(self.title_container, text="",image=self.image_tk,   compound="left", fg_color="#E6F3FF",font=("Helvetica", 20))
        self.back_button.grid(row=0, column=0,  pady=5,padx=20, sticky="w")
        
        self.back_button.bind("<Button-1>", self.on_image_click)
        
        # Now place the label on top of this background frame
        label = ctk.CTkLabel(self.title_container, text="Sign the sentence on camera", fg_color="#E6F3FF",font=("Helvetica", 20))
        label.grid(row=0, column=2, pady=5,sticky="e")
        
        self.title_container.grid_columnconfigure(3, weight=1)
        
        # Create a CTkProgressBar widget
        self.progress = ctk.CTkProgressBar(self, width=600,height=12,fg_color="#c9ffe6",progress_color="#02bd66")
        self.progress.grid(row=1, column=0, columnspan=2, pady=10)
        self.progress.set(0)  # Initial progress value

        
        self.light_mode_Gray81 = "#cfcfcf"
        self.dark_mode_gray20 = "#333333"
        self.bg_color = self.light_mode_Gray81
        
        if(ctk.get_appearance_mode() == "Dark"):
            self.bg_color = self.dark_mode_gray20
            self.gauge_text_color = "white"
                
        # Frame to contain both video and user's camera
        self.content_frame = ctk.CTkFrame(self,height=500,fg_color=self.bg_color)
        self.content_frame.grid(row=2, column=0, pady=10, sticky="nsew")

        
        # Frame to contain the user's camera feed
        self.camera_frame = ctk.CTkFrame(self.content_frame,height=500,bg_color=self.bg_color)
        self.camera_frame.grid(row=0, column=0, padx=0, sticky="nsew")

        # Video player
        self.video_player = None  # Initially set to None

        # Camera feed label
        self.camera_label = ctk.CTkLabel(self.camera_frame, text="")
        self.camera_label.grid(row=0, column=0, pady=(20,0) ,sticky="nsew")
        

        self.sequence = []
        self.sequence = [np.zeros(126, dtype=np.float64) for _ in range(90)]
        self.sentence = []
        self.predictions = []
        
        self.res_prob = []
        self.holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        self.keypoints_list = []
        self.sequence_list = []
        
        self.correct_count = 0
        self.check_marks = []


        self.fullSentenceLabel = ctk.CTkLabel(self, text="", font=("Helvetica", 16))
        self.fullSentenceLabel.grid(row=3, column=0, pady=10, sticky="nsew")
        

        # Correct answer label
        self.button_frame  = ctk.CTkFrame(self)
        self.button_frame.grid(row=4, column=0, pady=10, sticky="nsew")
        

        self.skipButton = ctk.CTkButton(self, text="Skip >", command=self.finishExercise)
        self.skipButton.grid(row=5, column=0, pady=(50,50),padx=50,sticky="e")

        
        # Bind window closing event to a method
        self.bind("<Destroy>", self.on_window_close)
        
        # Configure grid weights to make frames expand with the window
        self.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.camera_frame.grid_columnconfigure(0, weight=1)
        self.camera_label.grid_columnconfigure(0, weight=1)

     # init progress bar
    def start_progress(self):
        
        current_value = 0
        exercises = self.controller.lesson.get_exercises()
        current_exercise = self.controller.lesson.current_exercise
        total_exercises = len(exercises)
        if total_exercises > 0:
            current_value = (current_exercise + 1) / total_exercises
            self.progress.set(current_value)
        else:
            self.progress.set(current_value)  # If there are no exercises, set progress to 0
            
        print("Current value:", current_value)        

    # opens user's camera
    def start_camera(self):
        self.cap = cv2.VideoCapture(0,cv2.CAP_DSHOW,(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY))  # Start video capture from the default camera
        self.cap.set(cv2.CAP_PROP_FPS, 30.0)
        self.update_camera_feed()

    def on_window_close(self, event):
        # Release the camera resource
        if self.cap:
            self.cap.release()
            
    # update the word buttons that assemble a sentence
    def update_buttons(self):
        # Iterate over the list of words
        for index, word in enumerate(self.words):
            
            # Assuming you have a way to get the finish status for each word
            finish_status = word["finish"]  # Implement this method to get the finish status
            
            word = word["word"]
            
            button = self.buttons.get(word)
            
            # Update the button text if the finish status is 1
            if finish_status == 1:
                
                if button:
                    button.configure(
                 text=word,
                 image=self.checkmark,  # Set the checkmark image
                 compound="right",      # Align image to the right of the text
                 fg_color="gray",       # Gray out the button
             )
                    
            if index == self.current_word:
                button.configure(
                text=word,
                image=self.loading_icon,  # Set the loading icon
                compound="right",         # Align image to the right of the text
                fg_color="blue",          # Set the background color to blue
            )

    # set all relevent data of the exercise
    def set_exercise_data(self, obj):
        
        self.words = [{"word": word, "finish": 0} for word in obj["words"]]
        self.fullSentence = obj["sentence"]
        self.start_progress()
        
        # Create a frame to hold the buttons
        button_frame = ctk.CTkFrame(self.button_frame)
        button_frame.pack(pady=10)
    
        # Create buttons for each word and pack them inside the frame
        for index, word in enumerate(self.words, start=1):
            # Create a button with sequence number and store it in the dictionary
            if index == 1:
                word_button = ctk.CTkButton(button_frame, text=f"{index}.   {word['word']}     ", image=self.loading_icon,compound="right")
            else:
                word_button = ctk.CTkButton(button_frame, text=f"{index}.        {word['word']}", fg_color="gray")

            word_button.pack(side="left", padx=10)
            self.buttons[word["word"]] = word_button  # Store the button reference

    
        # Center the button frame
        button_frame.pack(anchor="center")
        
        self.start_camera()
        self.fullSentenceLabel.configure(text=f"Repeat the sentence: {self.fullSentence}", font=("Helvetica", 20))
        


    def update_camera_feed(self):
    
        ret, frame = self.cap.read()
        
        if ret:
            
           if(self.frame_count == 5):
               self.frame_count = 0
            
            
           # Make detections
           image, results = mediapipe_detection(frame, self.holistic)

           # Draw landmarks
           draw_styled_landmarks(image, results)
           
           # collect keypoints from mediapipe result
           keypoints = extract_keypoints(results)
   
           self.sequence.append(keypoints)
           self.sequence = self.sequence[-119:] # get 119 frames
          
          
           self.frame_count += 1
           self.waitFrames += 1
          
           if results.left_hand_landmarks or results.right_hand_landmarks:
        
               if len(self.sequence) == 119 and self.frame_count >= 5 and self.waitFrames >= 30 and self.current_word <= len(self.words)-1:
                  
                   res = loaded_model.predict(np.expand_dims(self.sequence, axis=0),verbose=0)[0]    

                   correct_indices = np.where(actions == self.words[self.current_word]["word"])[0]
                   correct_index = correct_indices[0]
                   correct_probability = res[correct_index]
                   
                   sorted_probabilities = np.sort(res)[::-1]
                   correct_rank = np.where(sorted_probabilities == correct_probability)[0][0] + 1
                   
                   print(f"Correct answer probability: {correct_probability:.10f}")
                   print(f"Correct answer rank: {correct_rank}")

                     # Check if the performed gesture matches the correct answer
                   if actions[np.argmax(res)] == self.words[self.current_word]["word"]:  

                         
                         self.words[self.current_word]["finish"] = 1
                         print(self.words)
                         self.waitFrames = 0
                         self.current_word += 1
                         self.update_buttons()
                         
                         if self.current_word == len(self.words):
                             self.after(1000, self.complete_exercise)
                        
                
           img = Image.fromarray(image)
           imgtk = ImageTk.PhotoImage(image=img,master=self.controller)
           self.camera_label.imgtk = imgtk
           self.camera_label.configure(image=imgtk)
           self.camera_label.after(30,self.update_camera_feed)

    
    def complete_exercise(self):
        print("Exercise completed successfully!")
        messagebox.showinfo("Success", "Exercise completed successfully!")
        self.finishExercise()

    def remove_check_marks(self):
        
        for widget in self.button_frame.winfo_children():
            widget.destroy()

    # reset variables when clicking back to homepage
    def on_image_click(self, event):
        self.close_camera()
        self.remove_check_marks()
        self.sequence = [np.zeros(126, dtype=np.float64) for _ in range(119)]
        self.controller.lesson.back_to_home()

    # when the user finish a lesson, resets variables and move to the next exercise
    def finishExercise(self):
            self.close_camera()
            self.sequence = [np.zeros(126, dtype=np.float64) for _ in range(119)]
            self.remove_check_marks()
            self.controller.lesson.next_exercise(1)

    def close_camera(self):
        if self.cap:
            self.cap.release()

    # Don't forget to release the camera resource when done
    # For example, override the destroy method to release the camera
    def __del__(self):
        if self.cap:
            self.cap.release()