#!/usr/bin/env python
# -*- coding: utf-8 -*-
        
#
#   test_functional.py.tmp test template generated 
#   from /home/srubio/src/fandango.git/fandango/functional.py
#   


import fandango.functional

def test_first():
    """
    Returns first element of sequence
    """
    assert fandango.functional.first((a for a in (1,2,3))) is 1

def test_last():
    """
    Returns last element of sequence
    """
    assert fandango.functional.last((a for a in (1,2,3))) is 3

def test_avg():
    """
    returns the average value of the sequence
    """
    data = 1,2,3,4
    assert fandango.functional.avg(data) == sum(data)/4.

def test_rms():
    """
    returns the rms value (sqrt of the squares average)
    """
    #assert fandango.functional.rms

def test_randomize():
    """
    returns a randomized version of the list
    """
    #assert fandango.functional.randomize

def test_randpop():
    """
    removes and returns a random item from the sequence
    """
    #assert fandango.functional.randpop

def test_floor():
    """
    Returns greatest multiple of 'unit' below 'x'
    """
    #assert fandango.functional.floor

def test_xor():
    """
    Returns (A and not B) or (not A and B);
    the difference with A^B is that it works also with different types and returns one of the two objects..
    """
    #assert fandango.functional.xor

def test_reldiff():
    """
    Checks relative (%) difference <floor between x and y
    floor would be a decimal value, e.g. 0.05
    """
    #assert fandango.functional.reldiff

def test_absdiff():
    """
    Checks absolute difference <floor between x and y
    floor would be a decimal value, e.g. 0.05
    """
    #assert fandango.functional.absdiff

def test_seqdiff():
    """
    Being x and y two arrays it checks (method) difference <floor between the elements of them.
    floor would be a decimal value, e.g. 0.05
    """
    #assert fandango.functional.seqdiff

def test_join():
    """
    It returns a list containing the objects of all given sequences.
    """
    #assert fandango.functional.join

def test_djoin():
    """
    This method merges dictionaries and/or lists
    """
    #assert fandango.functional.djoin

def test_kmap():
    
    __test_kmap = ''' [{'args': [<method 'lower' of 'str' objects>, 'BCA', 'YZX', False], 'result': [('A', 'x'), ('B', 'y'), ('C', 'z')]}] '''
    #assert fandango.functional.kmap

def test_splitList():
    """
    splits a list in lists of 'split' size
    """
    #assert fandango.functional.splitList

def test_contains():
    """
    Returns a in b; using a as regular expression if wanted
    """
    #assert fandango.functional.contains

def test_anyone():
    """
    Returns first that is true or last that is false
    """
    #assert fandango.functional.anyone

def test_everyone():
    """
    Returns last that is true or first that is false
    """
    #assert fandango.functional.everyone

def test_setitem():
    
    #assert fandango.functional.setitem

def test_getitem():
    
    #assert fandango.functional.getitem

def test_setlocal():
    
    #assert fandango.functional.setlocal

def test_matchAll():
    """
    Returns a list of matched strings from sequence.
    If sequence is list it returns exp as a list.
    """
    #assert fandango.functional.matchAll

def test_matchAny():
    """
    Returns seq if any of the expressions in exp is matched, if not it returns None
    """
    #assert fandango.functional.matchAny

def test_matchMap():
    """
    from a mapping type (dict or tuples list) with strings as keys it returns the value from the matched key or raises KeyError exception
    """
    #assert fandango.functional.matchMap

def test_matchTuples():
    """
    mapping is a (regexp,[regexp]) tuple list where it is verified that value matches any from the matched key
    """
    #assert fandango.functional.matchTuples

def test_inCl():
    """
    Returns a caseless "in" boolean function, using regex if wanted
    """
    #assert fandango.functional.inCl

def test_matchCl():
    """
    Returns a caseless match between expression and given string
    """
    #assert fandango.functional.matchCl

def test_searchCl():
    """
    Returns a caseless regular expression search between 
    expression and given string
    """
    #assert fandango.functional.searchCl

def test_replaceCl():
    """
    Replaces caseless expression exp by repl in string seq 
    repl can be string or callable(matchobj) ; to reuse matchobj.group(x) if needed in the replacement string
    lower argument controls whether replaced string should be always lower case or not
    """
    #assert fandango.functional.replaceCl

def test_splitCl():
    """
    Split an string by occurences of exp
    """
    #assert fandango.functional.splitCl

