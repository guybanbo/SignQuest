from db import DB
import os

class User:
    def __init__(self, controller):
        self.controller = controller
        self.name = "Firstname Lastname"
        self.email = "bla@gmail.com"
        self.id = "66768c47568f17afa85018dc"
        self.total_score = "200"
        self.admin = False
        self.completed_lessons = {}

    def set_total_score(self,total_score):
        self.total_score = total_score
        
        
    def set_user_details(self, data):
        self.name = data["name"]
        self.id = data["_id"]
        self.email = data["email"]
        self.admin = data.get("admin", False)  # Set admin to False if "admin" is not in data
            
            
    def get_user_details(self):
        return {
            "name": self.name,
            "email": self.email,
            "id": self.id,
            "total_score": self.total_score,
            "admin": self.admin
        }
    
    def get_completed_lessons(self):
        
        return DB.get_completed_lessons(self.id)
    
    def get_learned_words(self):
        
        return DB.get_learned_words(self.id)
    
    def change_password(self,current_password,new_password):
        
        return DB.change_password_db(self.id, current_password, new_password)
    
    def send_feedback(self,feedback,rating):
        
        return DB.save_user_feedback(self.id, feedback, rating)
    