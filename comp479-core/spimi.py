import core


class Inverter:
    def __init__(self, corpus):
        self.documents = corpus.documents
        self.tokens = self.get_tokens()

    def get_tokens(self):
        tokens = {}
        for document in self.documents:
            for key, value in document.tokens:
                if key not in tokens:
                    tokens[key] = list()
                    tokens[key].append(value)
                else:
                    tokens[key] = tokens[key].append(value)
        return tokens
