import streamlit as st
from models.courses_model import CoursesModel
from models.enrolments_model import EnrolmentsModel

class CoursesController:
    """Handles logic for displaying courses"""

    def __init__(self):
        self.course_model = CoursesModel()
        self.enrollment_model = EnrolmentsModel()


    def get_courses(self):
        """Retrieves all available courses from the database."""
        courses_response = self.course_model.get_courses()
        if courses_response["code"] == 200:
            return courses_response["data"]
        else:
            st.error("No courses available.")
            return []


    def get_student_enrollments(self, user_email):
        """Retrieves courses a student is enrolled in."""
        enrollments_response = self.enrollment_model.get_enrollments_by_user(user_email)
        if enrollments_response["code"] == 200:
            return enrollments_response["data"]
        else:
            return []

    def add_new_course(self, course_id, course_name):
        """Handles adding a new course."""
        return self.course_model.add_course(course_id.strip(), course_name.strip())