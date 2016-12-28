from google.appengine.ext import ndb


class Bucket(ndb.Model):
    hash_code =ndb.StringProperty(required=True)
    dictionary = ndb.JsonProperty(required=True)
   
   


