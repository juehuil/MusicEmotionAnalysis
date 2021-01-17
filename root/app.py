# creating Flask instance variable app
from ast import literal_eval
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin

from root.helpers import *
import datetime
import json
import numpy
import random

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
    pv = db.Column(db.Integer)
    pa = db.Column(db.Integer)
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
                result = music_recommend(user_exp_num.exp_num, user_music_num.music_num+1, user.uid, v, a)
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
    result = music_recommend(user_exp_num, 1, user_id, init_v, init_a)
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
    pv = -10
    pa = -10
    user_score = data["score"]
    user_fam = data["familiarity"]

    if user_exp_num >= 3:
        result = get_new_va(user_exp_num, user_music_num, user_id, music_id)
        pv = result[0]
        pa = result[1]

    new_user_music = UserMusic(uid=user_id, exp_num=user_exp_num, music_num=user_music_num, mid=music_id, v=valance, a=arousal, pv=pv, pa=pa, score=user_score, familiarity=user_fam)
    db.session.add(new_user_music)
    db.session.commit()

    if user_music_num < 4:
        result = music_recommend(user_exp_num, user_music_num+1, user_id, valance, arousal)
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


def music_recommend(exp_num, music_num, uid, v, a):
    user = User.query.filter_by(uid=uid).first()
    utype = user.utype
    mid = 0
    if exp_num <= 2:
        if music_num == 1:
            music = Music.query.filter((Music.mtype == utype) & (Music.mv > v)).order_by(Music.mv.asc()).all()
            print("music" + str(music))
            if not music:
                music = Music.query.filter((Music.mtype == utype) & (Music.mv <= v)).order_by(
                    Music.mv.desc()).all()

            valence = music[0].mv
            arousal = (a - music[0].ma)**2
            mid = music[0].mid
            for i in music:
                if i.mv > valence + 1 or i.mv < valence - 1:
                    break
                temp_a = (a-i.ma)**2
                if temp_a < arousal:
                    arousal = temp_a
                    mid = i.mid

        else:
            user_mem = UserMemory.query.filter_by(uid=uid, exp_num=exp_num, music_num=music_num-1).first()
            user_mus = UserMusic.query.filter_by(uid=uid, exp_num=exp_num, music_num=music_num-1).first()
            v = user_mus.v
            a = user_mus.a
            last_mid = user_mus.mid
            if user_mem:
                v = v + (user_mem.positive-0.5) * 5
            music = Music.query.filter(Music.mv > v).order_by(Music.mv.asc()).all()
            print("music" + str(music))
            if not music:
                music = Music.query.filter(Music.mv <= v).order_by(Music.mv.desc()).all()

            arousal = 10000
            mid = -1
            for i in music:
                if i.mv > music[0].mv + 1 or i.mv < music[0].mv - 1:
                    break
                temp_a = (a - i.ma) ** 2
                if i.mid != last_mid and temp_a < arousal:
                    arousal = temp_a
                    mid = i.mid
    else:
        if music_num == 1:
            user_mus = UserMusic.query.filter_by(uid=uid).all()
            scores = [0.003, 0.003, 0.003]
            count = [0.001, 0.001, 0.001]
            for i in user_mus:
                mus = Music.query.filter_by(mid=i.mid).first()
                count[mus.mtype-1] += 1
                scores[mus.mtype-1] += i.score
            for i in range(0, 3):
                scores[i] = float(scores[i])/count[i]
                scores[i] = int(scores[i]*10)
            print(str(scores[0]) + " " + str(scores[1]) + " " + str(scores[2]))
            total = scores[0] + scores[1] + scores[2]
            rand_num = random.randint(0, total)
            mtype = 3
            if rand_num < scores[0]:
                mtype = 1
            elif rand_num < scores[0] + scores[1]:
                mtype = 2
            print(str(rand_num) + " " + str(mtype) + " " + str(total))
            music = Music.query.filter((Music.mtype == mtype) & (Music.mv > v)).order_by(Music.mv.asc()).all()
            print("music" + str(music))
            if not music:
                music = Music.query.filter((Music.mtype == mtype) & (Music.mv <= v)).order_by(
                    Music.mv.desc()).all()

            valence = music[0].mv
            arousal = (a - music[0].ma)**2
            mid = music[0].mid
            for i in music:
                if i.mv > valence + 1 or i.mv < valence - 1:
                    break
                temp_a = (a-i.ma)**2
                if temp_a < arousal:
                    arousal = temp_a
                    mid = i.mid

        else:
            user_mus = UserMusic.query.filter_by(uid=uid).all()
            scores = [0.003, 0.003, 0.003]
            count = [0.001, 0.001, 0.001]
            for i in user_mus:
                mus = Music.query.filter_by(mid=i.mid).first()
                count[mus.mtype - 1] += 1
                scores[mus.mtype - 1] += i.score
            for i in range(0, 3):
                scores[i] = float(scores[i]) / count[i]
                scores[i] = int(scores[i] * 10)
            print(str(scores[0]) + " " + str(scores[1]) + " " + str(scores[2]))
            total = scores[0] + scores[1] + scores[2]
            rand_num = random.randint(0, total)
            mtype = 3
            if rand_num < scores[0]:
                mtype = 1
            elif rand_num < scores[0] + scores[1]:
                mtype = 2
            print(str(rand_num) + " " + str(mtype) + " " + str(total))
            music = Music.query.filter((Music.mtype == mtype) & (Music.mv > v)).order_by(Music.mv.asc()).all()
            print("music" + str(music))
            if not music:
                music = Music.query.filter((Music.mtype == mtype) & (Music.mv <= v)).order_by(
                    Music.mv.desc()).all()

            valence = music[0].mv
            arousal = (a - music[0].ma) ** 2
            mid = music[0].mid
            for i in music:
                if i.mv > valence + 1 or i.mv < valence - 1:
                    break
                temp_a = (a - i.ma) ** 2
                if temp_a < arousal:
                    arousal = temp_a
                    mid = i.mid

    music = Music.query.filter_by(mid=mid).first()
    print(str(music.mid) + " " + music.mname + " " + music.murl + " " + str(music.mtype))
    return [music.mid, music.mname, music.murl, music.mtype]


