---
permalink: /faq/
title: "Frequently Asked Questions"
author_profile: false
redirect_from: 
  - /faq.html
---
> 1:	Do the URLs in weburl_forscraper have to be in a specific format?

No; the code will standardize URLs into the following format: https://www.URL.  

> 2:	Will the code still work when the identifier is non-numeric?

Yes, as long as the identifier uniquely identifies the units of analysis of interest all code will continue to work. Note, however, that the current set-up adds leading zeroes to these identifiers (to a length of six characters total)—given the GVKEY identifier used in Compustat. As such, make sure to remove or alter the line “gvkey = gvkey.zfill(6)” if this is not desired. 

> 3:	How can I exclude specific pages for my own application?

We generally recommend collecting all available data, and selecting out specific pages further down the workflow. At the moment, for example, we select out specific types of pages in the “05 Combine selected texts.py” script. The most straightforward way to exclude individual pages is to add a classification code in the “categorization_applied.csv” file that we currently use to exclude pages and to then add this classification code in the selection script. For instance, if we want to exclude the page “2015_023804_1_1.txt” from the set in the general purpose set-up we could edit the column “classification_GPT” in the “categorization_applied.csv” file (which is currently ‘99’ in the example) for this row to for instance “0”. Editing the line “criteria = ['3', '7', '8', '10']” in the “05 Combine selected texts.py” script to “criteria = [‘0’,'3', '7', '8', '10']” would subsequently exclude this page from the combined dataset. 

> 4:	I receive the error “ModuleNotFoundError: No module named XYZ”. (where XYZ would be a name of a package). What should I do?

You would receive this error if you did not yet install the specific package into your Python installation. Please refer to to README file for a list of packages that are used in the entire workflow, or see the top lines for specific Python code files to see which packages get used. Alternatively, you could try simply running the scripts and installing those packages that get listed via the above error. See https://packaging.python.org/en/latest/tutorials/installing-packages/ for information on how to install packages into Python. 

> 5:	What packages are used in the codebase? What versions did these packages have at the time of development?

The following packages are used. The versions of these packages that were used at the time of writing are shown between parentheses. If you want to install these specific package versions (rather than the latest package version) when installing, please use the command “pip install package_name==version_number”. For example, “pip install bs4==0.0.1” installs bs4 version 0.0.1. 

•	bs4 (version 0.0.1)
•	datetime (version 5.2)
•	langdetect (version 1.0.9)
•	numpy (version 1.24.3)
•	openai (version 0.27.8)
•	pandas (version 2.0.2)
•	requests (version 2.31.0)
•	tiktoken (version 0.4.0)
•	url_normalize (version 1.4.3)

> 6:	How can I change the code to collect more than one annual snapshot?

This can be accomplished by altering the  ‘01 Collect frontpages.py’ script. Specifically, the script loops through the relevant years and looks for the closest snapshot to July 2nd of that year. This is done with the line “timestamp = datetime.date(year = int(year), month = 7, day = 2).strftime("%Y%m%d")”. It is possible to add a loop within the loop over years, where you additionally loop over months within those years, but not that this also requires updating the identifiers (to include month information rather than only year information) and filenames (which are built from the identifiers). Likewise, the statement “if str(snapshotyear[0:4]) != str(year):” would need to be altered to also filter out pages that are not in the specified months (as otherwise it might collect repeat pages within the same year). 

> 7:	Is the progress saved when the code breaks?

Yes, scraping progress is saved via the “scrapedURLs.csv” file. Specifically, completed attempts get written to this file, and if you stop (either due to the code breaking or manual stops by the researcher) the code will not re-do those pages that have already been attempted based on this file. In case you want to re-attempt certain pages (for instance due to errors being thrown that may be one-off errors, such as temporary connection outages) you need to remove those rows from the “scrapedURLs.csv” file. 

> 8:	Is it possible to parallelize the scraping?

It is possible to parallelize the scraping in a relatively straightforward manner: by splitting up the list of websites to check into sub-files and running separate Python instances for those sub-files you can have multiple scripts scraping the Wayback Machine. Do make sure to also write progress to separate files (e.g. “scrapedURLs_1.csv”, “scrapedURLs_2.csv”, etc.). In the case of pages that are one or more clicks deeper, it is likewise possible to parallelize the scraping by splitting the "URLs_1_deeper.csv” file. 

