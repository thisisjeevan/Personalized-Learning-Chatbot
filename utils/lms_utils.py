import json
import os
from datetime import datetime

# Singleton class to manage Learning Management System data
class LMSManager:
    _instance = None
    _data = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LMSManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.data_file = os.path.join(os.getcwd(), "lms_data.json")
        print(f"LMS data file path: {self.data_file}")  # Debug print
        self.load_data()

    def load_data(self):
        # Loads LMS data from JSON file or creates new structure if not exists
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    LMSManager._data = json.load(f)
                    print(f"Loaded existing data: {LMSManager._data}")  # Debug print
            else:
                LMSManager._data = {
                    'users': {},
                    'courses': {},
                    'enrollments': {}
                }
                self.save_data()
                print("Created new data file")  # Debug print
        except Exception as e:
            print(f"Error loading data: {e}")  # Debug print
            LMSManager._data = {
                'users': {},
                'courses': {},
                'enrollments': {}
            }

    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(LMSManager._data, f, indent=2)
            print(f"Saved data: {LMSManager._data}")  # Debug print
        except Exception as e:
            print(f"Error saving data: {e}")  # Debug print

    def create_course(self, course_name, description, materials):
        # Creates a new course with unique ID and metadata
        try:
            course_id = str(len(LMSManager._data['courses']) + 1)
            LMSManager._data['courses'][course_id] = {
                'name': course_name,
                'description': description,
                'materials': materials,
                'created_at': datetime.now().isoformat()
            }
            print(f"Created course {course_id}: {course_name}")  # Debug print
            self.save_data()
            return course_id
        except Exception as e:
            print(f"Error creating course: {e}")  # Debug print
            return None

    def enroll_user(self, user_id, course_id):
        # Enrolls a user in a specific course and initializes progress tracking
        try:
            if course_id not in LMSManager._data['courses']:
                print(f"Course {course_id} not found")  # Debug print
                return False
            
            if user_id not in LMSManager._data['users']:
                LMSManager._data['users'][user_id] = {
                    'enrolled_courses': [],
                    'progress': {}
                }

            if course_id not in LMSManager._data['users'][user_id]['enrolled_courses']:
                LMSManager._data['users'][user_id]['enrolled_courses'].append(course_id)
                LMSManager._data['users'][user_id]['progress'][course_id] = {
                    'status': 'enrolled',
                    'completed_materials': [],
                    'enrolled_at': datetime.now().isoformat()
                }
                print(f"Enrolled user {user_id} in course {course_id}")  # Debug print
                self.save_data()
            return True
        except Exception as e:
            print(f"Error enrolling user: {e}")  # Debug print
            return False

    def get_user_courses(self, user_id):
        # Retrieves all courses enrolled by a specific user with their progress
        try:
            print(f"Getting courses for user {user_id}")  # Debug print
            print(f"Current data: {LMSManager._data}")  # Debug print
            
            if user_id not in LMSManager._data['users']:
                print(f"User {user_id} not found in {LMSManager._data['users'].keys()}")  # Debug print
                return []
            
            courses = []
            for course_id in LMSManager._data['users'][user_id]['enrolled_courses']:
                course = LMSManager._data['courses'].get(course_id, {})
                progress = LMSManager._data['users'][user_id]['progress'].get(course_id, {})
                courses.append({
                    'course_id': course_id,
                    'name': course.get('name'),
                    'description': course.get('description'),
                    'status': progress.get('status'),
                    'enrolled_at': progress.get('enrolled_at')
                })
            print(f"Found courses: {courses}")  # Debug print
            return courses
        except Exception as e:
            print(f"Error getting user courses: {e}")  # Debug print
            return [] 