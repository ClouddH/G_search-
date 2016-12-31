
#import endpoints
import logging
import os
import lib.cloudstorage as gcs
import werkzeug
from flask import session as login_session
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
from models import Bucket,Ranks
import G_search
from google.appengine.api import memcache
import pickle
import operator
from google.appengine.api import taskqueue
from google.appengine.api import mail
from BeautifulSoup import BeautifulSoup
import sys
import random
import string 
from flask import session as login_session
from webapp2_extras import sessions
import httplib2
import urlfetch

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my_secret_key',
}


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


### Enable Search in different Language
### Google Facebook Log in  + Read Account info
### Waiting page 
### Better Web snippet 







class Handler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def dispatch(self):                                 # override dispatch
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)       # dispatch the main handler
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()
    

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
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
						for x in xrange(32))
		self.session['state'] = state
		self.render("home.html",STATE = state)




class Init_custom_index(Handler):
	def post(self):  
		

		seed_url = self.request.get("seed_url")
		max_pages = self.request.get("max_pages")

		
		task = taskqueue.add(
            url='/build_custom_index',
            params={'seed_url': seed_url,'max_pages':max_pages})
		



		self.write("start building!!!!")

class Init_public_index(Handler):
	def get(self):  
		
		task = taskqueue.add(
            url='/build_public_index',
            params={})

		
		self.response.write('start building public index !')





class Send_email(Handler):
	def post(self):
		mail.send_mail('noreply@garfieldsearch-153603.appspotmail.com',
                           'ggyy920904@hotmail.com',
                           'subject',
                           'body')

class Build_custom_index(Handler):
	def post(self):  
		self.write("start building index. A email will be sent when it is done ")
		buckets =list (Bucket.query())

		for bucket in buckets :
			bucket.key.delete()

		seed_url = self.request.get("seed_url")
		max_pages = self.request.get("max_pages")

		index, graph = G_search.crawl_web([(seed_url,int(max_pages))],"BFS")
		buckets = G_search.convert_to_buckets(index)
		ranks = G_search.compute_ranks(graph) 
		count=0
		for key in buckets:
			current_bucket = Bucket(owner ='custom',hash_code = str(key) ,dictionary= buckets[key])
			current_bucket.put()
			print "storing bucket %s" %str(count)
			count+=1

		
		curr_ranks = Ranks(owner ='public',ranks=ranks)
		curr_ranks.put()
		memcache.set("public_ranks",ranks)

		
		
		

		self.write("index initialized")
		


		self.write("building finished")
		task = taskqueue.add(url='/send_email',params={})
		print "enqueued"

class Build_public_index(Handler):
	def post(self):  
		self.write("start building index. A email will be sent when it is done ")
		buckets =list (Bucket.query())

		for bucket in buckets :
			bucket.key.delete()

		seeds =	[('http://stackoverflow.com/',10),('https://uwaterloo.ca/',10),('https://www.reddit.com/',10),('https://www.ft.com/',10)]
		index, graph = G_search.crawl_web(seeds,"BFS")
		buckets = G_search.convert_to_buckets(index)
		ranks = G_search.compute_ranks(graph) 
		count=0
		for key in buckets:
			current_bucket = Bucket(owner ='public',hash_code = str(key) ,dictionary= buckets[key])
			current_bucket.put()
			print "storing bucket %s" %str(count)
			count+=1

		
		curr_ranks = Ranks(owner='public',ranks=ranks)
		curr_ranks.put()
		memcache.set("public_ranks",ranks)

		
		
	
