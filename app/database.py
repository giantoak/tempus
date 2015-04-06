from app import app
from flask.ext.sqlalchemy import SQLAlchemy
from config import dburl, redisurl
import os
import redis

app.config['SQLALCHEMY_DATABASE_URI'] = dburl
db = SQLAlchemy(app)
rds = redis.Redis(redisurl)
