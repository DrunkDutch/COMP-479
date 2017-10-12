import core
import spimi
import os
import sys
import argparse


class QueryProcessor:

    def __init__(self, query_type="AND", query_list=[], merge="./merged/mf.txt", corpus="./../Corpus"):
        self.type = query_type
        self.terms = query_list
        self.merge = merge
        self.corpus = corpus
        self.index = {}
        self.get_index()

    def get_index(self):
        in_file = core.BlockFile(self.merge)
        in_file.open_file()
        in_line = in_file.read_line()
        while in_line:
            self.index[in_line.term] = in_line.postings
            in_line = in_file.read_line()

    def and_query(self):
        postings = []
        for index, term in enumerate(self.terms):
            postings[index] = set(self.index[term])
        intersection = set.intersection(*postings)
        return intersection

    def or_query(self):
        postings = []
        for index, term in enumerate(self.terms):
            postings[index] = set(self.index[term])
        union = set.union(*postings)
        return union

    def get_articles(self):
        pass

    def process_query(self):
        result_list = []
        if self.type is "AND":
            result_list = self.and_query()
        else:
            result_list = self.or_query()

        return  result_list




qp = QueryProcessor()
print len(qp.index.keys())
