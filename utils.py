import re
from typing import List

from nltk import pos_tag
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

def tokenize(text:str):
    # Remove dots in abbreviations like U.S. -> US
    text = re.sub(r'\b([A-Za-z])\.([A-Za-z])\.', r'\1\2', text)
    # Remove commas from numbers: 1,000 -> 1000
    text = re.sub(r'(\d),', r'\1', text)
    text = re.sub(r'(\d+).(\w+)', r'', text)
    tokens = word_tokenize(text)
    res = []
    for t in tokens:
        res.extend(re.split(r'[^a-zA-Z0-9.]+', t))
    res = [t.lower() for t in res]
    return res
def get_wordnet_pos(treebank_tag):
    # ignore tense
    if treebank_tag.startswith('V'):
        return wordnet.VERB
    # ignore plural
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    # comparative adjective
    elif treebank_tag.startswith('J'):
        return wordnet.ADJ
    # comparative adv
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def preprocess(line: str) -> List[str]:
    res = []
    lemmatizer = WordNetLemmatizer()
    tokens = tokenize(line)
    tagged_tokens = pos_tag(tokens)
    tagged_tokens = list(filter(lambda x : x[0]!='' and x[0] != '.', tagged_tokens))

    for token, tag in tagged_tokens:
        res.append(lemmatizer.lemmatize(token, pos=get_wordnet_pos(tag)))
    return res


def get_DOC_DIR(index_dir:str)->str:
    with open(f'{index_dir}/doc_path.txt','r') as f:
        line = f.readline()
        return line