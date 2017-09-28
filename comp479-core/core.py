import numpy
import nltk
import os
import re
import collections
import string
import heapq


# TODO: Look into wrapping the tag parser into a helper function for refined parsing
# TODO: Create wrapper class to hold the parsed text from above function


class Document:

    def __init__(self, source, index=0):
        self.raw = self.parse_tags("REUTERS", source, False)[index]
        self.id = self.get_id()
        self.topics_places = self.parse_tags("D", self.raw)
        self.text = self.parse_tags("TEXT", self.raw, False)[0]
        self.title = self.parse_tags("TITLE", self.text)[0]
        self.dateline = self.parse_tags("DATELINE", self.text)[0]
        self.body = self.get_body()
        self.tokens, self.occurence = self.tokenize()

    """
    Parser function to find the information contained within the desired tags
    Strips the tags from strict calls, but retains during non-strict due to regex restrictions
    on wildcard characters in look-ahead/behind structures
    """
    @staticmethod
    def parse_tags(tag, source, strict=True):
        results = []
        try:
            if strict:
                body_regex = re.compile('(?<=\<'+tag+'>).*?(?=\</'+tag+'>)', flags=re.DOTALL)
            else:
                body_regex = re.compile('<' + tag + '.*?>.*?</' + tag + '>', flags=re.DOTALL)
            results = re.findall(body_regex, source)
            if len(results) is 0:
                results = [""]
        except IndexError:
            results = [""]
        finally:
            return results

    def get_id(self):
        regex = re.compile("(?<=NEWID=\")\d+")
        result = re.findall(regex, self.raw)
        return result[0]


    """
    Parser function to return the actual body of the text, stripping away all metadata and tags
    """
    def get_body(self):
        if self.text.find("<BODY>") != -1:
            return self.text.split("</DATELINE>")[1].split("</BODY>")[0].replace("<BODY>", '')
        if self.text.find("<DATELINE>") != -1:
            return self.text.split("</DATELINE>")[1].split("</TEXT>")[0]
        if self.text.find("<TITLE>") != -1:
            return self.text.split("</TITLE>")[1].split("</TEXT>")[0]
        else:
            return self.text.split("</TEXT>")[0]

    def cleanup(self, input):
        dicts = {}
        punction = [unicode(x, "utf-8") for x in string.punctuation]
        stops = set(nltk.corpus.stopwords.words('english') + punction)
        for key in input.keys():
            if key not in stops:
                dicts[key] = self.id
        return dicts

    def tokenize(self):
        token_list = {}
        stemmer = nltk.PorterStemmer()
        count_list = {}
        text = [self.body, self.title]
        text.extend(self.topics_places)
        for section in text:
            for word in nltk.word_tokenize(section):
                stemmed_word = stemmer.stem(word)
                if not isinstance(stemmed_word, unicode):
                    stemmed_word = unicode(stemmed_word, "utf-8")
                if stemmed_word in count_list.keys():
                    count_list[stemmed_word] = count_list[stemmed_word] + 1
                else:
                    count_list[stemmed_word] = 1
                if stemmed_word not in token_list:
                    token_list[stemmed_word] = self.id
        cleaned = self.cleanup(token_list)
        sort = sorted(cleaned.items())
        tokens = collections.OrderedDict(sort)
        return sort, collections.OrderedDict(sorted(count_list.items()))


corpus = []
for file in os.listdir("./../Corpus"):
    if file.endswith(".sgm"):
        result = os.path.join("./../Corpus", file)
        corpus.append(result)

with open(corpus[0], 'r') as myfile:
    data = myfile.read()

print len(Document.parse_tags("REUTERS", data, False))
documents = []
for article in Document.parse_tags("REUTERS", data, False):
    documents.append(Document(article))
    print documents[-1].id

"""
Install punkt package from nltk to be able to tokenize english
install stopwords corpus for nltk to remove stopwords
"""

