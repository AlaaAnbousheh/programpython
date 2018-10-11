

import mysql.connector

tserver = ("leocalhost","root","")
def sconnect_server(tserver):
    flag=True
    cursor=''
    db=''
    try:
        serverlist=list(tserver)
        mydb = mysql.connector.connect(
          host=serverlist[0],
          user=serverlist[1],
          passwd=serverlist[2],

        )
        cursor=mydb.cursor()
        db=mydb
        flag=False

    except Exception as e:
            cursor=e
    return db,cursor,flag

def connect_server(tserver,mydatabase):
    flag=True
    cursor=''
    db=''
    try:
        serverlist=list(tserver)
        mydb = mysql.connector.connect(
          host=serverlist[0],
          user=serverlist[1],
          passwd=serverlist[2],
          database=mydatabase
        )
        cursor=mydb.cursor()
        db=mydb
        flag=False

    except Exception as e:
            cursor=e
    return db,cursor,flag

db,cursor,flag=sconnect_server(tserver)
if flag:
    print(cursor)
else:
    print(db,cursor)
