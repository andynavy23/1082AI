# 1082AI
## 以Heroku建立課程助教聊天機器人

### 功能：
 - 雲端執行（Heroku）
 - 連接資料庫（Mongodb）
 - 聊天記錄LOG
 - 特定條件下主動傳送訊息
 - 回復規則（package：exec）

### 開發環境與工具：
 - Mac Pro（開發電腦）
 - Python（程式語言）
 - Mongodb（資料庫連接）
 - Heroku（雲端託管執行）
 - Ngrok（本地開發測試）
 - Lin BOT（聊天機器人框架）
 - Robo 3T（資料庫GUI介面）

### 相關套件（可以參考 requirements.txt）：
 - Flask
 - line-bot-sdk
 - pymongo
 - requests
 - gunicorn

### 資料庫格式（Heroku 擴充功能 mLab MongoDB）：
 - users（Collection）
    - groupID（群組ID）
    - userID（使用者ID）
    - display_name（使用者名稱）
    - picture_url（使用者大頭照圖片連結）
    - status_message（使用者狀態內容）
    - join_datetime（加入使用者資料時間點）
 - groups（Collection）
    - groupID（群組ID）
    - datetime（加入群組時間點）
 - rules（Collection）
    - keyword（觸發規則關鍵字）
    - rule（規則）
    - output（輸出結果）
 - log（Collection）
    - userID（使用者ID）
    - messageID（說話內容ID）
    - text（說話內容）
    - message_type（說話類型：text、img、video．．．）
    - source_type（說話來源類型：user、group）
    - datetime（說話紀錄時間點）

### Demo：
1. 在 Heroku 上創建好資料庫後於本地端使用GUI連接確認後續資料有無更新
    - GUI畫面  
    ![創建資料庫](/img/創建資料庫.png)

2. 邀請機器人加入LINE課程群組，機器人會分辨是否加入過此群組同時通知管理者加入一個群組。
     - 加入群組會先在群組裡面跟大家打招呼  
     ![加入群組打招呼](/img/加入群組打招呼.png)
     - 將groupID、datetime加入資料庫（groups），並且發送訊息給管理者  
     ![通知管理者加入群組](/img/通知管理者加入群組.png)

3. 透過「報到」指令抓取使用者資料加入資料庫（users）
     - 使用者給予「報到」指令  
     ![使用者給予報到指令]](/img/使用者給予報到指令.png)
     - 機器人判斷說話內容為「報到」指令抓取userID等資訊加入資料庫  
     ![機器人將使用者資料加入資料庫](/img/機器人將使用者資料加入資料庫.png)
     - 機器人比對是否報導過，提醒使用者不用重複報到  
     ![機器人提醒重複報到](/img/機器人提醒重複報到.png)

4. 查看資料庫是否有資料匯入
    - GUI畫面  
    ![資料庫更新](/img/資料庫更新.png)

