import asyncio
import sqlite3
from sqlite3 import Error
from twilio.rest import Client


import callofduty
from callofduty import Mode, Platform, Title


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        return conn
    except Error as e:
        print(e)

def create_tables(conn):
    try:
        c = conn.cursor()
        c.execute(
                """ CREATE TABLE IF NOT EXISTS friends (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        status integer NOT NULL
                                    ); """
                                    )
    except Error as e:
        print(e)

def send_text(online_message, offline_message, online_list, offline_list):
    msg=''
    #create a string with online friends
    for f in online_list:
        online_message+= f + '\n'
    online_message+="\n"

    #create a string with offline friends
    for f in offline_list:
        offline_message+= f + "\n"

    if len(online_list) > 0 and len(offline_list) > 0:
        msg+=online_message+offline_message
    elif len(online_list) == 0 and len(offline_list) > 0:
        msg+=offline_message
    elif len(online_list) > 0 and len(offline_list) == 0:
        msg+=online_message

    # Your Account SID from twilio.com/console
    account_sid = "AC5381473413333239de1f629a23c5c874"
    # Your Auth Token from twilio.com/console
    auth_token  = "ec277c55e0b92c8bcf30fc2457151b71"
    client = Client(account_sid, auth_token)
    message = client.messages.create(
                to="+17735108759", 
                from_="+18606070114",
                body=msg)

async def main():
    cod_friends = ['jkwak', 'Thanos#2237758', 'miniaturepeanut', 'Marquez#9885129', 'Lamron#2633441']
    database = r"/root/cod_update/MasterDB.db"
    conn = create_connection(database);
    online_friends = []
    offline_friends = []
    if conn is not None:
        create_tables(conn);
    else:
        print("Error! cannot create the database connection.")

    client = await callofduty.Login("sam.kwarteng@gmail.com", "Threelie1")
    friend_list = await client.GetMyFriends();
    cur = conn.cursor()
    cur.execute("SELECT name FROM friends")
    all_friends = cur.fetchall()
    all_friends_formatted = []
    for f in all_friends:
        all_friends_formatted.append(f[0])

    #import pdb; pdb.set_trace() 
    for friend in friend_list:
        #if friend is online but not in the database
        if friend.online and friend.username not in all_friends_formatted:
            cur.execute(""" INSERT INTO friends (name, status)
                            VALUES (?,?);""", (friend.username, 1))
            conn.commit()
            if friend.username in cod_friends:
                online_friends.append(friend.username)
        #if friend is online and is in the database
        elif friend.username in all_friends_formatted:
            cur.execute("SELECT status FROM friends WHERE name=?", (friend.username,))
            current_status = cur.fetchall()
            current_status = current_status[0][0]
            #if the pulled status is different than the one currently in the database, update it 
            updated_status = 1 if friend.online else 0
            if current_status != updated_status:
                cur.execute(""" UPDATE friends SET status=? WHERE name=?""", (updated_status, friend.username))
                conn.commit()
            #send a text if the status was updated from offline to online
            if current_status == 0 and updated_status == 1 and friend.username in cod_friends:
                online_friends.append(friend.username)
            elif current_status == 1 and updated_status == 0 and friend.username in cod_friends:
                offline_friends.append(friend.username)
    if len(online_friends) > 0 or len(offline_friends) > 0:
            send_text(" \n\nFriends now online: ", "Friends now offline: ", online_friends, offline_friends)

    conn.close()
asyncio.get_event_loop().run_until_complete(main())


