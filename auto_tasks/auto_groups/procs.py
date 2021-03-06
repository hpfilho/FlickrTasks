# Procedures of script process-photos.py
#
# Author: Haraldo Albergaria
# Date  : Jan 01, 2018
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


###########################################
#  !!! IMPLEMENT THE PROCEDURES HERE !!!  #
###########################################


import flickrapi
import api_credentials
import json

from common import hasTag
from common import isInGroup

api_key = api_credentials.api_key
api_secret = api_credentials.api_secret
user_id = api_credentials.user_id

# Flickr api access
flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')

# World's Favorites
wf_group_url  = 'https://www.flickr.com/groups/worldsfavorite/'
wf_group_id   = flickr.urls.lookupGroup(api_key=api_key, url=wf_group_url)['group']['id']
wf_group_name = flickr.urls.lookupGroup(api_key=api_key, url=wf_group_url)['group']['groupname']['_content']

# MAS DE 100 FAVORITAS
mc_group_url  = 'https://www.flickr.com/groups/2874597@N21/'
mc_group_id   = flickr.urls.lookupGroup(api_key=api_key, url=mc_group_url)['group']['id']
mc_group_name = flickr.urls.lookupGroup(api_key=api_key, url=mc_group_url)['group']['groupname']['_content']

# 100 views + 10 favourites (unlimited)
ht_group_url  = 'https://www.flickr.com/groups/100v10f/'
ht_group_id   = flickr.urls.lookupGroup(api_key=api_key, url=ht_group_url)['group']['id']
ht_group_name = flickr.urls.lookupGroup(api_key=api_key, url=ht_group_url)['group']['groupname']['_content']
ht_group_tag  = '100v+10f'

# Fav/View >= 5% (please mind the rules)
fv_group_url  = 'https://www.flickr.com/groups/favs/'
fv_group_id   = flickr.urls.lookupGroup(api_key=api_key, url=fv_group_url)['group']['id']
fv_group_name = flickr.urls.lookupGroup(api_key=api_key, url=fv_group_url)['group']['groupname']['_content']

not_add_tag = 'DNA'

summary_file = '/home/pi/flickr_tasks/auto_tasks/auto_groups/summary_groups.log'


#===== PROCEDURES =======================================================#

def addPhotoToGroup(photo_id, photo_title, group_id, group_name):
    try:
        flickr.groups.pools.add(api_key=api_key, photo_id=photo_id, group_id=group_id)
        print('\nAdded photo to \'{0}\' group'.format(group_name), end='')
        summary = open(summary_file, 'a')
        summary.write('Added photo \'{0}\' to \'{1}\'\n'.format(photo_title, group_name))
        summary.close()
    except Exception as e:
        print('\nERROR: Unable to add photo \'{0}\' to group \'{1}\''.format(photo_title, group_name))
        print(e)

def remPhotoFromGroup(photo_id, photo_title, group_id, group_name):
    try:
        flickr.groups.pools.remove(api_key=api_key, photo_id=photo_id, group_id=group_id)
        print('\nRemoved photo from \'{0}\' group'.format(group_name), end='')
        summary = open(summary_file, 'a')
        summary.write('Removed photo \'{0}\' from \'{1}\'\n'.format(photo_title, group_name))
        summary.close()
    except Exception as e:
        print('\nERROR: Unable to remove photo \'{0}\' to group \'{1}\''.format(photo_title, group_name))
        print(e)


### !!! DO NOT DELETE OR CHANGE THE SIGNATURE OF THIS PROCEDURE !!!

def processPhoto(photo_id, photo_title, user_id):
    try:
        favorites = flickr.photos.getFavorites(photo_id=photo_id)['photo']
        info = flickr.photos.getInfo(api_key=api_key, photo_id=photo_id)['photo']

        is_public = info['visibility']['ispublic']
        safety_level = info['safety_level']

        photo_favs = int(favorites['total'])
        photo_views = int(info['views'])
        fv_ratio = photo_favs/photo_views

        print('favorites: {0}\nviews: {1}\nratio: {2:.1f}%'.format(photo_favs, photo_views, fv_ratio*100), end='')

        # Word's Favorites
        in_group = isInGroup(photo_id, wf_group_id)
        if not in_group and not hasTag(photo_id, not_add_tag) and is_public == 1 and safety_level == 0 and photo_favs >= 1:
            addPhotoToGroup(photo_id, photo_title, wf_group_id, wf_group_name)
        if in_group and (photo_favs == 0 or hasTag(photo_id, not_add_tag)):
            remPhotoFromGroup(photo_id, photo_title, wf_group_id, wf_group_name)

        # MAS DE 100 FAVORITAS
        in_group = isInGroup(photo_id, mc_group_id)
        if not in_group and not hasTag(photo_id, not_add_tag) and is_public == 1 and safety_level == 0 and photo_favs >= 100:
            addPhotoToGroup(photo_id, photo_title, mc_group_id, mc_group_name)
        if in_group and (photo_favs < 100 or hasTag(photo_id, not_add_tag)):
            remPhotoFromGroup(photo_id, photo_title, mc_group_id, mc_group_name)

        # 100 views + 10 favourites (unlimited)
        in_group = isInGroup(photo_id, ht_group_id)
        summary = open(summary_file, 'r')
        summary_str = summary.read()
        summary.close()
        if not in_group and ht_group_name not in summary_str and not hasTag(photo_id, not_add_tag) and is_public == 1 and safety_level == 0 and photo_views >= 100 and photo_favs >= 10:
            addPhotoToGroup(photo_id, photo_title, ht_group_id, ht_group_name)
            flickr.photos.addTags(api_key=api_key, photo_id=photo_id, tags=ht_group_tag)
        if in_group and (photo_views < 100 or photo_favs < 10 or hasTag(photo_id, not_add_tag)):
            remPhotoFromGroup(photo_id, photo_title, ht_group_id, ht_group_name)

        # Fav/View >= 5% (please mind the rules)
        in_group = isInGroup(photo_id, fv_group_id)
        summary = open(summary_file, 'r')
        summary_str = summary.read()
        summary.close()
        if not in_group and fv_group_name not in summary_str and not hasTag(photo_id, not_add_tag) and is_public == 1 and safety_level == 0 and photo_favs >= 5 and fv_ratio >= 0.05:
            addPhotoToGroup(photo_id, photo_title, fv_group_id, fv_group_name)
        if in_group and fv_ratio < 0.05:
            remPhotoFromGroup(photo_id, photo_title, fv_group_id, fv_group_name)

        print(' ')

    except:
        print('\nERROR: Unable to get information for photo \'{0}\''.format(photo_title))
