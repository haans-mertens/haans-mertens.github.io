import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
import csv
from urllib3.exceptions import HTTPError as BaseHTTPError
from url_normalize import url_normalize
import pyautogui
import datetime
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError

pd.set_option('display.max_columns', None)

################################################################################
### Set-up
################################################################################
###########################################
### The block below will create a new file if not yet present
### Here, we create two files:
###     a) The file that we use to track what has been scraped.
###     b) The file to which we write the URLs on the home page.
###########################################
try:
    createfile = open("scrapedURLs.csv", "r", encoding="utf-8")
except IOError:
    with open("scrapedURLs.csv", "w", encoding="utf-8", newline='') as createfile:
        csvwriter = csv.writer(createfile)
        csvwriter.writerow(['gvkey','year','level','nr','site','id','valid_scrape','timestamp','filename'])
        print("Tracking file created")

try:
    createfile = open("URLs_1_deeper.csv", "r", encoding="utf-8")
except IOError:
    with open("URLs_1_deeper.csv", "w", encoding="utf-8", newline='') as createfile:
        csvwriter = csv.writer(createfile)
        csvwriter.writerow(['gvkey','year','level','nr','id','source','deeperlink','timestamp_source'])
        print("URLs file created")
        time.sleep(5)

# We loop through all available years.
# Here, the archive started in 1996 and current year is 2021. Since Compustat runs until 2020, we run until then.
years = list(range(1996,2021,1))

###########################################                                
# Read the input data from Compustat
df = pd.read_excel("00 urls_in.xlsx", sheet_name='urls')
df['weburl'].replace('', np.nan, inplace=True)
df.dropna(subset=['weburl'], inplace=True)

print("Data loaded")
###########################################


# Read the tracking file, create a list from it.
csvreader = pd.read_csv("scrapedURLs.csv", low_memory=False)
newurls_keeptracklist = csvreader['id'].values.astype(str).tolist()

# If this is the first time running, create an empty list
if newurls_keeptracklist is None:
    newurls_keeptracklist = []

################################################################################
### Scraping
################################################################################
# Set up headers for the requests package (else some sites block it)
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}

