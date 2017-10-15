import core
import spimi
import os
import sys
import argparse
import nltk
import string
import datetime


class QueryProcessor:

    def __init__(self, query_type="AND", query_list=[], merge="./merged/mf.txt", corpus="./../Corpus", out_dir=" ./../output", digits=True, case=True, stop=True, stem=True):
        self.type = query_type
        self.terms = query_list
        self.merge = merge
        self.corpus = corpus
        self.out_dir = out_dir
        self.digits = digits
        self.case = case
        self.stop = stop
        self.stem = stem
        self.index = {}
        self.get_index()
        self.get_out_dir()
        self.terms = [self.clean(term) for term in self.terms]
        self.terms = [str(x) for x in self.terms if x is not None]

    def clean(self, input):
        output = input
        if self.digits:
            for s in output:
                if s.isdigit():
                    return None
        if self.case:
            output = output.lower()
        if self.stop:
            punctuation = [str(x) for x in string.punctuation]
            stops = set(nltk.corpus.stopwords.words('english') + punctuation)
            if output in stops:
                return None
        if self.stem:
            stemmer = nltk.PorterStemmer()
            output = stemmer.stem(output)
        return str(output)

    def get_out_dir(self):
        try:
            for f in os.listdir(self.out_dir):
                if f.endswith(".txt"):
                    os.remove(os.path.join(self.out_dir,f))
        except Exception:
            print "woops, Couldn't delete folders in output locations"
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

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
            try:
                postings.append(set(self.index[str(term)]))
            except KeyError:
                postings.append(set([]))
        intersection = set.intersection(*postings)
        return intersection

    def or_query(self):
        postings = []
        for index, term in enumerate(self.terms):
            try:
                postings.append(set(self.index[str(term)]))
            except KeyError:
                postings.append(set([]))
        union = set.union(*postings)
        return union

    def process_query(self):
        print "Processing query for terms " + " ".join(self.terms)
        result_list = []
        if self.type is "AND":
            result_list = self.and_query()
        else:
            result_list = self.or_query()

        self.get_articles(result_list)

    def get_articles(self, articles):
        for article in articles:
            corp_file = article / 1000
            art_index = (article % 1000) - 1
            if corp_file < 10:
                file_name = "reut2-00" + str(corp_file) + ".sgm"
            else:
                file_name = "reut2-0" + str(corp_file) + ".sgm"
            with open(os.path.join(self.corpus, file_name), "r") as reut:
                data = reut.read()
            doc_dump = core.Document.parse_tags("REUTERS", data, False)
            for index, doc in enumerate(doc_dump):
                if index == art_index:
                    print "Found result in article {}".format(article)
                    with open(os.path.join(self.out_dir, str(article)+".txt"), "w") as out_file:
                        out_file.write(doc)


def get_command_line(argv=None):
    program_name = os.path.basename(sys.argv[0])
    if argv is None:
        argv = sys.argv[1:]

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-a", "--AND",
                            help="Choose AND type query, if used with -o or --OR parameter, supercedes it", action="store_true")
        parser.add_argument("-o", "--OR",
                            help="Choose OR type query, if used with -a or --AND parameter, is superceded by it", action="store_true")
        parser.add_argument("-d", "--digits", action="store_true")
        parser.add_argument("-c", "--case", action="store_true")
        parser.add_argument("-s", "--stopwords", action="store_true")
        parser.add_argument("-m", "--stemmer", action="store_true", default=False)
        parser.add_argument("-q", "--query", help="Query Terms to search for")


        arguments = parser.parse_args(argv)
        return arguments
    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + " for help use --help")
        return None


if __name__ == __name__:
    now = datetime.datetime.now()
    options = get_command_line()
    query_type_in = "AND"
    if options.OR:
        query_type_in = "OR"
    if options.AND:
        query_type_in = "AND"
    if not options.AND and not options.OR:
        print "Please select a valid query type"
    q_list = options.query.split(" ")
    qp = QueryProcessor(query_type=query_type_in, query_list=q_list, digits=options.digits, case=options.case, stop=options.stopwords, stem=options.stemmer)
    # print len(qp.index.keys())
    qp.process_query()
    print datetime.datetime.now() - now
