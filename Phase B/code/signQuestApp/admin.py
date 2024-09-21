import customtkinter as ctk
from db import DB  # Ensure you have a module named db with a get_lessons function
from PIL import Image, ImageTk
from CTkTable import *
import textwrap
from tkinter import messagebox


class Admin(ctk.CTkFrame):
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
        

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="  Admin", image=self.image_tk,
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
        self.toolbar.grid_columnconfigure(0, weight=1)
        self.toolbar.grid_columnconfigure(1, weight=1)
        self.toolbar.grid_columnconfigure(2, weight=1)

        self.profile_button = ctk.CTkButton(self.toolbar, text="Hello "+ self.controller.user.name,command=lambda: self.my_profile_show_frame())
        self.profile_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.score_label = ctk.CTkLabel(self.toolbar, text="Score: "+ str(self.controller.user.total_score),font=("Helvetica", 14, "bold"))
        self.score_label.grid(row=0, column=1, padx=10, pady=10)

        self.signout_button = ctk.CTkButton(self.toolbar, text="Logout",command=self.controller.logout)
        self.signout_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        
        # Create home frame
        self.home_frame = ctk.CTkFrame(self.home_container, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame.grid_rowconfigure(2, weight=1)
        self.home_frame.grid(row=1, column=0, sticky="n")
        

        self.view_lessons_list()

    # show myprofile page when clicking on the button
    def my_profile_show_frame(self):
         
        self.controller.frames["MyProfile"].init_buttons_background()
        self.controller.show_frame("MyProfile")

    def clear_home_frame(self):
        for widget in self.home_frame.winfo_children():
            widget.destroy()
            
    
    def on_image_click(self, event):
        self.controller.show_frame("Homepage")

    # init colors according to color mode
    def init_buttons_background(self):
        
        if(self.last_button_clicked != None):

            if(ctk.get_appearance_mode() == "Dark"):
                self.last_button_clicked.configure(fg_color="#5b5b5b")  # Change to active state
            else:
                self.last_button_clicked.configure(fg_color="#bcbcbc")  # Change to active state
        
    # show matching data according to clicked section on menu
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
        if button.cget("text") == "Manage Lessons":
            self.view_lessons_list()
        elif button.cget("text") == "Manage Exercises":
            self.view_exercises_list()
        elif button.cget("text") == "View Feedbacks":
            self.view_feedbacks_list()
    
        self.home_frame.grid(row=1, column=0, sticky="n")

    def view_lessons_list(self, number_of_items=5, page=1):
        self.clear_home_frame()
        
        # Fetch lessons from the database with pagination
        lessons_list, total_lessons_db = DB.get_lessons_pagination(number_of_items, page)
        
        if not lessons_list or len(lessons_list) == 0:
            # Show message on the screen if no lessons are found
            no_lessons_label = ctk.CTkLabel(self.home_frame, text="No more lessons found.", text_color="red")
            no_lessons_label.grid(row=4, columnspan=4, padx=20, pady=10)
            go_back_button = ctk.CTkButton(self.home_frame, text="Go Back", command=lambda: self.view_lessons_list(number_of_items, page-1))
            go_back_button.grid(row=5, columnspan=4, padx=20, pady=10)
            self.add_new_lesson_form()
            return
        
        # Define headers for the lesson table, with separate columns for Edit and Delete
        headers = ["Lesson ID", "Lesson Content", "Action"]
        col_count = len(headers)
        
        # Define the width for wrapping the lesson content text 
        wrap_width = 70
        
        # Constructing the 2D array of values with headers mapped to field names
        values = [headers]  # Start with headers as the first row
        for lesson in lessons_list:
            lesson_id = str(lesson.get("_id"))  # Convert ObjectId to string
            lesson_number = str(lesson.get("lesson_number"))
            
            # Ensure lesson_content is a string, even if it's stored as a list of strings
            content = lesson.get("lesson_content", "")
            if isinstance(content, list):
                content = ", ".join(content)  # Join list items into a single string
            
            # Now wrap the content
            lesson_content = "\n".join(textwrap.wrap(content, width=wrap_width))
            
            # Placeholders for Edit and Delete actions
            edit_action = "Edit"
            delete_action = "Delete"
            
            row = [lesson_number, lesson_content, edit_action]
            values.append(row)
        
        row_count = len(lessons_list)
        
        # Create and display the table using CTkTable
        table = CTkTable(self.home_frame, row=row_count+1, column=col_count, values=values, header_color="#6fa8dc",
                         command=lambda e: self.on_lesson_table_click(e, table, lessons_list))
        table.grid(row=4, columnspan=4, padx=20, pady=20)
        
        # Calculate the total number of pages
        total_pages = (total_lessons_db + number_of_items - 1) // number_of_items
        
        # Add pagination controls (Previous and Next buttons)
        if page > 1:
            prev_button = ctk.CTkButton(self.home_frame, text="Previous", command=lambda: self.view_lessons_list(number_of_items, page-1))
            prev_button.grid(row=5, column=0, padx=10, pady=10, sticky="w")
        else:
            prev_button = ctk.CTkButton(self.home_frame, text="Previous", state="disabled")
            prev_button.grid(row=5, column=0, padx=10, pady=10, sticky="w")
        
        if page < total_pages:
            next_button = ctk.CTkButton(self.home_frame, text="Next", command=lambda: self.view_lessons_list(number_of_items, page+1))
            next_button.grid(row=5, column=3, padx=10, pady=10, sticky="e")
        else:
            next_button = ctk.CTkButton(self.home_frame, text="Next", state="disabled")
            next_button.grid(row=5, column=3, padx=10, pady=10, sticky="e")
        
        # Show current page number
        page_num = ctk.CTkLabel(self.home_frame, text=f"Page {page} of {total_pages}")
        page_num.grid(row=5, columnspan=2, column=1, padx=10, pady=20, sticky="nsew")
        
        # Add entry box to jump to a specific page
        page_label = ctk.CTkLabel(self.home_frame, text="Jump to page:")
        page_label.grid(row=6, column=1, padx=10, pady=20)
        
        page_entry = ctk.CTkEntry(self.home_frame)
        page_entry.grid(row=6, column=2, padx=10, pady=20)
        
        self.error_label = None

        
        def go_to_page():
            try:
                new_page = int(page_entry.get())  # Get the page number from the entry box
                if 1 <= new_page <= total_pages:
                    self.view_lessons_list(number_of_items, new_page)
                else:
                    # Handle out-of-bounds page numbers
                    self.error_label = ctk.CTkLabel(self.home_frame, text=f"Please enter a page number between 1 and {total_pages}.", text_color="red")
                    self.error_label.grid(row=8, columnspan=4, padx=20, pady=10)
            except ValueError:
                # Handle invalid input
                if self.error_label:
                    self.error_label.destroy()
                
                self.error_label = ctk.CTkLabel(self.home_frame, text="Please enter a valid page number.", text_color="red")
                self.error_label.grid(row=8, columnspan=4, padx=20, pady=10)
        
        jump_button = ctk.CTkButton(self.home_frame, text="Go", command=go_to_page)
        jump_button.grid(row=7, columnspan=4, padx=10, pady=10)
        
        self.add_new_lesson_form()

      
    # creating add new lesson ui form
    def add_new_lesson_form(self):
        
        form_frame = ctk.CTkFrame(self.home_frame, corner_radius=10 )
        form_frame.grid(row=9, column=0, padx=20, pady=20,columnspan=4,sticky="nsew")
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)
        
        # Add a form below the table
        form_title = ctk.CTkLabel(form_frame, text="Add a new lesson", font=("Arial", 16, "bold", "underline"))
        form_title.grid(row=0, columnspan=4, padx=20, pady=(10, 20),sticky="nsew")
        
        lesson_content_label = ctk.CTkLabel(form_frame, text="Lesson Content:")
        lesson_content_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        lesson_content_entry = ctk.CTkEntry(form_frame, width=200,placeholder_text="(separated with commas)")
        lesson_content_entry.grid(row=1, column=2, padx=10, pady=5, sticky="e")
    
        
        submit_button = ctk.CTkButton(form_frame, text="Submit", command=lambda: self.add_new_lesson(lesson_content_entry.get()))
        submit_button.grid(row=2, columnspan=4, padx=20, pady=20)
        
    
    # send new lesson data to DB
    def add_new_lesson(self,lesson_content):
        
        # Convert the lesson_content string into a list
        lesson_content_list = [item.strip() for item in lesson_content.split(',')]

        new_lesson = DB.create_lesson(lesson_content_list)
        
        if(new_lesson):
            messagebox.showinfo("Success","Lesson was added successfully!")
            #CTkMessagebox(title="Success", message="Lesson was added successfully!",icon="check")
        else:
            messagebox.showerror("Error","Failed to add a Lesson.")
            #CTkMessagebox(title="Error", message="Failed to add a Lesson.",icon="cancel")
                
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
               
    # popup for editing lesson content
    def on_lesson_table_click(self, e,table, lessons_list):
        try:
            # Depending on the structure of e, it might be necessary to inspect what it contains
            #print(f"Clicked: {e}")
            
            # Assuming e is a tuple (row, column, value)
            row = e.get('row')
            column = e.get('column')
            value = e.get('value')
                
            #lesson_id =  table.get(row, 0)
            lesson_content = table.get(row, 1)
            
            lesson_id = lessons_list[int(row-1)]["_id"]
            
            
            if(column == 2 and row > 0):
                
                # Create the popup window
                popup = ctk.CTkToplevel()
                popup.title("Edit Cell")
                
                popup.attributes("-topmost", True)
    
                
                # Show the current content
                label = ctk.CTkLabel(popup, text="Lesson Content:")
                label.pack(pady=10)
                
                # Entry widget to allow editing
                entry = ctk.CTkEntry(popup, width=200)
                entry.insert(0, lesson_content)
                entry.pack(pady=10)
                
                def save_changes():
                    new_value = entry.get()
                    lesson_content_list = [item.strip() for item in new_value.split(',')]
                    lesson_update = DB.update_lesson_content(lesson_id,lesson_content_list)
                    if(lesson_update):
                        pass
                        #CTkMessagebox(title="Success", message="Lesson content was updated successfully!",icon="check")
                    else:
                        pass
                        #CTkMessagebox(title="Error", message="Failed to update lesson's content",icon="cancel")
                    
                    table.insert(row, column-1, new_value)  # Update the table
                    if popup.winfo_exists():
                        popup.destroy()
                
                # Save button
                save_button = ctk.CTkButton(popup, text="Save", command=save_changes)
                save_button.pack(side="left", padx=10, pady=10)
                
                # Cancel button
                cancel_button = ctk.CTkButton(popup, text="Cancel", command=popup.destroy)
                cancel_button.pack(side="right", padx=10, pady=10)
                
                # Center the popup window
                popup.update_idletasks()  # Update the geometry before centering
                self.center_popup(popup,self)
                        

        except Exception as e:
            print(f"Error in on_table_click: {e}")
        
        
        
    def add_new_exercise(self):
        self.controller.show_frame("AddExercise")

    # creates table with list of exercises
    def view_exercises_list(self, number_of_items=10, page=1):
        self.clear_home_frame()
        
        # Fetch exercises from the database with pagination
        exercises_list, total_exercises_db = DB.get_exercises(number_of_items, page)
        
        # Add a button to add a new exercise
        add_exercise_button = ctk.CTkButton(self.home_frame, text="Add a New Exercise", command=self.add_new_exercise)
        add_exercise_button.grid(row=3, columnspan=4, padx=20, pady=20)
        
        if not exercises_list or len(exercises_list) == 0:
            # Show message on the screen if no exercises are found
            no_exercises_label = ctk.CTkLabel(self.home_frame, text="No more exercises found.", text_color="red")
            no_exercises_label.grid(row=4, columnspan=4, padx=20, pady=10)
            go_back_button = ctk.CTkButton(self.home_frame, text="Go Back", command=lambda: self.view_exercises_list(number_of_items, page-1))
            go_back_button.grid(row=5, columnspan=4, padx=20, pady=10)
            return
        
        # Define headers for the exercise table, with separate columns for Edit and Delete
        headers = ["Lesson Number", "Type", "Action", "Action"]
        col_count = len(headers)
        
        # Constructing the 2D array of values with headers mapped to field names
        values = [headers]  # Start with headers as the first row
        for exercise in exercises_list:
            exercise_id = str(exercise.get("_id"))  # Convert ObjectId to string
            lesson_id = exercise.get("lesson_id", "")
            lesson_number = exercise.get("lesson_number", "")
            exercise_type = exercise.get("type", "")
            exercise_type_name = self.controller.lesson.exercises_types[exercise_type]["name"]
        
            # Placeholders for Edit and Delete actions
            edit_action = "Edit"
            delete_action = "Delete"
        
            row = [lesson_number, exercise_type_name, edit_action, delete_action]
            values.append(row)
        
        row_count = len(exercises_list)
        
        # Create and display the table using CTkTable
        table = CTkTable(self.home_frame, row=row_count+1, column=col_count, values=values, header_color="#6fa8dc",
                         command=lambda e: self.on_exercise_table_click(e, table, exercises_list))
        table.grid(row=5, columnspan=4, padx=20, pady=10)
        
        # Add pagination controls (Previous and Next buttons)
        if page > 1:
            prev_button = ctk.CTkButton(self.home_frame, text="Previous", command=lambda: self.view_exercises_list(number_of_items, page-1))
            prev_button.grid(row=6, column=0, padx=20, pady=10, sticky="w")
        else:
            prev_button = ctk.CTkButton(self.home_frame, text="Previous", state="disabled")
            prev_button.grid(row=6, column=0, padx=20, pady=10, sticky="w")
    
        # Calculate the total number of pages
        total_pages = (total_exercises_db + number_of_items - 1) // number_of_items
        next_button = ctk.CTkButton(self.home_frame, text="Next", command=lambda: self.view_exercises_list(number_of_items, page+1))
        if page < total_pages:
            next_button.grid(row=6, column=3, padx=20, pady=10, sticky="e")
        else:
            next_button.grid(row=6, column=3, padx=20, pady=10, sticky="e")
            next_button.configure(state="disabled")
        
        # Show current page number
        page_num = ctk.CTkLabel(self.home_frame, text=f"Page {page} of {total_pages}")
        page_num.grid(row=6, columnspan=2, column=1, padx=10, pady=20, sticky="nsew")
        
        # Add entry box to jump to a specific page
        page_label = ctk.CTkLabel(self.home_frame, text="Jump to page:")
        page_label.grid(row=8, column=1, padx=10, pady=20)
        
        page_entry = ctk.CTkEntry(self.home_frame)
        page_entry.grid(row=8, column=2, padx=10, pady=20)
        
        def go_to_page():
            try:
                new_page = int(page_entry.get())  # Get the page number from the entry box
                if 1 <= new_page <= total_pages:
                    self.view_exercises_list(number_of_items, new_page)
                else:
                    # Handle out-of-bounds page numbers
                    error_label = ctk.CTkLabel(self.home_frame, text=f"Please enter a page number between 1 and {total_pages}.", text_color="red")
                    error_label.grid(row=10, columnspan=4, padx=20, pady=10)
            except ValueError:
                # Handle invalid input
                error_label = ctk.CTkLabel(self.home_frame, text="Please enter a valid page number.", text_color="red")
                error_label.grid(row=10, columnspan=4, padx=20, pady=10)
        
        jump_button = ctk.CTkButton(self.home_frame, text="Go", command=go_to_page)
        jump_button.grid(row=9, columnspan=4, padx=10, pady=10)


    # handle edit and delete exercise
    def on_exercise_table_click(self, e, table, exercise_list):
        try:
        
    
            # Assuming e is a tuple (row, column, value)
            row = e.get('row')
            column = e.get('column')
            value = e.get('value')
            
                    
            exercise_id = exercise_list[int(row)-1]["_id"]
  
            
            if(value=="Edit" and row > 0):
                self.controller.frames["EditExercise"].set_exercise_id(exercise_id)
                self.controller.show_frame("EditExercise")
            
            if(value=="Delete" and row > 0):
                
                confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this exercise?")
                if confirm:
                    # Proceed with the deletion
                    if(DB.hide_exercise(exercise_id)):
                         messagebox.showinfo("Success", "Exercise deleted successfully!")
                         table.delete_row(row)
                    else:
                        messagebox.showinfo("Error", "Failed to delete exercise!")

                else:
                    # Handle if the user cancels the deletion
                    print("Deletion canceled")
                
    
           
    
        except Exception as e:
            print(f"Error in on_exercise_table_click: {e}")


    def add_lesson_buttons(self):


        self.my_profile_button = ctk.CTkButton(self.lesson_scroll_frame, text="Manage Lessons", corner_radius=0, height=40, border_spacing=10,
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

        self.my_progress_button = ctk.CTkButton(self.lesson_scroll_frame, text="Manage Exercises", corner_radius=0, height=40, border_spacing=10,
                                            fg_color="transparent", text_color=("gray10", "gray90"),
                                            hover_color=("#a5e7fd", "#00688B"), anchor="w",
                                            command=lambda: self.on_button_click(self.my_progress_button))
        self.my_progress_button.grid(row=2, column=0, sticky="ew")
        self.lesson_buttons.append(self.my_progress_button)
        
        # Add the "Send Feedback" button
        self.view_feedback_button = ctk.CTkButton(self.lesson_scroll_frame, text="View Feedbacks", corner_radius=0, height=40, border_spacing=10,
                                                 fg_color="transparent", text_color=("gray10", "gray90"),
                                                 hover_color=("#a5e7fd", "#00688B"), anchor="w",
                                                 command=lambda: self.on_button_click(self.view_feedback_button))
        self.view_feedback_button.grid(row=3, column=0, sticky="ew")
        self.lesson_buttons.append(self.view_feedback_button)

        
    # creates table with feedbacks list
    def view_feedbacks_list(self):
        self.clear_home_frame()
        
        # Fetch feedbacks from the database
        feedback_list = DB.get_user_feedback()  # Retrieve all feedbacks
        
        if not feedback_list or len(feedback_list) == 0:
            # Show message on the screen if no feedbacks are found
            no_feedback_label = ctk.CTkLabel(self.home_frame, text="No feedbacks found.", text_color="red")
            no_feedback_label.grid(row=4, columnspan=2, padx=20, pady=10)
            return
    
        # Define headers and field names for the feedback table
        headers = ["User ID", "Feedback", "Rating", "Date"]
        col_count = len(headers)
    
        # Define the width for wrapping the feedback text (e.g., 50 characters)
        wrap_width = 70
    
        # Constructing the 2D array of values with headers mapped to field names
        values = [headers]  # Start with headers as the first row
        for feedback in feedback_list:
            row = [
                str(feedback.get("user_id")),  # Convert ObjectId to string
                "\n".join(textwrap.wrap(feedback.get("feedback"), width=wrap_width)),  # Wrap the feedback text
                feedback.get("rating"),
                feedback.get("date").strftime('%Y-%m-%d %H:%M:%S')  # Format date
            ]
            values.append(row)
    
        row_count = len(feedback_list)
    
        # Create and display the table
        table = CTkTable(self.home_frame, row=row_count+1, column=col_count, values=values, header_color="#6fa8dc")
        table.grid(row=4, columnspan=2, padx=20, pady=10)


    def change_appearance_mode_event(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)
        self.on_button_click(self.last_button_clicked)
        # -*- coding: utf-8 -*-

