import json
from typing import List

from helper import preprocess

index = None
with open('index.json', 'r') as f:
    index = json.load(f)

query = 'Australia Technology'
queries = preprocess(query)


def get_pointers_list_from_queries(query_list: List[str]) -> List[List[List[int]]]:
    def get_pointers_from_query(query: str) -> List[List[int]]:
        res = []
        for pointers in index[query]:
            # item is docId,lineNo,termNo
            res.append(pointers)
        return res

    res = []
    # for each query, we get its doc list, then add it to res.
    for query in query_list:
        res.append(get_pointers_from_query(query))
    return res


pointers_list = get_pointers_list_from_queries(queries)


def intersect(pointers_list: List[List[int]]):
    def first(i: int) -> List[int]:
        return pointers_list[i]

    def postings(pointers: List[int]):
        return [pointer[0] for pointer in pointers]

    def intersect(l1: List[int], l2: List[int]) -> List[int]:
        p1 = 0
        p2 = 0
        res = []
        while p1 < len(l1) and p2 < len(l2):
            if l1[p1] == l2[p2]:
                res.append(l1[p1])
                p1 = p1 + 1
                p2 = p2 + 1
            elif l1[p1] < l2[p2]:
                p1 = p1 + 1
            else:
                p2 = p2 + 1
        return res

    # sort by increasing frequency
    pointers_list.sort(key=lambda x: len(x))
    i = 0
    result = postings(first(i))
    i = i + 1

    while i != len(pointers_list) and len(result) != 0:
        result = intersect(result, postings(first(i)))
        i = i + 1
    return result

print(intersect(pointers_list))
