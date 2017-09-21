import numpy
import nltk
import os
import re

# TODO: Look into wrapping the tag parser into a helper function for refined parsing
# TODO: Create wrapper class to hold the parsed text from above function

corpus = []
for file in os.listdir("./../Corpus"):
    if file.endswith(".sgm"):
        result = os.path.join("./../Corpus", file)
        corpus.append(result)

with open(corpus[0], 'r') as myfile:
    data = myfile.read()
class Document:
    def __init__(self, source):
        self.raw = self.parse_tags("REUTERS", source, False)[0]
        self.topics = self.parse_tags("D", self.raw)
        self.text = self.parse_tags("TEXT", self.raw)[0]
        self.title = self.parse_tags("TITLE", self.text)[0]
        self.dateline = self.parse_tags("DATELINE", self.text)[0]
        self.body = self.get_body()

    """
    Parser function to find the information contained within the desired tags
    Strips the tags from strict calls, but retains during non-strict due to regex restrictions
    on wildcard characters in look-ahead/behind structures
    """
    @staticmethod
    def parse_tags(tag, source, strict=True):
        if strict:
            body_regex = re.compile('(?<=\<'+tag+'>).*?(?=\</'+tag+'>)', flags=re.DOTALL)
        else:
            body_regex = re.compile('<' + tag + '.*?>.*?</' + tag + '>', flags=re.DOTALL)
        results = re.findall(body_regex, source)
        return results

    """
    Parser function to return the actual body of the text, stripping away all metadata and tags
    """
    def get_body(self):
        if self.text.find("<BODY>") != -1:
            return self.text.split("</DATELINE>")[1].split("</BODY>")[0].replace("<BODY>", '')
        else:
            return self.text.split("</DATELINE>")[1].split("</TEXT>")[0]



first_pass = Document(data)
"""
Install punkt package from nltk to be able to tokenize english
"""


print nltk.sent_tokenize(first_pass.body)
