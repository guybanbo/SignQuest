from db import DB

# class for the enitity lesson

class Lesson:
    def __init__(self, controller):
        self.controller = controller
        self.exercises = []
        self.scores = []
        self.current_exercise = 0
        self.lesson_id = ""
        self.lesson_number = 0
        self.exercises_types = {
            0: {"screen": "InstructionExercise", "name": "Instruction Exercise"},
            1: {"screen": "MultipleChoiceExercise", "name": "Multiple Choice Exercise"},
            2: {"screen": "OpenQuestion", "name": "Open Question"},
            3: {"screen": "CompleteSentenceByGesture", "name": "Complete Sentence by Gesture"},
            4: {"screen": "SentenceGesture", "name": "Sentence Gesture"}
        }
        

    def set_lesson_id(self,lesson_id):
        self.lesson_id = lesson_id
        
    def get_lesson_id(self):
        return self.lesson_id
    
    # calcuate lesson score
    def calculate_score(self):
        correct_answers = sum(self.scores)
        total_exercises = len(self.scores)
        if total_exercises == 0:
            score_percentage = 0.0
        else:
            score_percentage = (correct_answers / total_exercises)
            
        return score_percentage

    def back_to_home(self):
        self.current_exercise = 0
        self.controller.show_frame("Homepage")
        
    # when user finishes lesson, save and show lesson's score
    def finish_lesson(self):
        total_score = self.calculate_score()
        print("lesson finished, your score:",self.scores,"total score:",total_score)
        
        if(not(DB.save_user_lesson(self.controller.user.id, self.lesson_id, total_score))):
            print("Failed to insert/update user's score")
                           
        self.current_exercise = 0
        self.controller.recreate_lesson_pages()
        self.controller.frames["LessonScorePage"].resume()
        self.controller.show_frame("LessonScorePage")
        
    def set_exercises(self,exercises):
        self.exercises = sorted(exercises, key=lambda x: x['exercise_number'])
        self.scores = [0]*len(self.exercises) 
        
    def get_exercises(self):
        return self.exercises
        
    '''
    
        Advances to the next exercise in a sequence, updates the score for the current exercise, and handles 
        transitions between exercises based on their type.
        
        Parameters:
        - score: The score obtained for the current exercise.
    
    '''
    def next_exercise(self,score):
        self.scores[self.current_exercise] = score
        self.current_exercise += 1
        if(self.current_exercise == len(self.exercises)):
            return self.finish_lesson()
        next_exer_type = self.exercises[self.current_exercise]["type"]
        next_exer_name = self.exercises_types[next_exer_type]["screen"]
      
    
        if(next_exer_type == self.exercises[self.current_exercise-1]["type"]):
            self.controller.recreate_page_by_name(next_exer_name)
        self.controller.frames[next_exer_name].set_exercise_data(self.exercises[self.current_exercise])
        self.controller.show_frame(next_exer_name)
        
        