from db import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import validates
from flask_bcrypt import Bcrypt

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)

    def set_password(self, password):
        return Bcrypt.generate_password_hash(password, 16).decode('utf-8')

    def check_password(self, password):
        bcrypt = Bcrypt()

        return bcrypt.check_password_hash(self.password, password)
    
    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise AssertionError('No username provided!')
        
        if len(username) < 5 or len(username) > 25:
            raise AssertionError('Username must be between 5 and 25 characters!')
        
        return username
    
    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise AssertionError('No email provided!')
        
        if '@' not in email:
            raise AssertionError('Invalid email format!')
        
        return email
