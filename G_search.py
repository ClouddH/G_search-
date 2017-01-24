import sys
import operator
import urllib
import urllib2
import httplib
import hashlib

from urlparse import urlparse
import url
from BeautifulSoup import BeautifulSoup


'''
 Fetch html content of the consumed url. Handles possible exception gracefully 

'''


def get_page(url):
    if "download" in url:
        return None
    try:
        req = urllib2.Request(url)
        response = urllib2.urlopen(req, None, 2.5)
        header = response.info().getheader('Content-Type')
        print header
        #header ="text/html"
        if header.find("text/html") != -1:

            html = response.read()
            return html
        else:
            return None
    except urllib2.HTTPError, e:
        print 'HTTPError = ' + str(e.code)
    except urllib2.URLError, e:
        print 'URLError = ' + str(e.reason)
    except httplib.HTTPException, e:
        print 'HTTPException'
    except Exception as e:
        print "Uncaught Error"
'''
  Helper method for the web crawler

'''


def get_next_target(page):
    start_link = page.find('<a href=')
    if start_link == -1:
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1:end_quote]
    return url, end_quote
'''
  Helper method for the web crawler

'''


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

'''
  Helper method for the web crawler

'''


def split_string(source, splitlist):
    result = []
    split_status = True

    for char in source:
        if char in splitlist:

            split_status = True

        else:
            if split_status:
                result.append(char)
                split_status = False
            else:
                result[-1] += char

    return result
'''
  Helper method for the web crawler

'''


def add_to_index(index, keyword, url):
    keyword = keyword.lower()
    if keyword in index:
        if url not in index[keyword]:
            index[keyword].append(url)
    else:
        index[keyword] = [url]
'''
  Helper method for the web crawler

'''


def add_page_to_index(index, url, content):

    content_token_list = split_string(
        content, " .,:;'\"{}[]=-_`~\n<>!?/\\#$%^&*()+")

    for token in content_token_list:
        if token.isalnum():
            add_to_index(index, token, url)
'''
  computes hashcode based on the consumed keyword or url to determine bucket 
  number to store the data when split the index to a dictionary of buckets

'''


def hash_string(keyword, buckets):

    total = 0
    for char in keyword:
        total += ord(char)
    return total % buckets
'''
 split the consumed index (too large to store in google datastore as a single
 	object) into multiple buckets

'''


def convert_to_buckets(index):
    print "start to convert"

    buckets = dict()

    num_buckets = len(index) / 250
    print num_buckets

    for key in index:
            #hash_code = hashlib.md5(key).hexdigest()
        hash_code = hash_string(key, num_buckets)
        if hash_code in buckets:
            buckets[hash_code][key] = index[key]

        else:
            buckets[hash_code] = {key: index[key]}

    print "number of buckets"
    print len(buckets)
    for hash_code in buckets:
        print len(buckets[hash_code])

    return buckets

'''
	Helper method that extracts a page sniipet for the consumed url 
	** currently sucks !  need improvement !!!

'''


def get_snippet(url, soup):

    print "curr url"
    print url
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

''' 
  Webcrawler method that uses BFS to do web crawling to build the search index.
  return the index , graph (modeling connection between pages), and snippet_lookup
  which stores the tiltle and page snippet for all the crawled url
  **  further decompose needed **

'''


def crawl_web(seeds, search_type):

    snippet_lookup = dict()
    index = dict()
    graph = dict()
    total_pages = 40

    for item in seeds:
        to_crawl = [item[0]]

        max_pages = item[1]

        crawled = []

        while to_crawl:

            current_domain = ""

            if search_type == "BFS":
                current_page = to_crawl[0]
                to_crawl = to_crawl[1:]
                if 'https://' in current_page or 'http://' in current_page:
                    o = urlparse(current_page)
                    current_domain = o.scheme + "://" + o.netloc

            crawled.append(current_page)
            print "crawling" + str(len(crawled))
            print current_page
            if len(crawled) - 1 >= max_pages:
                break
            content = get_page(current_page)
            if content:
                soup = BeautifulSoup(content)
                title = soup.title.string
                snippet = get_snippet(current_page, soup)
                snippet_lookup[current_page] = (title, snippet)
                add_page_to_index(index, current_page, content)
                outlinks = get_all_links(content)
                graph[current_page] = outlinks
                for link in outlinks:
                    if not link in crawled and not link == "#":

                        if link.find('https://') != -1 or link.find('http://') != -1:
                            to_crawl.append(link)

                        if link[0] == "/" and link.find("//") == -1 and url.url(current_domain + link):

                            to_crawl.append(current_domain + link)
    return index, graph, snippet_lookup

'''
  consumes the graph and produces a dictionary ranks that maps each url to items
  ranking score

'''


def compute_ranks(graph):
    print "computing ranks started"
    d = 0.8
    num_iterations = 10
    ranks = dict()

    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages

    for i in range(num_iterations):
        newranks = dict()

        for current_page in graph:
            newrank = (1 - d) / npages
            inlinks = []

            for page in graph:
                if current_page in graph[page]:
                    inlinks.append(page)

            for page in inlinks:

                newrank += d * (ranks[page] / len(graph[page]))

            newranks[current_page] = newrank
        ranks = newranks
    print "computing ranks ended"

    return ranks
