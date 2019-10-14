import random
import pymysql
class SQLgo():
    def __init__(self, ip=None, user=None, password=None , db=None, port=None):
        self.ip = ip
        self.user = user
        self.db = db
        self.port = int(port)
        self.password=password
        self.con =  pymysql.connect(
            host=self.ip,
            user=self.user,
            passwd=self.password,
            db=self.db,
            charset='utf8mb4',
            port=self.port
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()

    def env_value(self, env):
        with self.con.cursor() as cursor:
          try:
            sql="show variables like '%s'" %(env)
            cursor.execute(sql)
            result = cursor.fetchall()
            if result:
              if result[0][1] == 'ON':
                return True
              else:
                return False
            else:
              print('结果为空')
          except Exception as e:
            print(e) 
    def alive(self):
         with self.con.cursor() as cursor:
           cursor.execute('select 1')
           result = cursor.fetchall()
           if result == ((1,),):
             return True
           else:
             return False

    def query_info(self, sql=None):
        with self.con.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
        return result
    def slave_info(self):
        sql='show slave status'
        with self.con.cursor() as cursor:
            result=[]
            cursor.execute(sql)
            result=cursor.fetchall()
            binlog_file=int(result[0][5].replace('mysql-bin.',''))
            binlog_position=result[0][6]
            io_thread = result[0][10]
            sql_thread = result[0][11]
            second_behind = result[0][32]
            if io_thread=='Yes' and sql_thread=='Yes':
                 stats=True
            else:
                 stats=False
            if sql_thread=='Yes':
                 b_status=True
            else:
                b_status=False
            return {'slave_stats':stats,'binlog_file':binlog_file,'binlog_position':binlog_position,'second_behind':second_behind,'b_status':b_status}
           

