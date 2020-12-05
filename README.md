# beer_chatbot
A collection of my work towards generating a beer-forum inspired chatbot

I have been posting on TalkBeer, a craft beer forum, for years. I am fascinated by the rich troves of data available in the beer world: from beer ratings, to reviews, to forum posts themselves. 

I perform quantitative analysis for a living; creating a model from beer ratings is fun, but it isn't a stretch in any sense. To expand my skill set, I created a "chatbot" (really, more of a text generator) trained in the voice of one poster. My project flow requirements look like: 

1) Extract posts 
2) Clean and process them
3) Train a neural net and yield a model
5) "Read" a thread on TalkBeer
6) Choose a post from that thread to "respond" to
7) Use that post as a prompt to seed a response from the chatbot
8) Generate the response, clean it
9) Post the response back to TalkBeer, quoting the seed post

The end result would look as if the chatbot were actively reading the thread and responding to it. 

This repo contains my code for each of the steps to accomplish these tasks. 
