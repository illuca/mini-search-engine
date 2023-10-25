import json
import re
import sys
from collections import defaultdict
from itertools import product
from typing import List, DefaultDict, Dict, Tuple, Set
from nltk import WordNetLemmatizer, word_tokenize
from nltk.corpus import wordnet
import linecache

from utils import get_DOC_DIR


def get_origin_form(query):
    lemmatizer = WordNetLemmatizer()
    pos_list = [wordnet.NOUN, wordnet.VERB, wordnet.ADJ, wordnet.ADV]
    res = query
    for pos in pos_list:
        lemmatized = lemmatizer.lemmatize(query, pos=pos)
        if query != lemmatized:
            res = lemmatized
            break
    return res


def get_siblings(query: str) -> List:
    global Tense
    res = set()
    if query in Tense:
        res.update(Tense[query])
    origin = get_origin_form(query)
    res.add(origin)
    return res


def get_merged_postings(siblings):
    global Index
    postings_list = []
    for token in siblings:
        if token in Index:
            postings_list.append(Index[token])
    res = {}
    for d in postings_list:
        for key, value in d.items():
            if key in res:
                res[key].extend(value)  # merge the lists
            else:
                res[key] = value
    return res


def get_docs_from_queries(quries: List[str]) -> Dict[str, Dict]:
    global Index
    # transformed by the tags, and get the transformed query
    # then we get a sibling, for each sibling array, we get a merged posting list.
    res = defaultdict(Dict)
    for query in quries:
        siblings = get_siblings(query)
        postings = get_merged_postings(siblings)
        if len(postings) > 0:
            res[query] = postings
    return res


def intersect(queries: List[str], query_postings: Dict[str, Dict]):
    def first(i: int) -> Dict[int, List]:
        return query_postings[queries[i]]

    def get_postings(d: Dict[int, List]) -> List[int]:
        r = [x for x in d.keys()]
        r.sort()
        return r

    def intersect(l1: List[int], l2: List[int]) -> List[int]:
        p1 = 0
        p2 = 0
        res = []
        while p1 < len(l1) and p2 < len(l2):
            # doc id of posting list 1 equals doc id of posting list 2
            if l1[p1] == l2[p2]:
                # push doc id and distance
                res.append(l1[p1])
                p1 = p1 + 1
                p2 = p2 + 1
            elif l1[p1] < l2[p2]:
                p1 = p1 + 1
            else:
                p2 = p2 + 1
        return res

    i = 0
    result = get_postings(first(i))
    i = i + 1

    while i != len(queries) and len(result) != 0:
        result = intersect(result, get_postings(first(i)))
        i = i + 1
    return result


class Rank:
    def __init__(self, proximity=0, num_correct=0, doc_id=0, positions=[]):
        self.proximity = proximity
        self.num_correct = num_correct
        self.doc_id = doc_id
        self.positions = positions


def get_proximity(arr1: List[List], arr2: List[List]) -> (Tuple, Rank):
    order = Rank(0, 0, 0)
    minn = float('inf')
    pos = None
    for p1 in arr1:
        for p2 in arr2:
            a = p1[1]
            b = p2[1]
            if abs(a - b) - 1 < minn:
                minn = abs(a - b) - 1
                pos = a, b
                if a < b:
                    order = Rank(minn, 1)
                else:
                    order = Rank(minn, 0)

    return pos, order


def get_min_distance_positions(postings: Dict[str, List]) -> Tuple[int, List]:
    # Sort positions for each term
    # for term, positions in postings.items():
    #     postings[term] = sorted(positions)
    min_distance = float('inf')
    min_positions = None

    # Generate all combinations of positions for all terms
    all_positions = product(*postings.values())

    for positions in all_positions:
        distance = sum(abs(positions[i][1] - positions[i - 1][1]) for i in range(1, len(positions)))
        if distance < min_distance:
            min_distance = distance
            min_positions = positions

    return min_distance, min_positions


