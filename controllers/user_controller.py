from models.user_model import UserModel

class UserController:
    """Handles user-related operations."""

    def __init__(self):
        self.users_model = UserModel()

    def get_user_role(self, user_id):
        """Fetches and returns the user role."""
        return self.users_model.get_user_role(user_id)
    
    def get_user_tokens_used(self, user_id): 
        return self.users_model.get_user_tokens_used(user_id)
