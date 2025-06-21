import pymongo
from pymongo.errors import PyMongoError
from database import db
from response import response_handler

class CoursesModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CoursesModel, cls).__new__(cls)
            cls._instance.collection = db["courses"]
        return cls._instance
    
    def course_exists(self, course_id):
        """
        Checks if a course exists in the database.
        :param course_id: The ID of the course to check.
        :return: Response handler indicating if the course exists.
        """
        try:
            exists = self.collection.find_one({"course_id": course_id}) is not None
            if exists:
                return response_handler(200, "Course exists.")
            return response_handler(404, "Course not found.")
        except PyMongoError as e:
            return response_handler(500, "Database error while checking course existence.", str(e))


    def get_courses(self):
        """Fetches all available courses."""
        try:
            courses = list(self.collection.find({}, {"_id": 0, "course_id": 1, "course_name": 1}))
            if courses:
                return response_handler(200, "OK", courses)
            return response_handler(404, "No Courses Found", [])
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))
    def add_course(self, course_id, course_name):
        """Adds a new course to the database while ensuring no duplicate course_id."""
        try:
            # Check if course ID already exists
            if self.collection.find_one({"course_id": course_id}):
                return response_handler(400, "Course ID already exists.")

            # Insert new course
            self.collection.insert_one({"course_id": course_id, "course_name": course_name})
            return response_handler(200, "Course added successfully.")
        
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))