import os
import re
from collections import defaultdict
from typing import List
import json

from helper import preprocess

# Initialize an empty index
index = defaultdict(list)


def tokenize(text):
    # Remove abbreviations dots
    text = re.sub(r'U\.S\.', 'US', text)
    # Remove commas from numbers
    text = re.sub(r'(\d),', r'\1', text)
    # Replace sentence-ending punctuation with '.'
    text = re.sub(r'[!?]', '.', text)
    # Tokenize text based on remaining punctuation
    return re.findall(r'\b\w+\b|\d+', text)


docIds: List[int] = []


def list_files(directory):
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_file():
                docIds.append(int(entry.name))


# Specify the directory you want to list files from
path1 = './data/'
list_files(path1)
docIds.sort()



for doc_id in docIds:
    with open(path1 + str(doc_id), "r") as file:
        lines = file.readlines()
        token_no = 0
        for line_no, line in enumerate(lines):
            processed_tokens = preprocess(line)
            # TODO hyphen word
            for t in processed_tokens:
                index[t].append((doc_id, line_no, token_no))
                token_no = token_no + 1


with open('./index.json', 'w') as f:
    json.dump(index, f)
