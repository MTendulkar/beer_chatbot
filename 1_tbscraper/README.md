
# TalkBeer Scraper

The first step in my chatbot project is to figure out how to extract forum posts. Unfortunately, TalkBeer does not have an API. So I decided to scrape the posts using my credentials. This repository contains my self-taught adventures through Scrapy, a Python library written to facilicate web scraping (and, I later discovered, useful for posting, too!). 

Scrapy provides a framework to make URL calls, authenticate, store those authenticating cookies, traverse and download pages, and parse them using the Cascading Style Sheets (CSS) markup language. I use those capabilities to log in, search for the provided user's post history, navigate through each result in the search list, and extract the post to which it points. 

For ethical reasons, I have suppressed the URL in my code, and I will not be sharing the code to post. While the site admin is aware of my scraping activities, I don't want would-be spammers to use my code to harass the site. 


## How it Works

The primary handler calls the login URL and passes the 'login' method as a callback (you can think of a callback as the action that the app takes after it receives a response from the URL). 

The 'login' method provides authentication credentials as a dict and passes in the 'logged_in' callback method. The 'logged_in' method navigates directly to the search URL provided -- you'll note that I pre-filled the URL with the user_id of the person whose posts I plan to scrape. Here, the callback is the post parser. 

This is where the bulk of the action happens. The 'parse' method iterates down the search results on each page, extracting the things I care about via the 'process' method. That method, when finished, yields control back to the 'parse' method, which then checks to see if there is another search result. If there is, it increments its counter and navigates to the next page of results. The interesting thing is that search results are batched; so 'parse' actually resets its counter for each batch, to keep things simple. 

During extraction, I have a cleanup method ('cleanMessage') which attempts to handle all non-UTF-8 compatible tokens. This needs some work, as I still extracted dirty data, and had to push additional cleanup methods into the data ingestion step. 


## Getting Started

Clone the repo to your local machine. 

### Prerequisites 

You must have a TalkBeer account. 

In spiders/tbbot.py, change all 'tb.com' URLs to the correct site URL. Insert your credentials into lines 45 and 47. 

### How to run 

In terminal, navigate to the parent directory and type 

```
scrapy crawl tbbot [optional_name.csv]
```

In settings.py, I defaulted output to data.csv. 

