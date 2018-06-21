
# TalkBeer Reader

Now I have a trained model that, given some seed text, will predict the next word and continue the sequence for a specified length. 

I want to use this model to "respond" to posts on TalkBeer, which means I have to write a program that will read forum posts, extract them, and select a candidate for response. As a bonus, I can use the text of the post to seed the chatbot's response. 


## How it Works

This program also uses the Scrapy library. The architecture is functionally similar to the scraper. 

The primary handler calls the login URL and passes the 'login' method as a callback (you can think of a callback as the action that the app takes after it receives a response from the URL). 

The 'login' method provides authentication credentials as a dict and passes in the 'logged_in' callback method. The 'logged_in' method navigates directly to the thread URL provided. I only "read" and "post" to one thread. Here, the callback is 'start_last_page' method. This method finds the number of pages in the thread and, well, starts on the last page. From there, it parses the page. 

As before, the 'parse' method reads the list of post slugs on the page, then calls the 'process' method on each of them, yielding metadata that I return in a dict. Scrapy automatically appends it to the supplied CSV argument (in this case, the default is output.csv). 


## Getting Started

Clone the repo to your local machine. 

### Prerequisites 

You must have a TalkBeer account. 

In spiders/tbbot.py, change all 'tb.com' URLs to the correct site URL. Insert your credentials into lines 42 and 44. 

### How to run 

In terminal, navigate to the parent directory and type 

```
scrapy crawl tb_reader [-o optional_name.csv]
```

In settings.py, I defaulted output to output.csv. 

