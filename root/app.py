# creating Flask instance variable app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

ENV = 'post'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:lL@1998623@localhost/Test'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://gmetnwrezeyokw:d1471eb9f2cb47425469418f6d2cb80a7ad29df34f4f928f1116c6103cd35142@ec2-75-101-212-64.compute-1.amazonaws.com:5432/dfirkg7gdep2ks'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Music(db.Model):
    __tablename__ = 'music'
    mid = db.Column(db.Integer, primary_key=True)
    mname = db.Column(db.String(200), unique=True)
    murl = db.Column(db.String(200))
    mtype = db.Column(db.Integer)   # 1: Classical, 2: Pop, 3: Yanni
    mv = db.Column(db.Integer)
    ma = db.Column(db.Integer)

    def __init__(self, mid, mname, murl, mtype, mv, ma):
        self.mid = mid
        self.mname = mname
        self.murl = murl
        self.mtype = mtype
        self.mv = mv
        self.ma = ma
class User(db.Model):
    __tablename__ = 'user'
    uid = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(200), unique=True)
    upw = db.Column(db.String(200))
    utype = db.Column(db.Integer)       # 0: non, 0x100: Classical Fan, 0x010: pop Fan, 0x001: Yanni Fan

    def __init__(self, uid, uname, upw, utype):
        self.uid = uid
        self.uname = uname
        self.upw = upw
        self.utype = utype
class UserExp(db.Model):
    __tablename__ = 'user_exp'
    uid = db.Column(db.Integer, primary_key=True)
    exp_num = db.Column(db.Integer, unique = True)
    initial_v = db.Column(db.Integer)
    initial_a = db.Column(db.Integer)
    final_v = db.Column(db.Integer)
    final_a = db.Column(db.Integer)
    eval = db.Column(db.Integer)    ########
    recommend_rate = db.Column(db.Integer)

    def __init__(self, uid, exp_num, initial_v, initial_a, final_v, final_a, eval, recommend_rate):
        self.uid = uid
        self.exp_num =exp_num
        self.initial_v = initial_v
        self.initial_a = initial_a
        self.final_v =final_v
        self.final_a = final_a
        self.eval = eval
        self.recommend_rate = recommend_rate
class UserMusic(db.Model):
    __tablename__ = 'user_music'
    uid = db.Column(db.Integer, primary_key=True)
    exp_num = db.Column(db.Integer, primary_key=True, unique=True)
    music_num = db.Column(db.Integer)
    mid = db.Column(db.Integer)
    v = db.Column(db.Integer)
    a = db.Column(db.Integer)
    score = db.Column(db.Integer)
    familiarity = db.Column(db.Integer)

    def __init__(self, uid, exp_num, music_num, mid, v, a, score, familiarity):
        self.uid = uid
        self.exp_num = exp_num
        self.music_num = music_num
        self.mid = mid
        self.v = v
        self.a = a
        self.score = score
        self.familiarity = familiarity
class UserMemory(db.Model):
    __tablename__ = 'user_memory'
    uid = db.Column(db.Integer, primary_key=True)
    exp_num = db.Column(db.Integer, primary_key=True, unique=True)
    music_num = db.Column(db.Integer)
    memory = db.Column(db.Text())

    def __init__(self, uid, exp_num, music_num, memory):
        self.uid = uid
        self.exp_num = exp_num
        self.music_num = music_num
        self.memory = memory


@app.route('/')
def index():
    return 'it works!'


@app.route('/<name>')
def hello(name):
    return 'it works! {0}'.format(name)