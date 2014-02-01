import os.path

from .trie import Trie
from .utils import hexstrings2int


class Collator:

    def __init__(self, filename=None):

        if filename is None:
            filename = os.path.join(os.path.dirname(__file__), "allkeys.txt")
        self.table = Trie()
        self.load(filename)

    def load(self, filename):
        with open(filename) as keys_file:
            for line in keys_file:
                line = line.split("#")[0].split("%")[0].strip()

                if not line:
                    continue

                if line.startswith("@"):
                    pass
                else:
                    semicolon = line.find(";")
                    char_list = line[:semicolon].strip().split()
                    x = line[semicolon:]
                    coll_elements = []
                    while True:
                        begin = x.find("[")
                        if begin == -1:
                            break
                        end = x[begin:].find("]")
                        coll_element = x[begin:begin + end + 1]
                        x = x[begin + 1:]

                        chars = coll_element[2:-1].split(".")

                        coll_elements.append(hexstrings2int(chars))
                    self.table.add(hexstrings2int(char_list), coll_elements)

    def collation_elements(self, string):
        collation_elements = []

        lookup_key = [ord(ch) for ch in string]
        while lookup_key:
            value, lookup_key = self.table.find_prefix(lookup_key)
            if not value:
                # Calculate implicit weighting for CJK Ideographs
                # http://www.unicode.org/reports/tr10/#Implicit_Weights
                key = lookup_key[0]
                value = [
                    (0xFB40 + (key >> 15), 0x0020, 0x0002, 0x0001),
                    ((key & 0x7FFF) | 0x8000, 0x0000, 0x0000, 0x0000)
                ]
                lookup_key = lookup_key[1:]
            collation_elements.extend(value)

        return collation_elements

    def sort_key_from_collation_elements(self, collation_elements):
        sort_key = []

        for level in range(4):
            if level:
                sort_key.append(0)  # level separator
            for element in collation_elements:
                ce_l = element[level]
                if ce_l:
                    sort_key.append(ce_l)

        return tuple(sort_key)

    def sort_key(self, string):

        collation_elements = self.collation_elements(string)
        return self.sort_key_from_collation_elements(collation_elements)
