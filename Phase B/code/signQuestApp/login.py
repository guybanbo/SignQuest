import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image
from db import DB
from PIL import Image, ImageTk
from tkinter import messagebox


class Login(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        
        
        image_path = "images/bg1.png"  # Replace with the path to your image
        image = Image.open(image_path)
        image = image.resize((700, 464), Image.ANTIALIAS)  # Resize the image if necessary
        self.bg_img = ImageTk.PhotoImage(image,master=self.controller)  # Keep a reference to the image
        

        # Create a frame to hold the background image
        bg_frame = ctk.CTkFrame(self)
        bg_frame.configure(fg_color="#E6F3FF")
        bg_frame.grid(row=0, column=0, sticky="nsew")  # Use sticky to make the frame fill its cell

        # Configure grid to expand
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=1)

        # Create a label within the frame and fill it with the image
        bg_label = ctk.CTkLabel(bg_frame, image=self.bg_img, text="")
        bg_label.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)

        
        frame1 = ctk.CTkFrame(self,fg_color="white", bg_color="white", height=350, width=500,corner_radius=20)
        frame1.grid(row=0, column=1, sticky="nsew")
        
        frame1.grid_rowconfigure(0, weight=1)
        frame1.grid_columnconfigure(0, weight=1)
        
        frame2 = ctk.CTkFrame(frame1,fg_color="white", bg_color="white", height=350, width=500,corner_radius=20)
        frame2.grid(row=0, column=1)
        
        frame2.grid_propagate(False)  # Prevent frame2 from resizing based on its content

        
        title = ctk.CTkLabel(frame2,text="Welcome Back! \nLogin to Account",text_color="black",font=("",35,"bold"))
        title.grid(row=0,column=0,sticky="nw",pady=30,padx=10)
        
        self.usrname_entry = ctk.CTkEntry(frame2,text_color="white", placeholder_text="Email", fg_color="black", placeholder_text_color="white",
                                 font=("",16,"bold"), width=200, corner_radius=15, height=45)
        self.usrname_entry.grid(row=1,column=0,sticky="nwe",padx=30)
        
        self.passwd_entry = ctk.CTkEntry(frame2,text_color="white",placeholder_text="Password",fg_color="black",placeholder_text_color="white",
                                 font=("",16,"bold"), width=200,corner_radius=15, height=45, show="*")
        self.passwd_entry.grid(row=2,column=0,sticky="nwe",padx=30,pady=20)
        
        cr_acc = ctk.CTkLabel(frame2, text="Create Account!", text_color="black", cursor="hand2", font=("", 15))
        cr_acc.grid(row=3, column=0, sticky="w", pady=20, padx=40)
        
        # Bind the label to a click event
        cr_acc.bind("<Button-1>", lambda e: self.controller.show_frame("Register"))

        
        l_btn = ctk.CTkButton(frame2,text="Login",font=("",15,"bold"),height=40,width=60,fg_color="#0085FF",cursor="hand2",
                          corner_radius=15,command=self.login)
        l_btn.grid(row=3,column=0,sticky="ne",pady=20, padx=35)
        
    # collect the email and password and valiate the creditials, on success saves an encrypted credentials on the users pc
    def login(self):
        # Retrieve username and password from the entry fields
        email = self.usrname_entry.get()
        password = self.passwd_entry.get()
    
        # Use the updated validate_login function to check the credentials
        is_valid, user_details = DB.validate_login(email, password, False)
        
        if is_valid:
            messagebox.showinfo("Login Successful", f"Welcome back, {user_details['name']}!")
         
            self.save_credentials(email, password)
            
            
            self.controller.user.set_user_details(user_details)
            completion_percentage, completed_lessons, total_score = DB.get_completed_lessons(self.controller.user.id)
            if completed_lessons:
                self.controller.user.completed_lessons = completed_lessons
                self.controller.user.set_total_score(total_score)
                
            print(self.controller.user.name)
            self.controller.recreate_lesson_pages("Login")
            print(self.controller.user.name)
            self.controller.show_frame("Homepage")
            # You can now use the user_details for other purposes, such as personalization
            # For example, you might store them in a session variable or display them somewhere in the UI
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.")

    def save_credentials(self, email, password):
        # Save credentials to a text file (for demonstration purposes)
        with open("credentials.txt", "w") as file:
            file.write(f"Username: {email}\n")
            file.write(f"Password: {DB.hash_password(password)}\n")
