# IDWW - The Web Wrapper of Instadata, a holistic Python Instagram Scraper
integrating with MongoDb, sitarealemail.com, nltk, locator (nominatim) instagram_private_api and instagrapi

## What this Scraper can do:
- #### Collecting Keywords. Hashtags, **E-Mail-Addresses**, **Phone-Numbers**
- #### **Gender**, **Name** and **Language** analysis
- #### **Scrape linktree Profiles** and capture more links, identify **custom linked websites** and **social profiles** and check if the links given actaully work.
- #### Check if this profile is a bot
- #### Collect user information like the biography, profile picture, full name, and more, both in its original form and **normalized** (abstract fonts will be converted to normal letters)
- #### Use Proxies on **all** requests
- #### Split the load up to as many accounts as possible

### Warning: This Scraper is **fully automatic**, however, if you overdo the scraping, **ratelimits** can occur and get your Account **blocked** (you will need to manuaally verify yourself through email or a phone number).

### Info. This is built upon the simpler and more customizalbe [IDWW Package](https://github.com/DavideWiest/idww). IDWW (InstaData Web Wrapper) offers a upgraded version of this package that uses django for a **user interface**

# How this scraper works
- execute the program with **python3 manage.py runserver**. Visit the dashboard, authenticate using your authorization token, initialize and the run the scraper.
- *When properly configured*, the scraper will first connect to all given accounts through two of the best instagram api wrappers. It will also use proxies, if any are specified and work. When either an account or a proxy connection don't work, the scraper will continue, but inform you through a warning.
- After that, other initialization work, such as finding starting users will be completed
- The Program will now start scraping: It will scrape, analyze, and save all data to the database directly. Afterwards it will sleep for how SLEEP_TIME seconds. That means you can see if accounts are being scraped in real time in log.csv or through the MongoDB Compass application.
- With a chance of 1:1750, the program will enter a *long sleeping phase* to decrease odds of being ratelimited or blocked by Instagram's anti-scraping-measures. It will sleep in seconds for a random number between the range specified in LONG_SLEEP_TIME
- It will also reconnect to the MongoDB database 
- Midnights (if specified in ANALYZE_PREVENTION[0]) the program will reconnect the accounts, sleep for ANALYZE_PREVENTION[1] seconds, and reconnect the accounts

# How to start

### Info
- Variables which are written in CAPSLOCK can be changed to customize the program

### Must Do before starting
- install all packages from **requirements.txt**
- in **requirements.txt** you wil find two commented lines: Install the instagram_private_api package through the github link. When trying to run the scraper, you will likely see error messages from nltk. Use the given python commands to install the required nltk sub-packages. This is required for text analysis.
- download MongoDB on your pc and configure a mongodb link. This is the integrated, and strongly preferred Database. Recommened: Install MondoDB Compass
- create a database and a collection in your database (Using MongoDB Compass is advised)
- configure the Database variables, such as the database name in **modules/mongomanager.py**
- visit sitarealemail.com and get an API Link. Paste this Api-key in the variable API_KEY in **modules/mailhandler.py**
- configure your authorization token (which you will use to authenticate in the webapp) in **ww_resources/auth_token.txt**. You can use any string, but we encourage you to generate a UUID. Furthermore, to increase security, you can store it encrypted, or as a system variable.
- populate ACCOUNTS_DATA with valid instagram accounts that will be used to access Instagram. Example: ("username123", "password321")
- We highly encourage you to use **proxies** to increase privacy. Paste working proxies into the **resources/proxies.csv** file (a list of public proxies can be found inside resources/proxies3.csv) (see the structuring in resources/proxies2.csv: connection,port,latency,uptime,location_index. The last 3 values are used to sort the proxies by which is best. If you don't have this information, use 1 as default value)

### Optional Configuration
- If you want, you can configure a backup connection in case something happens to the primary one. If not, leave the backup connection out
- configure variables such as SLEEP_TIME, LONG_SLEEP_TIME or USERMAX: We advise you not to change the variables too much as we had success with the base configuration
- SLEEP_TIME should **not** be below 5 (seconds)


## log system

##### The Scraper has two kinds of logs: the Stdout (logged to console via print) and the main logger that logs status and time to complete after a profile was scraped 
This is how the log.csv messages are sturctured: function status | user id | layer | current time | time to complete
status and current time required

### Inquiries and Suggestions at **[davide.wiest2@gmail.com](mailto:davide.wiest2@gmail.com)**
#### I am a Python (Web) Developer that can work on a freelance basis.
