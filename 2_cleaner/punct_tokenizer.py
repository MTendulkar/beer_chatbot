
import re

def token_lookup():
    """
    Generate a dict to map punctuation into a token
    :return: dictionary mapping puncuation to token
    """
    return {
        '.': '||period||',
        ',': '||comma||',
        '=': '||equal_sign||',
        '"': '||double_quotes||',
        ';': '||semicolon||',
        '!': '||exclamation_mark||',
        '?': '||question_mark||',
        '(': '||left_parentheses||',
        ')': '||right_parentheses||',
        '--': '||emm_dash||',
        '-': '||dash||',
        '/': '||forward_slash||',
        " '": '||left_single_quote||',
        "' ": '||right_single_quote||',
        '\n': '||return||'
    }


def tokenize_regex(message): 
    """
    I am working in ASCII because I haven't figured 
    out how to process UTF-8. But I want to preserve
    the directional identity of smart punctuation. 

    This looks for regex patterns in ASCII and tokenizes
    them. 
    :return: clean ASCII text with tokenized punctuation
    """
    message = re.sub(r'([^\w])(")([^\s]*\w)' , r'\1 ||left_double_quote|| \3', message)
    message = re.sub(r'(\s[^\s]+)(")([^\w]+)' , r'\1 ||right_double_quote|| \3', message)
    message = re.sub(r"([^\w])(')([^\s]*\w)" , r'\1 ||left_single_quote|| \3', message)
    message = re.sub(r"(\s[^\s]+)(')([^\w]+)" , r'\1 ||right_single_quote|| \3', message)
    message = re.sub(r"(\s[^\s]+)(')([^\s]+)", r'\1 ||apostrophe|| \3', message) 

    return message 


def tokenize_utf8(message): 
    """
    Clean UTF-8 tokens
    :return: clean ASCII text
    """
    message = re.sub(ur"(\w*)(\xe2\x80\x9c)(\w*)" , ur"\1 ||left_double_quote|| \3", message)
    message = re.sub(ur"(\w*)(\xe2\x80\x9d)(\w*)" , ur"\1 ||right_double_quote|| \3", message)
    message = re.sub(ur"(\w*)(\xe2\x80\x98)(\w*)" , ur"\1 ||left_single_quote|| \3", message)
    message = re.sub(ur"(\w*)(\xe2\x80\x99)(\w*)" , ur"\1 ||right_single_quote|| \3", message)
    message = re.sub(ur"(\w*)(\u201c)(\w*)" , ur'\1 ||left_double_quote|| \3', message)
    message = re.sub(ur"(\w*)(\u201d)(\w*)" , ur'\1 ||right_double_quote|| \3', message)
    message = re.sub(ur"(\w*)(\u2018)(\w*)" , ur"\1 ||left_single_quote|| \3", message)
    message = re.sub(ur"(\w*)(\u2019)(\w*)" , ur"\1 ||right_single_quote|| \3", message)

    return message


def main(message): 
    message = tokenize_utf8(message)
    message = tokenize_regex(message)

    token_dict = token_lookup()

    for token, replacement in token_dict.items(): 
    	message = message.replace(token, ' {} '.format(replacement))


if __name__ == '__main__':
    main()
