from typing import Any, Text, Dict, List  # Importing necessary typing tools for type hints
from rasa_sdk import Action, Tracker  # Base classes for custom actions and tracking user interactions
from rasa_sdk.executor import CollectingDispatcher  # For sending responses back to the user
from rasa_sdk.events import SlotSet  # For setting slots in the conversation state
from utils.lms_utils import LMSManager  # Custom LMS utility for managing courses (assumed external module)

# Action to provide learning recommendations based on user input
class ActionProvideLearningRecommendations(Action):
    def __init__(self):
        # Initialize LMSManager instance for handling course-related operations
        super().__init__()
        self.lms = LMSManager()

    def name(self) -> Text:
        # Unique name for the action used in Rasa stories
        return "action_provide_learning_recommendations"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Main method to handle the user request:
        - Analyze user input
        - Generate personalized learning recommendations
        - Enroll user in courses
        """
        # Get the latest user message and user ID
        latest_message = tracker.latest_message['text'].lower()
        user_id = tracker.sender_id

        # Handle positive feedback
        if any(word in latest_message for word in ['helpful', 'thanks', 'good', 'great']):
            response = "I'm glad you found it helpful! You can type 'show my courses' to see your enrolled courses."
            dispatcher.utter_message(text=response)
            return []  # No slots to update

        # Initialize experience level and interest area
        experience = None
        interest = None

        # Determine experience level based on keywords
        if 'beginner' in latest_message:
            experience = 'beginner'
        elif 'intermediate' in latest_message:
            experience = 'intermediate'

        # Determine interest area based on keywords
        if 'data' in latest_message or 'science' in latest_message:
            interest = 'data science'
        elif 'web' in latest_message:
            interest = 'web development'
        elif 'mobile' in latest_message or 'app' in latest_message:
            interest = 'mobile apps'
        elif 'ai' in latest_message or 'artificial' in latest_message:
            interest = 'artificial intelligence'

        # If both experience and interest are provided, create a course recommendation
        if experience and interest:
            try:
                # Construct course name and description
                course_name = f"{interest.title()} for {experience.title()}s"
                description = f"A curated learning path for {experience}s in {interest}"

                # Define learning materials based on interest
                materials_dict = {
                    'data science': [
                        {"name": "Coursera Python for Everybody", "url": "https://www.coursera.org/specializations/python"},
                        {"name": "DataCamp Introduction to Python", "url": "https://www.datacamp.com/courses/intro-to-python-for-data-science"}
                    ],
                    'web development': [
                        {"name": "freeCodeCamp Web Development", "url": "https://www.freecodecamp.org/learn/responsive-web-design/"},
                        {"name": "MDN Web Docs", "url": "https://developer.mozilla.org/en-US/docs/Learn"},
                        {"name": "The Odin Project", "url": "https://www.theodinproject.com/"}
                    ],
                    'mobile apps': [
                        {"name": "Android Developer Fundamentals", "url": "https://developer.android.com/courses"},
                        {"name": "iOS App Development with Swift", "url": "https://developer.apple.com/tutorials/swiftui"},
                        {"name": "React Native Tutorial", "url": "https://reactnative.dev/docs/tutorial"}
                    ],
                    'artificial intelligence': [
                        {"name": "Fast.ai - Practical Deep Learning", "url": "https://www.fast.ai/"},
                        {"name": "Coursera Machine Learning Specialization", "url": "https://www.coursera.org/specializations/machine-learning-introduction"},
                        {"name": "DeepLearning.AI", "url": "https://www.deeplearning.ai/"},
                        {"name": "Google AI Education", "url": "https://ai.google/education/"}
                    ]
                }

                # Retrieve materials for the interest area
                materials = materials_dict.get(interest.lower(), [])

                # Create the course and enroll the user
                course_id = self.lms.create_course(course_name, description, materials)

                if course_id:
                    self.lms.enroll_user(user_id, course_id)
                    response = f"🎉 Welcome to {course_name}!\n\nHere are your learning materials:\n\n"
                    for material in materials:
                        response += f"📚 {material['name']}\n{material['url']}\n\n"
                    response += "Type 'show my courses' anytime to see your enrolled courses!"
                else:
                    response = "I'm having trouble setting up your course. Please try again."
            except Exception as e:
                response = "I encountered an error while setting up your course. Please try again."
        else:
            # Prompt user to provide both experience and interest
            response = "Please provide both your experience level and coding interest. For example: 'I'm a beginner interested in data science'."

        dispatcher.utter_message(text=response)
        return [SlotSet("experience_level", experience), SlotSet("coding_interest", interest)]


# Action to show user's enrolled courses
class ActionShowEnrollments(Action):
    def __init__(self):
        # Initialize LMSManager instance for retrieving course information
        super().__init__()
        self.lms = LMSManager()

    def name(self) -> Text:
        # Unique name for the action used in Rasa stories
        return "action_show_enrollments"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Main method to retrieve and display user's enrolled courses.
        """
        try:
            user_id = tracker.sender_id
            courses = self.lms.get_user_courses(user_id)

            if courses:
                response = "Here are your enrolled courses:\n\n"
                for course in courses:
                    response += f"📚 {course['name']}\nStatus: {course['status']}\nEnrolled: {course['enrolled_at'][:10]}\n\n"
            else:
                response = "You're not enrolled in any courses yet. Would you like some recommendations?"

            dispatcher.utter_message(text=response)
        except Exception as e:
            dispatcher.utter_message(text="Sorry, I encountered an error while retrieving your courses.")

        return []
