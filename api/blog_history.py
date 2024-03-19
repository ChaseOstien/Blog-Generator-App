from flask_restful import Resource, Api
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, current_user, create_access_token, get_jwt_identity, set_access_cookies, get_jwt
from sqlalchemy.exc import NoResultFound

from extensions import jwt
from db import get_db
from models import Blog, User

from datetime import datetime, timedelta, timezone

query_blogs = Blueprint('history', __name__)
api = Api(query_blogs)

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    db = get_db()
    identity = jwt_data["sub"]
    user = db.query(User).filter_by(id=identity).one_or_none()
    print(user)
    return user


def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response

class Query_blogs(Resource):
    @jwt_required(optional=True)
    def get(self):
        with get_db() as db:
            try:
                if current_user.id:
                    all_blogs = db.query(Blog).filter(Blog.user_id == current_user.id).order_by(Blog.created_at.desc()).all()
                else:
                    db.rollback()
                    return jsonify(message = 'Blog history failed to load!'), 500
            
                blog_data = []
                for blog in all_blogs:
                    blog_history = {
                        'id': blog.id,
                        'title': blog.title,
                        'content': blog.content,
                        'generated': blog.created_at
                    }
                    blog_data.append(blog_history)

                return jsonify(blog_data)
            except Exception as e:
                return jsonify(message='Blog history failed to load!', error=str(e)), 500
    
    @jwt_required(optional=True)
    def put(self, id):
        with get_db() as db:
            try:
                one_blog = db.query(Blog).filter(Blog.id == id).one()
                blog = {
                'id': one_blog.id,
                'title': one_blog.title,
                'content': one_blog.content,
                'generated': one_blog.created_at
                }
                return jsonify(blog)
            except NoResultFound:
                return jsonify(message='Blog not found'), 404
            except Exception as e:
                db.rollback()
                return jsonify(message='Failed to load blog', error=str(e)), 500

api.add_resource(Query_blogs, '/history')
api.add_resource(Query_blogs, '/history/<int:id>', endpoint='get_by_id')
query_blogs.after_request(refresh_expiring_jwts)
