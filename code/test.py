import json

with open('../data/test.txt', 'w') as f:
    json.dump({1: 'ayy', 2:'boo'}, f)