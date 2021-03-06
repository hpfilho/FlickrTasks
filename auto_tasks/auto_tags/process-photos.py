#!/usr/bin/python3

# This script executes tasks in all photos on a photostrean
# according to rules defined by the user. Can be used to add
# tags or add photos to groups according to views, favorites, etc.,
# for example.
#
# Author: Haraldo Albergaria
# Date  : Jan 01, 2018
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


####################################################
# !!!DO NOT MODIFY THIS FILE!!!                    #
# Implement the procedures in file procs.py        #
####################################################


import flickrapi
import json
import api_credentials
import procs

# Credentials
api_key = api_credentials.api_key
api_secret = api_credentials.api_secret
user_id = api_credentials.user_id

# Flickr api access
flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')


#===== MAIN CODE ==============================================================#

photos = flickr.people.getPhotos(user_id=user_id)

npages = int(photos['photos']['pages'])
ppage = int(photos['photos']['perpage'])
total = int(photos['photos']['total'])

print('=============================================')
print('Pages: {0} | Per page: {1} | Total: {2}'.format(npages, ppage, total))
print('=============================================')

summary = open(procs.summary_file, 'w')
summary.write('SUMMARY REPORT:\n')
summary.write('-----------------------------------------------\n')
summary.close()

for pg in range(npages, 0, -1):
    page = flickr.people.getPhotos(user_id=user_id, page=pg)
    ppage = len(page['photos']['photo'])
    print('\n\n\nPage: {0}/{1} | Photos: {2}'.format(pg, npages, ppage))
    print('---------------------------------------------')

    for ph in range(ppage-1, -1, -1):
        photo_id = page['photos']['photo'][ph]['id']
        photo_title = page['photos']['photo'][ph]['title']
        print(u'\nid: {0}\ntitle: {1}'.format(photo_id, photo_title))
        procs.processPhoto(photo_id, photo_title, user_id)

print('\n\n')
