import pymongo
from pymongo.errors import PyMongoError
from database import db
from response import response_handler


class ChatHistoryModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChatHistoryModel, cls).__new__(cls)
            cls._instance.collection = db["chat_history"]
        return cls._instance

    def save_chat(self, user_id, course_id, chat_id, query, response, main_topic):
        """Saves a chat entry to the chat history."""
        try:
            self.collection.insert_one(
                {
                    "user_id": user_id,
                    "course_id": course_id,
                    "chat_id": chat_id,
                    "query": query,
                    "response": response,
                    "main_topic": main_topic,
                }
            )
            return response_handler(201, "Chat Saved")
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))

    def get_chat_history(self, user_id, course_id):
        """Fetches the chat history for a user and a specific course."""
        try:
            chats = list(
                self.collection.find(
                    {"user_id": user_id, "course_id": course_id}, {"_id": 0}
                )
            )
            if chats:
                return response_handler(200, "OK", chats)
            return response_handler(404, "No Chat History Found", [])
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))

    def get_chat_history_by_course(self, course_id):
        """Fetches the chat history for all students in a specific course."""
        try:
            chats = list(self.collection.find({"course_id": course_id}, {"_id": 0}))
            if chats:
                return response_handler(200, "OK", chats)
            return response_handler(404, "No Chat History Found", [])

        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))

    def get_last_response(self, user_id, course_id):
        """Fetches the last response for a given user ID and course ID."""
        try:
            last_response = self.collection.find_one(
                {"user_id": user_id, "course_id": course_id},
                sort=[("chat_id", pymongo.DESCENDING)],
            )
            if last_response:
                return response_handler(200, "OK", last_response.get("response"))
            return response_handler(404, "No Response Found")
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))

    def delete_chat_by_user(self, user_id):
        """Deletes all chat entries for a given user ID."""
        try:
            result = self.collection.delete_many({"user_id": user_id})
            if result.deleted_count > 0:
                return response_handler(
                    200, "Chat(s) deleted", {"deleted_count": result.deleted_count}
                )
            else:
                return response_handler(404, "No chat found for given user id")
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))

    def get_all_chat_history(self):
        """Fetches query and response for all chat entries."""
        try:
            chats = list(
                self.collection.find({}, {"_id": 0, "query": 1, "response": 1})
            )
            if chats:
                return response_handler(200, "OK", chats)
            return response_handler(404, "No Chat History Found", [])
        except PyMongoError as e:
            return response_handler(500, "Internal Server Error", str(e))
