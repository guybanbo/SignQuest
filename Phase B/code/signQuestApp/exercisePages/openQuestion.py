import customtkinter as ctk
from tkinter import filedialog
from tkVideoPlayer import TkinterVideo
from tkinter import messagebox
from PIL import Image, ImageTk

# class for the frame "Open Question" exercise
class OpenQuestion(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        self.correct_answer = "Answer 1"
        self.video_url = ""
        
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
        label = ctk.CTkLabel(self.title_container, text="Type the matching word", fg_color="#E6F3FF",font=("Helvetica", 20))
        label.grid(row=0, column=2, pady=5,sticky="e")
        
        self.title_container.grid_columnconfigure(3, weight=1)

        
        self.progress = ctk.CTkProgressBar(self, width=600,height=12,fg_color="#c9ffe6",progress_color="#02bd66")
        self.progress.grid(row=1, column=0, columnspan=2, pady=10)
        self.progress.set(0)  # Initial progress value
        

        # Frame to contain the video player
        self.video_frame = ctk.CTkFrame(self,width=889, height=500)
        self.video_frame.grid(row=2,column=0,columnspan=2,pady=5,sticky="nsew")
        self.video_frame.pack_propagate(0)  # Prevent resizing based on content

        self.instructionText = ctk.CTkLabel(self, text="Enter the matching translation:",font=("Helvetica", 20))
        self.instructionText.grid(row=3, column=0,columnspan=2,  pady=5, sticky="nsew")
        

        # Entry for user to type answer
        self.answer_entry = ctk.CTkEntry(self,width=160,placeholder_text="Enter the matching word")
        self.answer_entry.grid(row=4,column=0,columnspan=2,pady=10,sticky="s")

        # Button to submit answer
        submit_button = ctk.CTkButton(self, text="Submit Answer", command=self.check_answer)
        submit_button.grid(row=5,column=0,columnspan=2,pady=10,sticky="s")

        self.skipButton = ctk.CTkButton(self, text="Skip >", command=self.finishExercise)
        self.skipButton.grid(row=6,column=0,columnspan=2,pady=30,padx=50,sticky="e")
    

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Video player
        self.video_player = None  # Initially set to None
        self.create_video_player()

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
        self.destroy_video_player()
        self.controller.lesson.back_to_home()   

    # when the user finish a lesson, resets variables and move to the next exercise
    def finishExercise(self):
        self.destroy_video_player()
        self.controller.lesson.next_exercise(0)
        
        # set all relevent data of the exercise
    def set_exercise_data(self, obj):
        self.correct_answer = obj["correct_answer"]
        self.video_url = obj["video_url"]
        self.start_progress()
        self.load_and_play_video()  # Load and play the video

    # creates video player to display a sign language gesture video
    def create_video_player(self):
        if self.video_player:
            self.video_player.destroy()  # Destroy the existing video player
        self.video_player = TkinterVideo(master=self.video_frame, scaled=True,keep_aspect=True)
        self.video_player.pack(expand=True, fill="both")

    def load_and_play_video(self):
        self.create_video_player()  # Recreate the video player instance
        self.video_player.load(self.video_url)
        self.video_player.play()
        # Bind the loop function to the <<Ended>> event of the video player
        self.video_player.bind('<<Ended>>', self.loop_video)

    def loop_video(self, event):
        # Replay the video when it ends
        self.video_player.play()
        
    def destroy_video_player(self):
        if self.video_player:
            self.video_player.destroy()  # Destroy the existing video player
            self.video_player = None  # Remove reference to the destroyed video player

    def check_answer(self):
        typed_answer = self.answer_entry.get().strip()
        print(f"Typed answer: {typed_answer}")
        score = 0

        if self.correct_answer == typed_answer:
            messagebox.showinfo("Success", "Exercise completed successfully!")
            score = 1
        else:
            messagebox.showinfo("Wrong answer", f"The correct answer is {self.correct_answer}")

        self.destroy_video_player()
        self.controller.lesson.next_exercise(score)