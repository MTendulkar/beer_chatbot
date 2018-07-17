import re

def cleanMessage(message): 
    """
    Clean UTF-8 tokens
    :return: clean ASCII text
    """
    message = re.sub(ur"(\w*)(\xe2\x80\x93)(\w*)" , ur"\1-\3", message)
    message = re.sub(ur"\u2022" , ur"", message)

    return message