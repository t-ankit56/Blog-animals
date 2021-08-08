from flask import Flask, render_template, url_for, redirect, request, flash, abort
from mail import Mail
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user, UserMixin
from functools import wraps

from sqlalchemy.ext.declarative import declarative_base
from html import unescape
from flask_mde import Mde
from flask_gravatar import Gravatar
import os
from dotenv import load_dotenv
from forms import *


load_dotenv()  # take environment variables from .env.

Base = declarative_base()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL1")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
db = SQLAlchemy(app)
mde = Mde(app)

gravatar = Gravatar(app,
                    size=30,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

login_manager = LoginManager()
login_manager.init_app(app)


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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def author_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_post = Blog.query.filter_by(author_id=current_user.id).first()
        if user_post is not None and current_user.id == user_post.author_id:
            return f(*args, **kwargs)
        return abort(403)

    return decorated_function


@app.route('/')
def home():
    all_post = db.session.query(Blog).all()
    response_home = {
        "title": [post.title for post in all_post],
        "subtitle": [post.subtitle for post in all_post],
        "author": [post.author for post in all_post],
        "date": [post.date for post in all_post],
        "link": [post.link for post in all_post],
        "id": [post.id for post in all_post]
    }
    return render_template("index.html", **response_home)


@app.route('/post/<int:post_id>')
def full_post(post_id):
    comment_form = CommentForm()
    post_to_show = Blog.query.get(post_id)
    unescaped_body = unescape(post_to_show.body)
    response_full_post = {
        "title": post_to_show.title,
        "subtitle": post_to_show.subtitle,
        "author": post_to_show.author,
        "date": post_to_show.date,
        "link": post_to_show.link,
        "id": post_to_show.id,
        "body": unescaped_body,
        "img_url": post_to_show.img_url,
        "comments": post_to_show.comments,
    }
    return render_template("post.html", **response_full_post, form=comment_form)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact', methods=["GET", "POST"])
def contact():
    contact_form = ContactForm()
    if contact_form.validate_on_submit():
        mail_msg = Mail()
        mail_msg.name = contact_form.name.data
        mail_msg.email = contact_form.email.data
        mail_msg.phone = contact_form.phone.data
        mail_msg.msg = contact_form.msg.data
        mail_msg.send_mail()
        return render_template("contact.html", msg_sent=True, form=contact_form)
    return render_template("contact.html", msg_sent=False, form=contact_form)


@app.route('/new-post', methods=["GET", "POST"])
@login_required
def new_post():
    new_post_form = NewPostForm()
    today_date = datetime.now().date()
    day = today_date.strftime("%d")
    month = today_date.strftime("%m")
    year = today_date.strftime("%Y")

    if new_post_form.validate_on_submit():
        new_post_database = Blog(author=current_user,
                                 title=new_post_form.title.data,
                                 subtitle=new_post_form.subtitle.data,
                                 date=f"{day}/{month}/{year}",
                                 img_url=new_post_form.img_url.data,
                                 body=new_post_form.body.data,
                                 link=new_post_form.link.data
                                 )
        db.session.add(new_post_database)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make-post.html", form=new_post_form, new=True)


@app.route('/edit-post', methods=["GET", "POST"])
@author_only
def edit_post():
    post_id = request.args.get("post_id")
    post_to_edit = Blog.query.get(post_id)
    edit_form = NewPostForm(obj=post_to_edit)
    if edit_form.validate_on_submit():
        post_to_edit.title = edit_form.title.data
        post_to_edit.subtitle = edit_form.subtitle.data
        post_to_edit.img_url = edit_form.img_url.data
        post_to_edit.body = unescape(edit_form.body.data)
        post_to_edit.link = edit_form.link.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make-post.html", form=edit_form, new=False, id=post_id)


@app.route('/delete-post/<int:post_id>', methods=['GET', 'POST'])
@author_only
def delete_post(post_id):
    post_to_delete = Blog.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        entered_password = login_form.password.data
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash("This User does not exist. Please check the email that you have entered")
        elif not check_password_hash(user.password, entered_password):
            flash("Incorrect Password. Please check the password and try again.")
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html", form=login_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        name = register_form.name.data
        email = register_form.email.data
        password = register_form.password.data
        re_password = register_form.re_password.data
        if password != re_password:
            flash("Your passwords does not match. Please try again.")
            return redirect(url_for('register'))
        exists = User.query.filter_by(email=email).first() is not None
        if exists:
            flash("This User Already Exists. Please Login Instead.")
            return redirect(url_for('login'))
        else:
            password_hash = generate_password_hash(password=password, method='pbkdf2:sha256', salt_length=10)
            new_user = User(name=name,
                            email=email,
                            password=password_hash)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
    return render_template("register.html", form=register_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/comment', methods=["GET", "POST"])
def comment():
    post_id = request.args.get('post_id')

    if current_user.is_authenticated:
        comment_form = CommentForm()
        now = datetime.now()
        date_time = now.strftime("%c")
        if comment_form.validate_on_submit():
            new_comment = Comments(comment=comment_form.comment.data,
                                   post=Blog.query.get(post_id),
                                   user=current_user,
                                   date_time=date_time,
                                   )
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for("full_post", post_id=post_id))
    else:
        flash("Please Login to comment.")
        return redirect(url_for("login"))
    return redirect(url_for("full_post"))


@login_required
@app.route('/delete-comment')
def delete_comment():
    comment_id = request.args.get('comment_id')
    post_id = request.args.get('post_id')
    comment_to_delete = Comments.query.get(comment_id)
    db.session.delete(comment_to_delete)
    db.session.commit()
    return redirect(url_for('full_post', post_id=post_id))


if __name__ == "__main__":
    app.run(debug=True)
