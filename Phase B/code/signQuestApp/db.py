from pymongo.mongo_client import MongoClient
from bson import ObjectId
import hashlib
from datetime import datetime
from pytz import timezone



uri = "mongodb+srv://elior676:M7unu629ia9Rdnkm@cluster0.z9v1smd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# Create a new client and connect to the server
client = MongoClient(uri)

# Select the database
db = client["signQuest"]


    
class DB():
    
    
    def update_lesson_content(lesson_id, new_lesson_content):
        try:
            # Select the collection
            collection = db["lessons"]
            
            # Create the filter and update documents
            filter_query = {"_id": ObjectId(lesson_id)}
            update_query = {"$set": {"lesson_content": new_lesson_content}}
            
            # Perform the update
            result = collection.update_one(filter_query, update_query)
            
            # Check if any document was modified
            if result.modified_count > 0:
                return True
            else:
                return False
        except Exception as e:
            # Log the exception or handle it as needed
            print("An error occurred:", e)
            return False
    
    def create_lesson(lesson_content):
        try:
            # Select the collection
            collection = db["lessons"]
            
            # Get the latest lesson number
            latest_lesson = collection.find_one(sort=[("lesson_number", -1)])
            latest_lesson_number = latest_lesson["lesson_number"] if latest_lesson else 0
            
            # Create the new lesson document
            new_lesson = {
                "lesson_number": latest_lesson_number + 1,
                "lesson_content": lesson_content
            }
            
            # Insert the new lesson into the collection
            result = collection.insert_one(new_lesson)
            
            # Return True if the insert was successful
            return result.acknowledged
        except Exception as e:
            # Log the exception or handle it as needed
            print("An error occurred:", e)
            return False
    
    
    def get_all_lessons():
        
         # Select the collection
         collection = db["lessons"]
     
         # Retrieve all lessons from the collection
         lessons = list(collection.find({}))
     
         # Close the connection
         #client.close()
     
         return lessons
            
    def get_lessons_pagination(number_of_items, page):
        # Select the collection
        collection = db["lessons"]
        
        # Calculate the number of items to skip based on the current page
        skip_items = (page - 1) * number_of_items
        
        # Retrieve total count of lessons
        total_lessons_db = collection.count_documents({})
        
        # Retrieve lessons with pagination
        lessons = list(collection.find({}).skip(skip_items).limit(number_of_items))
        
        # Close the connection if necessary (optional)
        # client.close()
        
        return lessons, total_lessons_db
    
    def hide_exercise(exercise_id):
        """
        Sets the 'hidden' field of an exercise to 1.
        If the 'hidden' field doesn't exist, it will be added and set to 1.
        
        :param exercise_id: The _id of the exercise to update (should be a string or ObjectId)
        :return: True if the exercise was successfully hidden, False otherwise
        """
        try:
            # Select the collection
            collection = db["exercises"]
            
            # Convert the exercise_id to ObjectId if it's a string
            if isinstance(exercise_id, str):
                exercise_id = ObjectId(exercise_id)
            
            # Update the document: set the 'hidden' field to 1
            result = collection.update_one(
                {"_id": exercise_id},
                {"$set": {"hidden": 1}}
            )
            
            # Return True if the document was modified, False otherwise
            return result.modified_count > 0
    
        except Exception as e:
            # Log the exception if needed
            print(f"An error occurred: {e}")
            
            # Return False if any exception occurs
            return False
    
    def get_exercises(number_of_items, page):
        # Select the collection
        collection = db["exercises"]
        
        # Count the total number of exercises
        total_count = collection.count_documents({})
        
        # Calculate the number of items to skip based on the current page
        skip_items = (page - 1) * number_of_items
        
        # Retrieve exercises with pagination
        exercises = list(collection.find({}).skip(skip_items).limit(number_of_items))
        
        # Filter exercises locally: only include those where 'hidden' is 0 or doesn't exist
        filtered_exercises = [exercise for exercise in exercises if exercise.get('hidden', 0) == 0]
        
        # Call the get_all_lessons function to retrieve all lessons
        lessons = DB.get_all_lessons()
        
        # Create a dictionary to map lesson_id to lesson_number
        lesson_map = {lesson['_id']: lesson['lesson_number'] for lesson in lessons}
        
        # Add lesson_number to each exercise
        for exercise in filtered_exercises:
            lesson_id = exercise.get('lesson_id')
            if lesson_id and ObjectId(lesson_id) in lesson_map:
                exercise['lesson_number'] = lesson_map[ObjectId(lesson_id)]
        
        return filtered_exercises, total_count
    
    def get_exercises_by_id(exercise_id):
        try:
            # Select the collection
            collection = db["exercises"]
            
            # Retrieve the exercise by its ID
            exercises = list(collection.find({"_id": ObjectId(exercise_id)}))
            
            # Filter exercises locally: only include those where 'hidden' is 0 or doesn't exist
            filtered_exercises = [exercise for exercise in exercises if exercise.get('hidden', 0) == 0]
        
            return filtered_exercises
        
        except Exception as e:
            # Log the exception if needed
            print(f"An error occurred: {e}")
            
            # Return an empty list if something goes wrong
            return []
    
        
    def get_exercises_by_lesson_id(lesson_id):
        try:
            # Select the collection
            collection = db["exercises"]
            
            # Retrieve exercises by lesson ID
            exercises = list(collection.find({"lesson_id": ObjectId(lesson_id)}))

            
            # Filter exercises locally: only include those where 'hidden' is 0 or doesn't exist
            filtered_exercises = [exercise for exercise in exercises if exercise.get('hidden', 0) == 0]
            
            return filtered_exercises
        
        except Exception as e:
            # Log the exception if needed
            print(f"An error occurred: {e}")
            
            # Return an empty list if something goes wrong
            return []
    
        
    def submit_exercise(exercise_data):
        try:
            # Select the collections
            exercises_collection = db["exercises"]
            lessons_collection = db["lessons"]
            
            # Ensure lesson_number is provided
            if "lesson_number" in exercise_data:
                # Find the lesson document by lesson_number
                lesson = lessons_collection.find_one({"lesson_number": exercise_data["lesson_number"]})
                
                if lesson:
                    # Set the lesson_id from the found lesson
                    exercise_data["lesson_id"] = lesson["_id"]
                else:
                    # Handle case where lesson_number is not found
                    print(f"Lesson with number {exercise_data['lesson_number']} not found.")
                    return False
            
            # Ensure lesson_id is an ObjectId
            if "lesson_id" in exercise_data:
                exercise_data["lesson_id"] = ObjectId(exercise_data["lesson_id"])
            
            # Transform comma-separated strings into arrays for relevant fields
            for key, value in exercise_data.items():
                if isinstance(value, str) and ',' in value:
                    exercise_data[key] = value.split(',')
            
            # Insert the document into the collection
            result = exercises_collection.insert_one(exercise_data)
            
            return True
    
        except Exception as e:
            # Log the exception if needed
            print(f"An error occurred: {e}")
            
            # Return False if insertion fails
            return False
        
        
    def update_exercise(exercise_id, updated_data):
        try:
            # Select the collection where exercises are stored
            collection = db["exercises"]
            
            # Query to find the exercise by its unique ID
            query = {"_id": ObjectId(exercise_id)}
            
            # Update the exercise with the new data
            update = {
                "$set": updated_data
            }
            
            # Perform the update operation
            result = collection.update_one(query, update)
            
            # Check if the update was successful
            if result.modified_count > 0:
                return True
            else:
                return False
        
        except Exception as e:
            # Log the exception if needed
            print(f"An error occurred: {e}")
            
            # Return False if the update fails
            return False
    
    def save_user_lesson(user_id, lesson_id, score):

        try:
            # Select the collection
            collection = db["user_lesson"]
            
            query = {"user_id": ObjectId(user_id), "lesson": ObjectId(lesson_id)}
            update = {"$set": {"score": score}}
            
            # Upsert the document: update if exists, otherwise insert
            result = collection.update_one(query, update, upsert=True)
            
            return True
 
        except Exception as e:
            # Log the exception if needed
            print(f"An error occurred: {e}")
            
            # Return False if insertion fails
            return False
        
    def get_password_hash(user_id):
        user_collection = db["users"]
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        return user["password"]
    
    def get_password_hash_by_email(email):
            users_collection = db["users"]
            user = users_collection.find_one({"email": email})
            if user:
                return user.get("password")  # Assuming the password hash is stored under the "password" field
            return None

    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    def change_password_db(user_id, current_password, new_password):
    
        try:
            current_password_hash_entry = DB.hash_password(current_password)
            current_password_hash_db = DB.get_password_hash(user_id)
            
            if current_password_hash_entry == current_password_hash_db:
                new_password_hash = DB.hash_password(new_password)
                user_collection = db["users"]
                user_collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"password": new_password_hash}}
                )
                return True
            
            else:
                return False
            
        except Exception as e:
            return False
        
    def update_user_name_db(user_id, new_name):
        try:
            user_collection = db["users"]
            result = user_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"name": new_name}}
            )
            
            if result.matched_count > 0:
                return True  # Successfully updated the name
            else:
                return False  # User not found
            
        except Exception as e:
            return False  # Handle exceptions as needed
        
    def get_user_details_by_email(email):
        users_collection = db["users"]
        user = users_collection.find_one({"email": email})
        
        if user:
            # Optionally remove the password field if you don't want to return it
            user.pop("password", None)
            return user
        
        return None
        
        
    def validate_login(email, password, hashed):
        try:
            # Retrieve the stored password hash from the database using the email
            stored_password_hash = DB.get_password_hash_by_email(email)
            entered_password_hash = password
            
            # Hash the entered password
            if(not hashed):
                entered_password_hash = DB.hash_password(password)
            
            print()
            
            # Compare the stored hash with the entered hash
            if entered_password_hash == stored_password_hash:
                # Retrieve additional user details after successful login
                user_details = DB.get_user_details_by_email(email)
                return True, user_details
            else:
                return False, None
        except Exception as e:
            print(f"Error during login validation: {e}")
            return False, None
        
  
    def get_completed_lessons(user_id):
        try:
            # Retrieve all lessons from the "lessons" collection
            all_lessons = db["lessons"].count_documents({})
            
            if all_lessons == 0:
                return 0, [], 0  # Avoid division by zero if there are no lessons
            
            # Retrieve the completed lessons for the user from the "user_lesson" collection
            completed_lessons_cursor = db["user_lesson"].find({"user_id": ObjectId(user_id)})
            completed_lessons = list(completed_lessons_cursor)
            
            # Get all lessons to map lesson_id to lesson_number
            all_lessons_list = DB.get_all_lessons()
            lesson_map = {lesson['_id']: lesson['lesson_number'] for lesson in all_lessons_list}
            
            # Add the lesson_number to each completed lesson
            for lesson in completed_lessons:
                lesson_id = lesson.get('lesson')
                if lesson_id and lesson_id in lesson_map:
                    lesson['lesson_number'] = lesson_map[lesson_id]
            
            # Calculate the percentage of completed lessons
            completion_percentage = (len(completed_lessons) / all_lessons) * 100
            
            # Sum the scores from the completed lessons
            total_score = int(sum(lesson.get("score", 0) for lesson in completed_lessons) * 100)
            
            return completion_percentage, completed_lessons, total_score
        
        except Exception as e:
            # Log the exception if needed
            print(f"An error occurred: {e}")
            return None, [], 0  # Return None, an empty list, and 0 score if an error occurs

    def get_learned_words(user_id):
        try:
            # Retrieve the completed lessons for the user from the "user_lesson" collection
            completed_lessons = db["user_lesson"].find({"user_id": ObjectId(user_id)})
    
            # Retrieve all lessons from the "lessons" collection
            all_lessons = list(db["lessons"].find({}))
    
            # Create a dictionary to map lesson IDs to lesson content
            lesson_content_map = {lesson["_id"]: lesson.get("lesson_content", []) for lesson in all_lessons}
            
       
            
            learned_words_set = set()
            
            print(lesson_content_map)
    
            # For each completed lesson, retrieve the lesson content from the dictionary
            for user_lesson in completed_lessons:
                lesson_id = user_lesson["lesson"]
                if lesson_id in lesson_content_map:
                    learned_words_set.update(lesson_content_map[lesson_id])
    
            # Count the number of unique learned words
            number_of_learned_words = len(learned_words_set)
    
            print(learned_words_set)
            return number_of_learned_words
    
        except Exception as e:
            # Log the exception if needed
            print(f"An error occurred: {e}")
            return None  # Return None if an error occurs
        
        
    def save_user_feedback(user_id, feedback, rating):
        try:
            
            # Select the collection
            collection = db["feedbacks"]
               
            query = {"user_id": ObjectId(user_id)}
            update = {
                "$set": {
                    "feedback": feedback,
                    "rating": rating,
                    "date": datetime.now()
                }
            }
            
            # Upsert the document: update if exists, otherwise insert
            result = collection.update_one(query, update, upsert=True)
            
            return True
    
        except Exception as e:
            # Log the exception if needed
            print(f"An error occurred: {e}")
            
            # Return False if insertion fails
            return False
            
    def get_user_feedback(user_id=None):
        try:
            # Select the collection
            collection = db["feedbacks"]
            
            if user_id:
                # Query for feedback by a specific user
                query = {"user_id": ObjectId(user_id)}
            else:
                # Retrieve all feedbacks if no user_id is provided
                query = {}
            
            # Find the documents that match the query
            feedbacks = collection.find(query)
            
            # Convert the cursor to a list of feedbacks
            feedback_list = list(feedbacks)
            
            return feedback_list
        
        except Exception as e:
            # Log the exception if needed
            print(f"An error occurred: {e}")
            
            # Return None if retrieval fails
            return None
        
    def register_user(name, email, password):
        users_collection = db["users"]
        
        # Check if the email already exists
        if DB.get_user_details_by_email(email):
            return False  # Email already exists
        
        # Hash the password
        hashed_password = DB.hash_password(password)
        
        # Create a new user document
        new_user = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "total_score": 0
        }
        
        # Insert the new user into the database
        users_collection.insert_one(new_user)
        
        return True  # Registration successful
        