class Search(Handler):
	def get(self,sth):
		
		query=self.request.get("query")
		type_search = self.request.get("type")
		#print type
		#print query
		
		
		num_results=10
		tokens = G_search.split_string(query," .,:;'\"{}[]=-_`~\n<>!?/\\#$%^&*()+")
	
		#print tokens

		index_set_list=[]
		num_buckets = len(list(Bucket.query()))
		print "check num buckets"
		if num_buckets==0:
			self.response.write("empty index")
			return None
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
		#ranks= memcache.get("ranks")
		if type_search =="public":
			if memcache.get('public_ranks'):
				ranks = memcache.get('public_ranks')

			else:	
				ranks = list(Ranks.query(owner='public'))[0].ranks
				memcache.set('public_ranks',ranks)


		url_ranks_look_up = dict()

		for link in links :
			url_ranks_look_up[link]=ranks[link]
		sorted_url_ranks_list = sorted(url_ranks_look_up.items(), key=operator.itemgetter(1),reverse=True)

		result=[]

		print result
		for url_rank_tuple in sorted_url_ranks_list:
			result.append(url_rank_tuple[0])
		
		if len(sorted_url_ranks_list)>num_results:
			result = result[:num_results]
		
		#result = G_search.look_up(index,query,ranks,10)
		print "url"
		print result
		if not result:
			self.response.write("keyword not found")


		result_tuple_lst=[]
		for link in result:
			if not memcache.get(link):
				soup = BeautifulSoup(urllib2.urlopen(link))
				title =  soup.title.string
				snippet = self.get_snippet(link,soup)


				#snippet =""
				#p1 = soup.p
				#result+=p1.text+"\n"

				#while len(result)<150:

				#	p2 = p1.findNext('p')
				#	p2_text = p2.text
					
					
				#	result+=p2.text+"\n"
				#	p1 = p2
				#result =result.encode('utf-8')
				t =(link,title,snippet)
				result_tuple_lst.append(t)
	
			
		#print result_tuple_lst	
		self.render("result.html" ,results =result_tuple_lst)

	def get_snippet(self,url,soup):
		
		print "curr url"
		print url
		result =""
		p1 = soup.p
		if not p1 :
			return ""
		result+=p1.text+"\n"

		while len(result)<150:

			p2 = p1.findNext('p')
			if p2:
				p2_text = p2.text
				
				
				result+=p2.text+"\n"
				p1 = p2
			else :
				return result.encode('utf-8')
				
		
		return str(result.encode('utf-8'))	


class FBconnect(Handler):
	def post(self):
	    print "function called"
	    print self.request.get('STATE')
	    print self.session['state']
	    if self.request.get('state') != self.session['state']:
	        response = make_response(json.dumps('Invalid state parameter.'), 401)
	        response.headers['Content-Type'] = 'application/json'
	        return response
	    access_token = self.request.get('access_token')
	    print access_token    
	    #access_token = request.data
	    print "access token received %s " % access_token

	    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
	        'web']['app_id']
	    app_secret = json.loads(
	        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
	    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
	        app_id, app_secret, access_token)
	    h = httplib2.Http()
	    result = h.request(url, 'GET')[1]

	    
	    print "result is here"
	    print result

	    # Use token to get user info from API
	    userinfo_url = "https://graph.facebook.com/v2.4/me"
	    # strip expire tag from access token
	    token = result.split("&")[0]


	    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
	    h = httplib2.Http()
	    result = h.request(url, 'GET')[1]
	    # print "url sent for API access:%s"% url
	    # print "API JSON result: %s" % result
	    data = json.loads(result)
	    self.sessions['provider'] = 'facebook'
	    self.sessions['username'] = data["name"]
	    self.sessions['email'] = data["email"]
	    self.sessions['facebook_id'] = data["id"]

	    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
	    stored_token = token.split("=")[1]
	    self.sessions['access_token'] = stored_token

	    # Get user picture
	    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
	    h = httplib2.Http()
	    result = h.request(url, 'GET')[1]
	    data = json.loads(result)

	    self.session['picture'] = data["data"]["url"]

	    # see if user exists
	    #user_id = getUserID(self.session['email'])
	    #if not user_id:
	    #    user_id = createUser(self.session)
	    #self.session['user_id'] = user_id
	    #print user_id

	    output = ''
	    output += '<h1>Welcome, '
	    output += self.session['username']

	    output += '!</h1>'
	    output += '<img src="'
	    output += self.session['picture']
	    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

	    flash("Now logged in as %s" % self.session['username'])
	    print "success!"
	    return output
	#def createUser(session):
	#    newUser = User(name=session['username'], email=session[
	#                   'email'], picture=session['picture'])
	#    session.add(newUser)
	#    session.commit()
	#    user = session.query(User).filter_by(email=login_session['email']).one()
	#    return user.id    

PAGE_RE = r'((?:[ ,./?"\'a-zA-Z0-9_=&-]+?)*)'

		

#PAGE_RE = r'((?:[,.?!'"% a-zA-Z0-9_-]+?)*)'

app = webapp2.WSGIApplication([("/", MainPage),
								("/initialize_custom_index",Init_custom_index),
								("/search%s" % PAGE_RE, Search),
								("/build_custom_index",Build_custom_index),
								("/send_email",Send_email),
								("/initialize_public_index",Init_public_index),
								("/build_public_index",Build_public_index),
								("/fbconnect",FBconnect)], debug=True,config=config)
