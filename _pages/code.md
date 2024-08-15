---
permalink: /code/
title: "Codebase"
author_profile: false
redirect_from: 
  - /code.html
---
The following contains the most up-to-date version of our codebase to scrape longitudinal organizational website data using the Wayback Machine. Before running any code, please read through the entire documentation, provided [here](https://haans-mertens.github.io/code/documentation). For frequently asked questions about the code- and database please see the [FAQ](https://haans-mertens.github.io/faq/).

The set-up should work as-is after extracting the content of the .zip file (accessible [here](https://github.com/haans-mertens/haans-mertens.github.io/raw/master/_pages/General%20purpose%20set-up.zip) into a folder (which can be located anywhere). Also note that the script will assume that the working directory is the same as the directory in which the scripts are located. The code has some checks built in to ensure this.

Summary
======
The core set-up is as follows:

1. Create empty folders called 'HTML', 'TXT_uncleaned, ‘TXT_cleaned’ and 'TXT_combined'.
2. Run the [‘01 Collect frontpages.py’](https://raw.githubusercontent.com/haans-mertens/haans-mertens.github.io/master/_pages/01%20Collect%20frontpages.py) script to collect the frontpages.
3. Run the [‘02 Collect further pages.py’](https://raw.githubusercontent.com/haans-mertens/haans-mertens.github.io/master/_pages/02%20Collect%20further%20pages.py) script to collect all pages one click deeper on the domain.
4. Archive the files in the 'HTML' folder to a .zip file called ['HTML.zip'](https://github.com/haans-mertens/haans-mertens.github.io/raw/master/_pages/HTML.zip).
5. Run the [‘03 Convert HTML to plaintext.py’](https://raw.githubusercontent.com/haans-mertens/haans-mertens.github.io/master/_pages/03%20Convert%20HTML%20to%20plaintext.py) script to process the files in [‘HTML.zip’](https://github.com/haans-mertens/haans-mertens.github.io/raw/master/_pages/HTML.zip).
6. Optional: Run the [‘04 GPT application.py’](https://raw.githubusercontent.com/haans-mertens/haans-mertens.github.io/master/_pages/04%20GPT%20application.py) script to classify the selected pages for further selection.
7. Archive the files in the 'TXT_uncleaned folder to a .zip file called ['TXT_uncleaned.zip'](https://github.com/haans-mertens/haans-mertens.github.io/raw/master/_pages/TXT_uncleaned.zip).
8. Run the [‘05 Clean and select.py’](https://raw.githubusercontent.com/haans-mertens/haans-mertens.github.io/master/_pages/05%20Clean%20and%20select.py) script to apply selection and cleaning of the texts into the ‘TXT_cleaned’ folder and combine the selected pages to one plaintext file per GVKEY/year into the ‘TXT_combined’ folder.

From there, you can work with the texts in the ‘TXT_cleaned’ and 'TXT_combined' folders in further analyses. The various metadata files that get created can be used to summarize the data or can serve as input in analyses.
