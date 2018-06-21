# beer_chatbot
A collection of my work towards generating a beer-forum inspired chatbot

I have been posting on TalkBeer, a forum dedicated to craft beer, for years. I am fascinated by the rich troves of data available in this domain, from beer ratings, to reviews, to forum posts themselves. 

I perform quantitative analysis for a living; creating a model from beer ratings is fun, but it isn't a stretch in any sense. To expand my skill set, I decided to create a "chatbot" (really, more of a text generator) trained in the voice of one poster. My project flow requirements look like: 

1) Extract posts 
2) Clean and process them
3) Create a neural net 
4) Train the neural net and yield a model
5) "Read" a thread on TalkBeer
6) Extract a target post
7) Use that post to "seed" a response from the chatbot
8) Generate the response, clean it
9) Post the response back to TalkBeer, quoting the "seed" post

The end result would look as if the chatbot were actively reading the thread and responding to it. 

This repo contains my code for each of the steps to accomplish these tasks. 
