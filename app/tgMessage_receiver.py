import json
import pickle
import time

group_ids = {}

from telethon import events

import config

client = config.get_client()
client.start()

if client:
  config.logging.info("client start")
with open("group_ids.json", 'r',encoding='utf-8') as f:
  group_ids = json.load(f, object_hook=config.custom_decoder)
  print(group_ids.keys())


@client.on(events.NewMessage(chats=list(group_ids.keys()), incoming=True))
async def handle_new_message(event):
  sender = await event.get_sender()
  message_text = event.message.message
  chat = await event.get_chat()
  sender_id = str(sender.id)
  sender_name = str(sender.first_name) + ' ' + str(sender.last_name)
  sender_username = str(sender.username)
  config.logging.info(
    f"get message {message_text} in chats {chat} by {sender_name}")
  if not sender or not hasattr(sender, 'bot') or sender.bot:
    return
  for keyword in config.data['keywords']:
    if len(message_text) > 10:
      return
    if keyword in message_text:
      title = -1000000000000 - chat.id
      data = {"keyword": keyword, "username": sender_username,
              "sender_name": sender_name, "sender_id": sender_id,
              "title": group_ids[title],
              "message_text": message_text,
              "datetime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
      config.logging.info(json.dumps(data))
      try:
        if config.data['auto_send']:
          await client.send_message(sender, config.data['message'])
          config.logging.info(sender_name + "   send success")
          config.save_message(sender_id, sender_name, sender_username,
                              group_ids[title], message_text, 'success',
                              pickle.dumps(sender))
        else:
          config.save_message(sender_id, sender_name, sender_username,
                              group_ids[title], message_text,
                              'error',
                              pickle.dumps(sender))
      except Exception as e:
        config.logging.exception(e)
        config.logging.error(sender_name + "   send faild")
        config.save_message(sender_id, sender_name, sender_username,
                            group_ids[title], message_text, 'error',
                            pickle.dumps(sender))
      return


config.logging.info(
    f"Listening for messages containing {config.data['keywords']} in chats {group_ids}...")
client.run_until_disconnected()
