import datetime
import json
import logging
import os

import pymysql
from dbutils.pooled_db import PooledDB
from telethon import TelegramClient

# 检查是否存在 config.json
if os.path.exists('config.json'):
  filename = 'config.json'
else:
  filename = 'config.json.template'

# 从文件中读取JSON数据
with open(filename, 'r') as file:
  data = json.load(file)

pool = PooledDB(
    creator=pymysql,
    host=data["mysql_ip"],
    mincached=2,
    maxconnections=50,
    blocking=True,
    port=data["mysql_port"],
    user=data["mysql_user"],
    password=data["mysql_pass"],
    database=data["mysql_database"]
)

def get_client():
  return TelegramClient(data['session_name'], data['api_id'],
                        data['api_hash'], timeout=60, proxy=(
      'socks5', data['proxy_ip'], data['proxy_port']))


logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s',
                    filename='log.log', filemode='a', encoding='utf-8',
                    level=logging.INFO)


def custom_decoder(dct):
  return {int(k): v for k, v in dct.items()}


def save_message(sender_id, sender_name, username, group_username, message,
    send_flag, sender):
  conn = pool.connection()
  cursor = conn.cursor()
  try:
    sql = "insert into message (sender_id,sender_name,username,group_username,message,send_flag,sender,date_time) values (%s,%s,%s,%s,%s,%s,%s,%s)"
    current_time = datetime.datetime.now()
    cursor.execute(sql,
                   (sender_id, sender_name, username, group_username, message,
                    send_flag, sender, current_time))
    conn.commit()
  except Exception as e:
    logging.error("insert faild")
    logging.exception(e)
  finally:
    cursor.close()
    conn.close()


def get_total(data, startTime, endTime):
  conn = pool.connection()
  cursor = conn.cursor()
  try:
    sql = f"select count(*) from message where TRUE"
    for each in data.keys():
      if data[each]:
        sql = sql + f" and {each}={data[each]}"
    if startTime and endTime:
      sql = sql + f" and date_time < {endTime} and date_time > {startTime}"
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]
  except Exception as e:
    logging.error("get total error")
    logging.exception(e)
  finally:
    cursor.close()
    conn.close()


def query_message(current, pageSize, data, startTime, endTime):
  conn = pool.connection()
  cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
  try:
    sql = f"select id,sender_id,sender_name,username,group_username,message,send_flag,date_format(date_time, '%Y-%m-%d %H:%i:%s') as created_at from message where TRUE"
    for each in data.keys():
      if data[each]:
        sql = sql + f" and {each}={data[each]}"
    if startTime and endTime:
      sql = sql + f" and date_time <= '{endTime} 23:59:59' and date_time >= '{startTime} 00:00:00'"
    sql = sql + f" limit {pageSize} offset {(current - 1) * pageSize}"
    cursor.execute(sql)
    result = cursor.fetchall()
    total = get_total(data, startTime, endTime)
    return result, total
  except Exception as e:
    logging.error("query message error")
    logging.exception(e)
  finally:
    cursor.close()
    conn.close()


def get_sender(id):
  conn = pool.connection()
  cursor = conn.cursor()
  try:
    sql = f"select sender from message where id={id}"
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]
  except Exception as e:
    logging.error("get sender error")
    logging.exception(e)
    return False
  finally:
    cursor.close()
    conn.close()


def update_message(id, send_flag):
  conn = pool.connection()
  cursor = conn.cursor()
  try:
    sql = f"update message set send_flag='{send_flag}',date_time='{datetime.datetime.now()}' where id={id}"
    cursor.execute(sql)
    conn.commit()
    return True
  except Exception as e:
    logging.error("update message error")
    logging.exception(e)
    return False
  finally:
    cursor.close()
    conn.close()
