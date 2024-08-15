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

###############################################################################
### USER INPUT: Adjust the desired cleaning steps below
###############################################################################
###############################################################################
### DECISION 1: Duplicates

# Remove duplicates? Yes / No

# Explanation: Some website addresses are associated with more than one firm 
#              identifier. We manually decided on the primary firm identifier
#              that each website address belongs to. Activating this cleaning 
#              rule removes all of the non-primary, duplicate observations. 

# Recommended: Yes.

setting_duplicate = "Yes"


###############################################################################
### DECISION 2: Invalid pages

# Remove invalid pages? Yes / No

# Explanation: Some webpages are invalid as they are, for example, only 
#              placeholders. We manually checked all webpages without links 
#              (which is a reliable sign of an invalid website) and kept track
#              of all clearly invalid pages. Activating this cleaning rule 
#              removes these webpages.            

# Recommended: Yes.

setting_invalidpages = "Yes"


###############################################################################
### DECISION 3: Invalid sentences

# Remove invalid sentences? Yes / No

# Explanation: Even valid pages can contain invalid sentences, for example, 
#              information on which browser to access the focal website with. 
#              We created a list of thousands of such faulty sentences. 
#              Activating this cleaning rule removes these sentences from the 
#              website texts, leaving behind the valid textual content.

# Recommended: Yes.

setting_invalid_sentences = "Yes"


###############################################################################
### DECISION 4: Non-English pages

# Remove non-English pages? Yes / No

# Explanation: Website texts can be multi-lingual, but many natural language 
#              processing applications are sensitive to multi-lingual texts, 
#              which can negatively affect their outputs. This cleaning rule
#              identifies the language that texts are written in 
#              and removes texts that are not English with a user-specified 
#              degree of certainty.

# Recommended: Yes.

# If yes: what threshold?

# Recommended: 85

setting_english = "Yes"
setting_english_threshold = 0.85


###############################################################################
### DECISION 5: Short texts

# Remove content below a length threshold? Yes / No

# Explanation: Text length is one of the most reliable indicators of faulty
#              website texts. This cleaning rule removes texts below a 
#              user-specified character length threshold.

# Recommended: Yes.

# If yes: what threshold?

# Recommended: TBD

setting_length = "Yes"
setting_length_threshold = 10 

###############################################################################
### DECISION 6: Include page titles in plaintext

# Include page title into the plaintext? Yes / No

# Explanation: It is possible to include the title of the HTML page in the 
#              processed website texts. This would add additional content
#              to these texts. However, titles often contain highly repeating
#              information between pages (e.g., always starting with the full
#              company name). Activating this rule will add the titles parsed
#              from the .html files to the plaintext files. 

# Recommended: No.

setting_incltitle = "No"


###############################################################################
### DECISION 7: Exclude specific categories of pages

# Remove specific page types? Yes / No

# Explanation: Certain types of pages are (for most research purposes) less
#              relevant than others. For instance, site functionality pages
#              typically contain technical details but not substantive content.
#              We inductively identified 16 types of pages and used GPT to classify
#              the pages. 
#
#              We identified the following pages:
#
#              1. Products & Services: Products or services offered, and example projects
#                   or case studies
#              2. News & Events: Articles, news updates, press releases, media kits,
#                   upcoming events, or blog posts related to the organization or its industry
#              3. Home: Main page or landing page
#              4. Contact & Locations: Contact information like address, email, contact
#                   or feedback forms, or information on physical locations or branches
#              5. Investor Relations: Financial reports, corporate governance information,
#                   or other shareholder information
#              6. About Us: Information about the organization or individual(s) behind the website
#              7. Legal: Site's terms and conditions, privacy policy, or other legal information
#              8. Resources, Support & Documentation: Assistance, troubleshooting guides,
#                   or customer support, and related resources available for download;
#                   FAQs; collections of images or videos
#              9. Sustainability & Social Responsibility: Sustainability-related and social
#                   efforts by the organization
#              10. Site Functionality: Website functionality, such as sitemaps, search
#                   functionality, user authentication or registration, the site's user forum
#                   or community, the e-commerce cart, etc.
#              11. Donate & Support: Asking for donations or support for a cause
#              12. Jobs & Opportunities: Information about job opportunities or career paths
#                   at the organization
#              13. Partners & Affiliates: Partners, sponsors, or affiliates of the organization
#              14. Team & Leadership: Team members, executives, or key personnel
#              15. Testimonials & Reviews: Customer testimonials or reviews about the
#                    offering of the organization
#              16. Other: Pages that don't fit into any of the other categories
#
#              Activating this rule will filter out pages of the type of page included in the list.
#              

# Recommended: Yes, page types 3 (Home), 7 (Legal), 8 (Resources, Support & Documentation),
#              and 10 (Site functionality)

setting_pagetype = "Yes"
setting_pagetypelist = ['3', '7', '8', '10']

###############################################################################
### END OF USER INPUT SECTION
###############################################################################
   
# Create a set containing the overall GVKEYs for which pages need to be excluded (here: duplicate websites)
if setting_duplicate == "Yes":
    gvkeys_todrop = pd.read_excel("exclusion_list.xlsx", sheet_name='gvkeys')
    gvkeys_todrop = gvkeys_todrop['gvkey_withslash'].tolist()
    gvkeys_todrop = set(gvkeys_todrop)
else:
    gvkeys_todrop = set([])

# Create a set containing the individual pages that have been manually identified as invalid.
if setting_invalidpages == "Yes":
    pages_todrop = pd.read_excel("exclusion_list.xlsx", sheet_name='pages')
    pages_todrop = pages_todrop['id_page'].tolist()
    pages_todrop = set(pages_todrop)
else:
    pages_todrop = set([])

