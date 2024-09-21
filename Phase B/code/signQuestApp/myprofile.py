import customtkinter as ctk
from db import DB  # Ensure you have a module named db with a get_lessons function
from PIL import Image, ImageTk
from CTkTable import *
from tkinter import messagebox




# class for the frame "My profile"
class MyProfile(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        self.last_button_clicked = None
        self.lesson_buttons = []
        self.my_profile_button = None
        self.my_progress_button = None

        # Set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create navigation frame
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid_columnconfigure(0, weight=1)
        self.navigation_frame.grid_rowconfigure(2, weight=1)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        
        
        image_path = "images/left-arrow.png"  # Replace with the path to your image
        image = Image.open(image_path)
        image = image.resize((25, 25), Image.ANTIALIAS)  # Resize the image if necessary
        self.image_tk = ImageTk.PhotoImage(image,master=self.controller)  # Keep a reference to the image
        

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="  Profile", image=self.image_tk,
                                                             compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Bind click event to the label
        self.navigation_frame_label.bind("<Button-1>", self.on_image_click)
        
        
        self.lesson_scroll_frame = ctk.CTkFrame(self.navigation_frame, corner_radius=0,height=600,fg_color="transparent")
        self.lesson_scroll_frame.grid(row=1, column=0, sticky="ew")
        self.lesson_scroll_frame.grid_columnconfigure(0, weight=1)
        self.lesson_scroll_frame.grid_rowconfigure(0, weight=1)
        # Add lesson buttons to navigation frame
        self.add_lesson_buttons()

        self.appearance_mode_menu = ctk.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=2, column=0, padx=20, pady=20, sticky="s")


        self.home_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_container.grid_columnconfigure(0, weight=1)
        self.home_container.grid_rowconfigure(1, weight=1)  # Give weight to row 1 (home_frame)
        self.home_container.grid(row=0, column=1, sticky="nsew")
        
        self.toolbar = ctk.CTkFrame(self.home_container, height=50)
        self.toolbar.grid(row=0, column=0, sticky="ew")
        self.toolbar.grid_columnconfigure(0, weight=0)
        self.toolbar.grid_columnconfigure(1, weight=0)
        self.toolbar.grid_columnconfigure(2, weight=1)

        self.profile_button = ctk.CTkButton(self.toolbar, text="Hello "+ self.controller.user.name)
        self.profile_button.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")
        
        if(self.controller.user.admin):
            self.profile_button = ctk.CTkButton(self.toolbar, text="Admin Page",command=lambda: self.admin_show_frame())
            self.profile_button.grid(row=0, column=1,padx=(5, 10), pady=10, sticky="w")

        self.score_label = ctk.CTkLabel(self.toolbar, text="Score: "+ str(self.controller.user.total_score),font=("Helvetica", 14, "bold"))
        self.score_label.grid(row=0, column=2, padx=10, pady=10)

        self.signout_button = ctk.CTkButton(self.toolbar, text="Logout",command=self.controller.logout)
        self.signout_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        
        # Create home frame
        self.home_frame = ctk.CTkFrame(self.home_container, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame.grid_rowconfigure(2, weight=1)
        self.home_frame.grid(row=1, column=0, sticky="n")
        

        self.create_user_form()
        self.create_change_password_form()

        
    def admin_show_frame(self):
        
       self.controller.frames["Admin"].init_buttons_background()
       self.controller.show_frame("Admin")


    def clear_home_frame(self):
        for widget in self.home_frame.winfo_children():
            widget.destroy() 

    
    # creates the ui for showing the user's progress
    def my_progress(self):
        self.my_progress_title = ctk.CTkLabel(self.home_frame, text="User Progress", font=("Arial", 16, "bold"))
        self.my_progress_title.grid(row=0, column=0, columnspan=2, pady=(20, 10))
        
        completed_lesson_percentage, completed_lesson_list, total_score = self.controller.user.get_completed_lessons()
        
        self.completed_label = ctk.CTkLabel(self.home_frame, text=f"You have completed {int(completed_lesson_percentage)}% of the lessons")
        self.completed_label.grid(row=1, column=0, padx=10, pady=5,  columnspan=2)
        
        learned_words = self.controller.user.get_learned_words()
        
        self.learned_words_label = ctk.CTkLabel(self.home_frame, text=f"You have learned {learned_words} words")
        self.learned_words_label.grid(row=2, column=0, padx=10, pady=5,  columnspan=2)
        
        self.learned_words_label = ctk.CTkLabel(self.home_frame, text=f"You have learned {learned_words} words")
        self.learned_words_label.grid(row=2, column=0, padx=10, pady=5, columnspan=3)
        
        
         
        self.table_label = ctk.CTkLabel(self.home_frame, text="Completed Lessons:",font=("Arial", 14, "bold"))
        self.table_label.grid(row=3, column=0, padx=10, pady=5, columnspan=3)
        
        
        headers = ["id", "Score"]
        col_count = len(headers)
        row_count = len(completed_lesson_list)
        
        field_names = ["_id", "score"]  # Assuming field names in completed_lesson_list
        
        completed_lesson_list.sort(key=lambda x: x['lesson_number'])
   
        
        # Constructing the 2D array of values with headers mapped to field names
        values = [headers]  # Start with headers as the first row
        for row in completed_lesson_list:
            formatted_row = [row["lesson_number"], f"{int(row['score'] * 100)}"]  # Format score to two decimal places
            values.append(formatted_row)
        
        table = CTkTable(self.home_frame, row=row_count+1, column=col_count, values=values,header_color="#6fa8dc")
        table.grid(row=4, columnspan=2, padx=20, pady=10)
        
    # creates user's details form
    def create_user_form(self):
        user_details = self.controller.user.get_user_details()

        self.user_form_title = ctk.CTkLabel(self.home_frame, text="User Details", font=("Arial", 16, "bold"))
        self.user_form_title.grid(row=0, column=0, columnspan=2, pady=(20, 10))

        self.name_label = ctk.CTkLabel(self.home_frame, text="Name:")
        self.name_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.name_entry = ctk.CTkEntry(self.home_frame)
        self.name_entry.insert(0, user_details["name"])
        self.name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        self.email_label = ctk.CTkLabel(self.home_frame, text="Email:")
        self.email_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.email_value = ctk.CTkLabel(self.home_frame, text=user_details["email"])
        self.email_value.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        self.id_label = ctk.CTkLabel(self.home_frame, text="ID:")
        self.id_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.id_value = ctk.CTkLabel(self.home_frame, text=user_details["id"])
        self.id_value.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        self.total_score_label = ctk.CTkLabel(self.home_frame, text="Total Score:")
        self.total_score_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self.total_score_value = ctk.CTkLabel(self.home_frame, text=user_details["total_score"])
        self.total_score_value.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        self.update_button = ctk.CTkButton(self.home_frame, text="Update", command=self.update_user_details)
        self.update_button.grid(row=5, column=0, columnspan=2, pady=10)

    # creates form for changing password
    def create_change_password_form(self):
        
        self.change_password_form_title = ctk.CTkLabel(self.home_frame, text="Change Password", font=("Arial", 16, "bold"))
        self.change_password_form_title.grid(row=6, column=0, columnspan=2, pady=(40, 10))

        self.current_password_label = ctk.CTkLabel(self.home_frame, text="Current Password:")
        self.current_password_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")

        self.current_password_entry = ctk.CTkEntry(self.home_frame, show="*")
        self.current_password_entry.grid(row=7, column=1, padx=10, pady=5, sticky="ew")

        self.new_password_label = ctk.CTkLabel(self.home_frame, text="New Password:")
        self.new_password_label.grid(row=8, column=0, padx=10, pady=5, sticky="w")

        self.new_password_entry = ctk.CTkEntry(self.home_frame, show="*")
        self.new_password_entry.grid(row=8, column=1, padx=10, pady=5, sticky="ew")

        self.change_password_button = ctk.CTkButton(self.home_frame, text="Change Password", command=self.change_password)
        self.change_password_button.grid(row=9, column=0, columnspan=2, pady=10)

    def update_user_details(self):
        # Get the updated details from the GUI
        updated_details = {
            "name": self.name_entry.get(),
            "email": self.email_value.cget("text"),
            "_id": self.id_value.cget("text"),
            "total_score": self.total_score_value.cget("text")
        }
        
        # Call the database function to update the user's name
        success = DB.update_user_name_db(updated_details["_id"], updated_details["name"])

        # Show a message box based on the result
        if success:
            messagebox.showinfo("Update Successful", f"Name updated to {updated_details['name']}.")
        else:
            messagebox.showerror("Update Failed", "Failed to update the name. Please try again.")

    def change_password(self):
        current_password = self.current_password_entry.get()
        new_password = self.new_password_entry.get()
        
        if self.controller.user.change_password(current_password, new_password):
            # Password change successful
            hashed_password = DB.hash_password(new_password)
            
            
            # Update the credentials file
            with open("credentials.txt", "w") as file:
                file.write(f"Username: {self.controller.user.email}\n")
                file.write(f"Password: {hashed_password}\n")
            
            messagebox.showinfo("Update Successful", "Password changed successfully")
        #ctk.CTkLabel(self.home_frame, text="Password changed successfully", text_color="green").grid(row=10, column=0, columnspan=2, pady=(10, 0))
        else:
            messagebox.showerror("Update Failed", "Current password is incorrect")
    
    def on_image_click(self, event):
        self.controller.show_frame("Homepage")

    def init_buttons_background(self):
        
        if(self.last_button_clicked != None):

            if(ctk.get_appearance_mode() == "Dark"):
                self.last_button_clicked.configure(fg_color="#5b5b5b")  # Change to active state
            else:
                self.last_button_clicked.configure(fg_color="#bcbcbc")  # Change to active state
        
    # handle menu buttons click, showing the relevent page
    def on_button_click(self, button):
        self.clear_home_frame()
        
        # Reset background of all buttons
        self.last_button_clicked = button
        for btn in self.lesson_buttons:
            btn.configure(fg_color="transparent")  # Reset to original state
        
        # Change background of the clicked button
        if ctk.get_appearance_mode() == "Dark":
            button.configure(fg_color="#5b5b5b")  # Change to active state
        else:
            button.configure(fg_color="#bcbcbc")  # Change to active state
    
        # Show specific content based on button clicked
        if button.cget("text") == "My Profile":
            self.create_user_form()
            self.create_change_password_form()
        elif button.cget("text") == "My Progress":
            self.my_progress()
        elif button.cget("text") == "Send Feedback":
            self.create_feedback_form()
    
        self.home_frame.grid(row=1, column=0, sticky="n")

    # creates menu buttons, my profile, my progress and send feedback
    def add_lesson_buttons(self):


        self.my_profile_button = ctk.CTkButton(self.lesson_scroll_frame, text="My Profile", corner_radius=0, height=40, border_spacing=10,
                                          fg_color="transparent", text_color=("gray10", "gray90"),
                                          hover_color=("#a5e7fd", "#00688B"), anchor="w",
                                          command=lambda: self.on_button_click(self.my_profile_button))
        self.my_profile_button.grid(row=1, column=0, sticky="ew")
        self.lesson_buttons.append(self.my_profile_button)
        
        self.last_button_clicked = self.my_profile_button
        
        if(ctk.get_appearance_mode() == "Dark"):
            self.my_profile_button.configure(fg_color="#5b5b5b")  # Change to active state
        else:
            self.my_profile_button.configure(fg_color="#bcbcbc")  # Change to active state

        self.my_progress_button = ctk.CTkButton(self.lesson_scroll_frame, text="My Progress", corner_radius=0, height=40, border_spacing=10,
                                            fg_color="transparent", text_color=("gray10", "gray90"),
                                            hover_color=("#a5e7fd", "#00688B"), anchor="w",
                                            command=lambda: self.on_button_click(self.my_progress_button))
        self.my_progress_button.grid(row=2, column=0, sticky="ew")
        self.lesson_buttons.append(self.my_progress_button)
        
        # Add the "Send Feedback" button
        self.send_feedback_button = ctk.CTkButton(self.lesson_scroll_frame, text="Send Feedback", corner_radius=0, height=40, border_spacing=10,
                                                 fg_color="transparent", text_color=("gray10", "gray90"),
                                                 hover_color=("#a5e7fd", "#00688B"), anchor="w",
                                                 command=lambda: self.on_button_click(self.send_feedback_button))
        self.send_feedback_button.grid(row=3, column=0, sticky="ew")
        self.lesson_buttons.append(self.send_feedback_button)

        
    # create form for sending a feedback
    def create_feedback_form(self):
        self.clear_home_frame()
        
        # Create a frame for the feedback form
        feedback_frame = ctk.CTkFrame(self.home_frame, corner_radius=10)
        feedback_frame.grid(row=0, column=0, padx=20, pady=20)
        
        # Create label and text entry for feedback
        feedback_label = ctk.CTkLabel(feedback_frame, text="Your Feedback:", font=("Arial", 14))
        feedback_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))
        
        self.feedback_text = ctk.CTkTextbox(feedback_frame, height=150, width=400, corner_radius=10)
        self.feedback_text.grid(row=1, column=0, padx=10, pady=(0, 10))
        
        # Create label and rating input
        rating_label = ctk.CTkLabel(feedback_frame, text="Rating (1-5):", font=("Arial", 14))
        rating_label.grid(row=2, column=0, sticky="w", padx=10, pady=(10, 0))
        
        self.rating = ctk.CTkEntry(feedback_frame, placeholder_text="Enter rating (1-5)", width=150, corner_radius=10)
        self.rating.grid(row=3, column=0, padx=10, pady=(0, 10))
        
        # Create a submit button
        submit_button = ctk.CTkButton(feedback_frame, text="Submit", command=self.submit_feedback, corner_radius=10, height=40)
        submit_button.grid(row=4, column=0, pady=10)
        
    # submit user's feedback to the db
    def submit_feedback(self):
        feedback = self.feedback_text.get("1.0", "end").strip()
        rating = self.rating.get().strip()
        
        # Validate rating input
        try:
            rating = int(rating)
            if not (1 <= rating <= 5):
                raise ValueError("Rating must be between 1 and 5.")
        except ValueError:
            messagebox.showerror("Error", "Rating must be an integer between 1 and 5.")
            return
    
        if not feedback:
            messagebox.showerror("Error", "Please provide feedback.")
            return
    
        if self.controller.user.send_feedback(feedback, rating):
            messagebox.showinfo("Success", "Feedback submitted successfully!")
        else:
            messagebox.showerror("Error", "Failed to submit feedback.")
    
        # Clear feedback form
        self.feedback_text.delete("1.0", "end")
        self.rating.delete(0, "end")



    def change_appearance_mode_event(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)
        self.on_button_click(self.last_button_clicked)
        