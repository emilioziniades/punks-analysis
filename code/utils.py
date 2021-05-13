def intervals(start, end, parts):
    # Breaks up an number into equal sized intervals
    duration = end - start
    part_duration = duration / parts
    return [[((i * part_duration) + start), (((i + 1) * part_duration) + start)] for i in range(parts)]


def flatten(list_of_list_of_dicts):
    list_of_dicts = []
    for list_of_dict in list_of_list_of_dicts:
        for dictionary in list_of_dict:
            list_of_dicts.append(dictionary)
    return list_of_dicts


def parseResultList(listOfDicts):
    return [_toDict(i) for i in listOfDicts]


def _toDict(dictToParse):
    # convert any 'AttributeDict' type found to 'dict'
    parsedDict = dict(dictToParse)
    for key, val in parsedDict.items():
        # check for nested dict structures to iterate through
        if  'dict' in str(type(val)).lower():
            parsedDict[key] = _toDict(val)
        # convert 'HexBytes' type to 'str'
        elif 'HexBytes' in str(type(val)):
            parsedDict[key] = val.hex()
    return parsedDict
