from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from flask import g
from os import getenv

load_dotenv()

engine = create_engine(getenv('DB_URL'), echo=True, pool_size=20, max_overflow=0)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# This function initializes the database connection and also closes the database connection
def init_db(app):
    Base.metadata.create_all(engine)

    app.teardown_appcontext(close_db)

# This function gets the database connection
def get_db():
    if 'db' not in g:
        # store db connection in app context
        g.db = Session()

    return Session()

# This function closes the database connection
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
