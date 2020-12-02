import sys
import psycopg2

from datetime import datetime
from pytz import timezone

host = 'localhost'
dbname = 'dpredict'
user = 'postgres'
password = 'postgres'
port = '5432'


def connection_check():

    try:
        connection = psycopg2.connect(host=host,
                                      dbname=dbname,
                                      user=user,
                                      password=password,
                                      port=port)

        connection.close()
    except Exception as e:
        print(e)
        sys.exit(1)


class POSTGRESQL(object):

    def __init__(self):
        self.connection = psycopg2.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password,
            port=port)
        self.cursor = self.connection.cursor()

    def execute(self, query, values):
        self.cursor.execute(query, values)
        # print(self.cursor.fetchone)

    def fetchone(self):
        return self.cursor.fetchone()

    def commit(self):
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

# cur = conn.cursor()
#
# # cur.execute(
# #     """
# #     CREATE TABLE log (
# #     state varchar,
# #     content text,
# #     date timestamp);
# #     """)
#
# date_today = datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")
#
# cur.execute(
#     """
#     INSERT INTO log (log_state, content, log_date) VALUES (%s, %s, %s)
#     """, ('fail', 'error', date_today))
# conn.commit()
#
# cur.close()
# conn.close()
