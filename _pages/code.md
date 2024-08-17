---
permalink: /code/
title: "Codebase"
author_profile: false
redirect_from: 
  - /code.html
---
This section contains the latest version of our codebase for scraping longitudinal website data using the Wayback Machine. For frequently asked questions about the code and database, please refer to the [FAQ](https://haans-mertens.github.io/faq/).

Setup instructions
======
1. Before running any code, please read through the entire documentation, provided [here](https://haans-mertens.github.io/code/documentation).
2. Ensure the working directory is the same as the directory containing the scripts. The code has checks to verify this.
3. Create empty folders called 'HTML', 'TXT_uncleaned, ‘TXT_cleaned’ and 'TXT_combined'.
4. Run the [‘01 Collect frontpages.py’](https://raw.githubusercontent.com/haans-mertens/haans-mertens.github.io/master/_pages/01%20Collect%20frontpages.py) script to collect the frontpages.
5. Run the [‘02 Collect further pages.py’](https://raw.githubusercontent.com/haans-mertens/haans-mertens.github.io/master/_pages/02%20Collect%20further%20pages.py) script to collect additional pages one click deeper into the domain.
6. Archive the files in the 'HTML' folder to a .zip file called 'HTML.zip'.
7. Run the [‘03 Convert HTML to plaintext.py’](https://raw.githubusercontent.com/haans-mertens/haans-mertens.github.io/master/_pages/03%20Convert%20HTML%20to%20plaintext.py) script to process the files in ‘HTML.zip’.
8. Optional: Run the [‘04 GPT application.py’](https://raw.githubusercontent.com/haans-mertens/haans-mertens.github.io/master/_pages/04%20GPT%20application.py) script to classify the selected pages for further selection.
9. Archive the files in the 'TXT_uncleaned folder to a .zip file called 'TXT_uncleaned.zip'.
10. Run the [‘05 Clean and select.py’](https://raw.githubusercontent.com/haans-mertens/haans-mertens.github.io/master/_pages/05%20Clean%20and%20select.py) script to clean and select the texts, placing them in the ‘TXT_cleaned’ folder. This script also combines the selected pages into a single plaintext file per firm/year in the ‘TXT_combined’ folder.

From there, you can use the texts in the ‘TXT_cleaned’ and ‘TXT_combined’ folders for further analyses. The generated metadata files can be used to summarize the data or as input for additional analyses.
