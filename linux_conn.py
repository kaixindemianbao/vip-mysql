#!/usr/bin/python3
import paramiko
from log import *
logger_obj=get_logger()
class cmd:
  def __init__(self,linux_host,linux_port,linux_user):
      self.host=linux_host
      self.port=linux_port
      self.user=linux_user
      self.myclient = paramiko.SSHClient()
      self.myclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  def test(self,cmd):
      try:
        self.myclient.connect(self.host,self.port,self.user,timeout=1)
        stdin, stdout, stderr = self.myclient.exec_command(cmd,timeout=2)
        if stdout.channel.recv_exit_status() == 0:
          cmd_status=True
        else:
          cmd_status=False
        self.myclient.close()
        return {'result':stdout.readlines(),'status':cmd_status}
      except Exception as e:
          logger_obj.info(e)

def bangding(host,port,username,vip,gateway,device,device_1):
# 新建一个ssh客户端对象
    aa=cmd(host,port,username)
    cmd1='arping -I %s -c 3 -s %s  %s' %(device,vip,gateway)
    res1=aa.test(cmd1)
    if res1['status']:
      logger_obj.error('VIP已存在 arping命令执行失败')
      exit(1)
    else:  
      cmmd='ifconfig %s %s/24' %(device_1,vip)
      res2 = aa.test(cmmd)
      if res2['status']:
        logger_obj.info('VIP绑定成功')
        return True
      else:
       logger_obj.error('VIP绑定失败')
       exit(1)
  
def jiebang(host,port,username,device_1,vip):
  try:
    aa=cmd(host,port,username)
    cmd1='ifconfig %s down' %(device_1)
    res1=aa.test(cmd1)
    if res1['status']:
      logger_obj.info('VIP解绑成功')
    else:
      logger_obj.info('VIP解绑失败')
  except Exception as e:
    logger_obj.info('机器无法连接,直接进行下一步')
