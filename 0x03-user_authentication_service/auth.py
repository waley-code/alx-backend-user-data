#!/usr/bin/env python3
"""
Main file
"""
import bcrypt
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError
from typing import Union
from db import DB
from user import User


def _hash_password(password: str) -> bytes:
    """Hash a password securely using bcrypt
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        self._db = DB()

    def _generate_uuid() -> str:
        """Generate a new UUID
        """
        return str(uuid.uuid4())

    def register_user(self, email: str, password: str) -> User:
        """Register a new user
        """
        try:
            existing_user = self._db.find_user_by(email=email)
        except NoResultFound:
            hashed_password = _hash_password(password)
            new_user = self._db.add_user(email, hashed_password)
            return new_user
        else:
            raise ValueError(f"User {email} already exists.")

    def valid_login(self, email: str, password: str) -> bool:
        """Check if login is valid
        """
        try:
            user = self._db.find_user_by(email=email)
            return bcrypt.checkpw(password.encode('utf-8'), user.hashed_password)
        except NoResultFound:
            return False

    def create_session(self, email: str) -> str:
        """Create a new session for the user
        """
        try:
            user = self._db.find_user_by(email=email)
            session_id = self._generate_uuid()
            self._db.update_user(user.id, session_id=session_id)
            return session_id
        except NoResultFound:
            raise NoResultFound(f"No user found with email '{email}'.")

    def get_user_from_session_id(self, session_id: str) -> Union[str, None]:
        """Get user based on session ID
        """
        if session_id is None:
            return None

        try:
            user = self._db.find_user_by(session_id=session_id)
            return user
        except NoResultFound:
            return None

    def destroy_session(self, user_id: int) -> None:
        """Updates the corresponding user's session ID to None"""
        try:
            user = self._db.find_user_by(id=user_id)
        except NoResultFound:
            return None

       self._db.update_user(user.id, session_id=None)
       return None

    def get_reset_password_token(self, email: str) -> str:
        """Get a reset password token
        """
        try:
            user = self._db.find_user_by(email=email)
            reset_token = self._generate_uuid()
            self._db.update_user(user.id, reset_token=reset_token)
            return reset_token
        except NoResultFound:
            raise ValueError(f"No user found with email '{email}'.")

    def update_password(self, reset_token: str, new_password: str) -> None:
        """Update user's password using reset token
        """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
            hashed_password = _hash_password(new_password)
            self._db.update_user(user.id, hashed_password=hashed_password,
                    reset_token=None)
        except NoResultFound:
            raise ValueError("Invalid reset token.")
