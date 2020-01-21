# -*- coding: utf-8 -*-
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(curPath)
import pymysql

class MySqlTools(object):
    def __init__(self,host='',user='',password='',db='',charset='utf8mb4'):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.charset = charset

    def get_conn(self):
        return pymysql.connect(host=self.host,user=self.user,password=self.password,db=self.db,
                                     charset=self.charset,cursorclass=pymysql.cursors.DictCursor)

    def execute_sql(self,sql):
        try:
            conn = self.get_conn()
            with conn.cursor() as cursor:
                cursor.execute(sql)
            conn.commit()
        finally:
            conn.close()

    def format_input(self,input_str):
        input_str = input_str.replace("'", "''").strip()
        input_str = input_str.replace("*", " ").strip()
        return input_str

    def query_table(self, table_name, where_filed=['1'], where_values=['1'],top=-1):
        try:
            conn = self.get_conn()
            with conn.cursor() as cursor:
                where_place_holder = ' and '.join([f + '=%s' for f in where_filed])
                if top>0:
                    sql = f"SELECT * FROM {table_name} WHERE {where_place_holder} limit {top}"
                else:
                    sql = f"SELECT * FROM {table_name} WHERE {where_place_holder}"

                cursor.execute(sql,tuple(where_values))
                result = cursor.fetchall()
                return result
        finally:
            conn.close()

    def insert_record(self, table_name,  insert_filed=[], insert_values=[]):
        try:
            conn = self.get_conn()
            insert_fileds = ','.join(insert_filed)
            insert_place_holder = ','.join(['%s' for f in insert_values])
            with conn.cursor() as cursor:
                insert_sql = f"INSERT INTO {table_name} ({insert_fileds}) VALUES ({insert_place_holder})"
                cursor.execute(insert_sql,tuple(insert_values))
            conn.commit()
        finally:
            conn.close()

    def update_record(self, table_name, update_filed, update_values, where_filed, where_values):
        try:
            conn = self.get_conn()
            args_values = []
            args_values.extend(update_values)
            args_values.append(where_values)
            update_fileds = ','.join([f+' = %s' for f in update_filed])
            with conn.cursor() as cursor:
                update_sql = f"UPDATE {table_name} SET {update_fileds} WHERE {where_filed} = %s"
                cursor.execute(update_sql,tuple(args_values))
            conn.commit()
        finally:
            conn.close()

    def delete_record(self, table_name, where_filed=[], where_values=[]):
        try:
            conn = self.get_conn()
            where_fileds = ' and '.join([f+'=%s' for f in where_filed])
            with conn.cursor() as cursor:
                insert_sql = f"DELETE FROM {table_name} WHERE {where_fileds}"
                cursor.execute(insert_sql, tuple(where_values))
            conn.commit()
        finally:
            conn.close()


# -*- coding: utf-8 -*-
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(curPath)

if __name__ == '__main__':
    table_fileds=['id','gender','name','avator','created_time','updated_time','content']
    insert_values=[1234,1,'chris','https://pic1.zhimg.com/aadd7b895_is.jpg',1578291999,1579504391,'hahah哈哈哈，成功了,']
    mysql = MySqlTools(host='localhost',user='root',password='123456',db='zhihu')
    # mysql.insert_record('answers',insert_filed=table_fileds,insert_values=insert_values)

    all_answers = mysql.query_table('answers')
    for answer in all_answers[:1]:
        print(answer)
    print(len(all_answers))
