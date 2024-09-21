import customtkinter as ctk
from tkVideoPlayer import TkinterVideo
from tkinter import messagebox
from tkinter import Canvas
import tkinter as tk

# class for the frame "Lesson score" that appears when the user finish a lesson
class LessonScorePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        
    def resume(self):
        self.setup_ui()
        self.display_score()
        
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        
        self.title_label = ctk.CTkLabel(self, text="Lesson Completed!", font=("Helvetica", 24))
        self.title_label.grid(row=0, column=0,  pady=(50, 10),padx=20)
        
        self.light_mode_Gray81 = "#cfcfcf"
        self.dark_mode_gray20 = "#333333"
        self.bg_color = self.light_mode_Gray81
        self.gauge_text_color = "#000000"
        
        print(ctk.get_appearance_mode())
        
        if(ctk.get_appearance_mode() == "Dark"):
            self.bg_color = self.dark_mode_gray20
            self.gauge_text_color = "white"
        
        self.canvas = Canvas(self, width=200, height=200, bg=self.bg_color, highlightthickness=0)
        self.canvas.grid(row=1, column=0, pady=10, padx=20)
        
        self.score_label = ctk.CTkLabel(self, text="", font=("Helvetica", 20))
        self.score_label.grid(row=2, column=0, padx=20)
        
        self.restart_button = ctk.CTkButton(self, text="Return to homepage", command=self.restart_lesson)
        self.restart_button.grid(row=3, column=0, pady=10, padx=20)
        

    # shows the score to the user with score gauge, a percent of successfully completed exercises
    def display_score(self):

        score_percentage = self.controller.lesson.calculate_score() * 100
        
        self.score_label.configure(text=f"Your Score: {score_percentage:.2f}%")
        
        self.draw_gauge(score_percentage)


    def draw_gauge(self, score_percentage):
        self.canvas.delete("all")
        
        start_angle = -90  # Starting from the top
        extent_angle = (score_percentage / 100) * 360  # How much of the circle to fill
        
        if score_percentage == 100:
            extent_angle = 359.9
            

        # Draw background circle
        self.canvas.create_oval(10, 10, 190, 190, outline="#f0f0f0", width=20)
        
        # Draw foreground arc (green color for the filled portion)
        self.canvas.create_arc(10, 10, 190, 190, start=start_angle, extent=extent_angle, outline="#4caf50", width=20, style=tk.ARC)
         
        # Draw text in the center
        self.canvas.create_text(100, 100, text=f"{score_percentage:.2f}%", font=("Helvetica", 16), fill=self.gauge_text_color)

    def restart_lesson(self):
        self.controller.show_frame("Homepage")  # Assuming there's a method to show the lesson page
