import json

import plotly.graph_objects as go

with open('balances.txt', 'r') as f:
    balances = json.load(f)
    print(balances)