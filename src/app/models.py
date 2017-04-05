# -*- coding:utf-8  -*-
from app import db
import datetime
from sqlalchemy.sql.expression import except_
ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), index=True, unique=True)
    password = db.Column(db.String(18), index=False, unique=False)
    email = db.Column(db.String(128), index=True, unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(256))
    last_seen = db.Column(db.DateTime)
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.id
    def __repr__(self):
        return '<User %r>' % (self.name)
    def save(self):
        db.session.add(self)
        db.session.commit()
    @classmethod
    def loginCheck(cls, userName,password):
        user = cls.query.filter(db.and_(
            db.or_(
            User.name == userName, User.email == userName),
            User.password == password)).first()
        return user
    @classmethod
    def loadUserById(cls,userId):
        return User.query.get(int(userId))
        
    def publishPost(self,body):
        p=Post(body=body,timestamp=datetime.datetime.utcnow(),author=self)
        db.session.add(p)
        db.session.commit()
        return True
    def deletePost(self,postId):
        posts = self.posts
        for p in posts:
            if(p.id == postId):
                db.session.delete(p)
                db.session.commit()
                return True
        return False
    def updatePost(self,postId,body):
        posts = self.posts
        for p in posts:
            if(p.id == postId):
                p.body=body
                p.timestamp=datetime.datetime.utcnow()
                return True
        return False
    def getPostByPostId(self,postId):
        posts = self.posts
        for p in posts:
            if(p.id == postId):
                return p
        return None
    def getRecentPosts(self,pageNo,pageSize):
        # pagination = user.posts.paginate(page, PER_PAGE, False).items
        pagination = Post.query.filter(Post.user_id==self.id).order_by(
            db.desc(Post.timestamp) 
            ).paginate(pageNo, pageSize, False)
        return pagination
    def getPosts(self):
        return self.posts
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    def __repr__(self):
        return '<Post %r>' % (self.body)
    @classmethod
    def loadRecentPosts(cls,pageNo,pageSize):
        # pagination = user.posts.paginate(page, PER_PAGE, False).items
        pagination = Post.query.order_by(
            db.desc(Post.timestamp) 
            ).paginate(pageNo, pageSize, False)
        return pagination
    def getOwner(self):
        return User.loadUserById(self.user_id)