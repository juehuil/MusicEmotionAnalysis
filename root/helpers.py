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

#
# if __name__ == '__main__':
#     print(get_sentiment_result('白日放歌须纵酒，青春作伴好还乡。'))
#     print(get_sentiment_result('思悠悠，恨悠悠，恨到归时方始休。'))
