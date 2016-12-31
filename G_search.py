import sys 
import operator
import urllib
import urllib2
import httplib
import hashlib
#import validators
from urlparse import urlparse
import url





#updated this
## check for header type   do not handle non html page 
def get_page(url):
	if "download" in url:
		return None
	try: 
		req = urllib2.Request(url)
		response = urllib2.urlopen(req ,None,2.5)
		header = response.info().getheader('Content-Type')
		print header
		#header ="text/html"
		if header.find("text/html")!=-1:

			html = response.read()
			return html
		else :
			return None	
	except urllib2.HTTPError, e:
    		print 'HTTPError = ' + str(e.code)
	except urllib2.URLError, e:
    		print 'URLError = ' + str(e.reason)
	except httplib.HTTPException, e:
		print  'HTTPException'
	except Exception as e:
			print "Uncaught Error"


def get_next_target(page):
    start_link = page.find('<a href=')
    if start_link == -1: 
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1:end_quote]
    return url, end_quote

def get_all_links(page):
	
    links = []
    while True:
        url, endpos = get_next_target(page)
        if url:
            links.append(url)
            page = page[endpos:]
        else:
            break
    return links

#print get_all_links(get_page("http://udacity.com/cs101x/urank/index.html"))

def split_string(source,splitlist):
	result =[]
	split_status = True

	for char in source:
		if char in splitlist:

			split_status = True

		else :	
			if split_status :
				result.append(char)
				split_status = False
			else :
				result[-1]+=char


	return result 			

def add_to_index(index, keyword, url):
    keyword = keyword.lower()
    if keyword in index:
    	if url not in index[keyword]:
        	index[keyword].append(url)
    else:
        index[keyword] = [url]

def add_page_to_index(index,url,content):
    
    content_token_list = split_string(content," .,:;'\"{}[]=-_`~\n<>!?/\\#$%^&*()+")
    
    for token in content_token_list :
    	if token.isalnum():
        	add_to_index(index,token,url)


def hash_string(keyword,buckets):
    
    total = 0
    for char in keyword:
        total+= ord(char)
    return total % buckets

def convert_to_buckets(index):

	buckets = dict()

	num_buckets = len(index)/250
	print num_buckets

	for key in index:
		#hash_code = hashlib.md5(key).hexdigest()
		hash_code =hash_string(key,num_buckets)
		if hash_code in buckets:
			buckets[hash_code][key] = index[key]

		else :	
			buckets[hash_code]= {key:index[key]}

	print "number of buckets"
	print len(buckets)
	for hash_code in buckets:
		print len(buckets[hash_code])

	return buckets

def crawl_web(seeds,search_type):
	print "crawling started"
	print seeds
	
	
	index =dict()
	graph =dict()
	total_pages =40

	for item in seeds:
		to_crawl =  [item[0]]
		print to_crawl

		max_pages = item[1]
		print max_pages
		crawled =[]

		while to_crawl:
		
			current_domain=""

			if search_type=="BFS":
				current_page = to_crawl[0]
				to_crawl=to_crawl[1:]
				if 'https://' in current_page or 'http://' in current_page:
					o =urlparse(current_page)
					current_domain = o.scheme+ "://"+ o.netloc
			if search_type =="DFS":
				pass
			crawled.append(current_page)
			print "crawling"+str(len(crawled))
			print current_page	
			if len(crawled)-1 >= max_pages:
				break
			content = get_page(current_page)
			if content:	
				add_page_to_index(index,current_page,content)
				outlinks = get_all_links(content)
				graph[current_page]=outlinks
				for link in outlinks :	
					if not link in crawled and not link=="#":
					
					
						if link.find('https://')!=-1 or  link.find('http://')!=-1:
							to_crawl.append(link) 	

						if link[0]=="/" and link.find("//")==-1 and url.url(current_domain+link):
							#print "modified local url"
							#print current_domain+link
							to_crawl.append(current_domain+link) 	

		print "finish indexing one seed "
		print "current_seed"+item[0]
		print "page crawled"+str(item[1])	

	return index,graph					


        

def compute_ranks(graph):
    print "computing ranks started"
    d = 0.8
    num_iterations =10
    ranks = dict()
    
    npages = len(graph)
    for page in graph: 
        ranks[page] = 1.0/npages
    
    for i in range(num_iterations):
        newranks=dict()
        
        for current_page in graph:
            newrank = (1-d)/npages
            inlinks=[]
            
            for page in graph :
                if current_page in graph[page]:
                    inlinks.append(page)
                    
            for page in inlinks:
                
                newrank+= d*(ranks[page]/len(graph[page]))
            
            newranks[current_page] = newrank
        ranks = newranks
    print "computing ranks ended"  

    return ranks    


def look_up(index,keyword,ranks,num_results):


 	#tokens = split_string(keyword," .,:;'\"{}[]=-_`~\n<>!?/\\#$%^&*()+")
	
	#print tokens

	#index_set_list=[]

	#for token  in tokens:
	#	if token  in index:
	#		index_set_list.append( set(index[token]) )
	#print index_set_list	

	#if not index_set_list:
	#	return None 		
	
	#links =list (set.intersection(*index_set_list)	)

	if not keyword in index:
		return None 

	links = index[keyword]
	url_ranks_look_up = dict()

	for link in links :
		url_ranks_look_up[link]=ranks[link]
	sorted_url_ranks_list = sorted(url_ranks_look_up.items(), key=operator.itemgetter(1),reverse=True)

	result=[]
	for url_rank_tuple in sorted_url_ranks_list:
		result.append(url_rank_tuple[0])
	
	if len(sorted_url_ranks_list)<=num_results:
		return result
	else :
		return result[:num_results]

#bad_url_2="/questions/41338715/golang-database-updating-a-non-existing-entry"
#url1 ="https://docs.python.org/"
#url2 ="https://uwaterloo.ca/"
#url3 = "http://www.nytimes.com/"
#url_cn = "http://www.pku.edu.cn/"

#ranks = compute_ranks(graph)
#bad_url="https://download.mozilla.org/?product=firefox-50.1.0-SSL&amp;os=win64&amp;lang=en-US"
#print get_page(bad_url_2)

#print index
#print buckets[12]['business']
#print ranks
#print index 

#print look_up(index,'recipe',ranks,2)
#print hash_string("business",18)



#url_4="http://stackoverflow.com/"
#buckets,graph = crawl_web(url_4,50,"BFS")
#=print crawled
#print url.url("http://stackoverflow.com/")

