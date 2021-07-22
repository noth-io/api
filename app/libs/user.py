
from models import User

class VerifyUser:
    def __init__(self, identity):
        # Get user from DB if exist
        user = User.query.filter_by(username=identity).first()
        if user:
            self.user = user


