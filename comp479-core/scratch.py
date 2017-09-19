import numpy
import nltk
import os
import re

corpus = []
for file in os.listdir("./../Corpus"):
    if file.endswith(".sgm"):
        result = os.path.join("./../Corpus", file)
        print(result)
        corpus.append(result)

with open(corpus[0], 'r') as myfile:
    data = myfile.read()
tag = 'TEXT'
body_regex = re.compile('<'+tag+'.*?>.*?</'+tag+'>', flags=re.DOTALL)
results = re.findall(body_regex, data)
print len(results)
"""
Install punkt package from nltk to be able to tokenize english
"""
print nltk.word_tokenize(results[0])[:100]
