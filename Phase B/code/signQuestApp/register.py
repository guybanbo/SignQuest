import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image
from db import DB
from PIL import Image, ImageTk
from tkinter import messagebox



class Register(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        
        image_path = "images/bg1.png"  # Replace with the path to your image
        image = Image.open(image_path)
        image = image.resize((700, 464), Image.ANTIALIAS)  # Resize the image if necessary
        self.bg_img = ImageTk.PhotoImage(image,master=self.controller)  # Keep a reference to the image
        

        #bg_img = ctk.CTkImage(light_image=Image.open("bg1.png"), dark_image=Image.open("bg1.png"), size=(700, 464))

        
        bg_frame = ctk.CTkFrame(self)
        bg_frame.configure(fg_color="#E6F3FF")
        bg_frame.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=1)
        
        # Create a label within the frame and fill it with the image
        bg_label = ctk.CTkLabel(bg_frame, image=self.bg_img, text="")
        bg_label.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)

        frame1 = ctk.CTkFrame(self, fg_color="white", bg_color="white", height=400, width=500, corner_radius=20)
        frame1.grid(row=0, column=1, sticky="nsew")
        
        frame1.grid_rowconfigure(0, weight=1)
        frame1.grid_columnconfigure(0, weight=1)
        
        frame2 = ctk.CTkFrame(frame1,fg_color="white", bg_color="white", height=400, width=500,corner_radius=20)
        frame2.grid_columnconfigure(0, weight=1)
        frame2.grid(row=0, column=0)
        

        
        frame2.grid_propagate(False)  # Prevent frame2 from resizing based on its content
        
        
        title = ctk.CTkLabel(frame2, text="Create Account", text_color="black", font=("", 35, "bold"))
        title.grid(row=0, column=0, sticky="nwe", pady=30, padx=10)
        
        self.name_entry = ctk.CTkEntry(frame2, text_color="white", placeholder_text="Name", fg_color="black",
                                       placeholder_text_color="white", font=("", 16, "bold"), width=200,
                                       corner_radius=15, height=45)
        self.name_entry.grid(row=1, column=0, sticky="nwe", padx=30)
        
        self.email_entry = ctk.CTkEntry(frame2, text_color="white", placeholder_text="Email", fg_color="black",
                                        placeholder_text_color="white", font=("", 16, "bold"), width=200,
                                        corner_radius=15, height=45)
        self.email_entry.grid(row=2, column=0, sticky="nwe", padx=30, pady=20)
        
        self.passwd_entry = ctk.CTkEntry(frame2, text_color="white", placeholder_text="Password", fg_color="black",
                                         placeholder_text_color="white", font=("", 16, "bold"), width=200,
                                         corner_radius=15, height=45, show="*")
        self.passwd_entry.grid(row=3, column=0, sticky="nwe", padx=30)
        
        reg_btn = ctk.CTkButton(frame2, text="Register", font=("", 15, "bold"), height=40, width=60,
                                fg_color="#0085FF", cursor="hand2", corner_radius=15, command=self.register)
        reg_btn.grid(row=4, column=0, sticky="nwe", pady=30, padx=30)
        
                
        cr_acc = ctk.CTkLabel(frame2, text="Already Registered? Login", text_color="black", cursor="hand2", font=("", 15))
        cr_acc.grid(row=5, column=0)
        
        # Bind the label to a click event
        cr_acc.bind("<Button-1>", lambda e: self.controller.show_frame("Login"))
    
    # register a new user, by collecting data from registration form and submit the data to the db.
    def register(self):
        # Retrieve user input from the entry fields
        name = self.name_entry.get()
        email = self.email_entry.get()
        password = self.passwd_entry.get()

        # Validate input (you might want to add more validation here)
        if not name or not email or not password:
            messagebox.showerror("Registration Failed", "Please fill in all fields.")
            return

        # Use DB class to register the user (assuming you have a function for that)
        success = DB.register_user(name, email, password)
        
        if success:
            messagebox.showinfo("Registration Successful", "Your account has been created!")
            self.controller.show_frame("Login")
        else:
            messagebox.showerror("Registration Failed", "An account with this email already exists.")
