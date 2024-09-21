import customtkinter as ctk
from bson import ObjectId
from db import DB  # Ensure you have a module named db with a get_lessons function
from PIL import Image, ImageTk
from CTkTable import *
from tkinter import messagebox


# class for the frame "Edit exercise" 
class EditExercise(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        self.exercise_id = ""
        self.exerciseData = {}
        
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
        
        self.back_button.bind("<Button-1>", self.on_back_button_click)
        
        # Now place the label on top of this background frame
        label = ctk.CTkLabel(self.title_container, text="Edit an exercise", fg_color="#E6F3FF",font=("Helvetica", 20))
        label.grid(row=0, column=2, pady=5,sticky="e")
        
        self.title_container.grid_columnconfigure(3, weight=1)
        

        
        # Create a frame for the dynamic form UI
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=1, columnspan=2,padx=20, pady=40, sticky="nsew")
        self.form_frame.pack_propagate(0)  
        self.form_frame.grid_columnconfigure(0, weight=1)
        self.form_frame.grid_columnconfigure(2, weight=1)
        
        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
    
    def on_back_button_click(self, event):
            self.controller.show_frame("Admin")
    
    def set_exercise_id(self,id):
        self.exercise_id = id
        self.exerciseData = DB.get_exercises_by_id(self.exercise_id)
        if(self.exerciseData):
            self.exerciseData = self.exerciseData[0]
            self.create_exercise_ui()
            
    # creates form according to the type of the exercise being edited
    def create_exercise_ui(self):
        # Clear existing widgets in the form_frame if any
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        
        # Multiple Choice Exercise
        if self.exerciseData.get("type") == 0:  
            ctk.CTkLabel(self.form_frame, text="Lesson ID:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.lesson_id_entry = ctk.CTkEntry(self.form_frame, width=250)
            self.lesson_id_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
            self.lesson_id_entry.insert(0, self.exerciseData.get("lesson_id", ""))
    
            ctk.CTkLabel(self.form_frame, text="Exercise Number:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
            self.exercise_number_entry = ctk.CTkEntry(self.form_frame, width=150)
            self.exercise_number_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
            self.exercise_number_entry.insert(0, self.exerciseData.get("exercise_number", ""))
    
            ctk.CTkLabel(self.form_frame, text="Video URL:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
            self.video_url_entry = ctk.CTkEntry(self.form_frame, width=250)
            self.video_url_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
            self.video_url_entry.insert(0, self.exerciseData.get("video_url", ""))
    
            ctk.CTkLabel(self.form_frame, text="Correct Answer:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
            self.correct_answer_entry = ctk.CTkEntry(self.form_frame, width=250)
            self.correct_answer_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
            self.correct_answer_entry.insert(0, self.exerciseData.get("correct_answer", ""))
        
        # Instruction Exercise
        elif self.exerciseData.get("type") == 1:  
            ctk.CTkLabel(self.form_frame, text="Lesson ID:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.lesson_id_entry = ctk.CTkEntry(self.form_frame, width=250)
            self.lesson_id_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
            self.lesson_id_entry.insert(0, self.exerciseData.get("lesson_id", ""))
    
            ctk.CTkLabel(self.form_frame, text="Exercise Number:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
            self.exercise_number_entry = ctk.CTkEntry(self.form_frame, width=150)
            self.exercise_number_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
            self.exercise_number_entry.insert(0, self.exerciseData.get("exercise_number", ""))
    
            ctk.CTkLabel(self.form_frame, text="Video URL:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
            self.video_url_entry = ctk.CTkEntry(self.form_frame, width=250)
            self.video_url_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
            self.video_url_entry.insert(0, self.exerciseData.get("video_url", ""))
            
            ctk.CTkLabel(self.form_frame, text="Answers (comma-separated):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
            self.answers_entry = ctk.CTkEntry(self.form_frame, width=250)
            self.answers_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
            self.answers_entry.insert(0, ', '.join(self.exerciseData.get("answers", [])))

    
            ctk.CTkLabel(self.form_frame, text="Correct Answer:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
            self.correct_answer_entry = ctk.CTkEntry(self.form_frame, width=250)
            self.correct_answer_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
            self.correct_answer_entry.insert(0, self.exerciseData.get("correct_answer", ""))
    
        # Open Question Exercise
        elif self.exerciseData.get("type") == 2:  
            ctk.CTkLabel(self.form_frame, text="Lesson ID:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.lesson_id_entry = ctk.CTkEntry(self.form_frame, width=250)
            self.lesson_id_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
            self.lesson_id_entry.insert(0, self.exerciseData.get("lesson_id", ""))
    
            ctk.CTkLabel(self.form_frame, text="Exercise Number:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
            self.exercise_number_entry = ctk.CTkEntry(self.form_frame, width=150)
            self.exercise_number_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
            self.exercise_number_entry.insert(0, self.exerciseData.get("exercise_number", ""))
    
            ctk.CTkLabel(self.form_frame, text="Video URL:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
            self.video_url_entry = ctk.CTkEntry(self.form_frame, width=250)
            self.video_url_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
            self.video_url_entry.insert(0, self.exerciseData.get("video_url", ""))
    
            ctk.CTkLabel(self.form_frame, text="Correct Answer:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
            self.correct_answer_entry = ctk.CTkEntry(self.form_frame, width=250)
            self.correct_answer_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
            self.correct_answer_entry.insert(0, self.exerciseData.get("correct_answer", ""))
    
        elif self.exerciseData.get("type") == 3:
            ctk.CTkLabel(self.form_frame, text="Lesson ID:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.lesson_id_entry = ctk.CTkEntry(self.form_frame, width=250)
            self.lesson_id_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
            self.lesson_id_entry.insert(0, self.exerciseData.get("lesson_id", ""))
    
            ctk.CTkLabel(self.form_frame, text="Exercise Number:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
            self.exercise_number_entry = ctk.CTkEntry(self.form_frame, width=150)
            self.exercise_number_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
            self.exercise_number_entry.insert(0, self.exerciseData.get("exercise_number", ""))
    
            ctk.CTkLabel(self.form_frame, text="Sentence:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
            self.sentence_entry = ctk.CTkEntry(self.form_frame, width=250)
            self.sentence_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
            self.sentence_entry.insert(0, self.exerciseData.get("sentence", ""))
    
            ctk.CTkLabel(self.form_frame, text="Correct Answer:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
            self.correct_answer_entry = ctk.CTkEntry(self.form_frame, width=250)
            self.correct_answer_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
            self.correct_answer_entry.insert(0, self.exerciseData.get("correct_answer", ""))
    
        # Sentence Gesture Exercise (type == 4)
        elif self.exerciseData.get("type") == 4:
            ctk.CTkLabel(self.form_frame, text="Lesson ID:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.lesson_id_entry = ctk.CTkEntry(self.form_frame, width=250)
            self.lesson_id_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
            self.lesson_id_entry.insert(0, self.exerciseData.get("lesson_id", ""))
        
            ctk.CTkLabel(self.form_frame, text="Exercise Number:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
            self.exercise_number_entry = ctk.CTkEntry(self.form_frame, width=150)
            self.exercise_number_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
            self.exercise_number_entry.insert(0, self.exerciseData.get("exercise_number", ""))
        
            ctk.CTkLabel(self.form_frame, text="Sentence:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
            self.sentence_entry_sg = ctk.CTkEntry(self.form_frame, width=250)
            self.sentence_entry_sg.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
            self.sentence_entry_sg.insert(0, self.exerciseData.get("sentence", ""))
        
            ctk.CTkLabel(self.form_frame, text="Words (comma-separated):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
            self.words_entry_sg = ctk.CTkEntry(self.form_frame, width=250)
            self.words_entry_sg.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
            self.words_entry_sg.insert(0, ', '.join(self.exerciseData.get("words", [])))
        
        # Add a submit button
        self.submit_button = ctk.CTkButton(self.form_frame, text="Submit", command=self.submit_exercise)
        self.submit_button.grid(row=6, column=1, pady=(20, 10))
        
    # submit edited exercise to DB
    def submit_exercise(self):
        lesson_id = ObjectId(self.lesson_id_entry.get())  # Convert lesson_id to ObjectId
    
        if self.exerciseData.get("type") == 0:  # Multiple Choice Exercise
            updated_data = {
                "lesson_id": lesson_id,
                "exercise_number": int(self.exercise_number_entry.get()),
                "video_url": self.video_url_entry.get(),
                "correct_answer": self.correct_answer_entry.get(),
            }
    
        elif self.exerciseData.get("type") == 1:  # Instruction Exercise
            updated_data = {
                "lesson_id": lesson_id,
                "exercise_number": int(self.exercise_number_entry.get()),
                "video_url": self.video_url_entry.get(),
                "answers": [answer.strip() for answer in self.answers_entry.get().split(",")],
                "correct_answer": self.correct_answer_entry.get(),
            }
    
        elif self.exerciseData.get("type") == 2:  # Open Question Exercise
            updated_data = {
                "lesson_id": ObjectId(self.lesson_id_entry_oq.get()),
                "exercise_number": int(self.exercise_number_entry_oq.get()),
                "video_url": self.video_url_entry_mc.get(),  # Assuming this is correct from your previous example
                "correct_answer": self.correct_answer_entry_oq.get(),
            }
    
        elif self.exerciseData.get("type") == 3:  # Complete Sentence by Gesture
            updated_data = {
                "lesson_id": lesson_id,
                "exercise_number": int(self.exercise_number_entry.get()),
                "sentence": self.sentence_entry.get(),
                "correct_answer": self.correct_answer_entry.get(),
            }
    
        elif self.exerciseData.get("type") == 4:  # Sentence Gesture
            updated_data = {
                "lesson_id": lesson_id,
                "exercise_number": int(self.exercise_number_entry.get()),
                "sentence": self.sentence_entry_sg.get(),
                "words": [word.strip() for word in self.words_entry_sg.get().split(",")],
            }
    
        
        # Update the database or perform the necessary action to save the data
        result = DB.update_exercise(self.exercise_id, updated_data)
        
        # Provide feedback to the user
        if result:
            messagebox.showinfo("Success","Exercise updated successfully.")
            #CTkMessagebox(title="Success", message="Exercise updated successfully.", icon="check")

        else:
            messagebox.showerror("Error","Failed to update the exercise.")
            #CTkMessagebox(title="Error", message="Failed to update the exercise.", icon="cancel")
        