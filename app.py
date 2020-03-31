# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from __future__ import unicode_literals

import time
import errno
import os
import sys
import tempfile
from argparse import ArgumentParser
# about Flask import
from flask import Flask, request, abort, render_template

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton
)

# about mongodb import
from pymongo import MongoClient
from bson.objectid import ObjectId 

# connection mongodb
db_name = 'heroku_tt6tdsz7'
db_host = 'ds029426.mlab.com'
db_port = 29426
db_user = 'heroku_tt6tdsz7'
db_pass = 'nd5f0njm3jh544ph8pmp32uo6i'
client = MongoClient(db_host,db_port,retryWrites=False)
db = client[db_name]
db.authenticate(db_user,db_pass)
users_db = db['users']
groups_db = db['groups']
rules_db = db['rules']
log_db = db['log']

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = '44438605c6135fcaae7ef26a8840c83e'
channel_access_token = 'cyhHv06/QDhSh9KpiYzhxQxJNcn4/UqgWazZxVDMG9fTTODbCiGLTX6otM03nf+NG/inIA43HS5aO1fdDifm3YGkpG4ZlPkDTO1Q4bfwNNSEYTkdMSqMwS/8H3mpJ+G+cQmbY4r69sY7XeWIiYyVawdB04t89/1O/w1cDnyilFU='
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

admin_user_id = 'U63ab88ce90a6b2780293fec894a99ac2'
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')


# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    # handle webhook body
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


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    userID = event.source.user_id
    profile = line_bot_api.get_profile(event.source.user_id)
    keyword_match_output = []
    for x in rules_db.find():
        if x['keyword'] in text:
            keyword_match_output.append(x)
    try:
        groupID = event.source.group_id
    except:
        pass
    log_info = {"userID": userID,
                "messageID": event.message.id,
                "text": text,
                "message_type": event.message.type,
                "source_type": event.source.type,
                "datetime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
    log_db.insert_one(log_info)

    if text == '報到':

        if isinstance(event.source, SourceGroup):
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

@handler.add(JoinEvent)
def handle_join(event):
    newcoming_text = "謝謝邀請我這個機器來此群組！！我會盡力為大家服務的～"
    groupID = {"groupID": event.source.group_id, "datetime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
    
    groups_db.insert_one(groupID)
    line_bot_api.push_message(admin_user_id,TextMessage(text='剛加入一個群組已將groupID存入資料庫！'))
    
    line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=newcoming_text)
        )
    
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


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=5000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    # create tmp dir for download content
    make_static_tmp_dir()

    
    #app.run(host='0.0.0.0',debug=options.debug, port=options.port,ssl_context='adhoc')
    app.run(host='0.0.0.0')