def test_sortedRe():
    """
    Returns a list sorted using regular expressions. 
        order = list of regular expressions to match ('[a-z]','[0-9].*','.*')
    """
    #assert fandango.functional.sortedRe

def test_toCl():
    """
    Replaces * by .* and ? by . in the given expression.
    """
    #assert fandango.functional.toCl

def test_toRegexp():
    """
    Case sensitive version of the previous one, for backwards compatibility
    """
    #assert fandango.functional.toRegexp

def test_filtersmart():
    """
    filtersmart(sequence,filters=['any_filter','+all_filter','!neg_filter'])
    
    appies a list of filters to a sequence of strings, 
    behavior of filters depends on first filter character:
        '[a-zA-Z0-9] : an individual filter matches all strings that contain it, one matching filter is enough
        '!' : negate, discards all matching values
        '+' : complementary, it must match all complementaries and at least a 'normal filter' to be valid
        '^' : matches string since the beginning (startswith instead of contains)
        '$' : matches the end of strings
        ',' : will be used as filter separator if a single string is provided
    """
    #assert fandango.functional.filtersmart

def test_Piped():
    """
    This class gives a "Pipeable" interface to a python method:
        cat | Piped(method,args) | Piped(list)
        list(method(args,cat))
    e.g.: 
    class grep:
        #keep only lines that match the regexp
        def __init__(self,pat,flags=0):
            self.fun = re.compile(pat,flags).match
        def __ror__(self,input):
            return ifilter(self.fun,input) #imap,izip,count,ifilter could ub useful
    cat('filename') | grep('myname') | printlines
    """
    #assert fandango.functional.Piped

def test_iPiped():
    """
    Used to pipe methods that already return iterators 
    e.g.: hdb.keys() | iPiped(filter,partial(fandango.inCl,'elotech')) | plist
    """
    #assert fandango.functional.iPiped

def test_zPiped():
    """
    Returns a callable that applies elements of a list of tuples to a set of functions 
    e.g. [(1,2),(3,0)] | zPiped(str,bool) | plist => [('1',True),('3',False)]
    """
    #assert fandango.functional.zPiped

def test_fbool():
    """
    Returns all(x) if sequence else bool(x) or False
    """
    #assert fandango.functional.fbool

def test_notNone():
    """
    Returns arg if not None, else returns default.
    """
    #assert fandango.functional.notNone

def test_isTrue():
    """
    Returns True if arg is not None, not False and not an empty iterable.
    """
    #assert fandango.functional.isTrue

def test_isNaN():
    
    #assert fandango.functional.isNaN

def test_isNone():
    
    #assert fandango.functional.isNone

def test_isFalse():
    
    #assert fandango.functional.isFalse

def test_isBool():
    
    #assert fandango.functional.isBool

def test_isString():
    """
    Returns True if seq type can be considered as string
    
    @TODO: repleace by this code: 
      import types;isinstance(seq,types.StringTypes)
    """
    #assert fandango.functional.isString

def test_isRegexp():
    """
    This function is just a hint, use it with care.
    """
    #assert fandango.functional.isRegexp

def test_isNumber():
    
    #assert fandango.functional.isNumber

def test_isDate():
    
    #assert fandango.functional.isDate

def test_isGenerator():
    
    #assert fandango.functional.isGenerator

def test_isSequence():
    """
    It excludes Strings, dictionaries but includes generators
    """
    #assert fandango.functional.isSequence

def test_isDictionary():
    """
    It includes dict-like and also nested lists if strict is False
    """
    #assert fandango.functional.isDictionary

def test_isHashable():
    
    #assert fandango.functional.isHashable

def test_isIterable():
    """
    It includes dicts and listlikes but not strings
    """
    #assert fandango.functional.isIterable

def test_isNested():
    
    #assert fandango.functional.isNested

def test_shape():
    """
    Returns the N dimensions of a python sequence
    """
    #assert fandango.functional.shape

def test_str2int():
    """
    It returns the first integer encountered in the string
    """
    #assert fandango.functional.str2int

def test_str2float():
    """
    It returns the first float (x.ye-z) encountered in the string
    """
    #assert fandango.functional.str2float

def test_str2bool():
    """
    It parses true/yes/no/false/1/0 as booleans
    """
    #assert fandango.functional.str2bool

def test_str2bytes():
    """
    Converts an string to a list of integers
    """
    #assert fandango.functional.str2bytes

