import json
import sqlite3
import time
from flask import g

DATABASE = 'database.db'

def get_db():
    conn  = getattr(g, '_database', None)
    if conn is None:
        conn  = g._database = sqlite3.connect(DATABASE)
    return conn

def init_db():
    conn  = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # chat table作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY,
        title TEXT,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # message table作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS message (
        chatid INTEGER PRIMARY KEY,
        messages TEXT
    )
    ''')
    conn.close()

# チャットを挿入する関数
def insert_chat(title):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO chat (title) VALUES (?)', (title,))
    conn.commit()
    return cursor.lastrowid

# チャットを更新する関数
def update_chat(chat_id, new_title):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE chat SET title = ? WHERE id = ?', (new_title, chat_id))
    conn.commit()

# すべてのチャットを取得する関数
def get_all_chats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chat')
    chats = []
    
    for row in cursor.fetchall():
        chat = dict(zip([column[0] for column in cursor.description], row))
        
        # createdAtをUNIXタイムスタンプに変換
        if 'createdAt' in chat:
            chat['createdAt'] = int(time.mktime(time.strptime(chat['createdAt'], '%Y-%m-%d %H:%M:%S')))
        
        chats.append(chat)
    
    return chats

def get_chat_by_id(chat_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chat WHERE id = ?', (chat_id,))
    
    row = cursor.fetchone()
    
    if row is not None:
        chat = dict(zip([column[0] for column in cursor.description], row))
        
        # createdAtをUNIXタイムスタンプに変換
        if 'createdAt' in chat:
            chat['createdAt'] = int(time.mktime(time.strptime(chat['createdAt'], '%Y-%m-%d %H:%M:%S')))
        
        return chat
    else:
        return None

# チャットを削除する関数
def delete_chat(chat_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chat WHERE id = ?', (chat_id,))
    cursor.execute('DELETE FROM message WHERE chatid = ?', (chat_id,))
    conn.commit()

# メッセージの挿入
def insert_message(chatid, messages):
    conn = get_db()
    cursor = conn.cursor()
    messages_json = json.dumps(messages)
    cursor.execute('INSERT OR REPLACE INTO message (chatid, messages) VALUES (?, ?)', (chatid, messages_json))
    conn.commit()

# メッセージの取得
def get_messages_by_chatid(chatid):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT messages FROM message WHERE chatid = ?', (chatid,))
    row = cursor.fetchone()
    if row:
        messages_json = row[0]
        return json.loads(messages_json)
    else:
        return None

