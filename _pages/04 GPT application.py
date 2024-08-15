import os
import openai
import csv
import pandas as pd
import time
import tiktoken
import sys

### NOTE: This script uses the openai package version 0.27.8. More recent versions of the package may not work with this script.

# Remove duplicates? Yes / No

# Explanation: Some website addresses are associated with more than one firm 
#              identifier. We manually decided on the primary firm identifier
#              that each website address belongs to. Activating this cleaning 
#              rule removes all of the non-primary, duplicate observations. 

# Recommended: Yes.
setting_duplicate = "Yes"

# Create a set containing the overall GVKEYs for which pages need to be excluded (here: duplicate websites)
if setting_duplicate == "Yes":
    gvkeys_todrop = pd.read_excel("exclusion_list.xlsx", sheet_name='gvkeys')
    gvkeys_todrop = gvkeys_todrop['gvkey_withslash'].tolist()
    gvkeys_todrop = set(gvkeys_todrop)
else:
    gvkeys_todrop = set([])
    

# This is what GPT3.5 / 4 use.
encoding = tiktoken.get_encoding("cl100k_base")

openai.api_key = "FILL IN YOUR OWN API KEY HERE"

list_definition = """1. Products & Services: Products or services offered, and example projects or case studies
                    2. News & Events: Articles, news updates, press releases, media kits, upcoming events, or blog posts related to the organization or its industry
                    3. Home: Main page or landing page
                    4. Contact & Locations: Contact information like address, email, contact or feedback forms, or information on physical locations or branches
                    5. Investor Relations: Financial reports, corporate governance information, or other shareholder information
                    6. About Us: Information about the organization or individual(s) behind the website
                    7. Legal: Site's terms and conditions, privacy policy, or other legal information
                    8. Resources, Support & Documentation: Assistance, troubleshooting guides, or customer support, and related resources available for download; FAQs; collections of images or videos
                    9. Sustainability & Social Responsibility: Sustainability-related and social efforts by the organization
                    10. Site Functionality: Website functionality, such as sitemaps, search functionality, user authentication or registration, the site's user forum or community, the e-commerce cart, etc.
                    11. Donate & Support: Asking for donations or support for a cause
                    12. Jobs & Opportunities: Information about job opportunities or career paths at the organization
                    13. Partners & Affiliates: Partners, sponsors, or affiliates of the organization
                    14. Team & Leadership: Team members, executives, or key personnel
                    15. Testimonials & Reviews: Customer testimonials or reviews about the offering of the organization
                    16. Other: Pages that don't fit into any of the other categories"""

df = pd.read_csv('input_categorization_allpages.csv', dtype=str)
df['gvkey_withslash'] = df['gvkey'].apply(lambda x: '/' + x)

try:
    createfile = open('categorization_applied.csv', "r", encoding="utf-8", newline='')
except IOError:
    with open('categorization_applied.csv', "w", encoding="utf-8", newline='') as createfile:
        csvwriter = csv.writer(createfile)
        csvwriter.writerow(['gvkey','year','id','site','HTML_title', 'path', 'path_cleaned','classification_GPT'])
        print("Output file created")

try:
    createfile = open('categorization_errors.csv', "r", encoding="utf-8", newline='')
except IOError:
    with open('categorization_errors.csv', "w", encoding="utf-8", newline='') as createfile:
        csvwriter = csv.writer(createfile)
        csvwriter.writerow(['gvkey','year','id','site','HTML_title', 'path', 'path_cleaned','error','retries'])
        print("Error file created")

# Read the tracking file, create a list from it.
csvreader = pd.read_csv('categorization_applied.csv', low_memory=False)
processed_files = csvreader['id'].values.astype(str).tolist()

# If this is the first time running, create an empty list
if processed_files is None:
    processed_files = []
    
tracker = len(processed_files)

totaltokens = 0

retries = 0

print("Starting categorization")
with open('categorization_applied.csv', "a", encoding="utf-8", newline='') as f:
    csvwriter = csv.writer(f)
    
    for index, row in df.iterrows():
        # Do not categorize duplicates
        if row["gvkey_withslash"] in gvkeys_todrop:
            continue

        # Do not categorize front pages
        if row["id"].split("_")[2] == "0":
            continue

        # Do not categorize pages already categorized
        if row["id"] in processed_files:
            continue
        
        else:
            retries = 0
            while retries <= 10:
                try:
                    if totaltokens >= 89250:
                        time.sleep(2)
                        print("Close to limit; sleeping for two seconds") 
                        totaltokens = 0

                    if row["HTML_title"] != "missing" and row["HTML_title"] != "Untitled":
                        content = "Title: "+str(row["HTML_title"])+", URL: "+str(row["path"])

                    else:
                        content = "URL: "+str(row["path"])

                    response = openai.ChatCompletion.create(
                      model="gpt-3.5-turbo",
                      messages=[
                        {
                          "role": "system",
                          "content": "You are a research assistant tasked with classifying web pages into one of the following categories: "+list_definition+"You will be provided with the title of the HTML page and the URL, with the domain name removed. Please select only one of these categories and report the category and nothing else. If you cannot determine the category based on the information provided, please use the '16. Other' category. Only provide the category's number and nothing else."
                        },
                        {
                          "role": "user",
                          "content": content
                        }
                      ],

                      # We set a low temperature, which is more appropriate for classification tasks that require consistency rather than creativity. 
                      # "Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic."
                      # We want it to be as replicable as possible.
                      # Limiting output tokens to two minimizes variation in output formatting. 
                      temperature=0,
                      max_tokens=2,
                      request_timeout=5,
                      top_p=1,
                      frequency_penalty=0,
                      presence_penalty=0
                    )

                    chat_response = response['choices'][0]['message']['content']
                    chat_response = chat_response.replace(".","")
                    chat_response = chat_response.strip()
                    
                    nrtokens_in = response["usage"]["prompt_tokens"]
                    nrtokens_out = response["usage"]["completion_tokens"]
                    totaltokens = totaltokens + nrtokens_in + nrtokens_out
                   
                    outrow = [row["gvkey"],row["year"],row['id'],row["site"],row["HTML_title"],row["path"],row["path_cleaned"],chat_response]
                    csvwriter.writerow(outrow)
                    f.flush()
                    processed_files.append(row["id"])
                    tracker += 1
                    print(str(row['id'])+" --- "+str(tracker)+"  "+str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                    retries = 99
                    
                except (openai.error.APIError, openai.error.ServiceUnavailableError, openai.error.RateLimitError, openai.error.Timeout) as error:
                    print(str(error)+" "+str(row["id"]))
                    print(retries)
                    time.sleep(0.5+retries*2)
                    with open('categorization_errors.csv', "a", encoding="utf-8", newline='') as f2:
                        csvwriter2 = csv.writer(f2)
                        outrow2 = [row["gvkey"],row["year"],row['id'],row["site"],row["HTML_title"],row["path"],row["path_cleaned"],error,retries]
                        csvwriter2.writerow(outrow2)
                    retries += 1
                    if retries == 10:
                        print("Ten retries: ending script.")
                        sys.exit()
            

print("Done, retries = "+str(retries)+" retries at end, "+str(tracker)+" rows completed out of "+str(len(df)))


                    

                    
                 
                
                
         