5. 新增規則至資料庫（單筆規則新增）
    - [網頁表單](https://ai1082.herokuapp.com/)使用GET Form，需要填入關鍵字、規則、輸出等資訊
    ![網頁表單](/img/網頁表單.png)
    - 關鍵字1：通知
    - 規則1：line_bot_api.push_message(admin_user_id,TextMessage(text='有人剛叫我通知你！'))
    - 輸出1：通知管理員
    ![關鍵字1](/img/關鍵字1.png)
    - 關鍵字2：檢舉
    - 規則2：line_bot_api.push_message(admin_user_id,TextMessage(text='有人剛叫我檢舉你！'))
    - 輸出2：檢舉管理員
    ![關鍵字2](/img/關鍵字2.png)

6. 機器人判斷訊息內容是否包含關鍵字，進而觸發規則產生輸出  
    - 只有關鍵字  
    ![只有關鍵字](/img/只有關鍵字.png)  
    - 內容包含關鍵字  
    ![內容包含關鍵字](/img/內容包含關鍵字.png)  
    - 規則輸出  
    ![規則輸出](/img/規則輸出.png)  
    - 訊息包含多個關鍵字  
    ![多個關鍵字](/img/多個關鍵字.png)  
    - 兩個規則輸出  
    ![兩個規則輸出](/img/兩個規則輸出.png)  


### 程式碼說明：
#### 執行主程式 app.py
```Python
# -*- coding: utf-8 -*-

## 套件模板匯入
from __future__ import unicode_literals
# about system import
import time
import errno
import os
import sys
import tempfile
from argparse import ArgumentParser
# about Flask import
from flask import Flask, request, abort
# about linebot import
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup,MessageAction,
    PostbackAction, DatetimePickerAction,
    StickerMessage, StickerSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    JoinEvent,ImageComponent, BoxComponent,
    TextComponent,ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton
)
# about mongodb import
from pymongo import MongoClient
from bson.objectid import ObjectId 

## 資料庫設定與連接
db_name = 'Mongodb資料庫名稱'
db_host = 'Mongodb連接資料庫URL'
db_port = Mongodb連接PORT
db_user = 'Mongodb使用者名稱'
db_pass = 'Mongodb使用者密碼'
client = MongoClient(db_host,db_port,retryWrites=False)
db = client[db_name]
db.authenticate(db_user,db_pass)
# 將連接的collection存入變數
users_db = db['users']
groups_db = db['groups']
rules_db = db['rules']
log_db = db['log']

app = Flask(__name__)

## 環境變數設定
admin_user_id = 'your admin LINE user ID'
channel_secret = 'your channel secret'
channel_access_token = 'your channel access token'
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

## 首頁
@app.route('/')
def index():
    return render_template('index.html')

## 設定POST請求位置與例外發生時回覆的訊息函式
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'

## 加入訊息事件發生時需要如何回覆的函式
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text # 訊息事件發生時的訊息內容
    userID = event.source.user_id # 訊息事件發生時的發訊息的使用者ID
    profile = line_bot_api.get_profile(event.source.user_id) # 訊息事件發生時的發訊息使用者相關資訊
    try:
        groupID = event.source.group_id # 訊息事件發生時的群組ID
    except:
        pass
    # 將每筆聊天記錄存成字典
    log_info = {"userID": userID,
                "messageID": event.message.id,
                "text": text,
                "message_type": event.message.type,
                "source_type": event.source.type,
                "datetime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
    # 加入資料集合中
    log_db.insert_one(log_info)
    # 判斷聊天內容是否為指令
    if text == '報到':
        if isinstance(event.source, SourceGroup):
             # 比對報到者資料是否已經存在
            user_match_output = users_db.find_one({"userID": userID})
            if user_match_output == None:
                user_info = {"groupID": groupID,
                            "userID": userID,
                            "display_name": profile.display_name,
                            "picture_url": profile.picture_url,
                            "status_message": profile.status_message,
                            "join_datetime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
                users_db.insert_one(user_info)
                line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text=profile.display_name + '的資料登記完成！'),
                    ]
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text=profile.display_name + '的資料已經登記過了喔！'),
                    ]
                )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="資料登記失敗，請聯絡老師或助教！！"))
    elif len(keyword_match_output) != 0:
        # function for exec
        def func():
            exec(rule_string)
        for rule_data in keyword_match_output:
            rule_string = str(rule_data['rule'])
            func()
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='觸發規則～'))
    else:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='Echo mode: ' + event.message.text))

## 加入群組事件發生時機器人會做的事情的函式
@handler.add(JoinEvent)
def handle_join(event):
    # 設定加入群組打招呼的罐頭訊息
    newcoming_text = "謝謝邀請我這個機器來此群組！！我會盡力為大家服務的～"
    # 將每筆加入群組紀錄存成字典
    groupID = {"groupID": event.source.group_id, "datetime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
    # 加入資料集合中
    groups_db.insert_one(groupID)
    line_bot_api.push_message(admin_user_id,TextMessage(text='剛加入一個群組已將groupID存入資料庫！'))
    
    line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=newcoming_text)
        )

## 新增規則資料設定 
@app.route("/rules", methods=['GET'])
def rules():
    keyword = request.args.get('keyword')
    rule = request.args.get('rule')
    output = request.args.get('output')
    keyword_match_output = rules_db.find_one({"keyword": keyword})
    if keyword_match_output is None:
        rule_info = {"keyword": keyword,
                     "rule": rule,
                     "output": output}
        rules_db.insert_one(rule_info)
        return "Rule added to database successfully !!"
    else:
        return "Rule addition to database failed !!"


## 設定 Web App 開啟的 Domain 與 Port
if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    # 設置監聽端口
    arg_parser.add_argument('-p', '--port', type=int, default=5000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()
    # 設置網域
    app.run(host='0.0.0.0')
```
