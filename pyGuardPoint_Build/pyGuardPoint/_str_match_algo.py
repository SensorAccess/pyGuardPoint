import json

from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import Levenshtein
from pyGuardPoint_Build.pyGuardPoint import Cardholder

EXPORT_FILENAME = '../../cardholder_export.json'

str_list = ['Joe@Biden.com', 'Joseph Biden', 'Joseph R Biden']




if __name__ == "__main__":
    with open(EXPORT_FILENAME) as f:
        entries = json.load(f)
    count = len(entries)
    print(f"Importing {str(count)} entries from {EXPORT_FILENAME}.")

    cardholders = []
    for entry in entries:
        cardholders.append(Cardholder(entry))

    cardholder_patterns = []
    for cardholder in cardholders:
        cardholder_patterns.append(cardholder.to_search_pattern())

    match_ratios = process.extract('joe r biden tech joe@biden.com', cardholder_patterns, scorer=fuzz.token_sort_ratio)
    #print(match_ratios)

    pos = cardholder_patterns.index(match_ratios[0][0])

    print(cardholders[pos].pretty_print())

'''from difflib import SequenceMatcher as SM

str1 = 'John Owen Countermac j.o@eml.cc'
str2 = 'John Owen'
str3 = 'Owen j.o@eml.cc'

#def cardholder_similarity_ratio():


similarity_ratio = SM(None, str1, str2).ratio()

print(similarity_ratio)

similarity_ratio = SM(None, str1, str3).ratio()

print(similarity_ratio)'''