However, it is likely that the pace of scraping in parallel on the same computer would exceed the rate limits imposed by the Wayback Machine’s API—which would likely result in a temporary or even permanent ban. As such, we recommend not parallelizing the scraping.

> 9:	Is it possible to speed up the different processing steps?

The main way to speed up the various steps after scraping is to split up the files to be processed (for example, cleaning the HTML pages). A relatively straightforward approach is to add selection on the years and to only process those pages that fall within the specified year. This enables you to run several Python instances in parallel. Of course, in case data gets written to for instance a CSV file do make sure that the scripts first write year-specific CSV files that you can then combine once all years are processed.

> 10:	What kind of errors may emerge when running the scripts, and what can I do about them?

The most common errors occur during the scraping process, with it being reliant on the Wayback Machine. The script is designed not to crash when facing an error, but instead to write the error to the “scrapedURLs.csv” file for further consideration. We have found that errors are very rare, but common examples include connection errors (which are typically but not always temporary and can be retried as per the answer to the “Is the progress saved when the code breaks?” question above. Others include for instance HTML type, parse, and encoding errors which in our experience are not resolved by retrying. 

Likewise, we limit the number of redirects during scraping to thirty (we have found that increasing this number does not lead to pages getting collected), and various HTML code errors such as the well-known 404 “Page does not exist”, 403 “Resource is forbidden”, and 502 “Bad gateway” codes. It is also our experience that these errors tend to persist even when retrying the scrape. Finally, a possible error is the JSON decode error when attempting to identify the available snapshots for a given URL via the API. This error can occur in particular when sending too many requests to the API and likely implies that you are (temporarily) blocked. Although this error should not occur when using our base code, if you attempt to for instance increase scraping speed by parallelizing the scraping (see “Is it possible to parallelize the scraping?”, above) then it is more likely that you would see this error. In that case, the best approach is to limit the scraping speed (for instance by building in a time lag between scrapes with the “sleep” command in Python). 

> 11:	What if the Internet Archive goes offline? Can I still use your codebase?

Although the core theoretical steps that we discuss in the paper would apply for any web scraping over time, much of the code base pertaining to the scraping step is tailored to the Internet Archive. This implies that the scraping code would need to be altered to match alternative data sources if the Internet Archive goes offline. 

We see two primary alternative approaches to scraping longitudinal data that does not require the Internet Archive: first, researchers could construct longitudinal databases themselves by scraping web pages at regular intervals. All steps and code provided would be applicable except minor differences in the HTML collection step (as one does not need to go through an API to download the pages of an input list). Of course, this approach is also different in that it requires researchers to wait long periods of time to construct such databases. Second, alternative web archiving services do exist, with the most feasible alternative being Common Crawl (https://commoncrawl.org/, archiving web pages since 2008). Similar to the above, our steps and code are applicable except for the initial HTML collection differing due to differences in the API set-up.

> 12:	I want to work with the files in the compressed archived (the .zip files). It is extremely slow to extract these. Is there any way to speed this up?

Although it is possible to open and work with the files directly from the compressed archive files (via Python, as we currently do in the codebase), it is also possible to extract the files to a local folder. We have found that this runs very slow (on Windows machines, at least) when real-time protection is turned on. It may help to temporarily turn this off while extracting—just be sure to turn it back on! If you are concerned about the files contained in the archives, then you may first scan these with your antivirus. 

> 13:	What are the minimum specifications for being able to work with the database?

Although we do not know the exact minimum requirements to work with these data, the major bottleneck for the data collection and processing is simply clock time—followed by memory as the secondary bottleneck. We tried to design our approach in such a way that other users would be able to work with our database (and any other data collected via this approach) reliably. To this end, we tested all our collection and processing scripts on a six-year-old workstation that is not particularly powerful (AMD Ryzen 7 1700 (3.0 GHz) processor, 2x 8 GB of 3200 MHz memory). It was able to comfortably run all reported steps, even if some required quite some clock time.

