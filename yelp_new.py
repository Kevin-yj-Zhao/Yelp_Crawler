#--*- encoding: utf-8 -*--
import urllib
import urllib2
import os,sys
import re
import BeautifulSoup
import cPickle as pickle
import string
import HTMLParser as hp
import time
import random
import csv

BASE_DIR = "DATA"

example_city = ["Chicago,IL"]

cities = [
				"Erie,PA",
				"Detroit,MI",
				"Boise,ID",
				"Walla Walla,WA",
				"College Station,TX",
				"Kalamazoo,MI",
				"Lafayette,IN",
				"Baton Rouge,LA",
				"Bloomington,IN",
				"Dubuque,IA",
				"Homosassa Springs,FL",
				"Cumberland,MD",
				"Shreveport,LA",
				"Los Angeles,CA",
				"Portland,OR",
				"Grand Rapids,MI",
				"Portland,ME",
				"Redding,CA",
				"Florence,AL,",
				"Tulsa,OK",
				"San Diego,CA",
				"Miami,FL",
				"Virginia Beach,VA",
				"Fort Smith,AR",
				"Buffalo,NY",
				"Sacramento,CA",
				"South Bend,IN",
				"Anchorage,AK",
				"Albuquerque,NM",
				"Kansas City,MO",
				"Jacksonville,NC",
				]

search_url = 'http://www.yelp.com/search?find_loc='
categories = {	'Active Life' : '&cflt=active',
                'Arts & Entertainment': '&cflt=arts',
                'Beauty & Spas': '&cflt=beautysvc',
                'Education': '&cflt=education',
                'Food': '&cflt=food',
                'Local Flavor': '&cflt=localflavor',
                'Nightlife': '&cflt=nightlife',
                'Religious Organnizations': '&cflt=religiousorgs',
                'Restaurants': '&cflt=restaurants',
                'Shopping': '&cflt=shopping',
             }
linkList = []

def FetchData(city, log):
	global linkList
	print '\t', city
	logfile = os.path.join(*[BASE_DIR, "status.log"])
	api = search_url + '+'.join(city.split(',')[0].split(' ')) + "%2C+" + city.split(',')[1]
	for k,v in categories.iteritems():
		if log[city]['categories'].has_key(k):
			continue
		DIR = os.path.join(*[BASE_DIR, city, k])
		url = api + v
		print '\t', k
		page = None
		i_headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.48'}
		req = urllib2.Request(url, headers=i_headers)
		print url
		try:
			page = urllib2.urlopen(req, timeout = 30).read()
		except:
			page = urllib2.urlopen(req).read()
		page1 = False
		if page != None:
			soup = BeautifulSoup.BeautifulSoup(page)
			count = soup.find('div', {"class": "page-of-pages"})
			try:
				pages = re.search(r'\d+', re.search(r'of \w+', str(count.string)).group()).group()
				pages = string.atoi(pages)
			except:
				pages = 1
			if pages > 3:
				pages = 3
			print "There are %i pages" % pages
			print "page No. 1"
			processUrl(url, DIR, city, k, page)
			page1 = True
			for i in range(1, pages):
				print "page No.", i + 1
				s = str(i * 10)
				nexturl = url + "&start=" + s
				processUrl(nexturl, DIR, city, k)
				Sleep(5,10)
		else:
			if not page1:
				processUrl(url, DIR, city, k)
			else:
				pass
		updatelist()
		log[city]['categories'][k] = 1
		f = open(logfile, 'wb')
		pickle.dump(log, f, 0)
		f.close()


