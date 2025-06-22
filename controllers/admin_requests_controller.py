from models.admin_model import AdminModel


class AdminController:
    """Handles admin request operations."""

    def __init__(self):
        self.admin_model = AdminModel()

    def get_admin_requests(self):
        """Fetches all admin requests."""
        return self.admin_model.get_all_requests()

    def approve_admin_request(self, user_id):
        """Approves an admin request and updates the user's role."""
        return self.admin_model.approve_request(user_id)

    def create_admin_request(self, user_id, email, reason):
        """Creates an admin access request."""
        return self.admin_model.create_admin_request(user_id, email, reason)