def test_str2type():
    """
    Tries to convert string to an standard python type.
    If use_eval is True, then it tries to evaluate as code.
    Lines separated by sep_exp will be automatically split
    """
    #assert fandango.functional.str2type

def test_doc2str():
    
    #assert fandango.functional.doc2str

def test_rtf2plain():
    
    #assert fandango.functional.rtf2plain

def test_html2text():
    
    #assert fandango.functional.html2text

def test_unicode2str():
    """
    Converts an unpacked unicode object (json) to 
    nested python primitives (map,list,str)
    """
    #assert fandango.functional.unicode2str

def test_toList():
    
    #assert fandango.functional.toList

def test_toString():
    
    #assert fandango.functional.toString

def test_toStringList():
    
    #assert fandango.functional.toStringList

def test_str2list():
    """
    Convert a single string into a list of strings
    
    Arguments allow to split by regexp and to keep or not the separator character 
    sep_offset = 0 : do not keep
    sep_offset = -1 : keep with posterior
    sep_offset = 1 : keep with precedent
    """
    #assert fandango.functional.str2list

def test_code2atoms():
    """
    Obtain individual elements of a python code
    """
    #assert fandango.functional.code2atoms

def test_shortstr():
    """
    Obtain a shorter string
    """
    #assert fandango.functional.shortstr

def test_text2list():
    """
    Return only non empty words of a text
    """
    #assert fandango.functional.text2list

def test_str2lines():
    """
    Convert string into a multiline text of the same length
    """
    #assert fandango.functional.str2lines

def test_list2lines():
    """
    Joins every element of the list ending in multiline character,
    if joiner, returns the result as a single string.
    if comment, it will escape the comments until the end of the line
    """
    #assert fandango.functional.list2lines

def test_list2str():
    
    #assert fandango.functional.list2str

def test_text2tuples():
    
    #assert fandango.functional.text2tuples

def test_tuples2text():
    
    #assert fandango.functional.tuples2text

def test_dict2str():
    
    #assert fandango.functional.dict2str

def test_str2dict():
    """
    convert "name'ksep'value'vsep',..." to {name:value,...} 
    argument may be string or sequence of strings
    if s is a mapping type it will be returned
    """
    #assert fandango.functional.str2dict

def test_obj2str():
    
    #assert fandango.functional.obj2str

def test_negbin():
    """
    Given a binary number as an string, it returns all bits negated
    """
    #assert fandango.functional.negbin

def test_char2int():
    """
    ord(c)
    """
    #assert fandango.functional.char2int

def test_int2char():
    """
    unichr(n)
    """
    #assert fandango.functional.int2char

def test_int2hex():
    
    #assert fandango.functional.int2hex

def test_int2bin():
    
    #assert fandango.functional.int2bin

def test_hex2int():
    
    #assert fandango.functional.hex2int

def test_bin2unsigned():
    
    #assert fandango.functional.bin2unsigned

def test_signedint2bin():
    """
    It converts an integer to an string with its binary representation
    """
    #assert fandango.functional.signedint2bin

def test_bin2signedint():
    """
    Converts an string with a binary number into a signed integer
    """
    #assert fandango.functional.bin2signedint

def test_int2bool():
    """
    Converts an integer to a binary represented as a boolean array
    """
    #assert fandango.functional.int2bool

def test_bool2int():
    """
    Converts a boolean array to an unsigned integer
    """
    #assert fandango.functional.bool2int

def test_set_default_time_format():
    """
    Usages:
    
        fandango.set_default_time_format('%Y-%m-%d %H:%M:%S')
        
        or
        
        fandango.set_default_time_format(fandango.ISO_TIME_FORMAT)
    """
    #assert fandango.functional.set_default_time_format

def test_now():
    
    #assert fandango.functional.now

def test_time2tuple():
    
    #assert fandango.functional.time2tuple

def test_tuple2time():
    
    #assert fandango.functional.tuple2time

def test_date2time():
    
    #assert fandango.functional.date2time

def test_date2str():
    
    #assert fandango.functional.date2str

def test_time2date():
    
    #assert fandango.functional.time2date

def test_utcdiff():
    
    #assert fandango.functional.utcdiff

