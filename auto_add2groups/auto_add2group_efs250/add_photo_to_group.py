#!/usr/bin/python3

# This automatically adds photos to a group pool
# according to the group rules
#
# Author: Haraldo Albergaria
# Date  : Nov 5, 2018
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


####################################################
# !!!DO NOT MODIFY THIS FILE!!!                    #
# Implement the procedures in file procs.py        #
# Include the rules in file data.py                #
####################################################


import flickrapi
import json
import api_credentials
import data
import procs
import os

def open_file(mode):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = dir_path + '/current_id'
    return open(file_path, mode)


error_1 = 'Error: 1: Photo not found'
error_3 = 'Error: 3: Photo already in pool'
error_5 = 'Error: 5: Photo limit reached'
error_6 = 'Error: 6: Your Photo has been added to the Pending Queue for this Pool'
error_7 = 'Error: 7: Your Photo has already been added to the Pending Queue for this Pool'

api_key = api_credentials.api_key
api_secret = api_credentials.api_secret
user_id = api_credentials.user_id

# Flickr api access
flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')

group_id = flickr.urls.lookupGroup(api_key=api_key, url=data.group_url)['group']['id']
group_name = flickr.urls.lookupGroup(api_key=api_key, url=data.group_url)['group']['groupname']['_content']

added = 0

while added < data.group_limit:

    try:
        current_id_file = open_file('r')
    except FileNotFoundError as e:
        print(e)
        current_id_file = open_file('w')
        current_id_file.close()
        current_id_file = open_file('r')
    except:
        print("Error: FATAL")
        break

    photo_id = current_id_file.read().replace('\n', '')

    try:
        photo_title = flickr.photos.getInfo(photo_id=photo_id)['photo']['title']['_content']
    except flickrapi.exceptions.FlickrError as e:
        print(e)
        if str(e) == error_1:
            print("Warng: Using the last photo from the user\'s photostream")
            photo_id = flickr.people.getPublicPhotos(user_id=user_id)['photos']['photo'][0]['id']
            photo_title = flickr.photos.getInfo(photo_id=photo_id)['photo']['title']['_content']
        else:
            break
    except:
        print("Error: FATAL")
        break

    current_id_file.close()

    if procs.isOkToAdd(photo_id):
        try:
            flickr.groups.pools.add(group_id=group_id, photo_id=photo_id)
            print("Added: Photo \'{0}\' to the group \'{1}\'".format(photo_title, group_name))
            added = added + 1
        except flickrapi.exceptions.FlickrError as e:
            print("Error: Unable to add photo \'{0}\' to the group \'{1}\'".format(photo_title, group_name))
            print(e)
            if str(e) != error_3 and str(e) != error_6 and str(e) != error_7:
                break
        except:
            print("Error: FATAL")
            break
    else:
        print("Error: Photo \'{0}\' is not elegible to be added to the group \'{1}\'".format(photo_title, group_name))

    next_id = flickr.photos.getContext(photo_id=photo_id)['nextphoto']['id']
    if next_id != 0:
        current_id_file = open_file('w')
        current_id_file.write('{0}'.format(next_id))
        current_id_file.close()
    else:
        print("Warng: Reached the end of the photoset")
        break

