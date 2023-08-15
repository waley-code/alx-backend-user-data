#!/usr/bin/env python3
"""DB module
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError
from user import Base, User


class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=True)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Add a new user to the database
        """
        new_user = User(email=email, hashed_password=hashed_password)
        self._session.add(new_user)
        self._session.commit()
        return new_user

    def find_user_by(self, **kwargs):
        """Find a user by filtering with keyword arguments
        """
        try:
            user = self._session.query(User).filter_by(**kwargs).first()
            if user is None:
                raise NoResultFound(
                        "No user found with the specified filters.")
            return user
        except InvalidRequestError as e:
            raise e  # Raising the InvalidRequestError as it is
        except NoResultFound:
            raise NoResultFound("No user found with the specified filters.")

    def update_user(self, user_id: int, **kwargs):
        """Update a user's attributes based on user_id and keyword arguments
        """
        try:
            user = self.find_user_by(id=user_id)
            for attr, value in kwargs.items():
                if hasattr(user, attr):
                    setattr(user, attr, value)
                else:
                    raise ValueError(f"Invalid attribute '{attr}' provided.")
            self._session.commit()
        except NoResultFound:
            raise NoResultFound(f"No user found with id '{user_id}'.")
