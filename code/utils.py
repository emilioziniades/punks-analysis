import math

def intervals(start, end, parts):
    # Breaks up an number into equal sized intervals
    duration = end - start
    part_duration = duration / parts
    return [[((i * part_duration) + start), (((i + 1) * part_duration) + start)] for i in range(parts)]


def non_equal_intervals(start, end, parts, transform_formula):
    duration = end - start
    transformed_array = list(map(transform_formula,range(parts + 1)))
    squash_factor = duration / transformed_array[-1]
    squash = lambda x: x * squash_factor
    squashed_array = list(map(squash, transformed_array))

    intervals = []
    for i, _ in enumerate(squashed_array):
        try:
            s = squashed_array[i] + start
            e = squashed_array[i+1] + start
            intervals.append([round(s), round(e)])
        except IndexError:
            continue

    print(intervals)
    print('\n')
    print([end - start for (start,end) in intervals])
    print('\n')
    return intervals


def flatten(list_of_list_of_dicts):
    list_of_dicts = []
    for list_of_dict in list_of_list_of_dicts:
        for dictionary in list_of_dict:
            list_of_dicts.append(dictionary)
    return list_of_dicts

def parse_result_list(list_of_dicts):
    return [_to_dict(i) for i in list_of_dicts]

def _to_dict(dict_to_parse):
    # convert any 'AttributeDict' type found to 'dict'
    parsed_dict = dict(dict_to_parse)
    for key, val in parsed_dict.items():
        # check for nested dict structures to iterate through
        if  'dict' in str(type(val)).lower():
            parsed_dict[key] = _to_dict(val)
        # convert 'HexBytes' type to 'str'
        elif 'HexBytes' in str(type(val)):
            parsed_dict[key] = val.hex()
    return parsed_dict


def gini_coefficient(balances_dictionary):
    print(False)

