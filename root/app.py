# creating Flask instance variable app
from ast import literal_eval
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin

from root.helpers import *
import datetime
import json
import numpy

app = Flask(__name__)
app.debug = True

CORS(app)

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
    mid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mname = db.Column(db.String(200), unique=True)
    murl = db.Column(db.String(200))
    mtype = db.Column(db.Integer)  # 1: Classical, 2: Pop, 3: Yanni
    mv = db.Column(db.Integer)
    ma = db.Column(db.Integer)


class User(db.Model):
    __tablename__ = 'user_info'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uname = db.Column(db.String(200), unique=True)
    upw = db.Column(db.String(200))
    utype = db.Column(db.Integer)  # 0: non, 0x100: Classical Fan, 0x010: pop Fan, 0x001: Yanni Fan
    profession = db.Column(db.String(200))
    age = db.Column(db.Integer)             # range
    gender = db.Column(db.Integer)          # 0: male, 1: female, 2: other, 3: prefer not to state
    expertise = db.Column(db.Integer)       # 1 - 5: 1 not familiar, 5 expert
    love_level = db.Column(db.Integer)      # 1 - 5: 1 lowest, 5 highest
    ustart = db.Column(db.DateTime)  # start date of the first experiment


class UserExp(db.Model):
    __tablename__ = 'user_exp'
    uid = db.Column(db.Integer, primary_key=True)
    exp_num = db.Column(db.Integer, primary_key=True)
    exp_start = db.Column(db.DateTime)
    exp_end = db.Column(db.DateTime)
    initial_v = db.Column(db.Integer)
    initial_a = db.Column(db.Integer)
    final_v = db.Column(db.Integer)
    final_a = db.Column(db.Integer)
    eval = db.Column(db.Integer)
    recommend_rate = db.Column(db.Integer)


class UserMusic(db.Model):
    __tablename__ = 'user_music'
    uid = db.Column(db.Integer, primary_key=True)
    exp_num = db.Column(db.Integer, primary_key=True)
    music_num = db.Column(db.Integer, primary_key=True)
    mid = db.Column(db.Integer)
    v = db.Column(db.Integer)
    a = db.Column(db.Integer)
    score = db.Column(db.Integer)
    familiarity = db.Column(db.Integer)


class UserMemory(db.Model):
    __tablename__ = 'user_memory'
    uid = db.Column(db.Integer, primary_key=True)
    exp_num = db.Column(db.Integer, primary_key=True)
    music_num = db.Column(db.Integer, primary_key=True)
    memory = db.Column(db.Text())
    positive = db.Column(db.Float)
    negative = db.Column(db.Float)
    confidence = db.Column(db.Float)
    sentiment = db.Column(db.Integer)


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
    return "Success!"


@app.route('/<name>')
def hello(name):
    return 'it works! {0}'.format(name)


@app.route('/register', methods=['POST'])
def register():
    data = convert(request.data)
    name = data["uname"]
    pw = data["upw"]
    user_type = data["utype"]
    profession = data["profession"]
    age = data["age"]
    gender = data["gender"]
    expertise = data["expertise"]
    love_level = data["love_level"]

    user = User.query.filter_by(uname=name).first()
    if user is not None:
        return "User Already Exist!"
    new_user = User(uname=name, upw=pw, utype=user_type, profession=profession, age=age, gender=gender, expertise=expertise,
                    love_level=love_level)
    db.session.add(new_user)
    db.session.commit()
    return new_user.uname + "!!"


@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    data = convert(request.data)
    name = data["uname"]
    pw = data["upw"]

    user = User.query.filter_by(uname=name).first()
    if user is None:
        return "user name does not exist!"
    elif user.upw == pw:
        user_exp_num = UserExp.query.filter_by(uid=user.uid).order_by(UserExp.exp_num.desc()).first()
        if user_exp_num is None:
            return json.dumps({"u_id": str(user.uid), "exp_num": 0, "music_num": 0, "start_date": str(user.ustart)})
        # return str(user_exp_num.exp_num) + " " + str(user.ustart)
        if user_exp_num.exp_end is None:
            user_music_num = UserMusic.query.filter_by(uid=user.uid, exp_num=user_exp_num.exp_num).order_by(UserMusic.music_num.desc()).first()
            exp_past_time = datetime.datetime.now()-user_exp_num.exp_start
            duration = int(exp_past_time.total_seconds()/3600)
            if user_music_num is not None and duration < 3:
                v = user_music_num.v
                a = user_music_num.a
                result = music_recommend(0, v, a)
                return json.dumps({"u_id": str(user.uid), "exp_num": user_exp_num.exp_num, "music_num": user_music_num.music_num,"start_date": str(user.ustart), "v": v, "a": a, "mid": result[0], "mname": result[1], "murl": result[2], "mtype": result[3]})
            else:
                exp_num = user_exp_num.exp_num-1
                db.session.delete(user_exp_num)
                db.session.commit()
                return json.dumps({"u_id": str(user.uid), "exp_num": exp_num, "music_num": 0, "start_date": str(user.ustart)})
        return json.dumps({"u_id": str(user.uid), "exp_num": user_exp_num.exp_num, "music_num": 0, "start_date": str(user.ustart)})
    else:
        return 'Incorrect Password!'


