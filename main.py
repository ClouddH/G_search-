
import endpoints
import logging
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

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


### Enable Search in different Language
### Test it online 
### Build a ok front-end 






class Handler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    #def create_file(self, filename,filecontent):
	#    """Create a file.
	#    The retry_params specified in the open call will override the default
	#    retry params for this particular file handle.
	#    Args:
	#      filename: filename.
	#    """

	    
	#    bucket_name = os.environ.get('BUCKET_NAME',
	#                                 app_identity.get_default_gcs_bucket_name())
	#    bucket = '/' + bucket_name
	#   filename = bucket + '/%s' %filename
	#    self.tmp_filenames_to_clean_up = []

	#    self.response.write('Creating file %s\n' % filename)

	#   write_retry_params = gcs.RetryParams(backoff_factor=1.1)
	#   gcs_file = gcs.open(filename,
	#                        'w',
	#                       content_type='text/plain',
	#                        options={'x-goog-meta-foo': 'foo',
	#                                 'x-goog-meta-bar': 'bar'},
	#                        retry_params=write_retry_params)
	    
	#    gcs_file.write(filecontent)
	#    gcs_file.close()
	#    self.tmp_filenames_to_clean_up.append(filename)	
	    
	#    self.read_file(filename)
	#    self.response.write('\n\n')


	#[START read]
    #def read_file(self, filename):
	    #self.response.write('Abbreviated file content (first line and last 1K):\n')

	#    gcs_file = gcs.open(filename)
	#    self.response.write(gcs_file.readline())
	#    gcs_file.seek(-3024000000000000000000000000000000000, os.SEEK_END)
	#    result =gcs_file.read()
	#    gcs_file.close()  
	    
	#    return result





class MainPage(Handler):

	def get(self):
	    self.render("home.html")




class Init(Handler):
	def post(self):  
		#self.write("start building index. A email will be sent when it is done ")
		#buckets =list (Bucket.query())

		#for bucket in buckets :
		#	bucket.key.delete()

		seed_url = self.request.get("seed_url")
		max_pages = self.request.get("max_pages")

		#buckets, graph = G_search.crawl_web(seed_url,int(max_pages),"BFS")
		#ranks = G_search.compute_ranks(graph) 
		#count=0
		#for key in buckets:
		#	current_bucket = Bucket(hash_code = str(key) ,dictionary= buckets[key])
		#	current_bucket.put()
		#	print "storing bucket %s" %str(count)
			#print "dict len"
			#print len(buckets[key])

			#for word in buckets[key]:
				#print"list len"
				#print len(buckets[key][word])
		#	count+=1

		#pickled_index = pickle.dumps(index)
		#pickled_ranks = pickle.dumps(ranks)
		#memcache.set("ranks",ranks)
		
		#self.create_file("index",pickled_index)
		#self.create_file("ranks",pickled_ranks)


		#self.write("index initialized")
		#taskqueue.add (params={'seed_url': seed_url ,'max_pages':max_pages},
		#	url="/tasks/build_index")
		taskqueue.add(url='/tasks/test')

		self.write("start building")

	
class Search(Handler):
	def get(self,query):
		"search called"
		num_results=10
		tokens = G_search.split_string(query," .,:;'\"{}[]=-_`~\n<>!?/\\#$%^&*()+")
	
		#print tokens

		index_set_list=[]
		num_buckets = len(list(Bucket.query()))
		#print "num_buckets"
		#print num_buckets

		for token  in tokens:
			token = token.lower()
			hash_code =G_search.hash_string(token,num_buckets)
			bucket =Bucket.query(Bucket.hash_code==str(hash_code)).get()
			dictionary =bucket.dictionary
			if token in dictionary:			
				index_set_list.append( set(dictionary[token]) )
		#print index_set_list	

		if not index_set_list:
			self.response.write("keyword not found")
			return None 		
	
		links =list (set.intersection(*index_set_list)	)

		#print query

		#index= pickle.loads(self.read_file("/app_default_bucket/index"))
		#ranks= pickle.loads(self.read_file("/app_default_bucket/ranks"))
		ranks= memcache.get("ranks")


		url_ranks_look_up = dict()

		for link in links :
			url_ranks_look_up[link]=ranks[link]
		sorted_url_ranks_list = sorted(url_ranks_look_up.items(), key=operator.itemgetter(1),reverse=True)

		result=[]
		for url_rank_tuple in sorted_url_ranks_list:
			result.append(url_rank_tuple[0])
		
		if len(sorted_url_ranks_list)>num_results:
			result = result[:num_results]
		
		#result = G_search.look_up(index,query,ranks,10)
		
		output =""
		if not result:
			self.response.write("keyword not found")
			return
		for item in result :
			output+=item+"\n\n"
		
		self.response.write(output)	

PAGE_RE = r'((?:[ ,.?"\'a-zA-Z0-9_-]+?)*)'

		

#PAGE_RE = r'((?:[,.?!'"% a-zA-Z0-9_-]+?)*)'

app = webapp2.WSGIApplication([("/", MainPage),
								("/initialize",Init),
								("/search/%s" % PAGE_RE, Search)], debug=True)
