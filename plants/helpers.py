from time import localtime
from datetime import datetime
from datetime import date


"""
get_path, gets the pathname of the file to be stored int he users private media 
            bucket. S3 does not have directories, only simulated irectories via
            organized pathnames.
            
:param instance: the user
:param filename: the name of the file
"""
def get_path(instance, filename):
    current_date =  date.today()
    username = instance.user.customer.name
    filename = instance.user.customer.file_upload.name
    return filename

"""
get_profile_pic_path, makes a path to store user profile picture.

:param instance: the user
:param filename: the name of the image file
"""
def get_profile_pic_path(instance, filename):
    return '{0}/account_data/{1}'.format(instance.user.username, filename)
