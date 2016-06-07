               
#!/usr/bin/env python
import sys
import urllib, urllib2
from xml.dom.minidom import parse
from xml.dom import minidom
import xml.dom.minidom
from lxml import etree
import time
import threading
 
class SplunkPollCollector(object):
               
                base_url = 'https://loninsplappp1.uk.db.com:8089'
                username = 'uddinmo'
                password = 'HussainYasin82'
                session_key_timer = 1800
               
                request = urllib2.Request(base_url + '/servicesNS/%s/search/auth/login' % (username),data = urllib.urlencode({'username': username, 'password': password}))
                server_content = urllib2.urlopen(request)
                session_key = minidom.parseString(server_content.read()).getElementsByTagName('sessionKey')[0].childNodes[0].nodeValue
                session_key_time = time.time()
                #print(session_key)
 
                def __init__(self,polling_time):
                                self.base_url = 'https://loninsplappp1.uk.db.com:8089'
                                self.base_url = SplunkPollCollector.base_url
                                self.polling_time = polling_time
                                self.term_signal = False
                                self.url_to_sid_mapping = {}
                                self.jobs_complete_with_no_hits = []
                                self.jobs_uncomplete_with_hits = []
                                self.jobs_completed = []
                                self.session_key = SplunkPollCollector.session_key
                                self.session_key_timer = 1800                  
                                self.data_folder = "/home/uddinmo/splunkAPI/data/UK/"
                                self.clear_all_splunk_jobs()
                                self.poll_and_finalise_done_jobs()
 
                def generate_session_key(self):
 
                                request = urllib2.Request(self.base_url + '/servicesNS/%s/search/auth/login' % (SplunkPollCollector.username),data = urllib.urlencode({'username': SplunkPollCollector.username, 'password': SplunkPollCollector.password}))
                                server_content = urllib2.urlopen(request)
 
                                self.session_key = minidom.parseString(server_content.read()).getElementsByTagName('sessionKey')[0].childNodes[0].nodeValue
                                #print(session_key)
                                return self.session_key
 
 
                def clear_all_splunk_jobs(self):
 
                                jobs_results = self.get_jobs()
                                jobs_results_xml = xml.dom.minidom.parseString(jobs_results)
                                entries = jobs_results_xml.getElementsByTagName('entry')
                                #print(jobs_results_xml.toprettyxml())
               
                                print("Purging " + str(len(entries)) + " job(s)")
                               
                                if len(entries) > 0:
 
                                                #for entry in range(len(entries)):
 
                                                jobs_results_lxml = etree.fromstring(jobs_results)                                                        
                                                sids = jobs_results_lxml.xpath('.//s:key[@name="sid"]', namespaces = {'s':'http://dev.splunk.com/ns/rest'})
 
                                                for each_sid in range(len(sids)):
                                                                print("Each Sid = " + str(each_sid))
                                                                sid = str(sids[each_sid].text)
                                                                print(sid)
                                                                print("Deleting " + sid)
                                                                self.delete_job(sid)
 
 
                def verify_if_job_already_sent(self ,url):
 
                                try:
                                                previously_completed_jobs = open(self.data_folder + "list_of_all_urls_examined.txt","r").read().splitlines()
                                except:
                                                previously_completed_jobs = []
 
                                newline = ''
                                while newline in previously_completed_jobs: previously_completed_jobs.remove(newline)
                                newline = '\r'
                                while newline in previously_completed_jobs: previously_completed_jobs.remove(newline)
 
                                if url in previously_completed_jobs:
                                                #print("Job already sent prior: " + url)
                                                return True
                                else:
                                                print("Job NOT sent prior. Processing...: " + url)
                                                return False
 
 
                def get_jobs(self):
 
                                request = urllib2.Request(self.base_url + '/servicesNS/%s/search/search/jobs/' % (SplunkPollCollector.username),
                                                headers = { 'Authorization': ('Splunk %s' %self.session_key)})
 
                                jobs_results = urllib2.urlopen(request).read()
                                return jobs_results
 
               
                def no_of_jobs_processing(self):
                                jobs_results = self.get_jobs()
                                jobs_results_xml = xml.dom.minidom.parseString(jobs_results)
                                entries = jobs_results_xml.getElementsByTagName('entry')                      #### Get the number of jobs: number of entry tags
                                print("Number of Entries: " + str(len(entries)))                                                                 
                               
 
                                if len(entries) > 0:            #### Parse as lxml and get number of isDone = 0 (Number of jobs still running)
 
                                                jobs_results_lxml = etree.fromstring(jobs_results)                                                        
                                                isDone = jobs_results_lxml.xpath('.//s:key[@name="isDone"]', namespaces = {'s':'http://dev.splunk.com/ns/rest'})
                                                number_of_jobs_processing = 0
 
                                                for eachJob in range(len(isDone)):
                                                                if int(isDone[eachJob].text)==0:
                                                                                number_of_jobs_processing+=1
                                                return number_of_jobs_processing
 
 
                def get_no_of_jobs(self):
                                jobs_results = self.get_jobs()
                                jobs_results_xml = xml.dom.minidom.parseString(jobs_results)
                                entries = jobs_results_xml.getElementsByTagName('entry')
                                return len(entries)
 
                def delete_job(self, sid):
 
                                url = self.base_url + '/servicesNS/' + SplunkPollCollector.username + '/search/search/jobs/' + str(sid) + '/control'
                                values = {'action':'cancel'}
                                data = urllib.urlencode(values)
                                headers = { 'Authorization': ('Splunk %s' %self.session_key)}
                                request = urllib2.Request(url,data,headers)
                                delete_request = urllib2.urlopen(request).read()                                                                                            # DELETE JOB FROM THE LIST OF JOBS BEING
                                print("Delete request sent for job: " + sid)
                               
 
                def poll_and_finalise_done_jobs(self):
                                noj = self.get_no_of_jobs()
                                if (self.term_signal!=True) or (noj > 0):
                                                jobs_results = self.get_jobs()
                                                jobs_results_xml = xml.dom.minidom.parseString(jobs_results)
                                                entries = jobs_results_xml.getElementsByTagName('entry')                                      # ALL JOBS (All entries)
 
                                                jobs_results_lxml = etree.fromstring(jobs_results)                                                        
                                                sid_list = jobs_results_lxml.xpath('.//s:key[@name="sid"]', namespaces = {'s':'http://dev.splunk.com/ns/rest'})
 
 
                                                for entry in entries:                                                                                                                                                                                         # ITERATE OVER EVERY <entry> TAG
 
                                                                key_tags = entry.getElementsByTagName('s:key')
                                                                sid = ''
                                                                isDone = ''
                                                                isDone_value = 0
                                                               
                                                                print
 
                                                                #####################  FINALISE/EXTRACT/DELETE #######################                  
                                                                eventCount = 0
                                                                for key_tag in key_tags:                                                                                                                                                               # ITERRATE OVER THE ELMENTS OF EVERY KEY TAG TO EXTRACT "sid","isDone", and "eventCount"
 
                                                                                if (len(key_tag.childNodes)!=0):
                                                                                                if (key_tag.attributes['name']) and (key_tag.attributes['name'].value=="sid"):                                                                                                        
                                                                                                                sid = str(key_tag.childNodes[0].nodeValue)                                                                                                                                                                                                       # SID VALUE #   <s:key name="sid">1437958204.26121</s:key>
 
                                                                                                elif (key_tag.attributes['name']) and (key_tag.attributes['name'].value=="isDone"):
                                                                                                                isDone_value = key_tag.childNodes[0].nodeValue                                                                                                                                                                          # isDone VALUE #
 
                                                                                                elif (key_tag.attributes['name']) and (key_tag.attributes['name'].value=="eventCount"):                                                                                                                                      
                                                                                                                eventCount = int(key_tag.childNodes[0].nodeValue)                                                                                                                                                     # eventCount VALUE #
 
                                                                if (isDone_value == '1') and (eventCount == 0):
                                                                                print("\nSID complete and no hits: " + sid)
                                                                                print("No hits for URL:>>>=====================>>>" + self.url_to_sid_mapping[sid] + '\n')
                                                                                self.jobs_complete_with_no_hits.append(str(sid))                                                                                                                                                                        # Add UNUSED URL to a list called "jobs_complete_with_no_hits" #
 
                                                                                list_of_unused_urls = open(self.data_folder + "list_of_unused_urls.txt","a")                                                                # CAPTURE RESULTS FOR UNUSED URL
                                                                                list_of_unused_urls.write(self.url_to_sid_mapping[sid]+'\n')
                                                                                list_of_unused_urls.close()                                                                       
 
                                                                                list_of_all_urls = open(self.data_folder + "list_of_all_urls_examined.txt","a")
                                                                                list_of_all_urls.write(self.url_to_sid_mapping[sid] +'\n')
                                                                                list_of_all_urls.close()  
 
                                                                                self.delete_job(sid)
                                                                                self.jobs_completed.append(self.url_to_sid_mapping[sid])
 
                                                                elif (isDone_value =='0') and (eventCount > 0):
                                                                                                                                        print("\nHits observed for sid: " + sid)

                                                                                print("Hits observed for URL:>>>=====================>>>" + self.url_to_sid_mapping[sid] + '\n')

                                                                                self.jobs_uncomplete_with_hits.append(str(sid))                                                                                                                                                                                           # Add USED URL to a list called "jobs_uncomplete_with_no_hits"  I.E. MATCHES #

 

                                                                                list_of_all_urls = open(self.data_folder + "list_of_all_urls_examined.txt","a")                                                       # CAPTURE RESULTS FOR USED URL

                                                                                list_of_all_urls.write(self.url_to_sid_mapping[sid] + '\n')

                                                                                list_of_all_urls.close()  

 

                                                                                self.delete_job(sid)

                                                                                self.jobs_completed.append(self.url_to_sid_mapping[sid])

 

                                                                elif (isDone_value =='1') and (eventCount > 0):

                                                                                print("\nHits observed for sid: " + sid)

                                                                                print("Hits observed for URL:>>>=====================>>>" + self.url_to_sid_mapping[sid] + '\n')

                                                                                self.jobs_uncomplete_with_hits.append(str(sid))                          

 

                                                                                list_of_all_urls = open(self.data_folder + "list_of_all_urls_examined.txt","a")                                                       # CAPTURE RESULTS FOR USED URL

                                                                                list_of_all_urls.write(self.url_to_sid_mapping[sid] + '\n')

                                                                                list_of_all_urls.close()  

 

                                                                                self.delete_job(sid)

                                                                                self.jobs_completed.append(self.url_to_sid_mapping[sid])                                                                      


                                                                                              

 

                                                                # CODE BLOCK TO GIVE RESULTS OF COMPLETED JOBS - POSSIBLE FUTURE USE #######################

 

                                                                #request = urllib2.Request(self.base_url + '/services/search/jobs/' + sid_completed_jobs + '/results?output_mode=csv', headers = { 'Authorization': ('Splunk %s' %self.session_key)})

                                                                #search_results = urllib2.urlopen(request)

                                                                #print search_results.read()

 

                                                threading.Timer(self.polling_time, self.poll_and_finalise_done_jobs).start()

 

                                elif (self.term_signal==True and self.get_no_of_jobs()==0):

                                                self.send_final_results()

 

                def send_final_results(self):

 

                                list_of_unused_urls = open(self.data_folder + "list_of_unused_urls.txt","a")

 

                                list_of_jobs_sent = open(self.data_folder + "list_of_jobs_sent.txt","w")

 

                                print('\n'*3)

                                print("|================================================================================================================================|")

                                print("| The following URL(s) have had no hits for the specified time:                                                                  |")

                                print("|                                                                                                                                |")

                                print("| List can be found at the following location: '/home/uddinmo/splunkAPI/data/list_of_unused_urls.txt' (Cygwin Absolute Path)   |")

                                print("|================================================================================================================================|")

                                print('\n')

 

 

                                list_of_unused_urls2 = open(self.data_folder + "list_of_unused_urls.txt","r").read().splitlines()

                                newline = ''

                                while newline in list_of_unused_urls2: list_of_unused_urls2.remove(newline)

                                newline = '\r'

                                while newline in list_of_unused_urls2: list_of_unused_urls2.remove(newline)

                                for url in list_of_unused_urls2:

                                                print (url)

 

                                ##########################################################

                                for url in self.jobs_completed:

                                                list_of_jobs_sent.write(url + '\n')

                                list_of_jobs_sent.close()

 

                                ###########   PRINT ALL URL TO SID MAPPING (Complete Jobs List)####################

 

                                #for url_sid_mapping in self.url_to_sid_mapping:

                                #             print(url_sid_mapping +":" + self.url_to_sid_mapping[url_sid_mapping])

 

                                list_of_all_urls = open(self.data_folder + "list_of_jobs_sent.txt","r").read().splitlines()

                                newline = ''

                                while newline in list_of_all_urls: list_of_all_urls.remove(newline)

                                newline = '\r'

                                while newline in list_of_all_urls: list_of_all_urls.remove(newline)

                                print('\n'*3)

 

                                print("|====================================================================================================================================|")

                                print("| The following is a complete list of URL(s) that have been examined for hits:                                                       |")

                                print("|                                                                                                                                    |")

                                print("| List can be found at the following location: '/home/uddinmo/splunkAPI/data/list_of_all_urls_examined.txt' (Cygwin Absolute Path) |")

                                print("|====================================================================================================================================|")

                                print('\n')

 

                                for url in list_of_all_urls:

                                                print (url)

 

class SplunkPollCollectorDE(SplunkPollCollector):

 

                base_url = "https://frainsplappp1.de.db.com:8089"

                username = 'uddinmo'

                password = 'HussainYasin82'

                session_key_timer = 1800

 

                request = urllib2.Request(base_url + '/servicesNS/%s/search/auth/login' % (username),data = urllib.urlencode({'username': username, 'password': password}))

                server_content = urllib2.urlopen(request)

                session_key = minidom.parseString(server_content.read()).getElementsByTagName('sessionKey')[0].childNodes[0].nodeValue

                session_key_time = time.time()

 

                def __init__(self,polling_time):

                                self.base_url = "https://frainsplappp1.de.db.com:8089"

                                self.polling_time = polling_time

                                self.term_signal = False

                                self.url_to_sid_mapping = {}

                                self.jobs_complete_with_no_hits = []

                                self.jobs_uncomplete_with_hits = []

                                self.jobs_completed = []

                                self.session_key = SplunkPollCollectorDE.session_key

                                self.session_key_time = 1800

                                self.data_folder = "/home/uddinmo/splunkAPI/data/DE/"

                                self.clear_all_splunk_jobs()

                                self.poll_and_finalise_done_jobs()

 