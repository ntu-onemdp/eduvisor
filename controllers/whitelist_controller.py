import pandas as pd
from models.enrolments_model import EnrolmentsModel
from models.courses_model import CoursesModel
from services.whitelist_file_processor_service import WhitelistFileProcessor

class WhitelistController:
    """Handles student whitelist operations."""

    def __init__(self):
        self.enrollment_model = EnrolmentsModel()
        self.course_model = CoursesModel()
    
    def check_course_exists(self, course_id):
        return self.course_model.course_exists(course_id)

    def get_whitelisted_students(self, course_id):
        """Fetches all whitelisted students for a given course."""
        return self.enrollment_model.get_whitelisted_students(course_id)

    def remove_student(self, course_id, student_email):
        """Removes a student from the whitelist."""
        return self.enrollment_model.remove_student_from_course(course_id, student_email)
    
    def add_students(self, course_id, student_emails):
        return self.enrollment_model.add_enrollments( course_id, student_emails)
    
    def process_whitelist_file(self, uploaded_file):
        """Processes and uploads a whitelist CSV file."""
        return WhitelistFileProcessor.extract_emails_from_file(uploaded_file)
    
        
        