# Create a list containing junk sentences.
if setting_invalid_sentences == "Yes":
    sentences_to_remove = pd.read_excel("exclusion_list.xlsx", sheet_name='sentences')
    sentences_to_remove = sentences_to_remove['sentence'].tolist()
    sentences_to_remove = sorted(sentences_to_remove, key=len, reverse=True)
else:
    sentences_to_remove = []

# Load up the page categorization.
if setting_pagetype == "Yes":
    gpt_df = pd.read_csv("categorization_applied.csv", low_memory=False, dtype=str)
    pagetype_droplist = gpt_df[gpt_df['classification_GPT'].isin(setting_pagetypelist)]
    pagetype_droplist = pagetype_droplist['id'].tolist()
    pagetype_droplist = set(pagetype_droplist)
else:
    pagetype_droplist = set([])
# Note that, for cost reasons, this categorization was only applied for pages that meet the above settings. 

titles_file = pd.read_csv('input_categorization_allpages.csv', low_memory=False, dtype=str)



i = 0
with open('metadata.csv', "w", encoding="utf-8", newline='') as createfile:
    csvwriter = csv.writer(createfile)
    csvwriter.writerow(['gvkey','gvkeywithslash','year','level','pagenr','id','numberofwords','duplicate','invalid_page','drop_pagetype','primarylang','primarylang_conf','languagelist','included_final'])
    with zipfile.ZipFile('TXT_uncleaned.zip', 'r') as zip:
                    for filename in zip.namelist()[1:]:
                        with zip.open(filename) as file:
                                text = file.read().decode('utf-8')
                                
                                splitname = filename.split("\\")
                                splitname = splitname[-1]
                                splitname = splitname.replace("TXT_uncleaned/","")
                                                               
                                splitname = splitname.split("_")
                                year = splitname[0]
                                
                                gvkey = splitname[1]
                                gvkeywithslash = "/"+gvkey
                                level = splitname[2]
                                number = splitname[3]
                                number = number.replace(".txt","")
                                
                                id_page = str(year)+"_"+str(gvkey)+"_"+str(level)+"_"+str(number)

                                if setting_incltitle == "Yes":
                                    # VLOOKUP to get website, and clean.
                                    df_focalpage = titles_file[(titles_file['id'].astype(str) == str(id_page))]
                                    title = df_focalpage['HTML_title'].iloc[0]
                                    title = title+" "
                                else:
                                    title = ""

                                # Exclude if duplicate
                                if gvkeywithslash in gvkeys_todrop:
                                        duplicatepage = 1
                                else:
                                        duplicatepage = 0
                                
                                # Exclude if invalid page
                                if id_page in pages_todrop:
                                        invalid_page = 1
                                else:
                                        invalid_page = 0

                                # Exclude if page type not to be included
                                if id_page in pagetype_droplist:
                                        drop_pagetype = 1
                                else:
                                        drop_pagetype = 0
                                        
                                # Remove junk sentences
                                if setting_invalid_sentences == "Yes":
                                    for sentence in sentences_to_remove:
                                        #text = re.sub(re.escape(sentence), " ", text, flags=re.IGNORECASE)
                                        text = text.replace(sentence, " ")
                                        text = text.replace('  ', ' ')
                                        text = text.replace('  ', ' ')
                                        text = text.replace('  ', ' ')
                                        text = text.replace('  ', ' ')
                                        text = text.replace('  ', ' ')
                                        text = text.strip()

                                # Classify the language
                                langlist = []
                                DetectorFactory.seed = 123456789

                                try:
                                    
                                    langlist = [detect_langs(text)]
                                    langlist = langlist[0]
                                    mainlang = str(langlist[0])
                                    primarylang = str(mainlang[0:2])
                                    primarylang_conf = mainlang[3:]
                                    primarylang_conf = float(primarylang_conf)
                                    
                                except Exception as e:  
                                    primarylang = "error"
                                    primarylang_conf = 0
                                    langlist = e
                                    
                                # Remove anything non alphanumeric
                                text_alpha  = re.sub(r'[^A-Za-z\s]+', '', text)
                                # Remove underscores (which are kept with the above)
                                text_alpha = text_alpha.replace('_', '')

                                # Note; this is done like this because otherwise numbers and the likes are included. This is a more sound representation of text length for usual applications. 
                                numberofwords = len(text_alpha.split())

                                include = 1
                                
                                # Use settings to determine keeping vs dropping:
                                if setting_duplicate == "Yes" and duplicatepage == 1:
                                    include = 0
                                if setting_invalidpages == "Yes" and invalid_page == 1:
                                    include = 0
                                if setting_english == "Yes" and ((primarylang == "en" and primarylang_conf < setting_english_threshold) or primarylang != "en"):
                                    include = 0
                                if setting_pagetype == "Yes" and drop_pagetype == 1:
                                    include = 0
                                if setting_length == "Yes" and numberofwords <= setting_length_threshold:
                                    include = 0
                                if setting_length == "No" and numberofwords <= 1:
                                    include = 0 

                                csvwriter.writerow([gvkey,gvkeywithslash,year,level,number,id_page,numberofwords,duplicatepage,invalid_page,drop_pagetype,primarylang,primarylang_conf,langlist,include])    

                                if include == 1:
                                    with open("TXT_cleaned\\"+str(id_page)+".txt", 'w', encoding = 'utf-8') as textfile:
                                            textfile.write(title+text+" \n\n")
                                    with open("TXT_combined\\"+str(year)+"_"+str(gvkey)+".txt", 'a', encoding = 'utf-8') as textfile:
                                            textfile.write(title+text+" \n\n")

                                i += 1
                                if i % 10000 == 0:
                                    print(i)
