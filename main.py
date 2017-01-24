
#import endpoints
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
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
from models import Bucket, Ranks, Snippet_Bucket
import G_search
from google.appengine.api import memcache
import pickle
import operator
from google.appengine.api import taskqueue
from google.appengine.api import mail
from BeautifulSoup import BeautifulSoup

import random
import string
from flask import session as login_session
from webapp2_extras import sessions
import httplib2
import urlfetch


from webapp2 import WSGIApplication, Route
if 'lib' not in sys.path:
    sys.path[0:0] = ['lib']


app_config = {
    'webapp2_extras.sessions': {
        'cookie_name': '_simpleauth_sess',
        'secret_key': "session_key"
    },
    'webapp2_extras.auth': {
        'user_attributes': []
    }
}


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


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
            # dispatch the main handler
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()


class MainPage(Handler):

    def get(self):
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in xrange(32))
        self.session['state'] = state
        self.render("home.html", STATE=state)


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


class Build_public_index(Handler):

    def post(self):

        self.write("start building index.")

        self.clean_up()

        # call web crawlers
        seeds = [('http://stackoverflow.com/', 300), ('https://uwaterloo.ca/', 300),
                 ('https://www.reddit.com/', 300), ('https://www.ft.com/', 300)]
        index, graph, snippet_lookup = G_search.crawl_web(seeds, "BFS")

        # split big dictionary into small buckets

        buckets = G_search.convert_to_buckets(index)
        snippet_buckets = G_search.convert_to_buckets(snippet_lookup)
        ranks = G_search.compute_ranks(graph)

        # write objects to data base

        for key in buckets:
            current_bucket = Bucket(
                owner='public', hash_code=str(key), dictionary=buckets[key])
            current_bucket.put()

        for key in snippet_buckets:
            current_bucket = Snippet_Bucket(
                hash_code=str(key), dictionary=snippet_buckets[key])
            current_bucket.put()

        curr_ranks = Ranks(owner='public', ranks=ranks)
        curr_ranks.put()

    def clean_up(self):

        buckets = list(Bucket.query())
        snippet_bucket = list(Snippet_Bucket.query())
        for bucket in buckets:
            bucket.key.delete()
        for bucket in snippet_bucket:
            bucket.key.delete()


'''
   terrible   Clean up !!!!

'''


class Search(Handler):

    def get(self, query):

        query = self.request.get("query")
        type_search = self.request.get("type")

        num_results = 10
        tokens = G_search.split_string(
            query, " .,:;'\"{}[]=-_`~\n<>!?/\\#$%^&*()+")

        index_set_list = []
        num_buckets = len(list(Bucket.query()))

        if num_buckets == 0:
            self.response.write("empty index")
            return None

        for token in tokens:
            token = token.lower()
            hash_code = G_search.hash_string(token, num_buckets)
            bucket = Bucket.query(Bucket.hash_code == str(hash_code)).get()
            dictionary = bucket.dictionary
            if token in dictionary:
                index_set_list.append(set(dictionary[token]))

        if not index_set_list:
            self.response.write("keyword not found")
            return None

        links = list(set.intersection(*index_set_list)	)

        if type_search == "public":

            ranks = list(Ranks.query())[0].ranks

        url_ranks_look_up = dict()

        for link in links:
            url_ranks_look_up[link] = ranks[link]
        sorted_url_ranks_list = sorted(
            url_ranks_look_up.items(), key=operator.itemgetter(1), reverse=True)

        result = []

        for url_rank_tuple in sorted_url_ranks_list:
            result.append(url_rank_tuple[0])

        if len(sorted_url_ranks_list) > num_results:
            result = result[:num_results]

        if not result:
            self.response.write("keyword not found")

        result_tuple_lst = []
        for link in result:

            num_buckets = len(list(Snippet_Bucket.query()))
            hash_code = G_search.hash_string(link, num_buckets)
            bucket = Snippet_Bucket.query(
                Snippet_Bucket.hash_code == str(hash_code)).get()
            dictionary = bucket.dictionary
            t = (link, dictionary[link][0], dictionary[link][1])

            result_tuple_lst.append(t)

        self.render("result.html", results=result_tuple_lst)

    def get_snippet(self, url, soup):

        result = ""
        p1 = soup.p
        if not p1:
            return ""

        result += p1.text + "\n"

        while len(result) < 150:

            p2 = p1.findNext('p')
            if p2:
                p2_text = p2.text

                result += p2.text + "\n"
                p1 = p2
            else:
                return result.encode('utf-8')

        return str(result.encode('utf-8'))


PAGE_RE = r'((?:[ ,./?"\'a-zA-Z0-9_=&-]+?)*)'


app = webapp2.WSGIApplication([("/", MainPage)
                               ("/search%s" % PAGE_RE, Search),
                               ("/send_email", Send_email),
                               ("/initialize_public_index", Init_public_index),
                               ("/build_public_index", Build_public_index)], debug=True, config=app_config)
