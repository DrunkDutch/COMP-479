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
                while sys.getsizeof(block_dict) / 1024 / 30 <= self.block_size:
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
            outFile = core.BlockFile(os.path.join(self.out_dir, block_name))
            outFile.open_file(mode="w")
            for element in sorted_block:
                docids = " ".join(str(doc) for doc in block_dict[element])
                outString = element + " " + docids
                outFile.write_line(outString + "\n")
            outFile.close_file()
            self.block_index += 1
            self.blocklist.append(os.path.join(self.out_dir, block_name))


class Merger:
    def __init__(self, blockfiles, file_name="mf.txt", out_dir="./merged"):
        self.file_name = file_name
        self.out_dir = out_dir
        self.block_files = blockfiles
        self.get_out_dir()
        self.prep_output()
        self.out_file = core.BlockFile(os.path.join(self.out_dir, self.file_name))

    def prep_files(self):
        open_files = []
        for out_file in self.block_files:
            open_files.append(core.BlockFile(out_file))
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
        return sorted(set(new_postings))

    def merge_indexes(self, indexes, index):
        new_indexes = []
        new_indexes.extend(indexes)
        new_indexes.append(index)
        return sorted(set(new_indexes))

    def merge(self):
        in_files = [f.open_file() for f in self.prep_files()]
        next_lines = [f.read_line() for f in in_files]
        self.out_file.open_file(mode="w")
        while next_lines:
            next_term = core.BlockLine(list(), None, list())
            for index, line in enumerate(next_lines):
                line_obj = line
                line_obj.indexes = [index]
                if next_term.term is None:
                    next_term = line_obj
                elif line_obj.term == next_term.term:
                    next_term = line_obj.merge(next_term)
                elif line_obj.term < next_term.term:
                    next_term = line_obj

            # TODO: FIX file indexing to close the proper file
            self.out_file.write_line(next_term)
            new_indexes = next_term.indexes
            new_next_lines = [in_files[index].read_line() for index in new_indexes]
            offset = 0  # Create offset for indexes for when looping over the new lines read to ensure that indexes are aligned after deletion
            for index, new_line in enumerate(new_next_lines):
                try:
                    if new_line is None:
                        del(next_lines[new_indexes[index-offset]])
                        print "Closing file " + str(in_files[new_indexes[index-offset]])
                        in_files[new_indexes[index-offset]].close_file()
                        del(in_files[new_indexes[index-offset]])
                        offset += 1
                    else:
                        # print "Setting new line for index {}".format(new_indexes[index-offset])
                        # print new_indexes
                        # print[str(f) for f in in_files]
                        next_lines[new_indexes[index-offset]] = new_line
                except IndexError:
                    print "{} EXCEPTION with size {}".format(new_line, len(next_lines))
                    continue
        self.out_file.close_file()
        for f in in_files:
            try:
                f.close_file()
            except Exception:
                continue

        print "Finished merging files"


if __name__ == "__main__":
    now = datetime.datetime.now()
    # print os.listdir("./blockfiles")
    # bfiles = [os.path.join("./blockfiles", file) for file in sorted(os.listdir("./blockfiles"))]
    corp = core.Corpus("./../Corpus")
    print corp.count
    invert = Inverter(corp)
    invert.index()
    merger = Merger(invert.blocklist)
    merger.merge()
    print datetime.datetime.now() - now

