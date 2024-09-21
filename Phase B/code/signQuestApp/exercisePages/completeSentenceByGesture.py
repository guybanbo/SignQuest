import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import threading
from model.model import *
from tkinter import messagebox


# class for the frame "Complete Sentence By Gesture" exercise
class CompleteSentenceByGesture(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        self.correct_answer = "Answer 1"
        self.complete_sentence = ""
        self.buttons = []  # To keep track of the created buttons
        self.cap = None  # Video capture for the user's camera
        self.frame_count = 0
        
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
        label = ctk.CTkLabel(self.title_container, text="Complete the sentence by gesture", fg_color="#E6F3FF",font=("Helvetica", 20))
        label.grid(row=0, column=2, pady=5,sticky="e")
        
        self.title_container.grid_columnconfigure(3, weight=1)
        

        self.progress = ctk.CTkProgressBar(self, width=600,height=12,fg_color="#c9ffe6",progress_color="#02bd66")
        self.progress.grid(row=1, column=0, columnspan=2, pady=10)
        self.progress.set(0)  # Initial progress value
        
        # Frame to contain the user's camera feed
        self.camera_frame = ctk.CTkFrame(self)
        self.camera_frame.grid(row=2,columnspan=2, pady=10, sticky="nsew")
        self.camera_frame.pack_propagate(0)  # Prevent resizing based on content


        # Camera feed label
        self.camera_label = ctk.CTkLabel(self.camera_frame,text="")
        self.camera_label.grid(row=0, columnspan=2, sticky="nsew")


        self.instructionText = ctk.CTkLabel(self, text="Sign the matching word:",font=("Helvetica", 20))
        self.instructionText.grid(row=3, column=0,columnspan=2,  pady=10, sticky="nsew")
        
        # Check marks frame
        self.check_marks_frame = ctk.CTkFrame(self,height=50)
        self.check_marks_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="nsew")
        self.check_marks_frame.grid_columnconfigure(0, weight=1)

        self.hint = ctk.CTkButton(self, text="Hint", command=self.show_hint)
        self.hint.grid(row=5,columnspan=2,padx=100,sticky="w")


        self.skipButton = ctk.CTkButton(self, text="Skip >", command=self.finishExercise)
        self.skipButton.grid(row=5,columnspan=2,padx=100,sticky="e")
        self.grid_rowconfigure(5, weight=1)
        
    
        self.camera_frame.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

           
        self.sequence = []
        self.sequence = [np.zeros(126, dtype=np.float64) for _ in range(119)]
        self.sentence = []
        self.predictions = []
    
        self.res_prob = []
        self.holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    
        self.keypoints_list = []
        self.sequence_list = []
        
        self.correct_count = 0
        self.check_marks = []
        
        # Bind window closing event to a method
        self.bind("<Destroy>", self.on_window_close)
        
    
    def center_popup(self,popup, main_window):
        # Get the dimensions and position of the main window
        main_window_x = main_window.winfo_rootx()
        main_window_y = main_window.winfo_rooty()
        main_window_width = main_window.winfo_width()
        main_window_height = main_window.winfo_height()
    
        # Get the dimensions of the screen
        screen_width = main_window.winfo_screenwidth()
        screen_height = main_window.winfo_screenheight()
    
        # Calculate the position of the popup
        window_width = popup.winfo_reqwidth()
        window_height = popup.winfo_reqheight()
        x = main_window_x + (main_window_width // 2) - (window_width // 2)
        y = main_window_y + (main_window_height // 2) - (window_height // 2)
    
        # Set the position of the popup
        popup.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # onclick, reveals the matching word of the sentence
    def show_hint(self):
        popup = ctk.CTkToplevel()
        popup.title("Hint")
        
        popup.attributes("-topmost", True)
    
        # Show the current content
        label = ctk.CTkLabel(popup, text="The matching word is: " + self.correct_answer, font=("Arial", 20))
        label.pack(pady=10, padx=20)
        
        # Update the popup size to fit the label content
        popup.update_idletasks()  # Let the geometry manager calculate the size
        
        # Set the popup size based on the content
        popup.geometry(f"{popup.winfo_width()}x{popup.winfo_height()}")
    
        # Center the popup on the screen
        self.center_popup(popup, self)
        
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

    # reset variables when clicking back to homepage
    def on_image_click(self, event):
        self.close_camera()
        self.sequence = [np.zeros(126, dtype=np.float64) for _ in range(119)]
        self.controller.lesson.back_to_home()
    
    # when the user finish a lesson, resets variables and move to the next exercise
    def finishExercise(self):
        self.close_camera()
        self.controller.lesson.next_exercise(1)

    # opens user's camera
    def start_camera(self):
        self.cap = cv2.VideoCapture(0,cv2.CAP_DSHOW,(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY))  # Start video capture from the default camera
        self.cap.set(cv2.CAP_PROP_FPS, 30.0)
        self.update_camera_feed()

    def on_window_close(self, event):
        # Release the camera resource
        if self.cap:
            self.cap.release()

    # set all relevent data of the exercise
    def set_exercise_data(self, obj):
        self.correct_answer = obj["correct_answer"]
        self.complete_sentence = obj["sentence"]
        self.start_progress()
        self.sentence_label = ctk.CTkLabel(self.check_marks_frame, text=self.complete_sentence,font= ("Arial", 20))
        self.sentence_label.grid(row=4, column=0, columnspan=2,pady=10, sticky="nsew")
        self.start_camera()

    def start_camera_feed_thread(self):
     # Create a separate thread for camera feed processing
     self.camera_thread = threading.Thread(target=self.update_camera_feed)
     self.camera_thread.daemon = True  # Daemonize the thread to close it when the main thread exits
     self.camera_thread.start()
     
    # update the ui with the missing word
    def update_sentence_with_answer(self):
        # Find the placeholder (which could be any length) and replace it with the correct answer
        placeholder = next(word for word in self.complete_sentence.split() if "_" in word)
        updated_sentence = self.complete_sentence.replace(placeholder, self.correct_answer)
        
        # Update the label with the new sentence
        self.sentence_label.configure(text=updated_sentence)

    # updates the camera frame on screen, extracting user's keypoints using mediapipe and predicts the signed word using the ML model.
    def update_camera_feed(self):

        ret, frame = self.cap.read()
        if ret:
            
           if(self.frame_count == 5):
                self.frame_count = 0
            
    
           # Make detections
           image, results = mediapipe_detection(frame, self.holistic)
           #print(results)
           
           # Draw landmarks
           draw_styled_landmarks(image, results)
           
           # 2. Prediction logic
           keypoints = extract_keypoints(results)
           self.keypoints_list.append(keypoints)
           self.sequence.append(keypoints)
           self.sequence = self.sequence[-119:]
           
           self.frame_count += 1
           
           # if one of the user's hand on the screen
           if results.left_hand_landmarks or results.right_hand_landmarks:
           
               # check that the collected frames are 119 in order to match the trained data
               if len(self.sequence) == 119 and self.frame_count==5:
                   res = loaded_model.predict(np.expand_dims(self.sequence, axis=0))[0]     #returns the predicted word
                   
                   self.predictions.append(np.argmax(res))
           
                   correct_indices = np.where(actions == self.correct_answer)[0]
                   correct_index = correct_indices[0]
                   correct_probability = res[correct_index]
                   
                   sorted_probabilities = np.sort(res)[::-1]
                   correct_rank = np.where(sorted_probabilities == correct_probability)[0][0] + 1
                   
                   print(f"Correct answer probability: {correct_probability:.10f}")
                   print(f"Correct answer rank: {correct_rank}")
                   
                   # Check if the performed gesture matches the correct answer
                   if actions[np.argmax(res)] == self.correct_answer:  
                        self.correct_count += 1
                        self.sequence = []
                        if self.correct_count == 1:
                            print("Exercise completed successfully!")
                            self.update_sentence_with_answer()
                            messagebox.showinfo("Success", "Exercise completed successfully!")
                            self.close_camera()
                            self.controller.lesson.next_exercise(1)
                   
                   
           img = Image.fromarray(image)
           imgtk = ImageTk.PhotoImage(image=img)
           self.camera_label.imgtk = imgtk
           self.camera_label.configure(image=imgtk)
           self.camera_label.after(30,self.update_camera_feed)

    
    def close_camera(self):
        if self.cap:
            self.cap.release()

    #releases the camera resource when done
    def __del__(self):
        if self.cap:
            self.cap.release()