from app import db,login,app
from datetime import datetime
from datetime import timedelta as td
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
import jwt
from hashlib import md5

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    completed_boards = db.relationship('CompletedBoard', backref='owner', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)
        
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
            
    def records(self):
        #games = CompletedBoard.query.join(
        #    completed_boards, (completed_boards.c.followed_id == Post.user_id)).filter(
        #        followers.c.follower_id == self.id)
        own = CompletedBoard.query.filter_by(user_id=self.id)
        return own.order_by(CompletedBoard.timestamp.desc())

            
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class BoardTemplate(db.Model):
    '''one-to-many '''
    id = db.Column(db.Integer, primary_key=True)
    nteams = db.Column(db.Integer)
    npoints = db.Column(db.Integer)
    segments = db.Column(db.Integer) #number of halves/quarters etc, number of timeouts
    name = db.Column(db.String(140))
    duration = db.Column(db.Interval, default=td(hours=1))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) #delete later
    nintervals = db.Column(db.Integer) #delete later
    points_to_win =db.Column(db.Integer) #delete later
    board_view=db.Column(db.String(140)) #html template of view layout
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #not strictly necessary.. if no user id, make public user id?

    def __repr__(self):
        return '<BoardTemplate {}>'.format(self.body)

class CompletedBoard(db.Model):
    '''inheirits from boardtemplate if I can figure that out'''
    id = db.Column(db.Integer, primary_key=True)
    #owner = db.Column(db.String(64), db.ForeignKey('user.username'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #template_id = db.Column(db.Integer, db.ForeignKey('board_template.id'))
    #template = db.relationship('BoardTemplate', backref='id', lazy='dynamic')
    #for now, later this should depend on template
    team1=db.Column(db.String(64))
    team2=db.Column(db.String(64))
    score1=db.Column(db.Integer)
    score2=db.Column(db.Integer)

    def __repr__(self):
        return '<CompletedBoard {}>'.format(self.body)
