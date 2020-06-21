from time import localtime
from datetime import datetime


"""
get_file_path, gets the pathname of the file to be stored int he users private media 
            bucket. S3 does not have directories, only simulated irectories via
            organized pathnames.
            
:param instance: the user
:param filename: the name of the file
"""
def get_csv_path(instance, filename):
    now = datetime.now()
    return '{0}/csv_uploads/{1}/{2}'.format(instance.user.username, now.strftime("%Y/%m/%d %H:%M:%S"), filename)


"""
get_profile_pic_path, makes a path to store user profile picture.

:param instance: the user
:param filename: the name of the image file
"""
def get_profile_pic_path(instance, filename):
    return '{0}/account_data/{1}'.format(instance.user.username, filename)
