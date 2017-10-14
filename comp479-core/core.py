import numpy
import nltk
import os
import re
import collections
import string
import pickle
import datetime
import sys
# reload(sys)
# sys.setdefaultencoding('utf8')


# TODO: Make Stemmer and stopwords optional based on arguments

class Corpus:

    def __init__(self, source, case=True, digits=True, stop=True, stem=True):
        self.path = source
        self.files = [os.path.join(self.path, file) for file in os.listdir(self.path) if file.endswith(".sgm")]
        self.case = case
        self.digits = digits
        self.stop = stop
        self.stem = stem
        self.documents = self.parse_documents()
        # self.save()

    def get_count(self):
        count = 0
        for doc in self.documents:
            count += doc.count
        return count

    def parse_documents(self):
        for file in self.files:
            print "Currently parsing articles from file {}", file
            with open(file, 'rb') as myfile:
                data = myfile.read()
            for article in Document.parse_tags("REUTERS", data, False):
                    yield Document(article, index=0, case=self.case, digits=self.digits, stem=self.stem, stop=self.stop)

    def save(self):
        with open("corpus.pk1", 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)


class Document:

    def __init__(self, source, index=0, case=True, digits=True, stop=True, stem=True):
        self.raw = self.parse_tags("REUTERS", source, False)[index]
        self.id = self.get_id()
        self.topics_places = self.parse_tags("D", self.raw)
        self.text = self.parse_tags("TEXT", self.raw, False)[0]
        self.title = self.parse_tags("TITLE", self.text)[0]
        self.dateline = self.parse_tags("DATELINE", self.text)[0]
        self.body = self.get_body()
        self.case = case
        self.digits = digits
        self.stop = stop
        self.stem = stem
        self.count = 0
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

    def clean(self, input):
        output = input
        if self.digits:
            for s in output:
                if s.isdigit():
                    return None
        if self.case:
            output = output.lower()
        if self.stop:
            punctuation = [unicode(x, "utf-8") for x in string.punctuation]
            stops = set(nltk.corpus.stopwords.words('english') + punctuation)
            if output in stops:
                return None
        if self.stem:
            stemmer = nltk.PorterStemmer()
            output = stemmer.stem(output)
        return output

    def tokenize(self):
        print self.id
        token_list = {}
        stemmer = nltk.PorterStemmer()
        count_list = {}
        text = [self.body, self.title]
        text.extend(self.topics_places)
        for section in text:
            for word in nltk.word_tokenize(section):
                try:
                    stemmed_word = self.clean(word)
                    if stemmed_word is None:
                        continue
                    if not isinstance(stemmed_word, unicode):
                        stemmed_word = unicode(stemmed_word, "utf-8")
                    if stemmed_word in count_list.keys():
                        count_list[stemmed_word] = count_list[stemmed_word] + 1
                    else:
                        count_list[stemmed_word] = 1
                    if stemmed_word not in token_list:
                        token_list[stemmed_word] = self.id
                    self.count += 1
                except UnicodeDecodeError:
                    token_list[word.split(".")[0]] = self.id
                    self.count += 1
        cleaned = token_list
        return cleaned, collections.OrderedDict(sorted(count_list.items()))

    def get_tokens(self):
        for token, docid in self.tokens.iteritems():
            yield token, docid


class BlockLine:
    def __init__(self, indexes, term, postings):
        self.indexes = indexes
        self.term = term
        self.postings = postings

    @classmethod
    def from_line_entry(cls, indexes, line):
        split_line = line.split(" ")
        return cls(indexes, split_line[0], [int(doc_id) for doc_id in split_line[1:]])

    def merge(self, other_bl):
        new_indexes = sorted(self.indexes + other_bl.indexes)
        new_postings = sorted(self.postings + other_bl.postings)
        return BlockLine(new_indexes, self.term, new_postings)

    def __str__(self):

        return "{} {}\n".format(self.term, " ".join([str(doc_id) for doc_id in self.postings]))


class BlockFile:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_handle = None
        self.term_count = 0

    def open_file(self, mode='r'):
        self.file_handle = open(self.file_path, mode)
        return self

    def write_line(self, line_obj):
        self.file_handle.write(str(line_obj))
        self.term_count += 1

    def read_line(self):
        line_string = self.file_handle.readline()
        if line_string:
            return BlockLine.from_line_entry(-1, line_string)
        else:
            return None

    def close_file(self):
        self.file_handle.close()

    def __str__(self):
        return str(self.file_path)


# corpus = []
# for file in os.listdir("./../Corpus"):
#     if file.endswith("0.sgm"):
#         result = os.path.join("./../Corpus", file)
#         corpus.append(result)
#
# with open(corpus[17], 'r') as myfile:
#     data = myfile.read()

# print len(Document.parse_tags("REUTERS", data, False))
# documents = []
# for article in Document.parse_tags("REUTERS", data, False):
#     documents.append(Document(article))
#     print documents[-1].id

# try:
#     with open('corpus.pkl', 'rb') as input:
#         corpus = pickle.load(input)
# except IOError:
#     corpus = Corpus("./../Corpus")
# finally:
#     print len(corpus.documents)
"""
Install punkt package from nltk to be able to tokenize english
install stopwords corpus for nltk to remove stopwords
"""

if __name__ == "__main__":
    now = datetime.datetime.now()
    corpus = Corpus("./../Corpus")
    print len(corpus.documents)
    print corpus.documents[0].tokens
    print datetime.datetime.now() - now