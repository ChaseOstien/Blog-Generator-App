from flask_restful import Resource, Api, reqparse
from flask import Blueprint, jsonify, make_response
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
from flask_bcrypt import Bcrypt

from db import get_db
from models import User
from extensions import jwt

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

auth = Blueprint('auth', __name__, url_prefix='/auth')
api = Api(auth)

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    db = get_db()
    identity = jwt_data["sub"]
    user = db.query(User).filter_by(id=identity).one_or_none()
    return user

class Login(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser(bundle_errors=True)
            parser.add_argument('username')
            parser.add_argument('password')
            args = parser.parse_args(strict=True)
            username = args.username
            password = args.password
            print(username, password)

            bcrypt = Bcrypt()

            db = get_db()
            
            try:
                # Attempt to retrieve the user from the database
                user = db.query(User).filter(User.username == username).one()

                # Check if the provided password matches the stored hash
                if bcrypt.check_password_hash(user.password, password):
                    access_token = create_access_token(identity=user)
                    response = jsonify(access_token=access_token)
                    set_access_cookies(response, access_token)
                    return response
                else:
                    return make_response(jsonify(message='Incorrect password!'), 401)
            except NoResultFound:
                # No user found with the provided username
                return make_response(jsonify(message='No user found with that username!'), 401)
            except MultipleResultsFound:
                # Multiple users found with the same username (shouldn't happen)
                return make_response(jsonify(message='Multiple users found with that username!'), 401)
        except Exception as e:
            print(f"Error: {e}")
            return jsonify(message='An unexpected error occurred!')

class Signup(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser(bundle_errors=True)
            parser.add_argument('username')
            parser.add_argument('password')
            parser.add_argument('email')
            args = parser.parse_args(strict=True)

            username = args.username
            password = args.password
            email = args.email

            bcrypt = Bcrypt()
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            db = get_db()

            try:
                newUser = User(
                    username = username, 
                    email = email,
                    password = hashed_password
                )

                db.add(newUser)
                db.commit()
            except SQLAlchemyError as e:
                print(f"Error adding user to database: {e}")
                db.rollback()
                return make_response(jsonify(message = 'Failed to add new user!'), 401)
        
            access_token = create_access_token(identity=newUser)
            response = jsonify(access_token=access_token)
            set_access_cookies(response, access_token)
            return response
        except Exception as e:
            print(f"Error: {e}")
            return jsonify(message = 'An unexpected error occured!')


class Logout(Resource):
    def post(self):
        response = jsonify({'msg': 'Logged out successfully!'})
        unset_jwt_cookies(response)
        return response


api.add_resource(Login, '/login')
api.add_resource(Signup, '/signup')
api.add_resource(Logout, '/logout')
