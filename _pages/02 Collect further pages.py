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
### Here, we create the file that we use to track what has been scraped.
###########################################
try:
    createfile = open("scrapedURLs.csv", "r", encoding="utf-8")
except IOError:
    with open("scrapedURLs.csv", "w", encoding="utf-8", newline='') as createfile:
        csvwriter = csv.writer(createfile)
        csvwriter.writerow(['gvkey','year','level','nr','site','id','valid_scrape','timestamp','filename'])
        print("Tracking file created")


###########################################
# Read the input data (the full list of one click deeper).
df = pd.read_csv("URLs_1_deeper.csv", low_memory=False)
# If you want to make a selection of years, uncomment the following:
# df = df[(df['year'].astype(int) > 2013)]
print("Data loaded")
###########################################

# Read the tracking file, create a list from it
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
with open("scrapedURLs.csv", "a", encoding="utf-8", newline='') as file:
        csvwriter = csv.writer(file)
        i = 0
        # Loop through the rows of the input file.
        for index, row in df.iterrows():
                    # Read relevant data from the row.
                    year = row['year']
                    gvkey = row['gvkey']
                    # Make sure that the gvkey has leading zeroes.
                    gvkey = str(gvkey)
                    gvkey = gvkey.zfill(6)

                    # We take as the reference point the middle day in the year.
                    # This will ensure that if there is any page in the year that it will be grabbed.
                    # This is needed due to having to use the 'closest' page to the reference point.
                    timestamp = datetime.date(year = int(year), month = 7, day = 2).strftime("%Y%m%d")

                    # Grab the URL and clean it, to be sure.
                    website = row['deeperlink']
                    website = website.lower()
                    website = website.replace('http://','')
                    website = website.replace('https://','')
                    website = website.replace('www.','')
                    website = "https://www."+website
                    # Remove right-most /
                    if website[-1:] == '/':
                            website = website[:-1]

                    # Check if the url can be normalized; if not, skip and document.
                    try:
                            website = url_normalize(website)
                    except Exception as e:
                            csvwriter.writerow([str(gvkey),str(year),str(row['level']),str(row['nr']),website,str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']),"URL normalization error",0,""])
                            newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']))
                            i += 1
                            continue
                    if website[-1:] == '/':
                            website = website[:-1]

                    # If the page is not yet collected, collect.
                    if newurls_keeptracklist.count(str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr'])) > 0:
                        i += 1
                        continue

                    else:
                                print(str(i)+" "+str(year)+" "+str(gvkey)+" "+str(row['level'])+" "+str(row['nr'])+" "+website)
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
                                    csvwriter.writerow([str(gvkey),str(year),str(row['level']),str(row['nr']),website,str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']),"No snapshot available",str(timestamp)])
                                    newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']))
                                    i+=1
                                    continue
                                else:
                                    snapshot = snapshots["closest"]
                                    snapshotyear = snapshot['timestamp']

                                    # Check if the closest snapshot is in the same year.
                                    # If not, document and continue.
                                    if str(snapshotyear[0:4]) != str(year):
                                        csvwriter.writerow([str(gvkey),str(year),str(row['level']),str(row['nr']),website,str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']),"No snapshot in year",str(timestamp)])
                                        newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']))
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
                                        csvwriter.writerow([str(gvkey),str(year),str(row['level']),str(row['nr']),website,str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']),str(e),str(timestamp)])
                                        newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']))
                                        i += 1
                                        continue
                                    
                                # If the status code is not valid, document and continue. Can also be retried later.
                                if page.status_code != 200:
                                        csvwriter.writerow([str(gvkey),str(year),str(row['level']),str(row['nr']),website,str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']),page.status_code,str(timestamp)])
                                        newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']))
                                        i += 1
                                        continue

                                # Process the collected website and save as HTML. 
                                try:
                                        webpage = page.content
                                        # Catch HTML processing errors. 
                                        try:
                                            soup = BeautifulSoup(webpage, "html.parser")
                                        except UnboundLocalError:
                                            csvwriter.writerow([str(gvkey),str(year),str(row['level']),str(row['nr']),website,str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']),"HTML parse error",str(timestamp)])
                                            newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']))
                                            i+=1
                                            continue
                                        except TypeError:
                                            csvwriter.writerow([str(gvkey),str(year),str(row['level']),str(row['nr']),website,str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']),"HTML type error",str(timestamp)])
                                            newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']))
                                            i+=1
                                            continue

                                        # In some cases, the HTML is completely empty.
                                        if len(str(soup)) == 0:
                                               csvwriter.writerow([str(gvkey),str(year),str(row['level']),str(row['nr']),website,str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']),"Empty HTML",str(timestamp)])
                                               newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']))
                                               i += 1
                                               continue
                                            
                                        # Write the HTML and document successful collection.
                                        # In extremely rare cases (1 out of 3.2 million in our case), there could be an encoding issue that is found when writing the file.
                                        htmlerror = 0
                                        with open("HTML\\"+str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr'])+".html", "w", encoding="utf-8") as htmlcode_out:
                                            try:
                                                htmlcode_out.write(str(soup))
                                                csvwriter.writerow([str(gvkey),str(year),str(row['level']),str(row['nr']),website,str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']),"Collected",str(timestamp)])
                                                newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']))
                                            except UnicodeEncodeError:
                                                csvwriter.writerow([str(gvkey),str(year),str(row['level']),str(row['nr']),website,str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']),"HTML encode error",str(timestamp)])
                                                newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']))
                                                htmlerror = 1
                                                
                                        # The block below removes the empty created file in case of the extremely rare encoding issue. 
                                        if htmlerror == 1 and os.path.exists("HTML\\"+str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr'])+".html"):
                                            os.remove("HTML\\"+str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr'])+".html")
                                            htmlerror = 0
                                            print("Removed "+str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr'])+".html")

                                # Catch issue with the data collection. Can also be retried later.
                                except RecursionError:
                                        csvwriter.writerow([str(gvkey),str(year),str(row['level']),str(row['nr']),website,str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']),"Recursion error",str(timestamp)])
                                        newurls_keeptracklist.append(str(year)+"_"+str(gvkey)+"_"+str(row['level'])+"_"+str(row['nr']))
                                        i += 1
                                        continue
                                    
                                # Update the CSV file.
                                file.flush()
                                i += 1
