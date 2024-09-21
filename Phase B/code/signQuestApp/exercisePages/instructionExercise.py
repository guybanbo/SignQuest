import customtkinter as ctk
from tkVideoPlayer import TkinterVideo
import cv2
from PIL import Image, ImageTk
import threading
from model.model import *
from tkinter import messagebox


# class for the frame "Instruction exercise", on one side frame with video, and on the other the user's camera feed
class InstructionExercise(ctk.CTkFrame):
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
        self.after_id = None
        self.countdown_id = None
        
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
        label = ctk.CTkLabel(self.title_container, text="Instruction Exercise", fg_color="#E6F3FF",font=("Helvetica", 20))
        label.grid(row=0, column=2, pady=5,sticky="e")
        
        self.title_container.grid_columnconfigure(3, weight=1)

                      
        # Create a CTkProgressBar widget
        self.progress = ctk.CTkProgressBar(self, width=600,height=15,fg_color="#c9ffe6",progress_color="#02bd66")
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
        self.content_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="nsew")

        # Frame to contain the video player
        self.video_frame = ctk.CTkFrame(self.content_frame,height=500)
        self.video_frame.grid(row=0, column=0, padx=(50,0), sticky="nsew")
        self.video_frame.grid_propagate(0)  # Prevent resizing based on content
        
        # Frame to contain the user's camera feed
        self.camera_frame = ctk.CTkFrame(self.content_frame,height=500,bg_color=self.bg_color)
        self.camera_frame.grid(row=0, column=1, padx=0, sticky="nsew")
        self.camera_frame.grid_propagate(0)  # Prevent resizing based on content
        
        # Video player
        self.video_player = None  # Initially set to None
        #self.create_video_player()
        
        # Camera feed label
        self.camera_label = ctk.CTkLabel(self.camera_frame, text="")
        self.camera_label.grid(row=0, column=0,padx=(100,0),pady=(20,0) ,sticky="e")
        
        
        self.sequence = [np.zeros(126, dtype=np.float64) for _ in range(119)]
        self.sentence = []
        self.predictions = []
        
        self.res_prob = []
        self.holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        self.keypoints_list = []
        self.sequence_list = []
        
        self.correct_count = 0
        self.check_marks = []

        # Correct answer label
        self.correct_answer_label = ctk.CTkLabel(self, text="", font=("Helvetica", 16))
        self.correct_answer_label.grid(row=3, column=0, columnspan=2, pady=10, sticky="nsew")
        
        # Check marks frame
        self.check_marks_frame = ctk.CTkFrame(self,height=50)
        self.check_marks_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="nsew")
        self.check_marks_frame.grid_columnconfigure(0, weight=1)

        
        self.skipButton = ctk.CTkButton(self, text="Skip >", command=self.finishExercise)
        self.skipButton.grid(row=6, column=0, columnspan=2, pady=40,padx=50,sticky="e")
        
        
        # Bind window closing event to a method
        self.bind("<Destroy>", self.on_window_close)
        
        # Configure grid weights to make frames expand with the window
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)
       
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
            
    # when the user finish a lesson, resets variables and move to the next exercise
    def finishExercise(self):
        self.sequence = [np.zeros(126, dtype=np.float64) for _ in range(119)]
        self.remove_check_marks()
        self.close_camera()
        self.correct_count = 0
        self.destroy_video_player()
        #self.controller.next_exercise()
        self.controller.lesson.next_exercise(1)

    # reset variables when clicking back to homepage
    def on_image_click(self, event):
        
        if self.countdown_id:
            self.after_cancel(self.countdown_id)  # Cancel the countdown if it's running
            self.countdown_id = None  # Reset the countdown_id variable

        
        self.remove_check_marks()
        self.stop_prediction()
        self.correct_count = 0
        self.close_camera()
        self.destroy_video_player()
        self.sequence = [np.zeros(126, dtype=np.float64) for _ in range(119)]
        self.controller.lesson.back_to_home()

       
    # opens user's camera
    def start_camera(self):
        self.cap = cv2.VideoCapture(0,cv2.CAP_DSHOW,(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY))  # Start video capture from the default camera
        self.cap.set(cv2.CAP_PROP_FPS, 30.0)
        self.update_camera_feed()

    def on_window_close(self, event):
        # Release the camera resource
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()
            
    # set all relevent data of the exercise
    def set_exercise_data(self, obj):
        self.correct_answer = obj["correct_answer"]
        self.video_url = obj["video_url"]
       # self.create_multiple_choice_buttons()
        self.start_progress()
        self.start_camera()
        self.load_and_play_video()  # Load and play the video
        self.correct_answer_label.configure(text=f"Repeat the sign:", font=("Helvetica", 20))
        sign_button = ctk.CTkButton(self.check_marks_frame, text=self.correct_answer, font=("Helvetica", 16),height=40)
        sign_button.grid(row=0,  column=0, columnspan=2)  # Use grid instead of pack

    # creates video player for the instruction video
    def create_video_player(self):
        print("create video player")
        if self.video_player:
            print("video player exist")
            self.video_player.destroy()  # Destroy the existing video player

        # Use `after` to schedule the creation of the video player on the main thread
        self.controller.after(0, self._create_video_player_internal)

    def _create_video_player_internal(self):
        self.video_player = TkinterVideo(master=self.video_frame, scaled=True, keep_aspect=True)
        self.video_player.configure(bg="black")
        self.video_player.pack(expand=True, fill="both")

                
    def destroy_video_player(self):
        if self.video_player:
            self.video_player.destroy()  # Destroy the existing video player
            self.video_player = None  # Remove reference to the destroyed video player


    def load_and_play_video(self):
        self.create_video_player()  # Recreate the video player instance

        # Use `after` to ensure the video loading and playing happens on the main thread
        self.controller.after(0, self._load_and_play_video_internal)

    def _load_and_play_video_internal(self):
        self.video_player.load(self.video_url)
        self.video_player.play()

        # Bind the loop function to the <<Ended>> event of the video player
        self.video_player.bind('<<Ended>>', self.loop_video)


    def loop_video(self, event):
        # Replay the video when it ends
        self.video_player.play()


    def start_camera_feed_thread(self):
     # Create a separate thread for camera feed processing
     self.camera_thread = threading.Thread(target=self.update_camera_feed)
     self.camera_thread.daemon = True  # Daemonize the thread to close it when the main thread exits
     self.camera_thread.start()


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
           
           # collect keypoints from mediapipe result
           keypoints = extract_keypoints(results)

           self.sequence.append(keypoints)
           self.sequence = self.sequence[-119:]  # get 119 frames
          
           self.frame_count += 1
          
            # if one of the user's hand on the screen
           if results.left_hand_landmarks or results.right_hand_landmarks:
               
               # check that the collected frames are 119 in order to match the trained data
               if len(self.sequence) == 119 and self.frame_count==5 and self.correct_count == 0:
                   
                   res = loaded_model.predict(np.expand_dims(self.sequence, axis=0),verbose=0)[0] #returns the predicted word
                   
                   
                   correct_indices = np.where(actions == self.correct_answer)[0]
                   correct_index = correct_indices[0]
                   correct_probability = res[correct_index]
                   
                   sorted_probabilities = np.sort(res)[::-1]
                   correct_rank = np.where(sorted_probabilities == correct_probability)[0][0] + 1
                   
                   print(f"Correct answer probability: {correct_probability:.10f}")
                   print(f"Correct answer rank: {correct_rank}")
                   
                   if actions[np.argmax(res)] == self.correct_answer:            
                       
                         self.correct_count += 1
                         
                         if self.correct_count == 1:
                             
                             self.update_check_marks()
                             print("Exercise completed successfully!")
               
            # update the ui of the camera feed
           img = Image.fromarray(image)
           imgtk = ImageTk.PhotoImage(image=img,master=self.controller)
           self.camera_label.imgtk = imgtk
           self.camera_label.configure(image=imgtk)
           self.after_id = self.camera_label.after(30, self.update_camera_feed)


    
    def stop_prediction(self):
        if self.after_id is not None:
            self.camera_label.after_cancel(self.after_id)
            self.after_id = None  # Reset after_id to None

    def remove_check_marks(self):
        # Iterate through the list of check mark labels
        for label in self.check_marks:
            label.destroy()  # Remove the label from the frame
    
        # Clear the list of check marks
        self.check_marks.clear()

    # update ui on successful exercise
    def update_check_marks(self):

        sign_button = ctk.CTkButton(self.check_marks_frame, text=self.correct_answer + " √", font=("Helvetica", 16),height=40,fg_color="green")
        sign_button.grid(row=0,  column=0, columnspan=2)  # Use grid instead of pack
        
        self.start_countdown(5)

        
    def start_countdown(self, seconds):
        if seconds > 0:
            self.correct_answer_label.configure(text=f"Good job! Starting next exercise in {seconds} seconds",font=("Helvetica", 20))
            self.countdown_id = self.after(1000, self.start_countdown, seconds - 1)
        else:
            self.finishExercise()
            #self.correct_answer_label.configure(text="Starting next exercise now!")

    def close_camera(self):
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()

    # Don't forget to release the camera resource when done
    # For example, override the destroy method to release the camera
    def __del__(self):
        if self.cap:
            self.cap.release()