

import os
import lib.cloudstorage as gcs

from google.appengine.api import app_identity
import endpoints

import jinja2
import webapp2
import time
import re

import urllib2
import json


import time

import json
from models import Bucket
import G_search
from google.appengine.api import memcache
import pickle
import operator
from google.appengine.api import taskqueue
from main import Handler
from main import Init

import logging



#class Init(webapp2.RequestHandler):
#	def post (self):  
#		logging.getLogger().setLevel(logging.DEBUG)
#		print "Q task execution started"
#		logging.info("Q task execution started")

#		buckets =list (Bucket.query())

#		for bucket in buckets :
#			bucket.key.delete()

		#seed_url = self.request.get("seed_url")
		#max_pages = self.request.get("max_pages")

#		buckets, graph = G_search.crawl_web(seed_url,int(max_pages),"BFS")
#		ranks = G_search.compute_ranks(graph) 
#		count=0
#		for key in buckets:
#			current_bucket = Bucket(hash_code = str(key) ,dictionary= buckets[key])
#			current_bucket.put()
#			print "storing bucket %s" %str(count)
			#print "dict len"
			#print len(buckets[key])

			#for word in buckets[key]:
				#print"list len"
				#print len(buckets[key][word])
#			count+=1

		#pickled_index = pickle.dumps(index)
		#pickled_ranks = pickle.dumps(ranks)
#		memcache.set("ranks",ranks)
		
		#self.create_file("index",pickled_index)
		#self.create_file("ranks",pickled_ranks)


#		self.write("index initialized")
#		logging.info("index initialized")
#		print "Q task execution ended"
#		elf.write("Q task execution ended")
#		taskqueue.add(url='tasks/send_email')


#class SendEmail(webapp2.RequestHandler):
#    def get(self):
#        """Send a reminder email to each User with an email about games.
#        Called every hour using a cron job"""
        #app_id = app_identity.get_application_id()
        #users = User.query(User.email != None)
        #for user in users:
        #    incompleted_games=Game.query(Game.user == user.key ,Game.game_over==False).get()

        #    if incompleted_games:
#        print "Email sending started"
#            if True:
#                subject = 'This is a reminder!'
#                body = 'Hello {}, You have active Hangman Game!'#.format(user.name)
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
#                mail.send_mail('noreply@{}.appspotmail.com'#.format(app_id),
#                           'garfieldchh@gmail.com',
#                           subject,
#                           body)

class Test(webapp2.RequestHandler):
	def get(self):
		#logging.getLogger().setLevel(logging.DEBUG)
		#logging.info("Testing")
		result = 1+1



app = webapp2.WSGIApplication([('/tasks/test',Test)], debug=True)	
    #('/tasks/build_index', Init),
    #'/tasks/send_email',SendEmail),
    	