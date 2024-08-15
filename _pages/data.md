---
permalink: /
title: "CompuCrawl database"
author_profile: false
redirect_from: 
  - /data/
  - /data.html
---
This folder contains the full set of code and data for the CompuCrawl database. The database contains the archived websites of publicly traded North American firms listed in the Compustat database between 1996 and 2020—representing 11,277 firms with 86,303 firm/year observations and 1,617,675 webpages in the final cleaned and selected set.

For those only interested in downloading the final database of texts, the files "HTML.zip", "TXT_uncleaned.zip", "TXT_cleaned.zip", and "TXT_combined.zip" contain the full set of HTML pages, the processed but uncleaned texts, the selected and cleaned texts, and combined and cleaned texts at the GVKEY/year level, respectively.

The files are ordered by moment of use in the work flow. For example, the first file in the list is the input file for code files 01 and 02, which create and update the two tracking files "scrapedURLs.csv" and "URLs_1_deeper.csv" and which write HTML files to its folder. "HTML.zip" is the resultant folder, converted to .zip for ease of sharing. Code file 03 then reads this .zip file and is therefore below it in the ordering.

The full set of files, in order of use, is as follows:
1. FAQ.docx: FAQ file containing answers to some frequently asked questions.
2. Compustat_2021.xlsx: The input file containing the URLs to be scraped and their date range.
3. 01 Collect frontpages.py: Python script scraping the front pages of the list of URLs and generating a list of URLs one page deeper in the domains.
4. URLs_1_deeper.csv: List of URLs one page deeper on the main domains.
5. 02 Collect further pages.py: Python script scraping the list of URLs one page deeper in the domains.
6. scrapedURLs.csv: Tracking file containing all URLs that were accessed and their scraping status.
7. HTML.zip: Archived version of the set of individual HTML files.
8. 03 Convert HTML to plaintext.py: Python script converting the individual HTML pages to plaintext.
9. TXT_uncleaned.zip: Archived version of the converted yet uncleaned plaintext files.
10. input_categorization_allpages.csv: Input file for classification of pages using GPT according to their HTML title and URL.
11. GPT application.py: Python script using OpenAI’s API to classify selected pages according to their HTML title and URL.
12. categorization_applied.csv: Output file containing classification of selected pages.
13. exclusion_list.xlsx: File containing three sheets: 'gvkeys' containing the GVKEYs of duplicate observations (that need to be excluded), 'pages' containing page IDs for pages that should be removed, and 'sentences' containing (sub-)sentences to be removed.
14. Clean and select.py: Python script applying data selection and cleaning (including selection based on page category), with setting and decisions described at the top of the script. This script also combined individual pages into one combined observation per GVKEY/year.
15. metadata.csv: Metadata containing information on all processed HTML pages, including those not selected.
16. TXT_cleaned.zip: Archived version of the selected and cleaned plaintext page files. This file serves as input for the word embeddings application.
17. TXT_combined.zip: Archived version of the combined plaintext files at the GVKEY/year level. This file serves as input for the data description using topic modeling.
18. 06 Topic model.R: R script that loads up the combined text data from the folder stored in "TXT_combined.zip", applies further cleaning, and estimates a 125-topic model.
19. TM_125.RData: RData file containing the results of the 125-topic model.
20. loadings125.csv: CSV file containing the loadings for all 125 topics for all GVKEY/year observations that were included in the topic model.
21. 125_topprob.xlsx: Overview of top-loading terms for the 125 topic model.
22. 07 Word2Vec train and align.py: Python script that loads the plaintext files in the "TXT_cleaned.zip" archive to train a series of Word2Vec models and subsequently align them in order to compare word embeddings across time periods.
23. Word2Vec_models.zip: Archived version of the saved Word2Vec models, both unaligned and aligned.
24. 08 Word2Vec work with aligned models.py: Python script which loads the trained Word2Vec models to trace the development of the embeddings for the terms “sustainability” and “profitability” over time.
25. 99 Scrape further levels down.py: Python script that can be used to generate a list of unscraped URLs from the pages that themselves were one level deeper than the front page.
26. URLs_2_deeper.csv: CSV file containing unscraped URLs from the pages that themselves were one level deeper than the front page.
