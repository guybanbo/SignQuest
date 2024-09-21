import customtkinter as ctk

from homepage import Homepage
from myprofile import MyProfile
from admin import Admin
from register import Register
from lessonScorePage import LessonScorePage
from entities.lesson import Lesson
from entities.user import User
from exercisePages.multipleAnswer import MultipleChoiceExercise
from exercisePages.instructionExercise import InstructionExercise
from exercisePages.openQuestion import OpenQuestion
from exercisePages.completeSentenceByGesture import CompleteSentenceByGesture
from exercisePages.sentenceGesture import SentenceGesture
from exerciseManage.addExercise import AddExercise
from exerciseManage.editExercise import EditExercise

import gc
import os
import sys  # Import sys module
from login import Login
from db import DB
from tkinter import messagebox

class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SignQuest")
        self.geometry("1500x800")   
        
        self.first_frame = "Homepage"
    
        self.user = User(self)
        
        # check if user already loggedin, if so, returns user details
        self.is_valid, self.user_details = self.check_credentials_and_login()
        
        if self.is_valid:
            self.user.set_user_details(self.user_details) 
            self.update_user_details()
        else: 
            self.first_frame = "Login"
            
        
        self.lesson = Lesson(self)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle window close event
        
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        

        self.frames = {}
        
        
        # init app frames
        for F in (InstructionExercise, MultipleChoiceExercise, OpenQuestion, CompleteSentenceByGesture, LessonScorePage, MyProfile,Homepage,Register, Login, Admin, AddExercise, SentenceGesture,EditExercise):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame

        self.show_frame(self.first_frame)
    
    # update user details after finish a lesson
    def update_user_details(self):

        
        completion_percentage, completed_lessons, total_score = DB.get_completed_lessons(self.user.id)
        if completed_lessons:
            self.user.completed_lessons = completed_lessons
            self.user.set_total_score(total_score)
        
    # recreating app frames in order to update the information
    def recreate_lesson_pages(self, keep_frame_name=None):

        # Define the page classes
        page_classes = {
            'InstructionExercise': InstructionExercise,
            'MultipleChoiceExercise': MultipleChoiceExercise,
            'OpenQuestion': OpenQuestion,
            'CompleteSentenceByGesture': CompleteSentenceByGesture,
            'LessonScorePage': LessonScorePage,
            'SentenceGesture': SentenceGesture,
            'MyProfile': MyProfile,
            'Homepage': Homepage,
            'Login': Login,
            'Register': Register,
            'Admin': Admin,
            'AddExercise': AddExercise,
            'EditExercise': EditExercise
        }
    
    
        # Delete all frames except the one to keep
        for page_name in list(self.frames.keys()):
            if page_name != keep_frame_name:
                # Make sure the frame is fully destroyed
                frame = self.frames[page_name]
                frame.grid_forget()  # Remove it from view (if using grid)
                frame.destroy()  # Destroy the widget completely
                del self.frames[page_name]  # Remove reference from the dictionary



    
        # Run garbage collection
        gc.collect()
        
           
        # Update user details
        self.update_user_details()
    
        # Recreate the frames
        for page_name, page_class in page_classes.items():
            if page_name != keep_frame_name:  # Avoid recreating the kept frame
                frame = page_class(parent=self.container, controller=self)
                self.frames[page_name] = frame
    
 
    
     
        
    # recreating specific app frame in order to update the information
    def recreate_page_by_name(self, page_name):
        
        page_classes = {
            'InstructionExercise': InstructionExercise,
            'MultipleChoiceExercise': MultipleChoiceExercise,
            'OpenQuestion': OpenQuestion,
            'CompleteSentenceByGesture': CompleteSentenceByGesture,
            'LessonScorePage': LessonScorePage,
            'MyProfile': MyProfile,
            'Homepage': Homepage,
            'Register': Register,
            'SentenceGesture': SentenceGesture
        }
        
        for key, frame in list(self.frames.items()):
            if key == page_name:
                 frame.destroy()
                 del self.frames[key]
                 del frame
        
        if page_name in page_classes:
            F = page_classes[page_name]
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            gc.collect()
        else:
            raise ValueError(f"Page name '{page_name}' is not recognized.")
            
    # show specific frame
    def show_frame(self, page_name):
        self.frames[page_name].grid(row=0, column=0, sticky="nsew")
        frame = self.frames[page_name]
        frame.tkraise()
        
    
    
    def on_closing(self):  # Method to handle window close event
        self.destroy()  # Destroy the window
        sys.exit()  # Ensure the program terminates
        
     
    # check if user loggedin and verify the details
    def check_credentials_and_login(self):
        credentials_file = "credentials.txt"
        
        # Check if the file exists
        if os.path.exists(credentials_file):
            with open(credentials_file, "r") as file:
                lines = file.readlines()
                email_line = lines[0].strip()
                password_line = lines[1].strip()
                
                # Extract email and password hash from the file
                email = email_line.split(":", 1)[1].strip()
                password_hash = password_line.split(":", 1)[1].strip()
                
                # Validate login and retrieve user details
                is_valid, user_details = DB.validate_login(email, password_hash, True)
                if is_valid:
                    return True, user_details
                else:
                    return False, None
        else:
            return False, None
        
    
    def logout(self): 
        
        credentials_file = "credentials.txt"
        
        if os.path.exists(credentials_file):
            try:
                # Delete the credentials file
                os.remove(credentials_file)
                print("Logged out successfully. Credentials file deleted.")
                # Optionally, you could also provide feedback to the user via a UI message
                messagebox.showinfo("Logout Successful", "You have been logged out.")
                #CTkMessagebox(title="Logout Successful", message="You have been logged out.", icon="info")
                self.show_frame("Login")
            except Exception as e:
                print(f"Error deleting credentials file: {e}")
                # Optionally, show an error message to the user
                #CTkMessagebox(title="Logout Failed", message="An error occurred while logging out.", icon="cancel")
                messagebox.showerror("Logout Failed", "An error occurred while logging out.")
        else:
            print("No credentials file found.")
            # Optionally, show a message that the user was already logged out
            #CTkMessagebox(title="Already Logged Out", message="No active session found.", icon="info")
            messagebox.showerror("Already Logged Out", "No active session found.")
    
       

if __name__ == "__main__":
    ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"
    
    app = MainApplication()
    app.mainloop()