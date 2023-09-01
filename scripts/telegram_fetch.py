import asyncio
import sqlite3
import json
import os
from datetime import datetime
from telethon.sync import TelegramClient
from googletrans import Translator
from misc_scripts import secrets

API_ID = os.environ["TELEGRAM_API_ID"]
API_HASH = os.environ["TELEGRAM_API_HASH"]
PHONE_NUMBER = os.environ["TELEGRAM_PHONE_NUMBER"]
DB_PATH = "/var/csirt/source/CVE-WEB/db.sqlite3"


# Channels:
# NoName057
# DDOSIA Project
# WeAreKillNET

CHANNEL_LINKS = [
    'https://t.me/noname05716',
    'https://t.me/+fiTz615tQ6BhZWFi',
    'https://t.me/killnetl'
]

def load_last_message_ids():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT channel_link, last_message_id FROM alerts_telegramdataids")
    ids = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    return ids

def save_last_message_ids(ids):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for channel_link, last_message_id in ids.items():
        cursor.execute("INSERT OR REPLACE INTO alerts_telegramdataids (channel_link, last_message_id) VALUES (?, ?)", (channel_link, last_message_id))
    
    conn.commit()
    conn.close()

async def fetch_messages_from_channels():
    last_message_ids = load_last_message_ids()

    async with TelegramClient('anon', API_ID, API_HASH) as client:
        for channel_link in CHANNEL_LINKS:
            channel = await client.get_entity(channel_link)
            
            offset_id = last_message_ids.get(channel_link, None)
            messages = await client.get_messages(channel, limit=None, offset_id=offset_id)
            
            if messages:
                last_message_ids[channel_link] = messages[0].id
            
            insert_messages_into_db(messages, channel.title)

    save_last_message_ids(last_message_ids)

def insert_messages_into_db(messages, channel_name):
    translator = Translator()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Reverse the messages order so the oldest ones are processed first
    for message in reversed(messages):
        translated_text = translator.translate(message.text, dest='en').text
        data = {
            "Sender ID": message.sender_id,
            "Username": getattr(message.sender, 'username', 'N/A'),
            "Date": str(message.date),
            "Message ID": message.id,
            "Views": getattr(message, 'views', 'N/A'),
            "Replying to Message ID": getattr(message, 'reply_to_msg_id', 'N/A'),
            "Forwarded from ID": getattr(message.forward, 'sender_id', 'N/A') if message.forward else 'N/A',
            "Forwarded Date": str(getattr(message.forward, 'date', 'N/A')) if message.forward else 'N/A',
        }
        cursor.execute("""
            INSERT INTO alerts_telegramdata (channel, message, message_translated, message_data, date_added)
            VALUES (?, ?, ?, ?, ?)
        """, (channel_name, message.text, translated_text, json.dumps(data), datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()

asyncio.run(fetch_messages_from_channels())
