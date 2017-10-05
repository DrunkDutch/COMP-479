import core
import sys
import os


class Inverter:
    def __init__(self, corpus, block_prefix="bl_", file_prefix="f_", block_size=1, block_index=0, out_dir="../output"):
        self.documents = corpus.documents
        self.tokens = self.get_tokens()
        self.block_prefix = block_prefix
        self.file_prefix = file_prefix
        self.block_size = block_size
        self.block_index = block_index
        self.out_dir = out_dir
        self.blocklist = []
        self.get_out_dir()

    def get_tokens(self):
        for document in self.documents:
            try:
                yield document.get_tokens().next()
            except StopIteration:
                pass

    def get_out_dir(self):
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

    def index(self):
        done = False
        while not done:
            block_dict = {}
            try:
                while sys.getsizeof(block_dict) / 1024 / 1024 <= self.block_size:
                    token = self.tokens.next()
                    if token[0] not in block_dict:
                        block_dict[token[0]] = list()
                        block_dict[token[0]].append(token[1])
                    else:
                        block_dict[token[0]].append(token[1])
            except StopIteration:
                print "Parsed all tokens in all documents"
                done = True

            sorted_block = [term for term in sorted(block_dict.keys())]
            block_name = self.block_prefix + str(self.block_index) + ".txt"
            with open(os.path.join(self.out_dir, block_name), 'w') as outFile:
                for element in sorted_block:
                    docids = " ".join(str(doc) for doc in block_dict[element])
                    outString = element + " " + docids
                    outFile.write(outString + "\n")
            self.block_index += 1
            self.blocklist.append(block_name)


corp = core.Corpus("./../Corpus")
invert = Inverter(corp)
invert.index()