@app.route('/music', methods=['POST'])
def music_playing():
    pass


@app.route('/experiment/start', methods=['POST'])
def start_experiment():
    data = convert(request.data)
    user_id = data["uid"]
    user_exp_num = data["exp_num"]
    init_v = data["initial_v"]
    init_a = data["initial_a"]
    exp_start = datetime.datetime.now()

    if user_exp_num == 1:
        user = User.query.filter_by(uid=user_id).first()
        user.ustart = exp_start
        db.session.commit()

    new_experiment = UserExp(uid=user_id, exp_num=user_exp_num, exp_start=exp_start, initial_a=init_a, initial_v=init_v)
    db.session.add(new_experiment)
    db.session.commit()
    result = music_recommend(0, 0, 0)
    return convert_music(result[0], result[1], result[2], result[3])


@app.route('/experiment/end', methods=['POST'])
def end_experiment():
    data = convert(request.data)
    user_id = data["uid"]
    user_exp_num = data["exp_num"]
    f_v = data["final_v"]
    f_a = data["final_a"]
    eva = data["evaluate"]
    rec = data["recommend_rate"]
    exp_end = datetime.datetime.now()

    exp = UserExp.query.filter_by(uid=user_id, exp_num=user_exp_num).first()
    exp.exp_end = exp_end
    exp.final_a = f_a
    exp.final_v = f_v
    exp.eval = eva
    exp.recommend_rate = rec
    db.session.commit()
    return "Successfully ended experiment!"


@app.route('/music/update', methods=['POST'])
def update_music():
    data = convert(request.data)
    user_id = data["uid"]
    user_exp_num = data["exp_num"]
    user_music_num = data["music_num"]
    music_id = data["mid"]
    valance = data["v"]
    arousal = data["a"]
    user_score = data["score"]
    user_fam = data["familiarity"]

    new_user_music = UserMusic(uid=user_id, exp_num=user_exp_num, music_num=user_music_num, mid=music_id, v=valance, a=arousal, score=user_score, familiarity=user_fam)
    db.session.add(new_user_music)
    db.session.commit()

    if user_music_num < 4:
        result = music_recommend(user_music_num, 0, 0)
        return convert_music(result[0], result[1], result[2], result[3])
    else:
        return "done!"


@app.route('/memory', methods=['POST'])
def update_memory():
    data = convert(request.data)
    user_id = data["uid"]
    user_exp_num = data["exp_num"]
    user_music_num = data["music_num"]
    user_mem = data["memory"]

    pos = get_sentiment_result(user_mem)['items'][0]['positive_prob']
    neg = get_sentiment_result(user_mem)['items'][0]['negative_prob']
    conf = get_sentiment_result(user_mem)['items'][0]['confidence']
    sent = get_sentiment_result(user_mem)['items'][0]['sentiment']
    # return str(pos) + " " + str(neg) + " " + str(conf) + " " + str(sent)

    new_memory = UserMemory(uid=user_id, exp_num=user_exp_num, music_num=user_music_num, memory=user_mem, positive=pos,
                            negative=neg, confidence=conf, sentiment=sent)
    db.session.add(new_memory)
    db.session.commit()
    return user_mem


def music_recommend(exp_num, music_num, utype, v, a):
    mid = 0
    if exp_num <= 2:
        if music_num == 1:
            music = Music.query.filter((Music.mtype == utype) & (Music.mv > v)).order_by(Music.mv.asc()).all()
            if music is []:
                music = Music.query.filter((Music.mtype == utype) & (Music.mv <= v)).order_by(
                    Music.mv.desc()).all()
            valence = music[0].mv
            arousal = (a - music[0].ma)**2
            mid = music[0].mid
            for i in music:
                if i.mv > valence + 1:
                    break
                temp_a = (a-i.ma)**2
                if temp_a < arousal:
                    arousal = temp_a
                    mid = i.mid

        else:
            pass
    else:
        if music_num == 1:
            pass
        else:
            pass

    music = Music.query.filter_by(mid=mid).first()
    print(str(music.mid) + " " + music.mname + " " + music.murl + " " + str(music.mtype))
    return [music.mid, music.mname, music.murl, music.mtype]


def convert_music(mid, mname, murl, mtype):
    return json.dumps(
        {"mid": mid, "mname": mname, "murl": murl, "mtype": mtype})


