from root.app import *
import json
import requests


def get_sentiment_result(text):
    """
    利用情感倾向分析API来获取返回数据
    :param text: 输入文本
    :return response: 返回的响应
    """
    if text == '':
        return ''
    # 请求接口
    url = 'https://aip.baidubce.com/oauth/2.0/token'
    # 需要先获取一个 token
    client_id = 'aKaEp6HGGA3aPXL4YGQifvq5'
    client_secret = '69fr24InE6HQgeZRfNXrHykN1g6zxvBs'
    params = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    response = requests.post(url=url, params=params, headers=headers).json()
    access_token = response['access_token']

    # 通用版情绪识别接口
    url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify'
    # 定制版情绪识别接口
    # url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify_custom'
    # 使用 token 调用情感倾向分析接口
    params = {
        'access_token': access_token
    }
    payload = json.dumps({
        'text': text
    })
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    response = requests.post(url=url, params=params, data=payload, headers=headers).json()
    return response


def get_new_va(exp_num, music_num, uid, mid):
    total_delta_v = 0
    total_delta_a = 0

    for i in range(1, exp_num):
        init_exp = UserExp.query.filter((UserExp.uid == uid)&(UserExp.exp_num == i)).first()
        init_v = init_exp.initial_v
        init_a = init_exp.initial_a
        user_music = UserMusic.query.filter((UserMusic.uid == uid)&(UserMusic.exp_num == i)).order_by(UserMusic.music_num.asc()).all()
        u_music_v = [-10, -10, -10, -10]
        u_music_a = [-10, -10, -10, -10]
        music_v = [-10, -10, -10, -10]
        music_a = [-10, -10, -10, -10]
        for i in range(0, 4):
            u_music_v[i] = user_music[i].v
            u_music_a[i] = user_music[i].a
            mus = Music.query.filter_by(mid=i.mid).first()
            music_v[i] = mus.v
            music_a[i] = mus.a
        pre_music_v = [init_v, u_music_v[0], u_music_v[1], u_music_v[2]]
        pre_music_a = [init_a, u_music_a[0], u_music_a[1], u_music_a[2]]
        delta_v = 0
        delta_a = 0
        for i in range(0, 4):
            delta_v += (u_music_v[i]-pre_music_v[i]+0.5)/(music_v[i]-pre_music_v[i]+0.5)
            delta_a += (u_music_a[i] - pre_music_a[i] + 0.5) / (music_a[i] - pre_music_a[i] + 0.5)
        total_delta_v += delta_v/4
        total_delta_a += delta_a/4

    total_delta_v = total_delta_v/(exp_num-1)
    total_delta_a = total_delta_a/(exp_num-1)

    current_mus = Music.query.filter_by(mid=mid).first()
    current_mus_v = current_mus.v
    current_mus_a = current_mus.a

    current_pre_v = 0
    current_pre_a = 0
    if music_num == 1:
        current_pre_v = UserExp.query.filter((UserExp.uid == uid)&(UserExp.exp_num == exp_num)).first().v
        current_pre_a = UserExp.query.filter((UserExp.uid == uid) & (UserExp.exp_num == exp_num)).first().a
    else:
        current_pre_v = UserMusic.query.filter((UserMusic.uid == uid)&(UserMusic.exp_num == exp_num)&(UserMusic.music_num==music_num)).first().pv
        current_pre_a = UserMusic.query.filter((UserMusic.uid == uid) & (UserMusic.exp_num == exp_num) & (UserMusic.music_num == music_num)).first().pa

    predict_v = total_delta_v * (current_mus_v-current_pre_v) + current_pre_v
    predict_a = total_delta_a * (current_mus_a-current_pre_a) + current_pre_a

    return predict_v, predict_a


def get_new_a(exp_num, music_num, uid):
    return -20


def add_music(name, url, type, v, a):
    new_music = Music(mname=name, murl=url, mtype=type, mv=v, ma=a)
    db.session.add(new_music)
    db.session.commit()
    print("success")


def read_musics(file_name):
    f = open(file_name, "r")
    for x in f:
        x = x.strip('\n')
        chunks = x.split(',')
        name = chunks[0]
        url = chunks[1]
        type = int(chunks[2])
        v = int(chunks[3])
        a = int(chunks[4])
        print(name + " " + url + " " + str(type) + " " + str(v) + " " + str(a))
        add_music(name, url, type, v, a)


if __name__ == '__main__':
    print(get_sentiment_result('白日放歌须纵酒，青春作伴好还乡。'))
    print(get_sentiment_result('思悠悠，恨悠悠，恨到归时方始休。'))
