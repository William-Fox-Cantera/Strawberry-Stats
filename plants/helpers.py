from time import localtime
from datetime import datetime
from datetime import date


"""
get_profile_pic_path, makes a path to store user profile picture.

:param instance: the user
:param filename: the name of the image file
"""
def get_profile_pic_path(instance, filename):
    return '{0}/account_data/{1}'.format(instance.user.username, filename)


def get_raw_upload_path(instance, filename):
    return '{0}/raw_data/{1}'.format(instance.user.username, filename)
