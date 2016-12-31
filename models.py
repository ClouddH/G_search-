from google.appengine.ext import ndb


class Bucket(ndb.Model):
    owner = ndb.StringProperty(required=True)
    hash_code =ndb.StringProperty(required=True)
    dictionary = ndb.JsonProperty(required=True)
   
class Ranks(ndb.Model):
	owner = ndb.StringProperty(required=True)
	ranks = ndb.JsonProperty(required=True) 


