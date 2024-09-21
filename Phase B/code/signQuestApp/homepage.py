import customtkinter
from db import DB  # Ensure you have a module named db with a get_lessons function
from PIL import Image, ImageTk
from tkinter import messagebox


# class for the frame Homepage
class Homepage(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        self.active_lesson_frame = None
        self.last_button_clicked = None
        self.lesson_buttons = []

        # Set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid_columnconfigure(0, weight=1)
        self.navigation_frame.grid_rowconfigure(2, weight=1)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
            
                        
        image_path = "images/signquest.png"  # Replace with the path to your image
        image = Image.open(image_path)
        image = image.resize((182, 41), Image.ANTIALIAS)  # Resize the image to the desired size
        self.image_tk = ImageTk.PhotoImage(image,master=self.controller)  # Keep a reference to the image

        
        # Create the label with the image
        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, image=self.image_tk, text="")
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Bind the click event to the function
        self.navigation_frame_label.bind("<Button-1>", self.welcome_page)
        
        
        self.lesson_scroll_frame = customtkinter.CTkScrollableFrame(self.navigation_frame, corner_radius=0,height=600)
        self.lesson_scroll_frame.grid(row=1, column=0, sticky="s")
        self.lesson_scroll_frame.grid_columnconfigure(0, weight=1)
        self.lesson_scroll_frame.grid_rowconfigure(0, weight=1)
        # Add lesson buttons to navigation frame
        self.add_lesson_buttons()

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=2, column=0, padx=20, pady=20, sticky="s")


        self.home_container = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_container.grid_columnconfigure(0, weight=1)
        self.home_container.grid_rowconfigure(1, weight=1)  # Give weight to row 1 (home_frame)
        self.home_container.grid(row=0, column=1, sticky="nsew")
        
        self.toolbar = customtkinter.CTkFrame(self.home_container, height=50)
        self.toolbar.grid(row=0, column=0, sticky="ew")
        self.toolbar.grid_columnconfigure(0, weight=0)
        self.toolbar.grid_columnconfigure(1, weight=0)
        self.toolbar.grid_columnconfigure(2, weight=1)


        self.profile_button = customtkinter.CTkButton(self.toolbar, text="Hello "+ self.controller.user.name,command=lambda: self.my_profile_show_frame())
        self.profile_button.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")
        
        if(self.controller.user.admin):
            self.profile_button = customtkinter.CTkButton(self.toolbar, text="Admin Page",command=lambda: self.admin_show_frame())
            self.profile_button.grid(row=0, column=1,padx=(5, 10), pady=10, sticky="w")

        self.score_label = customtkinter.CTkLabel(self.toolbar, text="Score: "+ str(self.controller.user.total_score),font=("Helvetica", 14, "bold"))
        self.score_label.grid(row=0, column=2, padx=10, pady=10)

        self.signout_button = customtkinter.CTkButton(self.toolbar, text="Logout",command=self.controller.logout)
        self.signout_button.grid(row=0, column=3, padx=10, pady=10, sticky="e")
        
        # Create home frame
        self.home_frame = customtkinter.CTkFrame(self.home_container, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)
        #self.home_frame.grid_rowconfigure(0, weight=1)
        #self.home_frame.grid_rowconfigure(3, weight=1)
        self.home_frame.grid(row=1, column=0, sticky="nsew")

        
        self.welcome_page("")
        
        

    def admin_show_frame(self):
        
       self.controller.frames["Admin"].init_buttons_background()
       self.controller.show_frame("Admin")
        
    def my_profile_show_frame(self):
        
       self.controller.frames["MyProfile"].init_buttons_background()
       self.controller.show_frame("MyProfile")

    # creates button for each lesson
    def add_lesson_buttons(self):
        lessons = DB.get_all_lessons()
        completed_lessons = self.controller.user.completed_lessons  # Get the list of completed lessons
        
        # Extract lesson ObjectIds from completed lessons
        completed_lesson_ids = {str(lesson['lesson']) for lesson in completed_lessons}
        
        for idx, lesson in enumerate(lessons):
            # Convert lesson ObjectId to string for comparison
            lesson_id_str = str(lesson['_id'])
    
            # Create the button with a check mark if the lesson is completed
            if lesson_id_str in completed_lesson_ids:
                text = f"Lesson {idx + 1}                               ✔️"  # Add check mark to the button text
            else:
                text = f"Lesson {idx + 1}"
    
            lesson_button = customtkinter.CTkButton(
                self.lesson_scroll_frame, corner_radius=0, height=40, border_spacing=10,
                text=text, fg_color="transparent", text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"), anchor="w"
            )
            lesson_button.configure(command=lambda button=lesson_button, l=lesson: self.lesson_button_event(button, l))
            lesson_button.grid(row=idx + 1, column=0, sticky="ew")
            self.lesson_buttons.append(lesson_button)


    
    def set_button_focus_background(self,button):
        
        for btn in self.lesson_buttons:
            btn.configure(fg_color="transparent")  # Reset to original state
        
        self.last_button_clicked = button
        
        
        if(customtkinter.get_appearance_mode() == "Dark"):
            self.last_button_clicked.configure(fg_color="gray30")  # Change to active state
        else:
            self.last_button_clicked.configure(fg_color="gray70")  # Change to active state
        

    def lesson_button_event(self, button, lesson):
        # Handle the lesson button event here
        print(f"Selected lesson: {lesson['_id']}")
        # Update the frame or perform any actions needed for the selected lesson
        

        self.set_button_focus_background(button)
        
        self.show_lesson_details(lesson)

    # triggered when clicking on a lesson, shows the lesson details
    def show_lesson_details(self, lesson):
        # Example: Update home_frame with lesson details
        for widget in self.home_frame.winfo_children():
            widget.destroy()

        lesson_details_label = customtkinter.CTkLabel(self.home_frame, text=f"Lesson {lesson['lesson_number']}",font=("Helvetica",  24, "underline"))
        lesson_details_label.grid(row=0, column=0, padx=20, pady=10, sticky="s")
    
        lesson_content_text = ', '.join(lesson['lesson_content'])
        lesson_content_label = customtkinter.CTkLabel(self.home_frame, text=f"Lesson Content: {lesson_content_text}",font=("Helvetica", 16))
        lesson_content_label.grid(row=1, column=0, padx=20, pady=10, sticky="n")
        
        
        go_button = customtkinter.CTkButton(self.home_frame, text="Start Lesson!", fg_color="green", text_color="white",font=("Helvetica", 16))
        go_button.configure(command=lambda l=lesson, b=go_button: self.open_lesson_frame(l, b))
        go_button.grid(row=2, column=0, padx=20, pady=30, sticky="n")
        
        self.home_frame.grid(row=1, column=0, sticky="nsew")
    
    # create the ui for the welcome page, when the app is first opened
    def welcome_page(self, event):
        # Clear the home_frame of any existing widgets
        for widget in self.home_frame.winfo_children():
            widget.destroy()
    
        # Add the welcome message
        welcome_label = customtkinter.CTkLabel(self.home_frame, text_color="#00519F",text="Welcome to SignQuest!", font=("Arial", 30, "bold"))
        welcome_label.pack(pady=(40,0))
    
        # Add the introduction text
        intro_text = ("SignQuest is a teaching system that offers basic ASL lessons with live sign language recognition. "
                      "Our app leverages advanced machine learning to help you learn and practice American Sign Language "
                      "in an engaging and effective way. With high-accuracy gesture recognition, you'll be able to master "
                      "ASL at your own pace.\n\nStart your journey to better communication today!")
        intro_label = customtkinter.CTkLabel(self.home_frame, text=intro_text, wraplength=700,font=("Arial", 14), justify="left")
        intro_label.pack(pady=(20,0))
    

                                
        image_path = "images/hello.png"  # Replace with the path to your image
        image = Image.open(image_path)
        image = image.resize((300, 420), Image.ANTIALIAS)  # Resize the image to the desired size
        image_tk = ImageTk.PhotoImage(image,master=self.controller)  # Keep a reference to the image

        
        image_label = customtkinter.CTkLabel(self.home_frame, image=image_tk,text="")
        image_label.pack(side="right", padx=20, pady=5)

            

    def how_to_start(self):
        
        # Add the "How to Start" section title
        how_to_start_label = customtkinter.CTkLabel(self.home_frame,  text_color="#00519F",text="How to Start", font=("Arial", 24, "bold"))
        how_to_start_label.pack(pady=(20, 0))
        
    
        # Add the step-by-step instructions
        steps = [
            ("1. Choose a Lesson:", "Begin by selecting a lesson that interests you. Each lesson contains a set of ASL words that you'll practice through various types of exercises."),
            ("2. Exercise Types:", None),
            ("    Repeat the Sign:", "Watch a video of an ASL gesture and replicate it in front of your webcam. If performed correctly, you'll receive feedback and move on to the next exercise."),
            ("    Multiple Choice:", "View a gesture video and choose the matching English word from a list. Your selection will be checked, and feedback will guide you to the next exercise."),
            ("    Type the Matching Word:", "Watch an ASL gesture video and type the corresponding English word. Submit your answer to receive feedback and progress to the next exercise."),
            ("    Missing Word:", "Complete a sentence by identifying the missing word and performing the matching ASL gesture in front of the camera."),
            ("    Sentence Exercise:", "Perform a sequence of ASL gestures to match a given sentence. The required gestures will be listed, with the current gesture highlighted in blue."),
            ("3. Complete the Lesson:", "After finishing all exercises, your score will be calculated and displayed in the lesson summary. From there, you can return to the homepage and select your next lesson.")
        ]
    
        # Display the steps with bold text
        for title, description in steps:
            # Check if the title should be underlined
            if title.startswith("1.") or title.startswith("2.") or title.startswith("3."):
                title_font = ("Arial", 14, "bold", "underline")
                padding = 10
            else:
                title_font = ("Arial", 12, "bold")
                padding = 5
            
            title_label = customtkinter.CTkLabel(self.home_frame, text=title, font=title_font, anchor="w", padx=100, pady=padding)
            title_label.pack(anchor="w")

            if description:
                description_label = customtkinter.CTkLabel(self.home_frame, text=description, wraplength=700, justify="left", anchor="w", padx=130)
                description_label.pack(anchor="w")
        
    # triggered when clicking on a go button inside lesson, opens required the lesson.
    def open_lesson_frame(self, lesson, button):
        
        # Disable the button to prevent multiple clicks
        button.configure(state="disabled")
        
        # Hide the currently active lesson frame if it exists
        if self.active_lesson_frame is not None:
            self.active_lesson_frame.grid_forget()

        try: 
            exercise_data = DB.get_exercises_by_lesson_id(lesson['_id'])
            sorted_exercise_list = sorted(exercise_data, key=lambda x: x['exercise_number'])
            
            if(sorted_exercise_list):
                    
                self.controller.lesson.set_lesson_id(lesson['_id'])
                self.controller.lesson.set_exercises(sorted_exercise_list)
             
                next_frame = self.controller.lesson.exercises_types[sorted_exercise_list[0]["type"]]["screen"]
        
                self.controller.frames[next_frame].set_exercise_data(sorted_exercise_list[0])
                self.controller.show_frame(next_frame)
            
            else:
                messagebox.showinfo("No exercises", "Lesson has no exercises.")
        
        finally:
            # Re-enable the button after all operations are complete
            self.home_frame.after(1000, lambda: button.configure(state="normal"))
            #button.configure(state="normal")


    def change_appearance_mode_event(self, new_appearance_mode):
        
        customtkinter.set_appearance_mode(new_appearance_mode)
                
        if(self.last_button_clicked != None):
            self.set_button_focus_background(self.last_button_clicked)