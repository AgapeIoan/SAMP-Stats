import json
from difflib import SequenceMatcher

from functools import lru_cache

with open("storage/language/commons.json", "r") as f:
    COMMONS = json.load(f) # LIST

def lev_dist(a, b):
    # Calculates the levenshtein distance between two strings
    
    @lru_cache(None)  # for memorization
    def min_dist(s1, s2):

        if s1 == len(a) or s2 == len(b):
            return len(a) - s1 + len(b) - s2

        # no change required
        if a[s1] == b[s2]:
            return min_dist(s1 + 1, s2 + 1)

        return 1 + min(
            min_dist(s1, s2 + 1),      # insert character
            min_dist(s1 + 1, s2),      # delete character
            min_dist(s1 + 1, s2 + 1),  # replace character
        )

    return min_dist(0, 0)

def compare_faction_names(string1, string2):
    # Returns the Levenshtein distance between two faction names.

    # "Paramedic Department LV" vs "Paramedic Department SF", should not match
    if string1[-2:] in COMMONS and string2[-2:] != string1[-2:]:
        return -1

    if string1 < string2:
        string1, string2 = string2, string1
    # Tratam cazul Hitmen vs Hitman Agency
    buffer_string = string2[:len(string1)]
    short_dist = lev_dist(buffer_string, string1)
    if short_dist < 2:
        return short_dist

    return lev_dist(string1, string2)

def is_lev_legit(lev_distance):
    # Maximum 2 chars should be accepted afaik. 
    return lev_distance <= 2 and lev_distance != -1

if __name__ == "__main__":
    text = "Hitman Agency"
    result = compare_faction_names(text, "Hitmen")

    print(result)