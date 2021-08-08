from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, PasswordField
from wtforms.validators import InputRequired
from wtforms.fields.html5 import EmailField
from flask_mde import MdeField


class ContactForm(FlaskForm):
    name = StringField(label="Name", validators=[InputRequired()])
    email = EmailField(label="Email", validators=[InputRequired()])
    phone = IntegerField(label="Phone Number", validators=[InputRequired()])
    msg = StringField(label="Message", validators=[InputRequired()])
    submit = SubmitField(label="Send")


class NewPostForm(FlaskForm):
    title = StringField(label="Blog Post Title: ", validators=[InputRequired()])
    subtitle = StringField(label="Subtitle: ", validators=[InputRequired()])
    # author = StringField(label="Your Name: ", validators=[InputRequired()])
    img_url = StringField(label="Blog Image URL: ", validators=[InputRequired()])
    link = StringField(label="Link for author website: ")
    body = MdeField(label="Blog Content: ", validators=[InputRequired()])
    submit = SubmitField(label="SUBMIT POST")


class LoginForm(FlaskForm):
    email = EmailField(label="Email: ", validators=[InputRequired()])
    password = PasswordField(label="Password: ", validators=[InputRequired()])
    submit = SubmitField(label="Login")


class RegisterForm(FlaskForm):
    name = StringField(label="Name", validators=[InputRequired()])
    email = EmailField(label="Email: ", validators=[InputRequired()])
    password = PasswordField(label="Password: ", validators=[InputRequired()])
    re_password = PasswordField(label="Re-Enter Password: ", validators=[InputRequired()])
    submit = SubmitField(label="Register")


class CommentForm(FlaskForm):
    comment = MdeField(label="Comment:", validators=[InputRequired()])
    submit = SubmitField(label="Submit Comment")
