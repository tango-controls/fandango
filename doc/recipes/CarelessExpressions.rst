Careless Regular Expressions
============================

Fandango implements a simplified set of regular expression syntax.

The methods matchCl, searchCl, splitCl, replaceCl, inCl replace re.match, re.search, re.split, re.sub respectively.

The differences with standard regular expressions are:

- regexp and target strings are converted to lower case prior to matching
- "*" and " " are equivalent to ".*"
- if extend=True: 
-- "!" at the beginning of expression implies negative matching
-- "exp1 & exp2" will require both expressions to be matched
 
This changes in syntax are implemented in functional.toCl and functional.matchCl methods
