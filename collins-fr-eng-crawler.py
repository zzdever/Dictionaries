# coding: utf-8

from urllib import urlencode
import urllib2
import urlparse
import re
import sys
import base64
import os
import gevent
from gevent import monkey
monkey.patch_all()
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup



root = 'Collins-French-English-Dictionary'   
category = ['Digit','A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
rootURL = [
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-digit',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-a',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-b',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-c',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-d',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-e',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-f',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-g',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-h',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-i',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-j',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-k',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-l',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-m',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-n',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-o',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-p',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-q',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-r',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-s',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-t',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-u',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-v',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-w',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-x',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-y',
    'http://www.collinsdictionary.com/browse/french-english/french-words-starting-with-z'
]




TOTAL_COUNT = 100




class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.url = ''
        self.links = []
        # status control
        self.isInCol = False
        self.divStackInCol = 0
        self.isInLi = False
        self.isLeaf = False
                
                
    def handle_starttag(self, tag, attrs):
		#print "Encountered the beginning of a %s tag" % tag            
        if tag == "div":
            if self.isInCol:
                self.divStackInCol = self.divStackInCol + 1
                
            if len(attrs)>0:
                # Word page has "definition_content"
                # "definition_content" is leaf page condition
                if (u'class', u'definition_main') in attrs:
                    self.isLeaf = True
                    self.links = []
                    
                if (u"class", u"col") in attrs:
                    self.isInCol = True
                    #print "In column"
   
        if tag == "li" and self.isInCol == True:
            self.isInLi = True 
            
        if tag=="a" and self.isInCol and self.isInLi:
            for (attr, val) in attrs:
                if attr==u'href':
                    self.links.append(val)
                    #print 'adding', val, 'for later grasping'

     
    def handle_data(self, data):
        if self.isInCol and self.isInLi:
            pass
            #print data.strip()

            
    def handle_endtag(self, tag):
        if tag == "div":
            if self.isInCol:
                self.divStackInCol = self.divStackInCol - 1
                if self.divStackInCol <= 0:
                    self.isInCol = False
                            
        if tag == 'li' and self.isInLi:
            self.isInLi = False
            #print "Out of li"
            




class Crawler():
    def __init__(self, rootURL, root, category):
        self.urlQueue = [] # if IRI, it is converted
        self.urlQueue.append(self.iriToUri(rootURL))
        self.root = root
        self.category = category
        #self.wordpageFile = open('/Users/ying/wordpage', 'w')

    def GetPage(self, url):
        print 'getting page:',url
        data = ''
        for t in range(3):
            try:
                data = urllib2.urlopen(url, timeout=15).read()
                if len(data)>0:
                    break
            except Exception,e:
                print 'Exception',e,url
                if(t==2):
                    f = open('error', 'a')
                    f.write('\n'+str(e)+'\n'+url+'\n')
                    f.close()
                
            
        if len(data)>0:
            return data
        else:
            print 'Getpage:',url,'blank'


    def urlEncodeNonAscii(self,b):
        return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

    def iriToUri(self, iri):
        parts= urlparse.urlparse(iri)
        return urlparse.urlunparse(
            part.encode('idna') if parti==1 else self.urlEncodeNonAscii(part.encode('utf-8'))
            for parti, part in enumerate(parts)
        )
        
    def Run(self):
        
        
        while True:
            url = ''
            if len(self.urlQueue) > 0:
                url = self.urlQueue.pop(0)
            else:
                f = open(self.root+'/'+self.category+'/'+'done', 'w')
                f.close()
                return
                #self.wordpageFile.write('=========done, got all word pages========')
                #self.wordpageFile.close()
        
        
            html = self.GetPage(url).decode('utf-8')
        
            hp = MyHTMLParser()
            hp.url = url
            hp.feed(html)
            hp.close()
    
            if hp.isLeaf == False:
                links = hp.links
                for link in links:
                    link = self.iriToUri(link)
                    print 'got links:', link
                    self.urlQueue.append(link)
            else:
                print url, 'is a leaf page'
                #self.wordpageFile.write(url)
                f = open(self.root+'/'+self.category+'/'+(url.split('/'))[-1]+'.html', 'w')
                f.write(html.encode('utf-8'))
                f.close()
            
        
        

def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

def iriToUri(iri):
    parts= urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti==1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )
        
def GetPage(url):
    print 'getting page:',url
    data = ''
    for t in range(3):
        try:
            data = urllib2.urlopen(url, timeout=15).read()
            if len(data)>0:
                break
        except Exception,e:
            print 'Exception',e,url
        
    if len(data)>0:
        return data
    else:
        print 'Getpage:',url,'blank'
            
            

    
'''

url = 'http://www.collinsdictionary.com/dictionary/french-english/0-de-mati%C3%A8res-grasses'
html = GetPage(iriToUri(url))

#soup = BeautifulSoup (html)
f = open('/Users/ying/'+(url.split('/'))[-1]+'.html', 'wb')

#head = (soup.find("head")).extract()
#f.write(str(head))


#definition_content = (soup.find("div", {"class" : "definition_content col main_bar"})).extract()
#print definition_content.prettify('utf-8')
f.write(html)



f.close()
#print subtree.encode('utf-8')
#div = soup("div", {"class" : "definition_content col main_bar"})

#children = div[0].findChildren ()
#print len(children)
#print children[0].decode('utf-8')   #### desired output
exit(0)



'''
    
  

def Driver(pid):
    i = pid
    
    path = os.path.join(root,category[i])
    if os.path.exists(path) == False:
        os.mkdir(path)
       
    crawler = Crawler(rootURL[i], root, category[i])
    crawler.Run()
    
   
if __name__=="__main__":
    if os.path.exists(root) == False:
        os.mkdir(root)
    f = open('error', 'w')
    f.close()
        
            
    threads = [gevent.spawn(Driver, i) for i in range(len(category))]
    gevent.joinall(threads)
    
    
    
    