def processUrl(url, d, city, category, page = None):
	global linkList
	if page == None:
		i_headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.48'}
		req = urllib2.Request(url, headers=i_headers)
		try:
			print url
			page = urllib2.urlopen(req, timeout = 20).read()
		except:
			pass
		if page == None:
			return
	parser = hp.HTMLParser()
	print "getting links"
	soup = BeautifulSoup.BeautifulSoup(page)
	search_results = soup.findAll(u'h3', {u'class': u'search-result-title'})
	for res in search_results:
		if res.span['class'] == "yla-pill-tip":
			continue
		link = res.a['href']
		try:
			print res.a.string, link
		except:
			print link
		temp = {}
		temp['url'] = link
		temp['downloaded'] = False
		temp['city'] = city
		temp['category'] = category
		temp['name'] = parser.unescape(res.a.string)
		linkList.append(temp)

def downloadpages():
	global linkList
	#linkList = []
	#linkfile = open(os.path.join(*[BASE_DIR, "links.csv"]), 'rb')
	#dreader = csv.DictReader(linkfile)
	sc = counter = 0
	#for row in dreader:
	#	linkList.append(row)
	for row in linkList:
		if row['downloaded'] == 'True':
			continue
		url = 'http://www.yelp.com' + row['url']
		print url
		i_headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.48'}
		req = urllib2.Request(url, headers=i_headers)
		try:
			page = urllib2.urlopen(req, timeout = 20).read()
			d = os.path.join(*[BASE_DIR, row['city'], row['category']])
			if not os.path.exists(d):
				os.makedirs(d)
				print "making dir : " + d
			no = len(os.listdir(d)) + 1
			if no < 10:
				no = '0' + str(no)
			fname = os.path.join(*[d, str(no) + u'.' + row['name']])
			print u"saving", fname
			f = open(fname, 'wb')
			f.write(page)
			f.close()
			linkList[linkList.index(row)]['downloaded'] = True
		except Exception, e:
			print e
		counter += 1
		Sleep(3, 5)
		if counter == 4:
			updatelist()
			Sleep(7, 10)
			sc += 1
			counter = 0
			if sc == 10:
				for i in range(10):
					Sleep(54, 60)
					sys.stdout.write('.')
				sys.stdout.write('\n')
				sc = 0

def updatelist():
	global linkList
	print "\tupdating linklist"
	linkfile = open(os.path.join(*[BASE_DIR, "links.csv"]), 'wb')
	fieldnames = ('url', 'downloaded', 'city', 'category', 'name')
	header = dict((n, n) for n in fieldnames)
	dwriter = csv.DictWriter(linkfile, fieldnames = fieldnames)
	dwriter.writerow(header)
	dwriter.writerows(linkList)
	linkfile.close()
	return

def installproxy():
	proxy = {'http': '127.0.0.1:8087'}
	proxy_s = urllib2.ProxyHandler(proxy)
	opener = urllib2.build_opener(proxy_s)
	urllib2.install_opener(opener)
	return

def Sleep(l, r):
	night = random.randint(l, r)
	time.sleep(night)
	return

def main(citylist):
	global linkList
	if not os.path.exists(BASE_DIR):
		os.makedirs(BASE_DIR)
	lfile = os.path.join(*[BASE_DIR, "links.csv"])
	if os.path.exists(lfile):
		linkfile = open(lfile, 'rb')
		dreader = csv.DictReader(linkfile)
		for row in dreader:
			linkList.append(row)
	logfile = os.path.join(*[BASE_DIR, "status.log"])
	if not os.path.exists(logfile):
		f = open(logfile, 'wb')
		d = dict.fromkeys(citylist)
		for k in d.keys():
			d[k] = {"done": 0, "categories": {}}
		pickle.dump(d, f, 0)
		f.close()
	f = open(logfile, 'rb')
	log = pickle.load(f)
	f.close()
	for city in citylist:
		if log[city]['done']:
			continue
		FetchData(city, log)
		log[city]['done'] = 1
		f = open(logfile, 'wb')
		pickle.dump(log, f, 0)
		f.close()
	updatelist()

if __name__ == "__main__":
	installproxy()
	#citylist = example_city
	reload(sys)
	sys.setdefaultencoding("utf-8")
	citylist = cities
	main(citylist)
	downloadpages()


