# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
import logging
import csv
import time 
import re
import codecs
from random import randint


def cleanMessage(message):
    # :param message: expects a string
    # :return cleanedMessage: a cleaned string

    cleanedMessage = message.lower() 
    # Space out newlines 
    cleanedMessage = re.sub('\n', '\n ', cleanedMessage)
    # Remove new lines within message
    # cleanedMessage = cleanedMessage.replace('\n',' ').lower()
    # Deal with some weird tokens
    #cleanedMessage = cleanedMessage.replace("\xc2\xa0", "")
    cleanedMessage = re.sub("([a-z])*\xe2\x80\x99([a-z]*)", "'", cleanedMessage)
    cleanedMessage = re.sub(ur"(\w*)(\xe2\x80\x99)(\w*)" , ur"\1'\3", cleanedMessage)
    cleanedMessage = re.sub(ur"(\w*)(\u201c)(\w*)" , ur"\1''\3", cleanedMessage)
    cleanedMessage = re.sub(ur"(\w*)(\u201d)(\w*)" , ur"\1''\3", cleanedMessage)
    cleanedMessage = re.sub(ur"(\w*)(\u2019)(\w*)" , ur"\1'\3", cleanedMessage)
    cleanedMessage = re.sub(ur"(\w*)(\xe2\x80\x93)(\w*)" , ur"\1-\3", cleanedMessage)
    cleanedMessage = re.sub(ur"\u2022" , ur"", cleanedMessage)
    # Remove punctuation
    #cleanedMessage = re.sub('([.,!?])',' ', cleanedMessage)
    # Remove multiple spaces in message
    # cleanedMessage = re.sub('\s+',' ', cleanedMessage)
    return cleanedMessage


