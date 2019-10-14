#!/usr/bin/python3
from  mysql_conn import *
import ConfigParser,time
from log import *
from linux_conn import *
import sys
import re
import operator
import argparse
conf = ConfigParser.ConfigParser()
conf.read("config.conf")
sections = conf.sections()
logger_obj=get_logger()

def common():
   host = conf.get('common', "vip")
   port = conf.get('common', "mysql_port")
   user = conf.get('common',"mysql_user")
   master_host=conf.get('server-master','host')
   master_port=conf.get('server-master','port')
   linux_port = conf.get('common', "linux_port")
   linux_user = conf.get('common',"linux_user")
   password = conf.get('common',"mysql_password")
   gateway = conf.get('common',"gateway")
   device = conf.get('common',"device")
   device_1 = conf.get('common',"device_1")
   return {'host':host,'port':port,'user':user,'password':password,'linux_user':linux_user,'linux_port':linux_port,'gateway':gateway,'master_host':master_host,'master_port':master_port,'device':device,'device_1':device_1}

def yunxing():
   result=common()
   i=4
   while(i>=0):
     time.sleep(1)
     try:
        a = SQLgo(result['host'],result['user'],result['password'],'information_schema',result['port'])
        print(a.alive())
        if a.alive():
          logger_obj.info('VIP_MYSQL 健康状态')
     except Exception as e:
        i=i-1
        logger_obj.error(e)
   jiebang(result['master_host'],result['linux_port'],result['linux_user'],result['device_1'],result['host'])
   qiehuan()

def jiance(): 
   for  i in sections:
     if re.match('server-master',i):
       result=common()
       host = conf.get(i, "host")
       port = conf.get(i, "port")
       try:
         a = SQLgo(host,result['user'],result['password'],'information_schema',port)
         if a.alive():
           e=['gtid_mode','rpl_semi_sync_master_enabled']
           g=[]
           for i in e:
             jieguo=a.env_value(i)
             if jieguo:
               g.append('正确')
             else:
               print("%s %s检测没有通过" %(i,host))
               g.append('错误')
           if '错误' in g:
             print("检测没有通过")
           else:
             print("主库检测通过")
       except Exception as e:
          print("%s 进程不存在"  %(host,e))
     elif re.match('server-slave',i):
       host = conf.get(i, "host")
       port = conf.get(i, "port")
       try:
         a = SQLgo(host,result['user'],result['password'],'information_schema',port)
         if a.alive():
            c = ['gtid_mode','log_slave_updates','read_only','rpl_semi_sync_slave_enabled']
            d = []
            for i in  c:
              if a.env_value(i):
                d.append('正确')
              else:
                print("%s %s检测没有通过" %(i,host))
                d.append('错误')
            if a.slave_info()['slave_stats']:
               d.append('正确')
            else:
               d.append('错误')
               print("%s 复制检测未通过" %(host))
            if  '错误' in d:
              print("%s 请重新设置" %(host))
            else:
              print("%s 从库检测通过" %(host))
       except Exception as e:
         print("%s 进程不存在 %s"  %(host,e))

def qiehuan():
  c=[]
  res1=common()
  for i in sections:
     if re.match('server-slave',i):
       host = conf.get(i, "host")
       port = conf.get(i, "port")
       print(port)
       try:
         a = SQLgo(host,res1['user'],res1['password'],'information_schema',port)
         if  a.alive(): 
           result=a.slave_info()
           if a.slave_info()['b_status']:
             result['host']=host
             result['port']=port
             c.append(result)
             get_logger().info('选择新主进行对比,复制异常从库不参与选举')
         else:
             print("复制进程错误")
       except Exception as e:
         print("%s 进程不存在"  %(host))
  sorted_x = sorted(c, key=operator.itemgetter('binlog_file','binlog_position'),reverse=True)
  count = 10
  res2=common()
  while (count > 5):
    a = SQLgo(sorted_x[0]['host'],res2['user'],res2['password'],'information_schema',sorted_x[0]['port'])
    cc= a.slave_info()
    if(cc['second_behind']==0):
      result= caozuo(sorted_x,res2)
      print(result)
      if result:
        get_logger().info('新主选择成功,进行以下操作')
        a.query_info("set global read_only = 'OFF'")
        get_logger().info('打开读写开关')
      else:
        get_logger().info('VIP绑定失败')
        exit(1)
      count=4
    count=count-1
    continue
  
def caozuo(sorted_x,res2):
  slave_change(sorted_x,res2,sorted_x[0]['host'],sorted_x[0]['port'])
  return bangding(sorted_x[0]['host'],res2['linux_port'],res2['linux_user'],res2['host'],res2['gateway'],res2['device'],res2['device_1']) 
 
def slave_change(value,res2,host,port):
  if value[1:]:
    for i in value[1:]:
      a = SQLgo(i['host'],res2['user'],res2['password'],'information_schema',i['port'])
    get_logger().info("生成CHANGE语句,指向新主")
    get_logger().info("CHANGE MASTER TO MASTER_HOST=%s, MASTER_PORT=%s, MASTER_AUTO_POSITION=1, MASTER_USER='repl', MASTER_PASSWORD='123'" %(host,port))
  else:
    get_logger().info("从库不存在,集群处于单实例模式")


parser = argparse.ArgumentParser(description='manual to this script') 
parser.add_argument('--run', help="运行监控程序" )
parser.add_argument('--check', help="执行监控检测" )
parser.add_argument('--switch', help="执行高可用切换")
args = parser.parse_args()

if args.run:
  yunxing()
elif args.check:
  jiance()
elif args.switch:
  print("wae")