def convert_music(mid, mname, murl, mtype):
    return json.dumps(
        {"mid": mid, "mname": mname, "murl": murl, "mtype": mtype})


def get_new_va(exp_num, music_num, uid, mid):
    total_delta_v = 0
    total_delta_a = 0

    for i in range(1, exp_num):
        print("exp num: " + str(i))
        init_exp = UserExp.query.filter((UserExp.uid == uid)&(UserExp.exp_num == i)).first()
        init_v = init_exp.initial_v
        init_a = init_exp.initial_a
        user_music = UserMusic.query.filter((UserMusic.uid == uid)&(UserMusic.exp_num == i)).order_by(UserMusic.music_num.asc()).all()
        u_music_v = [-10, -10, -10, -10]
        u_music_a = [-10, -10, -10, -10]
        music_v = [-10, -10, -10, -10]
        music_a = [-10, -10, -10, -10]
        for i in range(0, 4):
            print("\tmusic_num: " + str(i))
            u_music_v[i] = user_music[i].v
            u_music_a[i] = user_music[i].a
            mus = Music.query.filter_by(mid=i+1).first()
            music_v[i] = mus.mv
            music_a[i] = mus.ma
        pre_music_v = [init_v, u_music_v[0], u_music_v[1], u_music_v[2]]
        pre_music_a = [init_a, u_music_a[0], u_music_a[1], u_music_a[2]]
        delta_v = 0
        delta_a = 0
        for i in range(0, 4):
            temp_v = (u_music_v[i]-pre_music_v[i]+0.5)/(music_v[i]-pre_music_v[i]+0.5)
            delta_v += temp_v
            temp_a = (u_music_a[i] - pre_music_a[i] + 0.5) / (music_a[i] - pre_music_a[i] + 0.5)
            delta_a += delta_a
            print("\ttemp v: " + str(temp_v) + "\ttemp a: " + str(temp_a))

        total_delta_v += (delta_v/4)
        total_delta_a += (delta_a/4)
        print("total delta v: " + str(total_delta_v) + "\ttotal delta a: " + str(total_delta_a))

    total_delta_v = total_delta_v/(exp_num-1)
    total_delta_a = total_delta_a/(exp_num-1)
    print("total_delta_v: " + str(total_delta_v) + "\ttotal_delta_a: " + str(total_delta_a))

    current_mus = Music.query.filter_by(mid=mid).first()
    current_mus_v = current_mus.mv
    current_mus_a = current_mus.ma
    print("current_mus_v: " + str(current_mus_v) + "\tcurrent_mus_a: " + str(current_mus_a))

    current_pre_v = 0
    current_pre_a = 0
    if music_num == 1:
        current_pre_v = UserExp.query.filter((UserExp.uid == uid)&(UserExp.exp_num == exp_num)).first().initial_v
        current_pre_a = UserExp.query.filter((UserExp.uid == uid) & (UserExp.exp_num == exp_num)).first().initial_a
    else:
        current_pre_v = UserMusic.query.filter((UserMusic.uid == uid)&(UserMusic.exp_num == exp_num)&(UserMusic.music_num==music_num-1)).first().pv
        current_pre_a = UserMusic.query.filter((UserMusic.uid == uid) & (UserMusic.exp_num == exp_num) & (UserMusic.music_num == music_num-1)).first().pa
    print("current_pre_v: " + str(current_pre_v) + "\tcurrent_pre_a: " + str(current_pre_a))
    predict_v = int(total_delta_v * (current_mus_v-current_pre_v) + current_pre_v)
    predict_a = int(total_delta_a * (current_mus_a-current_pre_a) + current_pre_a)
    print("predict_v: " + str(predict_v) + "\tpredict_a: " + str(predict_a))
    return [predict_v, predict_a]


def get_w(uid):
    user_mem = UserMemory.query.filter_by(uid=uid).all()
    w = 0
    count = 0.01
    for i in user_mem:
        mem = i.positive-0.5
        user_mus = UserMusic.query.filter_by(uid=i.uid, exp_num=i.exp_num, music_num=i.music_num).first()
        user_v = user_mus.v
        music_v = Music.query.filter_by(mid=user_mus.mid).first().mv
        w += (user_v-music_v)/mem
        count +=1
    w = w/count
    return w



