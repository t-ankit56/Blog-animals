from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from main import db, Base
from flask_login import UserMixin


class User(UserMixin, db.Model, Base):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    posts = relationship("Blog", back_populates="author")
    comments = relationship("Comments", back_populates="user")


class Blog(db.Model, Base):
    __tablename__ = "blog"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, ForeignKey('users.id'))
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(200), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), unique=True, nullable=False)
    date = db.Column(db.String(50), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    body = db.Column(db.String(), nullable=False)
    img_url = db.Column(db.String(), nullable=True)
    comments = relationship("Comments", back_populates="post")


class Comments(db.Model, Base):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, ForeignKey('blog.id'))
    user_id = db.Column(db.Integer, ForeignKey('users.id'))
    post = relationship("Blog", back_populates="comments")
    user = relationship("User", back_populates="comments")
    comment = db.Column(db.String(200), nullable=True)
    date_time = db.Column(db.String(), nullable=False)


# db.create_all()