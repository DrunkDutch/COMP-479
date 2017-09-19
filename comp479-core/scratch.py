import numpy
import nltk
import os


for file in os.listdir("./../Corpus"):
    if file.endswith(".sgm"):
        print(os.path.join("./../Corpus", file))
