import pymongo
from datetime import datetime
from pymongo.errors import PyMongoError
from database import db
from response import response_handler


def should_deactivate_account(registration_date):
    current_date = datetime.now()
    reg_year = registration_date.year

    if (
        datetime(reg_year, 5, 15) < registration_date <= datetime(reg_year, 12, 15)
    ):  # case 1: student registered after 15 may to the 15 dec -> deactivate on 15 dec
        if current_date >= datetime(reg_year, 12, 15):
            return True
    else:  # case 2: student registered aftfer 15 dec year x to the 15 may year x+1 -> deactivate on 15 may year x+1
        year = reg_year
        if registration_date.month == 12:
            year += 1

        if current_date >= datetime(year, 5, 15):
            return True

    return False


class UserModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserModel, cls).__new__(cls)
            cls._instance.collection = db["users"]
        return cls._instance

    def user_exists(self, oid):
        try:
            user = self.collection.find_one({"user_id": oid})
            return response_handler(200, "OK", user is not None)
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))

    def create_user(self, oid, email):
        try:
            new_user = {
                "user_id": oid,
                "status": "ACTIVATED",
                "registration_date": datetime.now(),
                "chat_id_counter": 0,
                "tokens_used": 0,
                "role": "STUDENT",
                "email": email,
            }
            self.collection.insert_one(new_user)
            return response_handler(201, "Created", {"user_id": oid, "email": email})
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))

    def login_user(self, oid):
        try:
            # Find user in the database
            user = self.collection.find_one({"user_id": oid})

            if not user:
                return response_handler(404, "User Not Found")

            # Check if the status field exists
            status = user.get("status")
            if not status:
                return response_handler(400, "User Status Not Found")

            if status == "DEACTIVATED":
                return response_handler(403, "Account Deactivated")

            if status == "ACTIVATED":
                registration_date = user.get("registration_date")
                if not registration_date:
                    return response_handler(400, "Registration Date Missing")

                # Check if the account should be deactivated
                if should_deactivate_account(registration_date):
                    self.collection.update_one(
                        {"user_id": oid}, {"$set": {"status": "DEACTIVATED"}}
                    )
                    return response_handler(403, "Account Deactivated")

                # Return the user if active
                return response_handler(200, "OK", user)

            # Unexpected status
            return response_handler(400, f"Unexpected User Status: {status}")

        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))

    def get_chat_id_counter(self, user_id):
        try:
            user = self.collection.find_one({"user_id": user_id})
            if user:
                return response_handler(200, "OK", user.get("chat_id_counter", 0))
            return response_handler(404, "User Not Found")
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))

    def increment_chat_id(self, user_id):
        try:
            result = self.collection.update_one(
                {"user_id": user_id}, {"$inc": {"chat_id_counter": 1}}
            )
            if result.modified_count > 0:
                user = self.collection.find_one({"user_id": user_id})
                return response_handler(200, "OK", user["chat_id_counter"])
            return response_handler(404, "User Not Found")
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))

    def update_tokens_used(self, user_id, tokens_used):
        """Updates the tokens used by a user."""
        try:
            result = self.collection.update_one(
                {"user_id": user_id}, {"$inc": {"tokens_used": tokens_used}}
            )
            if result.matched_count > 0:
                return response_handler(200, "OK", "Tokens updated successfully")
            return response_handler(404, "User Not Found")
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))

    def get_user_tokens_used(self, user_id):
        """Gets the total tokens used by a user."""
        try:
            user = self.collection.find_one({"user_id": user_id})
            if user:
                return response_handler(200, "OK", user.get("tokens_used", 0))
            return response_handler(404, "User Not Found")
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))

    def get_user_chat_count(self, user_id):
        """Gets the total chat count of a user."""
        try:
            user = self.collection.find_one({"user_id": user_id})
            if user:
                return response_handler(200, "OK", user.get("chat_id_counter", 0))
            return response_handler(404, "User Not Found")
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))

    def get_user_role(self, user_id):
        """Gets the role of a user."""
        try:
            user = self.collection.find_one({"user_id": user_id})
            if user:
                role = user.get("role", "STUDENT")
                return response_handler(200, "OK", role)
            return response_handler(404, "User Not Found")
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))

    def get_average_token_usage(self):
        """Calculate the average number of tokens used by all users with role 'STUDENT'."""
        try:
            pipeline = [
                {"$group": {"_id": None, "avg_tokens": {"$avg": "$tokens_used"}}}
            ]
            print(pipeline)
            result = list(self.collection.aggregate(pipeline))
            avg_tokens = result[0]["avg_tokens"] if result else 0
            return response_handler(200, "OK", round(avg_tokens, 2))
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))

    def get_total_chat_count(self):
        """Sum the total number of chats across all users with role 'STUDENT'."""
        try:
            pipeline = [
                {"$group": {"_id": None, "total_chats": {"$sum": "$chat_id_counter"}}}
            ]
            result = list(self.collection.aggregate(pipeline))
            total_chats = result[0]["total_chats"] if result else 0
            return response_handler(200, "OK", total_chats)
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))
