import pymongo
from pymongo.errors import PyMongoError
from database import db
from response import response_handler


class EnrolmentsModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EnrolmentsModel, cls).__new__(cls)
            cls._instance.collection = db["enrolments"]
            cls._instance.collection.create_index(
                [
                    ("course_id", pymongo.ASCENDING),
                    ("student_email", pymongo.ASCENDING),
                ],
                unique=True,
            )
        return cls._instance

    def add_enrollments(self, course_id, student_emails):
        """
        Adds multiple students to a course in a single batch operation.
        :param course_id: The course ID to enroll students in.
        :param student_emails: List of student email addresses.
        :return: Dictionary summarizing the operation.
        """
        try:
            # Prepare enrollment documents
            enrollment_docs = [
                {
                    "course_id": course_id,
                    "student_email": f"{email.strip()}@e.ntu.edu.sg",
                    "enrolled": True,
                }
                for email in student_emails
            ]
            print(enrollment_docs)

            # Bulk insert (ignoring duplicates)
            insert_result = self.collection.bulk_write(
                [pymongo.InsertOne(doc) for doc in enrollment_docs], ordered=False
            )

            return response_handler(
                200, f"Successfully enrolled students in {course_id}."
            )

        except pymongo.errors.BulkWriteError as e:
            inserted_count = e.details["nInserted"]
            return response_handler(
                200,
                f"Enrolled {inserted_count} students, as some were already enrolled.",
            )

        except PyMongoError as e:
            return response_handler(
                500, "Database error while adding enrolments.", str(e)
            )

    def check_enrollment(self, course_id, student_email):
        """
        Checks if a student is enrolled in a given course.

        :param course_id: The course ID.
        :param student_email: The student's email address.
        :return: Dictionary with the enrollment status.
        """
        try:
            result = self.collection.find_one(
                {"course_id": course_id, "student_email": student_email}
            )

            if result:
                return response_handler(
                    200, f"Student {student_email} is enrolled in {course_id}."
                )
            else:
                return response_handler(
                    404, f"Student {student_email} is NOT enrolled in {course_id}."
                )

        except PyMongoError as e:
            return response_handler(
                500, "Database error while checking enrollment.", str(e)
            )

    def get_enrollments_by_user(self, user_email):
        """
        Retrieves all courses a user is enrolled in.

        :param user_email: The student's email address.
        :return: Dictionary where course_id is the key and details are the value.
        """
        try:
            # Query MongoDB to find all enrollments for the given user
            enrollments = self.collection.find({"student_email": user_email})

            # Convert cursor to dictionary with course_id as the key
            enrollments_dict = {
                enrollment["course_id"]: enrollment for enrollment in enrollments
            }
            print(enrollments_dict)

            return response_handler(
                200, "Enrollments retrieved successfully.", data=enrollments_dict
            )

        except PyMongoError as e:
            return response_handler(
                500, "Database error while fetching enrollments.", str(e)
            )

    def get_whitelisted_students(self, course_id):
        """
        Retrieves the list of students whitelisted (enrolled) in a specific course.
        :param course_id: The ID of the course.
        :return: List of student emails enrolled in the course.
        """
        try:
            students = list(
                self.collection.find(
                    {"course_id": course_id}, {"_id": 0, "student_email": 1}
                )
            )
            return response_handler(
                200, "OK", [student["student_email"] for student in students]
            )

        except PyMongoError as e:
            return response_handler(
                500, "Database error while fetching whitelisted students.", []
            )

    def remove_student_from_course(self, course_id, student_email):
        """
        Removes a student from the whitelist (unenrolls from a course).
        :param course_id: The course ID.
        :param student_email: The student's email address.
        :return: Response handler indicating success or failure.
        """
        try:
            result = self.collection.delete_one(
                {"course_id": course_id, "student_email": student_email}
            )

            if result.deleted_count > 0:
                return response_handler(
                    200, f"Successfully removed {student_email} from {course_id}."
                )
            return response_handler(
                404, f"Student {student_email} is not enrolled in {course_id}."
            )

        except PyMongoError as e:
            return response_handler(
                500, "Database error while removing student.", str(e)
            )
