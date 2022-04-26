''' Utilities for working with strings in AtoM CSVs
'''
from typing import List


def split_by(string: str, split_char: str) -> List[str]:
    ''' Split a string into an array by arbitrary character.

    Args:
        string (str): The string to split
        split_char (str): The character to split the string by

    Returns:
        (List[str]): A list of strings split by the split_char
    '''
    items = []
    if string is None:
        return items
    for sub in string.split(split_char):
        sub_clean = sub.strip()
        if sub_clean:
            items.append(sub_clean)
    return items


def cardinality(string: str) -> int:
    ''' Determine the cardinality of a string. If a string is empty or Falsy,
    its cardinality is zero. Otherwise, the cardinality is the number of pipe
    characters plus one.

    Args:
        string (str): The string to calculate cardinality for

    Returns:
        (int): The cardinality of the string
    '''
    if string is None:
        return 0
    if not string.strip():
        return 0
    return string.count('|') + 1
