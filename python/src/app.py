from flask import Flask, jsonify
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_cors import CORS
import os
import logging

from assistant.assistant import Assistant
from assistant.db import init_db, get_messages_by_chatid, get_all_chats, insert_chat, update_chat, get_chat_by_id, delete_chat


app = Flask(__name__)
CORS(app) # 開発環境用のCORS許可設定
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "default_secret_key")
app.json.ensure_ascii = False
app.logger.setLevel(logging.INFO)
socketio = SocketIO(app, cors_allowed_origins="*")

# クライアントがサーバーに接続した際のイベントハンドラ
@socketio.on('connect')
def handle_connect():
    app.logger.info("connect")

# チャットルームに参加するイベントハンドラ
@socketio.on('join')
def join(msg):
    join_room(str(msg["room"]))
    app.logger.info(f'user join room: {msg["room"]}')

# チャットルームから退出するイベントハンドラ
@socketio.on('leave')
def join(msg):
    leave_room(str(msg["room"]))
    app.logger.info(f'user leave room: {msg["room"]}')

# ユーザーからのチャットメッセージを処理しAIのメッセージを生成するイベントハンドラ
@socketio.on('chatMessage')
def handle_message(msg):
    app.logger.info("user message: {}".format(msg))
    if msg is not None:
        if get_chat_by_id(msg['chatid']) == None:
            chatid = msg['chatid']
            app.logger.error(f'chatid is not exist: {chatid}')
            emit(
                'chatMessage',
                {
                    'chatid': chatid,
                    'type': 'ai',
                    'message': f'このチャット(id: {chatid})は存在しないようです。'
                },
                broadcast=True,
                room=str(msg["chatid"])
            )
            return
        emit('chatMessage', msg, broadcast=True, room=str(msg["chatid"]))

        # AI応答を生成し、クライアントにブロードキャスト
        assistant = Assistant(msg['chatid'])
        assistant_msg = assistant.generate_response(msg['message'])
        emit('chatMessage', assistant_msg, broadcast=True, room=str(msg["chatid"]))
        app.logger.info("assistant message: {}".format(assistant_msg))

# 特定のチャットルームの履歴を取得するエンドポイント
@app.route('/chat-history/<chatid>', methods=['GET'])
def get_chat_history(chatid):
    history = get_messages_by_chatid(chatid)
    if history is None:
        return jsonify([])
    else :
        history = [{
            'chatid': chatid,
            'type': h['type'],
            'message': h['data']['content']
        } for h in history]
        app.logger.info("history: {}".format(history))
        return jsonify(history)

# 特定のチャットルームの情報を取得するエンドポイント
@app.route('/chat/<chatid>', methods=['GET'])
def get_chat(chatid):
    chat = get_chat_by_id(chatid)
    app.logger.info("chat: {}".format(chat))
    return jsonify(chat)

# 特定のチャットルームを削除するエンドポイント
@app.route('/chat/<chatid>', methods=['DELETE'])
def del_chat(chatid):
    delete_chat(chatid)
    return jsonify({})

# 特定のチャットルーム一覧を取得するエンドポイント
@app.route('/chat', methods=['GET'])
def get_chat_list():
    chats = get_all_chats()
    app.logger.info(f'chat list: {chats}')
    return jsonify(chats)

# チャットルームを追加するエンドポイント
@app.route('/chat', methods=['POST'])
def add_chat():
    title = ''
    chatid = insert_chat(title)
    update_chat(chatid, f'チャット {chatid}')
    app.logger.info(f'add chat: {chatid}')
    return jsonify(chatid)

if __name__ == "__main__":
    app.logger.info("server start")
    init_db()
    socketio.run(app, host='0.0.0.0', port=8080, use_reloader=True, debug=True)