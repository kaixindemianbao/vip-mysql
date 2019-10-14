import logging
def get_logger():
  logger_obj = logging.getLogger('test')      
  logger_obj.setLevel(logging.INFO)       
  fh = logging.FileHandler("mha.log")      
  fh.setLevel(logging.INFO)                           
  formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')       
  fh.setFormatter(formater)     
  logger_obj.handlers=[]             
  logger_obj.addHandler(fh) 
  return logger_obj                          

