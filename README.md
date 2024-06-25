# Linear Time Suffix Array Creator
Creates the suffix array of a string in linear time (in terms of string length) using Ukkonen's algorithm.
Expects the string to end in the unique chracter '$' and accepts characters with an ord value of less than 128 (eg accepts all ascii but not unicode).


A suffix array of a string is the lexographical order of each suffix of a string.  Using "banana$" as an example:

6 : $

5 : a$

3 : ana$

1 : anana$

0 : banana$

4 : na$

2 : nana$ 


.: [6, 5, 3, 1, 0, 4, 2] is the suffix array.
