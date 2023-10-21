from typing import List

from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer

def normalize_number_string(number_str):
    return number_str.replace(",", "")

def my_normalize(string:str)->str:
    return normalize_number_string(string)

def preprocess(line: str) -> List[str]:
    lemmatizer = WordNetLemmatizer()
    stemmer = PorterStemmer()

    tokens = word_tokenize(line)

    splitted = []
    for token in tokens:
        for t in token.split('-'):
            splitted.append(t)

    lemmatized = [lemmatizer.lemmatize(t) for t in splitted]
    stemmed = [stemmer.stem(t) for t in lemmatized]
    res = [my_normalize(t) for t in stemmed]
    return res