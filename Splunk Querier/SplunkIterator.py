#!/usr/bin/env python
import sys
import urllib, urllib2
from xml.dom.minidom import parse
from xml.dom import minidom
import xml.dom.minidom
from lxml import etree
import time
import splunk_poller_collector
import multiprocessing
 
class SplunkIterator(object):      
 
                username = 'username'
                password = 'password'
                base_url = 'https://www.xxx.yyy:8089'
 
                def __init__(self,session_key_timer,my_poller):
 
                                self.session_key_timer = session_key_timer
                                self.refresh_time = time.time() + session_key_timer
                                self.urls_list = open("fqdn-urls.txt","r").read().splitlines()
                                self.data_folder = "/home/uddinmo/splunkAPI/data/UK/"
 
                                request = urllib2.Request(SplunkIterator.base_url + '/servicesNS/%s/search/auth/login' % (SplunkIterator.username),data = urllib.urlencode({'username': SplunkIterator.username, 'password': SplunkIterator.password}))
                                server_content = urllib2.urlopen(request)
                                self.session_key = minidom.parseString(server_content.read()).getElementsByTagName('sessionKey')[0].childNodes[0].nodeValue
                                self.session_key_time = time.time()
                                self.my_poller = my_poller
 
                                self.main()
 
 
                # This is to send the saved search to splunk
 
                def send_job_request(self,url):
 
                                # search_query = "search index=proxylogs earliest=\"07/01/2015:00:00:00\" latest=\"08/28/2015:03:00:00\" domain=\"*" + url + "\" | stats dc(host) by host, client_ip, domain"
                                search_query = "search index=proxylogs "+ url +  " earliest=\"01/01/2014:00:00:00\" latest=\"08/28/2015:03:00:00\" | where domain LIKE \"%".format() + url + "\"|chart dc(req_line) by req_line, domain"                                               # FOR URLs
                                # search_query = "search index=proxylogs TERM(" + url +") earliest=\"01/01/2014:00:00:00\" latest=\"08/28/2015:00:00:00\" | where domain LIKE \"" + url + "\"|chart dc(req_line) by req_line, domain"                                                        # FOR IP's
                               
                                request = urllib2.Request(self.base_url + '/services/search/jobs',
                                data = urllib.urlencode({'search': search_query,'output_mode': 'csv'}),
                                headers = { 'Authorization': ('Splunk %s' %self.session_key)})
                                search_results = urllib2.urlopen(request)
                                #print(search_results)
                                sid = xml.dom.minidom.parse(search_results).getElementsByTagName('sid')[0].firstChild.data
                                print("Adding SID data: sid=" + sid + ",url=" + url)
                                self.my_poller.url_to_sid_mapping[str(sid)] = url
 
                ###########################################
 
                def send_job_to_pending_queue(self, url):
 
                                if self.my_poller.no_of_jobs_processing() < 10:               
                                                self.send_job_request(url)
                                else:
                                                time.sleep(5)
                                                self.send_job_to_pending_queue(url)
 
 
                ###########################################
 
                ############                START                   ###############
 
                ###########################################
 
 
                def main(self):
 
                                newline = ''                                                                                                                                                                                                                                        
                                while newline in self.urls_list: self.urls_list.remove(newline)
                                newline = '\r'
                                while newline in self.urls_list: self.urls_list.remove(newline)                                                                      # SANITISE LIST OF URL'S TO PARSE                            
 
                                self.my_poller.clear_all_splunk_jobs()                                                                                                                                                                  # ENSURE NO CURRENT SEARCHES
 
                                for url in self.urls_list:                                                                                                                                                                                                                    # ITERATE THROUGH URLS
                                                if not self.my_poller.verify_if_job_already_sent(url):
                                                               
                                                                if time.time() > self.refresh_time:                                                                                                           # Generate a new session key if session-key age > 30 mins
                                                                                refresh_time = time.time() + self.session_key_timer
                                                                                session_key =  self.my_poller.generate_session_key()
                                                                                print("New session_key generated")                                                                    
                                                                                print "Session Key: %s" % session_key                                                  
 
                                                                no_of_proc_jobs = self.my_poller.no_of_jobs_processing()
                                                                print("There are " + str(no_of_proc_jobs) + " jobs being processed")
 
                                                                if no_of_proc_jobs < 10:             
                                                                                self.send_job_request(url)
                                                                else:
                                                                                self.send_job_to_pending_queue(url)
                                                else:                                                                                                                                                                                                                                                      # ADDED
                                                                print("Job already sent prior: " + url)                                                                                                       # ADDED
 
                                                continue                                                                                                                                                                                                                                              # ADDED
 
                                print("All jobs submitted...awaiting completion of last batch")
                                self.my_poller.term_signal=True
 
 
class SplunkIteratorDE(SplunkIterator):
 
                username = 'username'
                password = 'pwd'
                base_url = 'https://germany-splunk-instance:8089'
 
                def __init__(self,session_key_timer,my_poller):
 
                                self.session_key_timer = session_key_timer
                                self.refresh_time = time.time() + session_key_timer
                                self.urls_list = open("fqdn-urls.txt","r").read().splitlines()
                                self.data_folder = "/home/uddinmo/splunkAPI/data/DE/"
 
                                request = urllib2.Request(SplunkIteratorDE.base_url + '/servicesNS/%s/search/auth/login' % (SplunkIteratorDE.username),data = urllib.urlencode({'username': SplunkIteratorDE.username, 'password': SplunkIteratorDE.password}))
                                server_content = urllib2.urlopen(request)
                                self.session_key = minidom.parseString(server_content.read()).getElementsByTagName('sessionKey')[0].childNodes[0].nodeValue
                                self.session_key_time = time.time()
                                self.my_poller = my_poller
                                self.main()
 
 
def perform_uk_search():
                                my_poller_uk = splunk_poller_collector.SplunkPollCollector(10)                                               # INITIATE POLLER_COLLECTOR OBJECT TO RUN EVERY 5 SECS
                                my_iterator_uk =  SplunkIterator(1800,my_poller_uk)
 
def perform_de_search():
                                my_poller_de = splunk_poller_collector.SplunkPollCollectorDE(10)                                         # INITIATE POLLER_COLLECTOR OBJECT TO RUN EVERY 5 SECS
                                my_iterator_de =  SplunkIteratorDE(1800,my_poller_de)
 
if __name__ == '__main__':
 
                #perform_uk_search()
                #perform_de_search()
               
                
                pocress2 = multiprocessing.Process(target=perform_de_search())
                pocress1 = multiprocessing.Process(target=perform_uk_search())
 
                process2.start()
                process1.start()
                