class TbbotSpider(scrapy.Spider):
    name = 'tb_reader'
    allowed_domains = ['tb.com']

    def start_requests(self):
        yield scrapy.Request('https://www.tb.com/community/login/',
            callback=self.login, dont_filter = True) 

    def login(self, response): 
        return scrapy.FormRequest.from_response( 
            response,
            formdata={'login': '', 
                      'register': '0',
                      'password': ''},
            callback=self.logged_in, dont_filter = True)

    def logged_in(self, response): 
        print "Login request made" 

        url = 'https://www.tb.com/community/threads/trump-presidency-thread.37086/'

        yield scrapy.Request(url = url, 
            headers = response.headers, 
            meta={"iteration": 0},
            callback = self.start_last_page, 
            dont_filter = True)

    def start_last_page(self, response): 
        num_pages = response.css('div.PageNav::attr(data-last)').extract_first()

        print "Pages in thread: " + num_pages

        #num_pages = num_pages - 1

        rand_page = False 

        if rand_page: 
            page = response.url + 'page-' + str(randint(1,int(num_pages)))
            print "Navigating to random page: " + page 
        else: 
            page = response.url + 'page-' + str(int(num_pages) - response.meta['iteration'])
            print "Navigating to page: " + page 
            
        yield scrapy.Request(url = page, 
            headers = response.headers, 
            callback = self.parse, 
            #meta = {"iteration": response.meta["iteration"] + 1}, 
            meta = response.meta, 
            dont_filter = True)


    def parse(self, response):

        if response.meta['iteration'] > 1: 
            return
        else: 
            response.meta['iteration'] = response.meta['iteration'] + 1

        ## Parse all the posts on this page
        
        print response.url 

        # Grab the post slugs on this page
        # Sample: [u'threads/trump-presidency-thread.37086/page-2809#post-1717119',
        #          u'threads/trump-presidency-thread.37086/page-2809#post-1717124',
        #          u'threads/trump-presidency-thread.37086/page-2809#post-1717128',
        #          u'threads/trump-presidency-thread.37086/page-2809#post-1717129',
        #          u'threads/trump-presidency-thread.37086/page-2809#post-1717141',
        #          u'threads/trump-presidency-thread.37086/page-2809#post-1717142',
        #          u'threads/trump-presidency-thread.37086/page-2809#post-1717143',
        #          u'threads/trump-presidency-thread.37086/page-2809#post-1717146',
        #          u'threads/trump-presidency-thread.37086/page-2809#post-1717152',
        #          u'threads/trump-presidency-thread.37086/page-2809#post-1717153',
        #          u'threads/trump-presidency-thread.37086/page-2809#post-1717155',
        #          u'threads/trump-presidency-thread.37086/page-2809#post-1717158',
        #          u'threads/trump-presidency-thread.37086/page-2809#post-1717163',
        #          u'threads/trump-presidency-thread.37086/page-2809#post-1717181']
        slugs = response.css("div.publicControls").css("a.item.muted.postNumber.hashPermalink.OverlayTrigger::attr(href)").extract()

        # Verbose progress
        print slugs[0]
        print "Slugs successful" 

        # Iterate through the post slugs
        for j in range(0, len(slugs)): 
            base = 'http://www.tb.com/community/'
            url = base + slugs[j]

            #time.sleep(1) 

            print "Requesting " + url 

            # request the base URL, enrich with slug, and set callback method
            yield scrapy.Request(url = url, headers = response.headers, 
                callback = self.process, meta={"slug": slugs[j]}, dont_filter = True)

        # For next page
        # Sample: https://www.tb.com/community/threads/trump-presidency-thread.37086/page-2809

        # Split URL into list
        url_parts = response.url.split('-')
        next_page = ''.join(url_parts[0:-1]) + '-' + str(int(url_parts[-1]) - 1)

        print "Next page: " + next_page 

        # Disabled by default; comment out to cycle through previous posts 
        next_page = False 
        
        # If there is a next page 
        if next_page:
            #next_page_url = 'www.tb.com/community/' + next_page

            print "Going to next page: " + next_page 
            yield scrapy.Request(url = response.urljoin(next_page), 
                callback = self.parse, 
                headers = response.headers, 
                meta={"iteration": response.meta['iteration']}, 
                dont_filter = True)


    # Given a thread URL and a post slug, find the 
    # post associated with that slug and strip the 
    # information we want from it 
    def process(self, response):

        VERBOSE = 0

        slug = response.meta['slug']

        print "Slug unpacking successful: " + slug 

        post = slug.split('#')[-1]
        print post

        if VERBOSE: 
            print "Page URL is " + response.url 
            print "Post slug is " + post 

        post_list = response.css('div.pageContent').css('form.InlineModForm.section').css('ol.messageList').css('li.message::attr(id)').extract()

        if VERBOSE: 
            print "Message list obtained" 
            print post_list 

        for i in range(0, len(post_list)):
            if post_list[i] != post:
                #print "iteration " + str(i)
                continue 
            else: 
                # username 
                # replaced all 1s with i 
                username = response.css("div.messageInfo.primaryContent")[i].css("a.username.author::text").extract_first()

                if VERBOSE: 
                    print username

                # time 
                time = response.css("div.messageMeta.ToggleTriggerAnchor")[i].css("span.DateTime::attr(title)").extract_first()

                # thread
                thread = response.css("div.titleBar").css("h1::text").extract_first()

                # forum (has to be the zero-index item)
                forum = response.css("div.titleBar").css("a::text")[0].extract()

                # responding to 
                # responding_to = response.css("div.bbCodeBlock.bbCodeQuote::attr(data-author)")[i].extract()
                responding_to = response.css("blockquote.messageText.SelectQuoteContainer.ugc.baseHtml")[i].css("div.bbCodeBlock.bbCodeQuote::attr(data-author)").extract_first()

                if VERBOSE: 
                    print responding_to 

                # quoted text 
                raw_quoted_text = response.css("blockquote.messageText.SelectQuoteContainer.ugc.baseHtml")[i].css("div.quote::text").extract()
                raw_quoted_text = re.sub('"', "''", ' '.join(raw_quoted_text))
                quoted_text = cleanMessage(raw_quoted_text)

                if VERBOSE: 
                    print quoted_text 

                # text
                raw_body = response.css("div.messageContent")[i].css("article").css("blockquote.messageText.SelectQuoteContainer.ugc.baseHtml::text").extract()
                raw_body = re.sub('"', "''", ' '.join(raw_body))
                body = cleanMessage(raw_body) 

                scraped_info = {
                    'username' : username,
                    'time' : time,
                    'thread' : thread,
                    'forum' : forum,
                    'responding_to' : responding_to,
                    'quoted_text' : quoted_text, 
                    'raw_quoted_text' : raw_quoted_text,
                    'body' : body, 
                    'raw_body': raw_body, 
                    'post_url' : response.url 
                }

                print "Extracting post from " + username
                #print response.body  

                yield scraped_info

