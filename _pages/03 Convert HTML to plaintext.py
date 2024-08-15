import glob
import csv
import os
import re
from bs4 import BeautifulSoup
from bs4 import Comment
import pprint
import re
import pandas as pd
from url_normalize import url_normalize
from langdetect import detect_langs
from langdetect import DetectorFactory
from urllib import parse
import zipfile
import unicodedata ####
i = 0

DetectorFactory.seed = 123456789

scrapedurls = pd.read_csv('scrapedURLs.csv', low_memory=False, dtype=str)

i = 0

with zipfile.ZipFile('HTML.zip', 'r') as zip:
    with open('input_categorization_allpages.csv', "w", encoding="utf-8", newline='') as createfile:
                    csvwriter = csv.writer(createfile)
                    csvwriter.writerow(['gvkey','year','id','site','HTML_title', 'path', 'path_cleaned'])
        
                    for filename in zip.namelist()[1:]:
                        with zip.open(filename) as file:
                                file_text = file.read().decode('utf-8')
                                # Remove HTML comments that the LXML parser often is incorrectly parsing. 
                                file_text = re.sub(r'<!--(.*?)-->', '', str(file_text))
                                
                                splitname = filename.split("\\")
                                splitname = splitname[-1]
                                splitname = splitname.split("_")
                                year = splitname[0]
                                year = year.replace("HTML/","")
                                
                                gvkey = splitname[1]
                                gvkey = gvkey.replace(".txt","")
                                gvkeywithslash = "/"+gvkey
                                level = splitname[2]
                                number = splitname[3]
                                number = number.replace(".html","")
                                id_page = str(year)+"_"+str(gvkey)+"_"+str(level)+"_"+str(number)

                                soup_original = BeautifulSoup(file_text, 'lxml')

                                # Write page title and path for further classification. 
                                # VLOOKUP to get website, and clean.
                                df_focalpage = scrapedurls[(scrapedurls['id'].astype(str) == str(id_page))]
                                website = df_focalpage['site'].iloc[0]
                                            
                                try:
                                    # Try to retrieve the title tag's content from the parsed HTML file, stripping leading/trailing whitespaces
                                    title = soup_original.title.string.strip()
                                                
                                except:
                                    # If no title is present, store the title tag as missing
                                    title = 'missing'

                                # Strip whitespace, tabs, new lines. 
                                title = re.sub('\s+',' ',title)
                                title = title.replace('\r', ' ').replace('\n', ' ')
                                title = re.sub(' +', ' ', title)
                                title = title.strip()
                                            
                                path = parse.urlsplit(website).path
                                                
                                # Remove slash, underscore, file endings (e.g., html), and leading/trailing whitespaces from path   
                                path_cleaned = re.sub('/', ' ', path)
                                path_cleaned = re.sub('_', ' ', path_cleaned)
                                path_cleaned = re.sub('\..*', '', path_cleaned)
                                path_cleaned = path_cleaned.strip()
                                                
                                csvwriter.writerow([gvkey,year,id_page,website,str(title),path,path_cleaned])
                                
                                soup = soup_original

                                # Find and remove the title tag
                                title_tag = soup.find('title')
                                if title_tag:
                                    title_tag.decompose()
                                    
                                # Keep text in links. 
                                for script in soup(["a"]):
                                    script.extract()

                                # Remove HTML sections by tag name
                                for tag in soup(["script", "style", 'header', 'footer', 'nav', 'sidebar',"meta","button","hidden","hide","visuallyhidden","code","pre","samp","option"]):
                                    tag.decompose()

                                # Remove divs with certain classes
                                for div in soup('div', {'class': ['header', 'footer', 'nav', 'sidebar',"meta","button","hidden","hide","visuallyhidden","d-none"]}):
                                    div.decompose()

                                # Remove code blocks:
                                for widget in soup('p', {'class': ['widgetState']}):
                                    widget.decompose()

                                # Identify elements with CSS properties hiding content
                                hidden_elements = soup.find_all(style=re.compile(r'display:\s*none|visibility:\s*hidden|opacity:\s*0'))

                                # Identify elements with hidden attribute or aria-hidden="true"
                                hidden_elements += soup.find_all(lambda tag: tag.has_attr('hidden') or tag.has_attr('aria-hidden'))

                                # Remove identified hidden elements
                                for element in hidden_elements:
                                    element.decompose()
                                    
                                # Find and remove the div with style="display: none;" or "display: none". These are hidden and contain UI/UX info.
                                hidden_divs = soup.find_all('div', style="display: none;")
                                # Remove each hidden div
                                for div in hidden_divs:
                                    div.decompose()

                                # Remove any remaining CSS rules or attributes that may hide content
                                style_tags = soup.find_all('style')
                                for style_tag in style_tags:
                                    style_content = style_tag.get_text()
                                    style_content = re.sub(r'display:\s*none|visibility:\s*hidden|opacity:\s*0', '', style_content)
                                    style_tag.string = style_content

                                text = soup.get_text(separator=' ')
                                text = text.replace("REPLACEMENT CHARACTER"," ")
                                # Remove any lingering URLs (only removed content after / until the next space).
                                text = re.sub(r"/[^ ]+ ", ' ', text)

                                # Cleaning curly brackets, accounting for potentially unbalanced brackets. 
                                while re.search(r'{[^{}]*}', text):
                                    # Remove unbalanced curly brackets
                                    text = re.sub(r'{[^{}]*}', ' ', text)

                                text=text.replace('-\n', '')
                                
                                # Strip whitespace, tabs, new lines. 
                                text = re.sub('\s+',' ',text)
                                text = re.sub(' +', ' ', text)
                                text = text.strip()

                                text = " "+text+" "

                                # Remove leftover code <*>
                                text  = re.sub('<[^>]+>', ' ', text)
                                text=text.replace('-\n', '')

                                text = text.replace("[ ]"," ")

                                # Strip whitespace, tabs, new lines. 
                                text = re.sub('\s+',' ',text)
                                text = re.sub(' +', ' ', text)
                                text = text.strip()

                                text = re.sub('\s+',' ',text)
                                text = re.sub(' +', ' ', text)
                                text = text.strip()

                                text = text.replace('  ', ' ')
                                text = text.replace('  ', ' ')
                                text = text.replace('  ', ' ')
                                text = text.replace('  ', ' ')
                                text = text.replace('  ', ' ')
                                text = text.strip()
                                
                                # Keep letters, whitespace, punctuation marks, numbers.
                                text = re.sub(r'[^\w\s.,?!:;\-()[\]\'"\d]+', ' ', text)

                                # Safer to replace these with space to prevent concatenated words.  
                                text = text.replace('—',' ')
                                text = text.replace('–',' ')
                                text = text.replace('-',' ') 
                                
                                # Remove anything non alphanumeric
                                # text  = re.sub(r'[^A-Za-z\s]+', ' ', text)
                                text = unicodedata.normalize('NFKD', text) ###
                                text = text.encode('ascii', 'ignore').decode('utf-8') ###
                                
                                # Remove underscores (which are kept with the above)
                                text = text.replace('_', ' ')

                                text = text.replace('  ', ' ')
                                text = text.replace('  ', ' ')
                                text = text.replace('  ', ' ')
                                text = text.replace('  ', ' ')
                                text = text.replace('  ', ' ')
                                text = text.strip()

                                with open("TXT_uncleaned\\"+str(id_page)+".txt", 'w', encoding = 'utf-8') as textfile:
                                        textfile.write(text+" \n\n")

                                i += 1
                                if i % 10000 == 0:
                                    print(i)