def get_num_correct_order(positions: List) -> int:
    p = [position[1] for position in positions]
    res = 0
    for i in range(0, len(p) - 1):
        if p[i] < p[i + 1]:
            res = res + 1
    return res


def order_by_proximity(queries: List[str], id_postings: Dict[int, Dict]) -> Dict[int, Rank]:
    # for each query,
    ranks: DefaultDict[int, Rank] = defaultdict(lambda: Rank())
    for doc_id, postings in id_postings.items():
        # for each query, we record
        min_distance, min_positions = get_min_distance_positions(postings)
        num_correct = get_num_correct_order(min_positions)
        ranks[doc_id] = Rank(min_distance, -num_correct, doc_id, min_positions)
    res = dict(sorted(ranks.items(), key=lambda item: (item[1].proximity, item[1].num_correct, item[1].doc_id)))
    return res


def process_query(line: str) -> List[str]:
    res = []
    text = re.sub(r'\b([A-Za-z])\.([A-Za-z])\.', r'\1\2', line)
    text = re.sub(r'(\d),', r'\1', text)
    tokens = word_tokenize(text)
    res = [t.lower() for t in tokens]
    return res


def convert_dict(queries, query_postings):
    global docs
    d = defaultdict(lambda: defaultdict(list))
    for query in queries:
        for doc_id in docs:
            d[doc_id][query] = query_postings[query][doc_id]
    return d


def read_specific_lines(filename, line_numbers):
    lines = [linecache.getline(filename, i).strip('\n') for i in line_numbers]
    for line in lines:
        print(line)
def get_sorted_line_number(positions: List[List]) -> List[int]:
    res = []
    visited = set()
    for p in positions:
        if not p[0] in visited:
            res.append(p[0])
            visited.add(p[0])
    res.sort()
    return res
def display_proximity_and_positions(rank:Rank):
    positions = rank.positions
    global queries
    print(f'  {rank.proximity}',end=" ")
    for x,y in zip(queries, positions):
        print(f'{x}:{y}',end=" ")
    print()

INDEX_DIR = sys.argv[1]

DOC_DIR = get_DOC_DIR(INDEX_DIR)

Index: Dict[str, Dict[int, List[List]]] = defaultdict(lambda: defaultdict(list))
Tense: Dict[str, List] = {}
with open(f'{INDEX_DIR}/index.json', 'r') as f:
    tmp_index = json.load(f)
    for token, postings in tmp_index.items():
        for doc_id, positions in postings.items():
            Index[token][int(doc_id)] = positions


with open(f'{INDEX_DIR}/tense.json', 'r') as f:
    Tense = json.load(f)

while True:
    # query = "> US finance COMPANY investor"
    query = input()
    # query = "> bank expect distribution"
    # query = "> AUStralia Technology"
    queries = []
    TEXT_DISPLAY=False
    if query[0] == '>':
        TEXT_DISPLAY = True
        queries = process_query(query[2:len(query)])
    else:
        queries = process_query(query)

    query_postings = get_docs_from_queries(queries)
    if len(query_postings) == 0:
        continue

    # sort by increasing frequency, the num of distinct doc where term appears
    if len(queries) == 0:
        continue
    elif len(queries) == 1:
        postings = query_postings[queries[0]]
        for doc_id, positions in postings.items():
            if TEXT_DISPLAY:
                print(f'> {doc_id}')
                read_specific_lines(f'{INDEX_DIR}/{doc_id}', line_numbers)
            else:
                print(doc_id)
    else:
        sorted_queries = sorted(queries, key=lambda q: len(query_postings[q]))
        docs = intersect(sorted_queries, query_postings)
        id_postings = convert_dict(queries, query_postings)
        ordered_docs: Dict[int, Rank] = order_by_proximity(queries, id_postings)
        for doc_id, rank in ordered_docs.items():
            line_numbers: List = get_sorted_line_number(rank.positions)
            if TEXT_DISPLAY:
                print(f'> {doc_id}')
                # display_proximity_and_positions(rank)
                read_specific_lines(f'{DOC_DIR}/{doc_id}', line_numbers)
            else:
                print(doc_id)


