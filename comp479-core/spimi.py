import core
import sys


class Inverter:
    def __init__(self, corpus, block_prefix="bl_", file_prefix="f_", block_size=1, block_index=0, out_dir="./output"):
        self.documents = corpus.documents
        self.tokens = self.get_tokens()
        self.block_prefix = block_prefix
        self.file_prefix = file_prefix
        self.block_size = block_size
        self.block_index = block_index
        self.out_dir = out_dir

    def get_tokens(self):
        for document in self.documents:
            for key, value in document.tokens:
                yield (key, value)

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

