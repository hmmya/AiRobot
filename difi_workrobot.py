# -*- coding: utf-8 -*-
"""
@Time ： 2023/5/11 23:40
@File ：difi_workrobot.py
@IDE ：PyCharm
@Version ：Python3
"""
# -*- coding: utf-8 -*-
import requests
import sys
import os
os.environ['NTWORK_LOG'] = "ERROR"
import ntwork

conversation_id_dict = {}
api_key = input("粘贴你在Dify创建应用的API密钥后按回车开始：")
conversation = int(input("群聊中是否同用一个会话，是输入1，否输入2："))


def send_message(query, user="", response_mode="blocking", conversation_id=None):
    global api_key
    url = 'https://api.dify.ai/v1/chat-messages'
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": {},
        "query": query,
        "user": user,
        "response_mode": response_mode,
    }
    if conversation_id:
        data["conversation_id"] = conversation_id

    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 200 :
        json_data = res.json()
        answer = json_data.get('answer')

        return {"answer":answer.strip(),"conversation_id":json_data.get('conversation_id')}
    else:
        return {"answer":"","conversation_id":None}



wework = ntwork.WeWork()
print("---------------仅支持企业微信4.0.8.6027版本---------------")
print("---------------启动程序后自动打开企业微信------------------")
# 打开pc企业微信, smart: 是否管理已经登录的微信
wework.open(smart=True)
print("---------------等待手动登录------------------------------")
# 等待登录
wework.wait_login()

info_data = (wework.get_self_info())
print(f"手机号码：{info_data.get('mobile')}")
print(f"用户名id：{info_data.get('user_id')}")
print(f"用户名：{info_data.get('username')}")
print("---------------机器人正常工作中---------------")

# 注册消息回调
@wework.msg_register(ntwork.MT_RECV_TEXT_MSG)
def on_recv_text_msg(wework_instance: ntwork.WeWork, message):
    global content_dict
    data = message["data"]

    sender_user_id = data["sender"]
    self_user_id = wework_instance.get_login_info()["user_id"]
    conversation_id: str = data["conversation_id"]


    # 判断消息不是自己发的并且不是群消息时，回复对方【私聊回复】
    if sender_user_id != self_user_id and not conversation_id.startswith("R:"):

        if len(data['content']) < 200 :
            # content_dict = send_message(data['content'])
            if conversation == 1:
                if conversation_id not in conversation_id_dict:
                    conversation_id_dict[conversation_id] = None

                content_dict = send_message(query=data['content'], conversation_id=conversation_id_dict[conversation_id])
                conversation_id_dict[conversation_id] = content_dict["conversation_id"]
            else:
                content_dict = send_message(query=data['content'])
        else:

            content_dict["answer"] = "发送文字请小于200个字符。"

        if content_dict["answer"] != "" :
            wework_instance.send_text(conversation_id=conversation_id,content=f' {content_dict["answer"]}')

    # 判断消息不是自己，同时为群聊消息，后面再判断有@自己，然后提取内容【群聊回复】
    if sender_user_id != self_user_id and  conversation_id.startswith("R:") :

        at_list =  [d['user_id'] for d in data["at_list"]]

        if self_user_id in at_list :
            content = data['content'].split("\u2005")[1]
            sender = data["sender"]
            if len(data['content']) < 200:
                if conversation == 1 :
                    if conversation_id not in conversation_id_dict :
                        conversation_id_dict[conversation_id] = None

                    content_dict = send_message(query=content, conversation_id=conversation_id_dict[conversation_id])
                    conversation_id_dict[conversation_id] = content_dict["conversation_id"]
                else:
                    content_dict = send_message(query=content)

            else:
                content_dict["answer"] = "发送文字请小于200个字符。"

            if content_dict["answer"] != "" :

                wework_instance.send_room_at_msg(conversation_id=conversation_id, content=f' {content_dict["answer"]}',at_list=[sender])



try:
    while True:
        pass
except KeyboardInterrupt:
    ntwork.exit_()
    sys.exit()