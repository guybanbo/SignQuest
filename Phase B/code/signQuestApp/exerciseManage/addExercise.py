import customtkinter as ctk
from db import DB  # Ensure you have a module named db with a get_lessons function
from PIL import Image, ImageTk
from CTkMessagebox import CTkMessagebox
from tkinter import messagebox

class AddExercise(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        
        # Load and set the back button arrow image
        image_path = "images/left-arrow.png"  # Replace with the path to your image
        image = Image.open(image_path)
        image = image.resize((25, 25), Image.ANTIALIAS)  # Resize the image if necessary
        self.image_tk = ImageTk.PhotoImage(image,master=self.controller)  # Keep a reference to the image

        # Add the back button to the frame
        self.navigation_frame_label = ctk.CTkLabel(self, text="  Back", image=self.image_tk,
                                                   compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Bind click event to the label
        self.navigation_frame_label.bind("<Button-1>", self.on_back_button_click)

        # Create Tabview
        self.tabview = ctk.CTkTabview(self, width=400)
        self.tabview.grid(row=1, column=0, padx=(20, 20), pady=(20, 20), sticky="nsew")
        #self.tabview.grid_rowconfigure(0, weight=1)
        
        
        # Adding tabs for each exercise type
        self.tabview.add("InstructionExercise")
        self.tabview.add("MultipleChoiceExercise")
        self.tabview.add("OpenQuestion")
        self.tabview.add("CompleteSentenceByGesture")
        self.tabview.add("SentenceGesture")

        # Center the form on the screen
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Add form elements to each tab
        self.create_instruction_exercise_tab()
        self.create_multiple_choice_exercise_tab()
        self.create_open_question_tab()
        self.create_complete_sentence_by_gesture_tab()
        self.create_sentence_gesture_tab()

    # when the user clicks back -> it will go to admin page
    def on_back_button_click(self, event):
            self.controller.show_frame("Admin")

    # creating the ui tabs for exercises types
    def create_instruction_exercise_tab(self):
        tab = self.tabview.tab("InstructionExercise")
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_rowconfigure(6, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(2, weight=1)
    
        ctk.CTkLabel(tab, text="Instruction Exercise", font=("Arial", 16, "bold")).grid(row=1, column=1, pady=(20, 10))
    
        ctk.CTkLabel(tab, text="Lesson Number:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.lesson_id_entry = ctk.CTkEntry(tab,width=250)
        self.lesson_id_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
    
        ctk.CTkLabel(tab, text="Exercise Number:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.exercise_number_entry = ctk.CTkEntry(tab,width=150)
        self.exercise_number_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
    
        ctk.CTkLabel(tab, text="Video URL:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.video_url_entry = ctk.CTkEntry(tab,width=150)
        self.video_url_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
    
        ctk.CTkLabel(tab, text="Correct Answer:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.correct_answer_entry = ctk.CTkEntry(tab,width=150)
        self.correct_answer_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
    
        self.submit_button = ctk.CTkButton(tab, text="Submit", command=self.submit_instruction_exercise)
        self.submit_button.grid(row=6, column=1, pady=(20, 10))
    
    # creating the ui tabs for exercises types
    def create_multiple_choice_exercise_tab(self):
        tab = self.tabview.tab("MultipleChoiceExercise")
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_rowconfigure(7, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(2, weight=1)
    
        ctk.CTkLabel(tab, text="Multiple Choice Exercise", font=("Arial", 16, "bold")).grid(row=1, column=1, pady=(20, 10))
    
        ctk.CTkLabel(tab, text="Lesson Number:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.lesson_id_entry_mc = ctk.CTkEntry(tab,width=250)
        self.lesson_id_entry_mc.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
    
        ctk.CTkLabel(tab, text="Exercise Number:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.exercise_number_entry_mc = ctk.CTkEntry(tab,width=150)
        self.exercise_number_entry_mc.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
    
        ctk.CTkLabel(tab, text="Video URL:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.video_url_entry_mc = ctk.CTkEntry(tab,width=150)
        self.video_url_entry_mc.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
    
        ctk.CTkLabel(tab, text="Answers (comma-separated):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.answers_entry = ctk.CTkEntry(tab,width=150)
        self.answers_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
    
        ctk.CTkLabel(tab, text="Correct Answer:").grid(row=6, column=0, padx=10, pady=5, sticky="e")
        self.correct_answer_entry_mc = ctk.CTkEntry(tab,width=150)
        self.correct_answer_entry_mc.grid(row=6, column=1, padx=10, pady=5, sticky="ew")
    
        self.submit_button = ctk.CTkButton(tab, text="Submit", command=self.submit_multiple_choice_exercise)
        self.submit_button.grid(row=7, column=1, pady=(20, 10))
    
    # creating the ui tabs for exercises types
    def create_open_question_tab(self):
        tab = self.tabview.tab("OpenQuestion")
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_rowconfigure(6, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(2, weight=1)
    
        ctk.CTkLabel(tab, text="Open Question", font=("Arial", 16, "bold")).grid(row=1, column=1, pady=(20, 10))
    
        ctk.CTkLabel(tab, text="Lesson Number:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.lesson_id_entry_oq = ctk.CTkEntry(tab,width=250)
        self.lesson_id_entry_oq.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
    
        ctk.CTkLabel(tab, text="Exercise Number:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.exercise_number_entry_oq = ctk.CTkEntry(tab,width=150)
        self.exercise_number_entry_oq.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
    
        ctk.CTkLabel(tab, text="Video URL:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.video_url_entry_oq = ctk.CTkEntry(tab,width=150)
        self.video_url_entry_oq.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
    
        ctk.CTkLabel(tab, text="Correct Answer:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.correct_answer_entry_oq = ctk.CTkEntry(tab,width=150)
        self.correct_answer_entry_oq.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
    
        self.submit_button = ctk.CTkButton(tab, text="Submit", command=self.submit_open_question)
        self.submit_button.grid(row=6, column=1, pady=(20, 10))
    
    # creating the ui tabs for exercises types
    def create_complete_sentence_by_gesture_tab(self):
        tab = self.tabview.tab("CompleteSentenceByGesture")
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_rowconfigure(6, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(2, weight=1)
    
        ctk.CTkLabel(tab, text="Complete Sentence by Gesture", font=("Arial", 16, "bold")).grid(row=1, column=1, pady=(20, 10))
    
        ctk.CTkLabel(tab, text="Lesson Number:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.lesson_id_entry_csb = ctk.CTkEntry(tab,width=250)
        self.lesson_id_entry_csb.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
    
        ctk.CTkLabel(tab, text="Exercise Number:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.exercise_number_entry_csb = ctk.CTkEntry(tab,width=150)
        self.exercise_number_entry_csb.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
    
        ctk.CTkLabel(tab, text="Sentence:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.sentence_entry = ctk.CTkEntry(tab,width=150)
        self.sentence_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
    
        ctk.CTkLabel(tab, text="Correct Answer:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.correct_answer_entry_csb = ctk.CTkEntry(tab,width=150)
        self.correct_answer_entry_csb.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
    
        self.submit_button = ctk.CTkButton(tab, text="Submit", command=self.submit_complete_sentence_by_gesture)
        self.submit_button.grid(row=6, column=1, pady=(20, 10))
    
    # creating the ui tabs for exercises types
    def create_sentence_gesture_tab(self):
        tab = self.tabview.tab("SentenceGesture")
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_rowconfigure(6, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(2, weight=1)
    
        ctk.CTkLabel(tab, text="Sentence Gesture", font=("Arial", 16, "bold")).grid(row=1, column=1, pady=(20, 10))
    
        ctk.CTkLabel(tab, text="Lesson Number:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.lesson_id_entry_sg = ctk.CTkEntry(tab,width=250)
        self.lesson_id_entry_sg.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
    
        ctk.CTkLabel(tab, text="Exercise Number:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.exercise_number_entry_sg = ctk.CTkEntry(tab,width=150)
        self.exercise_number_entry_sg.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
    
        ctk.CTkLabel(tab, text="Sentence:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.sentence_entry_sg = ctk.CTkEntry(tab,width=150)
        self.sentence_entry_sg.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
    
        ctk.CTkLabel(tab, text="Words (comma-separated):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.words_entry_sg = ctk.CTkEntry(tab,width=150)
        self.words_entry_sg.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
    
        self.submit_button = ctk.CTkButton(tab, text="Submit", command=self.submit_sentence_gesture)
        self.submit_button.grid(row=6, column=1, pady=(20, 10))

     # send new exercise data to db 
    def submit_exercise_db(self,exercise_data):
        
        
        print(exercise_data)
        
        response = DB.submit_exercise(exercise_data)
        
        if(response):
            messagebox.showinfo("Success", "Exercise was added successfully!")
            self.controller.frames["Admin"].view_exercises_list()
        else:
            messagebox.showinfo("Error", "Failed to add an Exercise.")

    # send new exercise data to db 
    def submit_instruction_exercise(self):
        # Retrieve data from the input fields
        lesson_id = self.lesson_id_entry.get()
        exercise_number = self.exercise_number_entry.get()
        video_url = self.video_url_entry.get()
        correct_answer = self.correct_answer_entry.get()
    
        # Create the exercise data dictionary
        instruction_exercise_data = {
            "lesson_number": int(lesson_id),
            "exercise_number": int(exercise_number),
            "type": 0,  # Assuming 1 represents instruction exercise
            "video_url": video_url,
            "correct_answer": correct_answer
        }
    
        # Handle the submission (e.g., send to a server, save to a database)
        self.submit_exercise_db(instruction_exercise_data)
    
    # send new exercise data to db 
    def submit_multiple_choice_exercise(self):
        # Retrieve data from the input fields
        lesson_id = self.lesson_id_entry_mc.get()
        exercise_number = self.exercise_number_entry_mc.get()
        video_url = self.video_url_entry_mc.get()
        answers = self.answers_entry.get().split(',')
        correct_answer = self.correct_answer_entry_mc.get()
    
        # Create the exercise data dictionary
        multiple_choice_exercise_data = {
            "lesson_number": int(lesson_id),
            "exercise_number": int(exercise_number),
            "type": 1,  # Assuming 2 represents multiple choice exercise
            "video_url": video_url,
            "answers": answers,
            "correct_answer": correct_answer
        }
    
        # Handle the submission (e.g., send to a server, save to a database)
        self.submit_exercise_db(multiple_choice_exercise_data)
    
    # send new exercise data to db 
    def submit_open_question(self):
        # Retrieve data from the input fields
        lesson_id = self.lesson_id_entry_oq.get()
        exercise_number = self.exercise_number_entry_oq.get()
        video_url = self.video_url_entry_mc.get()
        correct_answer = self.correct_answer_entry_oq.get()
    
        # Create the exercise data dictionary
        open_question_data = {
            "lesson_number": int(lesson_id),
            "exercise_number": int(exercise_number),
            "type": 2,  # Assuming 2 represents open question exercise
            "video_url": video_url,
            "correct_answer": correct_answer
        }
    
        # Handle the submission (e.g., send to a server, save to a database)
        self.submit_exercise_db(open_question_data)
    
    # send new exercise data to db 
    def submit_complete_sentence_by_gesture(self):
        # Retrieve data from the input fields
        lesson_id = self.lesson_id_entry_csb.get()
        exercise_number = self.exercise_number_entry_csb.get()
        sentence = self.sentence_entry_csb.get()
        correct_answer = self.correct_answer_entry_csb.get()
    
        # Create the exercise data dictionary
        complete_sentence_by_gesture_data = {
            "lesson_number": int(lesson_id),
            "exercise_number": int(exercise_number),
            "type": 3,  # Assuming 4 represents complete sentence by gesture exercise
            "sentence": sentence,
            "correct_answer": correct_answer
        }
    
        # Handle the submission (e.g., send to a server, save to a database)
        self.submit_exercise_db(complete_sentence_by_gesture_data)
    
    # send new exercise data to db 
    def submit_sentence_gesture(self):
        # Retrieve data from the input fields
        lesson_id = self.lesson_id_entry_sg.get()
        exercise_number = self.exercise_number_entry_sg.get()
        sentence = self.sentence_entry_sg.get()
        words = self.words_entry_sg.get().split(',')
    
        # Create the exercise data dictionary
        sentence_gesture_data = {
            "lesson_number": int(lesson_id),
            "exercise_number": int(exercise_number),
            "type": 4,  # Assuming 4 represents sentence gesture exercise
            "sentence": sentence,
            "words": words
        }
    
        # Handle the submission (e.g., send to a server, save to a database)
        self.submit_exercise_db(sentence_gesture_data)