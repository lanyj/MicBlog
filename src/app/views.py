# -*- coding:utf-8 -*-
import datetime
from string import strip

from flask import (
    render_template, flash, redirect, session, url_for, request, g)
from flask.ext.login import (
    login_user, logout_user, current_user, login_required)
from forms import (
    LoginForm, SignUpForm, PublishBlogForm, AboutMeForm)
from models import (
    User, Post, ROLE_USER, ROLE_ADMIN)
from utils import PER_PAGE
from app import app, db, lm
from flask_sqlalchemy import Pagination

@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@app.route('/index')
# @app.route('/index/<int:page>', defaults={'page':1}, methods=["POST", "GET"])
# @app.route('/index/page/<int:page>', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.loadRecentPosts(page, PER_PAGE)
        
    return render_template(
        "index.html",
        title="Home",
        pagination=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect('index')

    form = LoginForm()
    if form.validate_on_submit():
        user = User.loginCheck(request.form.get('user_name'),request.form.get('user_password'))
        if user:
            login_user(user)
            user.last_seen = datetime.datetime.now()
            try:
                db.session.add(user)
                db.session.commit()
            except:
                flash("The Database error!")
                return redirect('/login')
            flash('Hello: ' + request.form.get('user_name'))
            return redirect(url_for("index"))
        else:
            flash('Login failed, Your name is not exist!')
            return redirect('/login')

    return render_template(
        "login.html",
        title="Sign In",
        form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    user = User()
    if form.validate_on_submit():
        user_name = request.form.get('user_name')
        user_password = request.form.get('user_password')
        user_email = request.form.get('user_email')
        
        register_check = User.query.filter(db.or_(
            User.name == user_name, User.email == user_email)).first()
        if register_check:
            flash("error: The user's name or email already exists!")
            return redirect('/sign-up')

        if len(user_name) and len(user_email):
            user.name = user_name
            user.email = user_email
            user.password = user_password
            user.role = ROLE_USER
            try:
                db.session.add(user)
                db.session.commit()
            except Exception as err:
                print err
                flash("The Database error!")
                return redirect('/sign-up')

            flash("Sign up successful!")
            return redirect('/index')

    return render_template(
        "sign_up.html",
        form=form)


@app.route('/user/<int:userId>', defaults={'page':1}, methods=["POST", "GET"])
@app.route('/user/<int:userId>/page/<int:page>', methods=['GET', 'POST'])
def users(userId, page):
    form = AboutMeForm()
    u = User.loadUserById(userId)
    # pagination = user.posts.paginate(page, PER_PAGE, False).items
    pagination = u.getRecentPosts(page, PER_PAGE)
    if current_user is None:
        curr=User(id=-1,name='anonymous',email='None')
    else:
        curr=current_user
    return render_template(
        "user.html",
        form=form,
        curr=curr,
        user=u,
        pagination=pagination)


@app.route('/publish', methods=["POST", "GET"])
@login_required
def publish():
    form = PublishBlogForm()
    if form.validate_on_submit():
        blog_body = request.form.get("body")
        if not len(strip(blog_body)):
            flash("The content is necessray!")
            return redirect(url_for("publish"))
        try:
            current_user.publishPost(blog_body)
        except:
            flash("Database error!")
            return redirect(url_for("publish"))

        flash("Publish Successful!", "success")
        return redirect(url_for("users", userId=current_user.id))

    return render_template(
        "publish.html",
        form=form)

@app.route('/user/delete/<int:postId>')
@login_required
def deletePost(postId):
    current_user.deletePost(postId)
    return redirect(url_for("users", userId=current_user.id))
    
@app.route('/user/about-me', methods=["POST", "GET"])
@login_required
def about_me():
    user = current_user
    if request.method == "POST":
        content = request.form.get("describe")
        if len(content) and len(content) <= 256:
            user.about_me = content
            try:
                db.session.add(user)
                db.session.commit()
            except:
                flash("Database error!")
                return redirect(url_for("users", userId=user.id))
        else:
            flash("Sorry, May be your data have some error.")
    return redirect(url_for("users", userId=user.id))
