import pymongo
from datetime import datetime
from pymongo.errors import PyMongoError
from database import db
from response import response_handler


class AdminModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AdminModel, cls).__new__(cls)
            cls._instance.collection = db["admin_requests"]
            cls._users_collection = db["users"]
        return cls._instance

    def create_admin_request(self, user_id, email, reason):
        """Creates a new admin access request."""
        try:
            # Check if a request already exists for the user_id
            existing_request = self.collection.find_one({"user_id": user_id})
            if existing_request:
                return response_handler(
                    409,
                    "Request already exists for this user.",
                    "Request already exists for this user.",
                )

            # Insert the new request
            self.collection.insert_one(
                {
                    "user_id": user_id,
                    "email": email,
                    "reason": reason,
                    "request_date": datetime.now(),
                }
            )
            return response_handler(201, "Admin Request Created")
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))

    def get_all_requests(self):
        """Fetches all admin requests."""
        try:
            requests = list(
                self.collection.find(
                    {},
                    {
                        "_id": 0,
                        "user_id": 1,
                        "email": 1,
                        "reason": 1,
                        "request_date": 1,
                    },
                )
            )
            if requests:
                return response_handler(200, "OK", requests)
            return response_handler(404, "No Admin Requests Found", [])
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))

    def approve_request(self, user_id):
        """Approves an admin access request and updates the user's role."""
        try:
            # Check if the user_id exists in the users collection
            user = self._users_collection.find_one({"user_id": user_id})
            if not user:
                return response_handler(404, "User Not Found")

            # Update the user's role to ADMIN
            self._users_collection.update_one(
                {"user_id": user_id}, {"$set": {"role": "ADMIN"}}
            )

            # Delete the admin request
            self.collection.delete_one({"user_id": user_id})
            return response_handler(200, "Request Approved")
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))
