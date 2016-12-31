import urllib2
from BeautifulSoup import BeautifulSoup

url ="http://meta.stackoverflow.com"

#print soup.title.string


urls =['http://meta.stackoverflow.com', 'http://stackoverflow.blog',
 'http://chat.stackoverflow.com', 'https://stackoverflow.com/users/signup?ssrc=site_switcher&amp;returnurl=%2fusers%2fstory%2fcurrent&amp;amp;utm_source=stackoverflow.com&amp;amp;utm_medium=dev-story&amp;amp;utm_campaign=signup-redirect',
 'https://stackoverflow.com/users/signup?ssrc=head&returnurl=%2fusers%2fstory%2fcurrent&amp;utm_source=stackoverflow.com&amp;utm_medium=dev-story&amp;utm_campaign=signup-redirect',
 'http://stackoverflow.com/tour', 'https://stackoverflow.com/users/login?ssrc=head&returnurl=http%3a%2f%2fstackoverflow.com%2f', 
 'https://stackoverflow.com/users/login?ssrc=site_switcher&amp;returnurl=http%3a%2f%2fstackoverflow.com%2f', 
 'http://stackoverflow.com/']


def get_snippet(url):
	soup = BeautifulSoup(urllib2.urlopen(url))
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
			
	
	return result.encode('utf-8')



for url in urls:
	print get_snippet(url)	


# Get the content of all the elements in the page. 


#text =""
#while len(text)<150:
#	text = BeautifulSoup(urllib2.urlopen(url)).find("p").getText(separator=" ")
#print text
# Limit the content to the first 150 bytes, eliminate leading or
# trailing whitespace.
#snippet = " ".join(text.split()).strip()[0:150]

# If text was longer than this (most likely), also add '...'
#if len(text) > 150:
#  snippet += "..."

#print snippet  