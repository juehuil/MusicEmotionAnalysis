# creating Flask instance variable app

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from ast import literal_eval
import datetime
import json

app = Flask(__name__)
app.debug = True


ENV = 'post'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:lL@1998623@localhost/Test'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://gmetnwrezeyokw:d1471eb9f2cb47425469418f6d2cb80' \
                                            'a7ad29df34f4f928f1116c6103cd35142@ec2-75-101-212-64.compute-1' \
                                            '.amazonaws.com:5432/dfirkg7gdep2ks'


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
    __tablename__ = 'user_info'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uname = db.Column(db.String(200), unique=True)
    upw = db.Column(db.String(200))
    utype = db.Column(db.Integer)       # 0: non, 0x100: Classical Fan, 0x010: pop Fan, 0x001: Yanni Fan

class UserExp(db.Model):
    __tablename__ = 'user_exp'
    uid = db.Column(db.Integer, primary_key=True)
    exp_num = db.Column(db.Integer, unique=True)
    exp_start = db.Column(db.DateTime, unique=True)
    exp_end = db.Column(db.DateTime, unique=True)
    initial_v = db.Column(db.Integer)
    initial_a = db.Column(db.Integer)
    final_v = db.Column(db.Integer)
    final_a = db.Column(db.Integer)
    eval = db.Column(db.Integer)
    recommend_rate = db.Column(db.Integer)


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



class UserMemory(db.Model):
    __tablename__ = 'user_memory'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exp_num = db.Column(db.Integer, primary_key=True, unique=True)
    music_num = db.Column(db.Integer)
    memory = db.Column(db.Text())

    def __init__(self, uid, exp_num, music_num, memory):
        self.uid = uid
        self.exp_num = exp_num
        self.music_num = music_num
        self.memory = memory


def convert(byte):
    data = literal_eval(byte.decode('utf-8'))
    return data

"""
@app.route('/upload', methods=['POST'])
def upload():
    data = convert(request.data)
    now = datetime.datetime.utcnow()
    data["upload_time"] = now.strftime('%Y-%m-%d %H:%M:%S')
    data["v_counts"] = 0
    data["j_counts"] = 0
    cur = mysql.connection.cursor()
    #cur.execute("INSERT INTO Category(compet_id, category_name) VALUES(1, 'Best Movie')")
    cur.execute("INSERT INTO Movie(uid, film_name, v_counts, j_counts, upload_time, url, category_id, summary) VALUES(%(uid)s,%(film_name)s,%(v_counts)s,%(j_counts)s,%(upload_time)s,%(url)s,%(category_id)s,%(summary)s)",data)
    mysql.connection.commit()
    return "upload success"

@app.route('/login', methods=['POST'])
def login():
    data = convert(request.data)
    name = data["uname"]
    upw = data["upw"]
    # SELECT uid FROM table WHERE uname = uname AND upw = upw
    return "login success"

@app.route('/expnum', methods=['POST'])
def expnum():
    data = convert(request.data)
    uid = data["uid"]
    # SELECT exp_num FROM table WHERE uid = uid
    return exp_num + 1

@app.route('/create_exp', methods=['POST'])
def create_exp():
    data = convert(request.data)
    exp_num = data["exp_num"]
    uid = data["uid"]
    # INSERT uid, exp_num INTO table
    return exp_num + 1

@app.route('/', methods=['POST'])
def create_exp():
    data = convert(request.data)
    exp_num = data["exp_num"]
    uid = data["uid"]
    # INSERT uid, exp_num INTO table
    return exp_num + 1
"""

@app.route('/')
def index():
    ### Test Login
    name = "jessy"
    pw = "12345689"

    user = User.query.filter_by(uname=name).first()
    if (user is None):
        return "user name does not exist!"
    elif (user.upw == "123456789"):
        return 'You are logged in'
    else:
        return 'Incorrect Password!'

@app.route('/<name>')
def hello(name):
    return 'it works! {0}'.format(name)

@app.route('/login', methods=['POST'])
def login():
    data = convert(request.data)
    name = data["uname"]
    pw = data["upw"]

    user = User.query.filter_by(uname=name).first()
    if (user is None):
        return "user name does not exist!"
    elif (user.upw == pw):
        user_exp_num = UserExp.query.filter_by(uid=user.uid).order_by("exp_num desc")
        if user_exp_num == None:
            return 0
        else:
            return user_exp_num
        return name
    else:
        return 'Incorrect Password!'

@app.route('/register', methods=['POST'])
def register():
    data = convert(request.data)
    name = data["uname"]
    pw = data["upw"]
    user_type = data["utype"]
    user = User.query.filter_by(uname=name).first()
    if user != None:
        return "User Already Exist!"
    new_user = User(uname=name, upw=pw, utype=user_type)
    db.session.add(new_user)
    db.session.commit()
    return new_user.uname + "!!"