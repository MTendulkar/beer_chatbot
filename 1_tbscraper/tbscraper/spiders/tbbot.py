# -*- coding: utf-8 -*-
import scrapy
import logging
import codecs
import time 
import re

# FALSE by default. If this is set to true, it will only
# scrape one page of results, for quick examination. 
DEBUG = False

def cleanMessage(cleanedMessage):
    # :param message: expects a string
    # :return cleanedMessage: a cleaned string

    # Space out newlines 
    cleanedMessage = re.sub('\n', '\n ', cleanedMessage)
    cleanedMessage = codecs.decode(cleanedMessage, 'utf-8')
    cleanedMessage = re.sub('"', '\"', cleanedMessage)
    cleanedMessage = re.sub("'", "\'", cleanedMessage)
    cleanedMessage = cleanedMessage.strip() 
    return cleanedMessage


class TbbotSpider(scrapy.Spider):
    name = 'tbbot'
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
        print response.headers 

        url = 'https://www.tb.com/community/search/member?user_id=977'

        yield scrapy.Request(url = url, headers = response.headers, callback = self.parse, dont_filter = True)


    def parse(self, response):
        if 'iteration' in response.meta:
            response.meta['iteration'] = response.meta['iteration'] + 1
        else: 
            response.meta['iteration'] = 1

        # Results are batched. If we reach the end of the batch, 
        # announce it, point to the next batch, and reset the 
        # counter. 
        if response.css('div.PageNav::attr(data-last)').extract_first() == str(response.meta['iteration']):
            print "Reached end of this result batch" 
            next_page = response.css('div.secondaryContent.olderMessages').css('a::attr(href)').extract_first()
            next_page = 'http://www.tb.com/community/' + next_page 
            response.meta['iteration'] = 0

        # If we are done with all results, then stop 
        elif response.css('div.messageBody::text').extract_first() == 'No results found.': 
            print "No more results found." 
            next_page = False 

            return 

        # If we are in the middle of a batch or at a non-terminal 
        # page, then the next page should increment as normal 
        else: 
            next_page = response.url.split('?')[0] + '?page=' + str(response.meta['iteration'] + 1)
        
        # Grab the post slugs on this page
        slugs = response.css(".snippet").css("a::attr(href)").extract()

        # Verbose progress
        #print slugs[0]
        print "Slugs successful"
        print "Next page is " + next_page  

        # Iterate through the post slugs
        for j in range(0, len(slugs)): 
            base = 'http://www.tb.com/community/'
            url = base + slugs[j]

            time.sleep(1) 

            # request the base URL, enrich with slug, and set callback method
            yield scrapy.Request(url = url, headers = response.headers, 
                callback = self.process, meta={"slug": slugs[j]}, dont_filter = True)

        # Iterate through each page in the result set 
        if DEBUG: 
            next_page = False 
        
        # If there is a next page 
        if next_page:
            print "Going to next page: " + next_page 
            yield scrapy.Request(url = response.urljoin(next_page), callback = self.parse, 
                headers = response.headers, meta={"iteration": response.meta['iteration']}, 
                dont_filter = True)

    # Given a thread URL and a post slug, find the 
    # post associated with that slug and strip the 
    # information we want from it 
    def process(self, response):
        slug = response.meta['slug']

        #print "Slug unpacking successful"

        post = slug.split('/')[-2]
        post = 'post-' + str(post)

        #print "Post url is " + post 

        post_list = response.css('div.pageContent').css('form.InlineModForm.section').css('ol.messageList').css('li.message::attr(id)').extract()

        #print "Message list obtained" 

        for i in range(0, len(post_list)):
        #for i in range(0, 2): 
            if post_list[i] != post:
                #print "iteration " + str(i)
                continue 
            else: 
                # username 
                username = response.css("div.messageInfo.primaryContent")[i].css("a.username.author::text").extract_first()

                if DEBUG:
                    print "Username: " + username 

                # thread
                thread = response.css("div.titleBar").css("h1::text").extract_first()

                if DEBUG:
                    print "Thread: " + thread 

                # forum (has to be the zero-index item)
                forum = response.css("div.titleBar").css("a::text")[0].extract()

                if DEBUG:
                    print "Forum: " + forum 

                # responding to 
                responding_to = response.css("blockquote.messageText.SelectQuoteContainer.ugc.baseHtml")[i].css("div.bbCodeBlock.bbCodeQuote::attr(data-author)").extract_first()

                if DEBUG:
                    print "Responding to: " + responding_to

                # quoted text 
                raw_quoted_text = ' '.join(response.css(
                    "blockquote.messageText.SelectQuoteContainer.ugc.baseHtml")[i].css("div.quote::text"
                    ).extract())
                clean_quoted_text = cleanMessage(raw_quoted_text)

 
                if DEBUG:
                    print "Raw quoted text: " + raw_quoted_text
                    print "Clean quoted text: " + quoted_text

                raw_body = ' '.join(response.css("li#" + post + ".message").css(
                    "div.messageInfo.primaryContent").css("div.messageContent").css(
                    "blockquote.messageText.SelectQuoteContainer.ugc.baseHtml::text").extract())
                clean_body = cleanMessage(raw_body)
                
                if DEBUG: 
                    print "Raw body: " + raw_body

                raw_body = re.sub('"', "''", raw_body)

                if DEBUG: 
                    print "Clean up double-quote marks..." 
                    print "Raw body: " + raw_body

                body = cleanMessage(raw_body) 

                if DEBUG: 
                    print "Clean body: " + body 

                scraped_info = {
                    'username' : username,
                    #'time' : time,
                    'thread' : thread,
                    'forum' : forum,
                    'responding_to' : responding_to,
                    'clean_quoted_text' : clean_quoted_text, 
                    #'raw_quoted_text' : raw_quoted_text,
                    'clean_body' : clean_body, 
                    #'raw_body': raw_body, 
                    'post_url' : response.url 
                }


                if DEBUG:
                    print "Return dict created"

                return(scraped_info)