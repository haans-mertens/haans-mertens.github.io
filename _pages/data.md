---
permalink: /data/
title: "*CompuCrawl* database"
author_profile: false
redirect_from: 
  - /data.html
---
This page contains the complete code and data for the CompuCrawl database, which includes archived websites of publicly traded North American firms listed in the Compustat database between 1996 and 2020. The database encompasses 11,277 firms with 86,303 firm/year observations and 1,617,675 webpages in the final cleaned and selected set.

Final database files
======
If you are interested in the final database of texts, the following files are available:
- ["HTML.zip"](https://www.dropbox.com/scl/fi/sadofeczgvw5iqd58u4dh/HTML.zip?rlkey=zau82qcgqa0weieysqp66q4sm&dl=0): Contains the full set of HTML pages.
- ["TXT_uncleaned.zip"](https://www.dropbox.com/scl/fi/qdjm2cie9r64vhmdsa3jv/TXT_uncleaned.zip?rlkey=19na0vi9rf2hxs2m4ga8d2lht&dl=0): Includes processed but uncleaned text files.
- ["TXT_cleaned.zip"](https://www.dropbox.com/scl/fi/vxrun4k5zprqc2zl5gj9d/TXT_cleaned.zip?rlkey=nmbh3n5p24ebs887yzri4fxu0&dl=0): Contains selected and cleaned text files.
- ["TXT_combined.zip"](https://www.dropbox.com/scl/fi/nyz23wc5b8zml7zyijicd/TXT_combined.zip?rlkey=tg5ywz7m0pght589xxuwj1nqp&dl=0): Includes combined and cleaned text files at the GVKEY/year level. 

Full workflow and file descriptions
======
The full set of files, in order of use, is as follows:
1. [**Compustat_2021.xlsx:**](https://www.dropbox.com/scl/fi/nccafl7omgebgpcfyz4jt/Compustat_2021.xlsx?rlkey=e0m1y2vrop2jdcg79czxt1df8&dl=0) The input file containing the URLs to be scraped and their date range.
2. [**01 Collect frontpages.py:**](https://www.dropbox.com/scl/fi/x1ol9yk0794ayqlse9hsa/01-Collect-frontpages.py?rlkey=ty7hm1pmq9j9oajd6hj73v010&dl=0) Python script scraping the front pages of the list of URLs and generating a list of URLs one page deeper in the domains.
3. [**URLs_1_deeper.csv:**](https://www.dropbox.com/scl/fi/jirf2mchti417ncnz7w77/URLs_1_deeper.csv?rlkey=562o7sn4xuikotixoa1dfvwjh&dl=0) List of URLs one page deeper on the main domains.
4. [**02 Collect further pages.py:**](https://www.dropbox.com/scl/fi/4cncdplut79xdkhavvell/02-Collect-further-pages.py?rlkey=6sbvwcjvctxpaliphvjvvok3v&dl=0) Python script scraping the list of URLs one page deeper in the domains.
5. [**scrapedURLs.csv:**](https://www.dropbox.com/scl/fi/knhyksggjyqwq4ewep7qy/scrapedURLs.csv?rlkey=l2tstrw3sejtd2haybsr15ll8&dl=0) Tracking file containing all URLs that were accessed and their scraping status.
6. [**HTML.zip:**](https://www.dropbox.com/scl/fi/sadofeczgvw5iqd58u4dh/HTML.zip?rlkey=zau82qcgqa0weieysqp66q4sm&dl=0) Archived version of the set of individual HTML files.
7. [**03 Convert HTML to plaintext.py:**](https://www.dropbox.com/scl/fi/5qmek8ij1lgg1vx3tjqx6/03-Convert-HTML-to-plaintext.py?rlkey=xg495ew46o6mq32lipyky59v7&dl=0) Python script converting the individual HTML pages to plaintext.
8. [**TXT_uncleaned.zip:**](https://www.dropbox.com/scl/fi/qdjm2cie9r64vhmdsa3jv/TXT_uncleaned.zip?rlkey=19na0vi9rf2hxs2m4ga8d2lht&dl=0) Archived version of the converted yet uncleaned plaintext files.
9. [**input_categorization_allpages.csv:**](https://www.dropbox.com/scl/fi/qsf7vfh1vjt9fgazhqb8e/input_categorization_allpages.csv?rlkey=zoeuci4iyehbus0tkphriy8f1&dl=0) Input file for classification of pages using GPT according to their HTML title and URL.
10. [**04 GPT application.py:**](https://www.dropbox.com/scl/fi/tr0c32gkzbzvgpi4119w2/04-GPT-application.py?rlkey=fdza2kyk9f0lncd98ro7nkjy0&dl=0) Python script using OpenAI’s API to classify selected pages according to their HTML title and URL.
11. [**categorization_applied.csv:**](https://www.dropbox.com/scl/fi/4dkhnlyt179zg15cu7ry4/categorization_applied.csv?rlkey=uaixtzi7kn1yc21bi915sbkpe&dl=0) Output file containing the classification of the selected pages.
12. [**exclusion_list.xlsx:**](https://www.dropbox.com/scl/fi/4jkx0vdyzqqvjgle8ggp4/exclusion_list.xlsx?rlkey=z7jem35kxqf98slq6lxpq3h2l&dl=0) File containing three sheets: 'gvkeys' containing the GVKEYs of duplicate observations (that need to be excluded), 'pages' containing page IDs for pages that should be removed, and 'sentences' containing (sub-)sentences to be removed.
13. [**05 Clean and select.py:**](https://www.dropbox.com/scl/fi/79twj2473nt2povjmjtds/05-Clean-and-select.py?rlkey=0dvugjyg0jxch8hx4xsdpp8k3&dl=0) Python script applying data selection and cleaning (including selection based on page category), with setting and decisions described at the top of the script. This script also combines individual pages into one combined observation per GVKEY/year.
14. [**metadata.csv:**](https://www.dropbox.com/scl/fi/79twj2473nt2povjmjtds/05-Clean-and-select.py?rlkey=0dvugjyg0jxch8hx4xsdpp8k3&dl=0) Metadata containing information on all processed HTML pages, including those not selected.
15. [**TXT_cleaned.zip:**](https://www.dropbox.com/scl/fi/vxrun4k5zprqc2zl5gj9d/TXT_cleaned.zip?rlkey=nmbh3n5p24ebs887yzri4fxu0&dl=0) Archived version of the selected and cleaned plaintext page files. This file serves as input for the word embeddings application.
16. [**TXT_combined.zip:**](https://www.dropbox.com/scl/fi/nyz23wc5b8zml7zyijicd/TXT_combined.zip?rlkey=tg5ywz7m0pght589xxuwj1nqp&dl=0) Archived version of the combined plaintext files at the GVKEY/year level. This file serves as input for the data description using topic modeling.
17. [**06 Topic model.R:**](https://www.dropbox.com/scl/fi/qugbm1slf74wtfzsfya2z/06-Topic-model.R?rlkey=we10ke9pp6erou2yifa665rr2&dl=0) R script that loads up the combined text data from the folder stored in "TXT_combined.zip", applies further cleaning, and estimates a 125-topic model.
18. [**TM_125.RData:**](https://www.dropbox.com/scl/fi/38quhvlejg94av22iep8m/TM_125.RData?rlkey=rxizjmtii2ufcc3rzolndg3l6&dl=0) RData file containing the results of the 125-topic model.
19. [**loadings125.csv:**](https://www.dropbox.com/scl/fi/mjgzdj0dg39yyqo8lwj1d/loadings125.csv?rlkey=rcqacdw2urpua4yhh7x1p7k9x&dl=0) CSV file containing the loadings for all 125 topics for all GVKEY/year observations that were included in the topic model.
20. [**125_topprob.xlsx:**](https://www.dropbox.com/scl/fi/gc4fbe5i8fx2pfwj34th9/125_topprob.xlsx?rlkey=eus10bmp4kia074i2v6kqixsy&dl=0) Overview of top-loading terms for the 125 topic model.
21. [**07 Word2Vec train and align.py:**](https://www.dropbox.com/scl/fi/kays9eqw80nqsm5jj2v57/07-Word2Vec-train-and-align.py?rlkey=mrrglcvhigdg6kei1ydvmvyng&dl=0) Python script that loads the plaintext files in the "TXT_cleaned.zip" archive to train a series of Word2Vec models and subsequently align them in order to compare word embeddings across time periods.
22. [**Word2Vec_models.zip:**](https://www.dropbox.com/scl/fi/r2jqux2pzz7h0tve48seu/Word2Vec_models.zip?rlkey=3ccuoee9vhft1891d5qmr5d40&dl=0) Archived version of the saved Word2Vec models, both unaligned and aligned.
23. [**08 Word2Vec work with aligned models.py:**](https://www.dropbox.com/scl/fi/i9zqlbhhw3hwsp01b7v6l/08-Word2Vec-work-with-aligned-models.py?rlkey=ejm6cp5inursdeqy4nzoyj7hc&dl=0) Python script which loads the trained Word2Vec models to trace the development of the embeddings for the terms “sustainability” and “profitability” over time.
24. [**99 Scrape further levels down.py:**](https://www.dropbox.com/scl/fi/d8rp0mu56sw84v1aj5p2x/99-Scrape-further-levels-down.py?rlkey=uhdpe5r2cli4oywh5nmq74x47&dl=0) Python script that can be used to generate a list of unscraped URLs from the pages that themselves were one level deeper than the front page.
25. [**URLs_2_deeper.csv:**](https://www.dropbox.com/scl/fi/csw6rafn3vul1c5sd3zrm/URLs_2_deeper.csv?rlkey=ghva6lqed5qf2vaajtkhlkc5c&dl=0) CSV file containing unscraped URLs from the pages that themselves were one level deeper than the front page.