def test_time2str():
    """
    cad: introduce your own custom format (see below)
    use DEFAULT_TIME_FORMAT to set a default one
    us=False; True to introduce ms precission
    bt=True; negative epochs are considered relative from now
    utc=False; if True it converts to UTC
    iso=False; if True, 'T' will be used to separate date and time
    
    cad accepts the following formats:
    
    %a 	Locale’s abbreviated weekday name. 	 
    %A 	Locale’s full weekday name. 	 
    %b 	Locale’s abbreviated month name. 	 
    %B 	Locale’s full month name. 	 
    %c 	Locale’s appropriate date and time representation. 	 
    %d 	Day of the month as a decimal number [01,31]. 	 
    %H 	Hour (24-hour clock) as a decimal number [00,23]. 	 
    %I 	Hour (12-hour clock) as a decimal number [01,12]. 	 
    %j 	Day of the year as a decimal number [001,366]. 	 
    %m 	Month as a decimal number [01,12]. 	 
    %M 	Minute as a decimal number [00,59]. 	 
    %p 	Locale’s equivalent of either AM or PM. 	(1)
    %S 	Second as a decimal number [00,61]. 	(2)
    %U 	Week number of the year (Sunday as the first day of the week) as a decimal number [00,53]. 
    All days in a new year preceding the first Sunday are considered to be in week 0. 	(3)
    %w 	Weekday as a decimal number [0(Sunday),6]. 	 
    %W 	Week number of the year (Monday as the first day of the week) as a decimal number [00,53]. 
    All days in a new year preceding the first Monday are considered to be in week 0. 	(3)
    %x 	Locale’s appropriate date representation. 	 
    %X 	Locale’s appropriate time representation. 	 
    %y 	Year without century as a decimal number [00,99]. 	 
    %Y 	Year with century as a decimal number. 	 
    %Z 	Time zone name (no characters if no time zone exists). 	 
    %% 	A literal '%' character.
    """
    #assert fandango.functional.time2str

def test_str2time():
    """
    :param seq: Date must be in ((Y-m-d|d/m/Y) (H:M[:S]?)) format or -N [d/m/y/s/h]
    
    See RAW_TIME and TIME_UNITS to see the units used for pattern matching.
    
    The conversion itself is done by time.strptime method.
    
    :param cad: You can pass a custom time format
    """
    #assert fandango.functional.str2time

def test_time2gmt():
    
    #assert fandango.functional.time2gmt

def test_timezone():
    
    #assert fandango.functional.timezone

def test_ctime2time():
    
    #assert fandango.functional.ctime2time

def test_mysql2time():
    
    #assert fandango.functional.mysql2time

def test_iif():
    """
    if condition is boolean return (falsepart,truepart)[condition]
    if condition is callable returns truepart if condition(tp) else falsepart
    if forward is True condition(truepart) is returned instead of truepart
    if forward is callable, forward(truepart) is returned instead
    """
    #assert fandango.functional.iif

def test_ifThen():
    """
    This function allows to execute a callable on an object only if it 
    has a valid value. ifThen(value,callable) will return callable(value) 
    only if value is not in falsables.
    
    It is a List-like method, it can be combined with fandango.excepts.trial
    """
    #assert fandango.functional.ifThen

def test_call():
    """
    Calls a method from local scope parsing a pipe-like argument list
    """
    #assert fandango.functional.call

def test_retry():
    
    #assert fandango.functional.retry

def test_retried():
    """
    
    """
    #assert fandango.functional.retried

def test_evalF():
    """
    Returns a function that executes the formula passes as argument.
    The formula should use x,y,z as predefined arguments, or use args[..] array instead
    
    e.g.:
    map(evalF("x>2"),range(5)) : [False, False, False, True, True]
    
    It is optimized to be efficient (but still 50% slower than a pure lambda)
    """
    #assert fandango.functional.evalF

def test_testF():
    """
    it returns how many times f(*args) can be executed in t seconds
    """
    #assert fandango.functional.testF

def test_evalX():
    """
    evalX is an enhanced eval function capable of evaluating multiple types 
    and import modules if needed.
    
    The _locals/modules/instances dictionaries WILL BE UPDATED with the result
    of the code! (if '=' or import are used)
    
    It is used by some fandango classes to send python code to remote threads;
    that will evaluate and return the values as pickle objects.
    
    target may be:
         - dictionary of built-in types (pickable): 
                {'__target__':callable or method_name,
                '__args__':[],'__class_':'',
                '__module':'','__class_args__':[]}
         - string to eval: eval('import $MODULE' or '$VAR=code()' or 'code()')
         - list if list[0] is callable: value = list[0](*list[1:]) 
         - callable: value = callable()
    """
    #assert fandango.functional.evalX