# We will write newly scraped pages to the scrapedURLs.csv file
with open("scrapedURLs.csv", "a", encoding="utf-8", newline='') as scrapefile:
    # We will write the URLs to the URLs_1_deeper.csv file
    with open("URLs_1_deeper.csv", "a", encoding="utf-8", newline='') as urlsfile:
        csvwriterurls = csv.writer(urlsfile)

        # Loop through each year.
        for year in years:
                print(year)
                # Take only the observations for firms active in the focal year.
                df_selection = df[(df['firstyear'].astype(int) <= int(year)) & (df['lastyear'].astype(int) >= int(year))]
                # We take as the reference point the middle day in the year.
                # This will ensure that if there is any page in the year that it will be grabbed.
                # This is needed due to having to use the 'closest' page to the reference point.
                timestamp = datetime.date(year = int(year), month = 7, day = 2).strftime("%Y%m%d")
                csvwriterscrape = csv.writer(scrapefile)
                
                # i tracks the firms
                i = 0

                # Go through each row
                for index, row in df_selection.iterrows():
                    nrurls = 0
                    j = 0 
                    website = row['weburl_forscraper']
                    # Grab the URL and clean it, to be sure.
                    website = website.lower()
                    website = website.replace('http://','')
                    website = website.replace('https://','')
                    website = website.replace('www.','')
                    website = "https://www."+website
                    # Remove right-most /
                    if website[-1:] == '/':
                            website = website[:-1]

                    gvkey = row['gvkey']
                    gvkey = str(gvkey)
                    # Make sure gvkey has the leading zeroes.
                    gvkey = gvkey.zfill(6)
                                                    
                    # Check if the url can be normalized; if not, skip and document.
                    try:
                            website = url_normalize(website)
                    except Exception as e:
                            csvwriterscrape.writerow([str(gvkey),str(year),"0","0",website,str(year)+"_"+str(gvkey)+"_0_0","URL normalization error",0,""])
                            newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_0_0")
                            i += 1
                            continue
                    if website[-1:] == '/':
                            website = website[:-1]

                    # If the page is not yet collected, collect.
                    if newurls_keeptracklist.count(str(year)+"_"+str(gvkey)+"_0_0") > 0:
                        i += 1

                    else:
                                print(str(i)+" "+str(year)+" "+str(gvkey)+" "+website)
                                # We first check if and which pages are available.
                                waybackurl = "http://archive.org/wayback/available?url="+website+"&timestamp="+str(timestamp)
                                while True:
                                    try:
                                        response = requests.get(waybackurl)
                                        snapshots = response.json()["archived_snapshots"]
                                    except ConnectionError:
                                        print("-------------------------------------------")
                                        print("Connection error: sleeping for one minute  ")
                                        print("-------------------------------------------")
                                        time.sleep(60)
                                        continue
                                    except JSONDecodeError:
                                        print("-------------------------------------------")
                                        print("JSON Decode error: sleeping for one minute ")
                                        print("-------------------------------------------")
                                        time.sleep(60)
                                        continue
                                    break
                                
                                # Check if there are any pages.
                                # If not, document and continue.
                                if len(snapshots) == 0:
                                    csvwriterscrape.writerow([str(gvkey),str(year),"0","0",website,str(year)+"_"+str(gvkey)+"_0_0","No snapshot available",str(timestamp),""])
                                    newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_0_0")
                                    i+=1
                                    continue

                                else:
                                    snapshot = snapshots["closest"]
                                    snapshotyear = snapshot['timestamp']

                                    # Check if the closest snapshot is in the same year.
                                    # If not, document and continue.
                                    if str(snapshotyear[0:4]) != str(year):
                                        csvwriterscrape.writerow([str(gvkey),str(year),"0","0",website,str(year)+"_"+str(gvkey)+"_0_0","No snapshot in year",str(timestamp),""])
                                        newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_0_0")
                                        i+=1
                                        continue
                                    else:
                                        snapshot = snapshot["url"]
                                    
                                # Scrape the archived page. 
                                try:
                                        page = requests.get(snapshot, allow_redirects=True, timeout = 60, headers=headers)

                                # There are many possible errors.
                                # Catch all these and write. Can be revisited later (often, retrying later would solve the issue).
                                except Exception as e:
                                        csvwriterscrape.writerow([str(gvkey),str(year),"0","0",website,str(year)+"_"+str(gvkey)+"_0_0",str(e),str(timestamp)])
                                        newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_0_0")
                                        i += 1
                                        continue

                                # If the status code is not valid, document and continue. Can also be retried later.
                                if page.status_code != 200:
                                        csvwriterscrape.writerow([str(gvkey),str(year),"0","0",website,str(year)+"_"+str(gvkey)+"_0_0",page.status_code,str(timestamp),""])
                                        newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_0_0")
                                        i += 1
                                        continue
                                    
                                # Process the collected website and save as HTML.
                                try:
                                        webpage = page.content
                                        
                                        # Catch HTML processing errors. 
                                        try:
                                            soup = BeautifulSoup(webpage, "html.parser")
                                        except UnboundLocalError:
                                            csvwriterscrape.writerow([str(gvkey),str(year),"0","0",website,str(year)+"_"+str(gvkey)+"_0_0","HTML parse error",str(timestamp),""])
                                            newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_0_0")
                                            i+=1
                                            continue
                                        except TypeError:
                                            csvwriterscrape.writerow([str(gvkey),str(year),"0","0",website,str(year)+"_"+str(gvkey)+"_0_0","HTML type error",str(timestamp),""])
                                            newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_0_0")
                                            i+=1
                                            continue

                                        # In some cases, the HTML is completely empty.
                                        if len(str(soup)) == 0:
                                               csvwriterscrape.writerow([str(gvkey),str(year),"0","0",website,str(year)+"_"+str(gvkey)+"_0_0","Empty HTML",str(timestamp),""])
                                               newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_0_0")
                                               i += 1
                                               continue
                                            
                                        # Write the HTML and document successful collection.
                                        # In extremely rare cases (1 among the millions in our case), there could be an encoding issue that is found when writing the file.
                                        htmlerror = 0
                                        with open("HTML\\"+str(year)+"_"+str(gvkey)+"_0_0.html", "w", encoding="utf-8") as htmlcode_out:
                                            try:
                                                htmlcode_out.write(str(soup))
                                                csvwriterscrape.writerow([str(gvkey),str(year),"0","0",website,str(year)+"_"+str(gvkey)+"_0_0","Collected",str(timestamp),str(year)+"_"+str(gvkey)+"_0_0.html"])
                                                newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_0_0")
                                            except UnicodeEncodeError:
                                                csvwriterscrape.writerow([str(gvkey),str(year),"0","0",website,str(year)+"_"+str(gvkey)+"_0_0","HTML encode error",str(timestamp),""])
                                                newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_0_0")
                                                htmlerror = 1
                                                
                                        # The block below removes the empty created file in case of the extremely rare encoding issue. 
                                        if htmlerror == 1 and os.path.exists("HTML\\"+str(year)+"_"+str(gvkey)+"_0_0.html", "w", encoding="utf-8"):
                                            os.remove("HTML\\"+str(year)+"_"+str(gvkey)+"_0_0.html", "w", encoding="utf-8")
                                            htmlerror = 0
                                            print("Removed "+str(year)+"_"+str(gvkey)+"_0_0"+".html")


                                # Catch issue with the data collection. Can also be retried later.
                                except RecursionError:
                                        csvwriterscrape.writerow([str(gvkey),str(year),"0",str(j),website,str(year)+"_"+str(gvkey)+"_0_0","Recursion error",str(timestamp),""])
                                        newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_0_0")
                                        i += 1
                                        continue

                                # Process the HTML to get all URLs.
                                urls = []
                                urls += [link['href'] for link in soup.find_all('a', {'href': True})]
                                urls = set(urls)
                                urls = list(urls)

                                # The list will contain a lot of junk; we will go through cleaning and write the valid ones
                                # to this list.
                                urls_cleaned = []
                                
                                for url_new in urls:
                                    # Remove "/web/YYMMDDSSSSSS/" if present
                                    if url_new[:9] == "/web/"+str(year):
                                        url_new = url_new[20:]
                                    # Remove "http://web.archive.org/web/YYMMDDSSSSSS/" if present
                                    if url_new[:22] == "http://web.archive.org":
                                        url_new = url_new[42:]

                                    # These links point to content on the same page.
                                    # Keeping them would lead to repeating pages.
                                    url_new = url_new.split("?")[0]
                                    url_new = url_new.split("#")[0]
                                    # Do not keep e-mail addresses.

                                    if "mailto" in url_new:
                                            continue
                                    # Cleaning
                                    if url_new[:2] == "//":
                                            url_new = url_new.replace("//","")
                                            
                                    if url_new[-1:] == '/':
                                            url_new = url_new[:-1]
                                    # Filter out problematic filetypes that can't be scraped (e.g. images).     
                                    if (len(url_new) >= 4 and (url_new[-4:] != '.gif' and url_new[-4:] != '.pdf' and url_new[-4:] != '.svg' and
                                                             url_new[-4:] != '.png' and url_new[-4:] != '.jpg' and
                                                             url_new[-5:] != '.jpeg' and url_new[-4:] != '.exe' and
                                                             url_new[-4:] != '.mp4' and url_new[-4:] != '.mp3' and
                                                             url_new[-4:] != '.doc' and url_new[-5:] != '.docx' and
                                                             url_new[-3:] != 'rss' and url_new[-3:] != 'xml' and 
                                                             url_new[-4:] != '.avi' and url_new != "http" and url_new != "https" and url_new != "javascript")):

                                        # If first character is /, append with website
                                        if url_new[:1] == '/' or url_new[:2] == "./":
                                              url_new = url_new.replace("./","/")  
                                              newtoscrape = website+url_new

                                              newtoscrape = newtoscrape.replace('http://','')
                                              newtoscrape = newtoscrape.replace('https://','')
                                              newtoscrape = newtoscrape.replace('www.','')
                                              newtoscrape = newtoscrape.split(":")[0]
                                              newtoscrape = "https://www."+newtoscrape

                                              newtoscrape = url_normalize(newtoscrape)
                                              
                                              if newtoscrape[-1:] == '/':
                                                    newtoscrape = newtoscrape[:-1]
                                              urls_cleaned.append(newtoscrape)

                                            
                                        else:
                                              checkurl = url_new.replace('.html','')
                                              checkurl = checkurl.replace('.htm','')
                                              checkurl = checkurl.replace('.php','')
                                              # Some URLS do not have the / at the start but are still within the same domain.
                                              # e.g. not /about but about.
                                              # Since those don't have a period in the URL (after removing .htm or .html) we can check for them.
                                              if checkurl.count(".") == 0:
                                                    newtoscrape = website+'/'+url_new
                                                    newtoscrape = newtoscrape.replace('http://','')
                                                    newtoscrape = newtoscrape.replace('https://','')
                                                    newtoscrape = newtoscrape.replace('www.','')
                                                    newtoscrape = newtoscrape.split(":")[0]
                                                    newtoscrape = "https://www."+newtoscrape

                                                    newtoscrape = url_normalize(newtoscrape)
                                                  
                                                    if newtoscrape[-1:] == '/':
                                                        newtoscrape = newtoscrape[:-1]
                                                    urls_cleaned.append(newtoscrape)
                                              else:
                                                  url_new = url_new.replace('http://','')
                                                  url_new = url_new.replace('https://','')
                                                  url_new = url_new.replace('www.','')
                                                  url_new = url_new.split(":")[0]
                                                  url_new = "www."+url_new
                                                  try:
                                                          url_new = url_normalize(url_new)
                                                  except Exception as e:
                                                          continue
                                                  if url_new[-1:] == '/':
                                                        url_new = url_new[:-1]

                                                  newtoscrapeurl = website
                                                  newtoscrapeurl = newtoscrapeurl.replace('http://','')
                                                  newtoscrapeurl = newtoscrapeurl.replace('https://','')
                                                  newtoscrapeurl = newtoscrapeurl.replace('www.','')
                                                  newtoscrapeurl = newtoscrapeurl.split(":")[0]
                                                  newtoscrapeurl = "www."+newtoscrapeurl
                                                  newtoscrapeurl = url_normalize(newtoscrapeurl)
                                                  if newtoscrapeurl[-1:] == '/':
                                                        newtoscrapeurl = newtoscrapeurl[:-1]

                                                  newtoscrape = url_new      
                                                  # This checks that the cleaned URL is indeed in the same domain
                                                  # The left-most part of the URL (with the length of the source URL) should be the same. 
                                                  if newtoscrape[:len(newtoscrapeurl)] != newtoscrapeurl:
                                                          continue
                                                  # The cleaned URL cannot be the original URL.
                                                  if newtoscrape == website:
                                                          continue
                                                  urls_cleaned.append(newtoscrape)
                                # Remove duplicates.      
                                urls_cleaned = set(urls_cleaned)
                                urls_cleaned = list(urls_cleaned)
                                nrurls = len(urls_cleaned)

                                # Add the frontpage to the ongoing list. 
                                newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_0_0")

                                j += 1
                                # Update the CSV.
                                scrapefile.flush()

                                # Write all the processed URLs.
                                for uniqueurl in urls_cleaned:
                                      #print(uniqueurl)
                                      csvwriterurls.writerow([str(gvkey),str(year),"1",str(j),str(year)+"_"+str(gvkey)+"_1_"+str(j),website,uniqueurl,str(timestamp)])
                                      j += 1
                                      urlsfile.flush()
                                      

                                nrurls = 0
                                i += 1
                    


