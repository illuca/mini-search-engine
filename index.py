import os
import sys
from collections import defaultdict
from typing import List, DefaultDict, Tuple
import json

from nltk import WordNetLemmatizer
from nltk.corpus import wordnet

from utils import preprocess


def list_files(directory: str) -> List[int]:
    res = []
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_file():
                res.append(int(entry.name))
    return res


def build_tense_index(tokens: List[str]):
    global tense_index
    lemmatizer = WordNetLemmatizer()
    for token in tokens:
        lemmatized = lemmatizer.lemmatize(token, pos=wordnet.VERB)
        if token != lemmatized:
            tense_index[lemmatized].append(token)

def build_index(doc_ids: List[int]):
    global DOC_DIR, NUM_TOKENS, Index
    for doc_id in doc_ids:
        with open(f'{DOC_DIR}/{doc_id}', "r") as file:
            lines = file.readlines()
            token_no = 0
            for line_no, line in enumerate(lines):
                line_no = line_no + 1
                processed_tokens = preprocess(line)
                NUM_TOKENS = NUM_TOKENS + len(processed_tokens)
                for t in processed_tokens:
                    build_tense_index(processed_tokens)
                    Index[t][doc_id].append((line_no, token_no))
                    token_no = token_no + 1


Index: DefaultDict[str, DefaultDict[int, List[Tuple[int, int]]]] = defaultdict(lambda: defaultdict(list))
tense_index = defaultdict(list)

# Specify the directory you want to list files from
DOC_DIR = sys.argv[1]
INDEX_DIR = sys.argv[2]
doc_ids = list_files(DOC_DIR)
doc_ids.sort()

NUM_DOCS = len(doc_ids)
NUM_TOKENS = 0
NUM_DISTINCT_TOKENS = 0

build_index(doc_ids)

# first sort by term, then sort by frequency(i.e. length of posting list)
Index = {k: v for k, v in sorted(Index.items(), key=lambda item: (item[0], len(item[1])))}
NUM_DISTINCT_TOKENS = len(Index.keys())

print(f'Total number of documents:{NUM_DOCS}')
print(f'Total number of tokens:{NUM_TOKENS}')
print(f'Total number of terms:{NUM_DISTINCT_TOKENS}')

if not os.path.exists(INDEX_DIR):
    os.makedirs(INDEX_DIR)
with open(f'{INDEX_DIR}/index.json', 'w') as f:
    json.dump(Index, f)

with open(f'{INDEX_DIR}/tense.json', 'w') as f:
    json.dump(tense_index, f)
with open(f'{INDEX_DIR}/doc_path.txt','w') as f:
    f.write(DOC_DIR)

# write words of index to file
# with open('./words.txt', 'w') as f:
#     for k, v in Index.items():
#         f.write(f'{k}\n')
