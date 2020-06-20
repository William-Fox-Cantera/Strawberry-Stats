from time import localtime
from datetime import datetime


"""
get_file_path, gets the pathname of the file to be stored int he users private media 
            bucket. S3 does not have directories, only simulated irectories via
            organized pathnames.
            
:param instance: the user
:param filename: the name of the file
"""
def get_file_path(instance, filename):
    now = datetime.now()
    print(now)
    return '{0}/uploads/{1}/{2}'.format(instance.user.username, now.strftime("%Y/%m/%d %H:%M:%S"), filename)