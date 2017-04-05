# -*- coding:utf-8 -*-
'''
Created on 2017年3月24日

@author: jay
'''
from flask_wtf import Form
from wtforms import TextField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import Required, Email, Length
from wtforms.fields.simple import PasswordField


class LoginForm(Form):
    user_name = TextField('user name', validators=[
        Required(), Length(max=15)])
    user_password = PasswordField('user password',validators=[Required(),Length(min=6,max=12)]);
#     remember_me = BooleanField('remember me', default=False)
    submit = SubmitField('Log in')


class SignUpForm(Form):
    user_name = TextField('user name', validators=[
        Required(), Length(max=15)])
    user_email = TextField('user email', validators=[
        Email(), Required(), Length(max=128)])
    user_password = PasswordField('user password',validators=[Required(),Length(min=6,max=12)]);
    submit = SubmitField('Sign up')


class PublishBlogForm(Form):
    body = TextAreaField('blog content', validators=[Required()])
    submit = SubmitField('Submit')


class AboutMeForm(Form):
    describe = TextAreaField('about me', validators=[
        Required(), Length(max=256)])
    submit = SubmitField('Submit')