'''
Copyright 2022 National Centre for Truth and Reconciliation

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


Utilities for working with strings in AtoM CSVs
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
