import core
import sys
import os
import datetime


class Inverter:
    def __init__(self, corpus, block_prefix="bl_", file_prefix="f_", block_size=1, block_index=0, out_dir="./blockfiles"):
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
            self.blocklist.append(os.path.join(self.out_dir, block_name))


class Merger:
    def __init__(self, blockfiles, file_name="mf_", out_dir="./merged"):
        self.file_name = file_name
        self.out_dir = out_dir
        self.block_files = blockfiles
        self.get_out_dir()
        self.prep_output()

    def prep_files(self):
        open_files = []
        for out_file in self.block_files:
            open_files.append(open(out_file, "r"))
        return open_files

    def prep_output(self):
        try:
            os.remove(os.path.join(self.out_dir, self.file_name))
        except Exception:
            print "Could not find file to delete"
            pass

    def get_out_dir(self):
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

    def merge_posting(self, dic1, dic2):
        new_postings = []
        new_postings.extend(dic1)
        new_postings.extend(dic2)
        return sorted(new_postings)

    def merge(self):
        in_files = self.prep_files()
        next_lines = [f.readline() for f in in_files]
        while next_lines:
            next_term = None
            postings = []
            indexes = []
            for index, line in enumerate(next_lines):
                term = line.split(" ")[0]
                docIds = [int(docId) for docId in line.split(" ")[1:]]
                if not next_term:
                    indexes.append(index)
                    next_term = term
                    postings = docIds
                elif term == next_term:
                    indexes.append(index)
                    postings = self.merge_posting(postings, docIds)
                elif term < next_term:
                    indexes = [index]
                    next_term = term
                    postings = docIds

            # TODO: FIX file indexing to close the proper file
            next_posting = " ".join(str(doc) for doc in postings)
            out_string = next_term + " " + next_posting
            with open(os.path.join(self.out_dir, self.file_name), 'a') as outFile:
                outFile.write(out_string + "\n")
            new_next_lines = [in_files[index].readline() for index in indexes]

            for index, new_line in enumerate(new_next_lines):
                try:
                    if not new_line:
                        del next_lines[indexes[index]]
                        in_files[indexes[index]].close()
                        print "Closing file" + str(indexes[index])
                        del in_files[indexes[index]]
                    else:
                        next_lines[indexes[index]] = new_line
                except IndexError:
                    continue

        print "Finished merging files"


if __name__ == "__main__":
    now = datetime.datetime.now()
    corp = core.Corpus("./../Corpus")
    invert = Inverter(corp)
    invert.index()
    merger = Merger(invert.blocklist)
    merger.merge()
    print datetime.datetime.now() - now

