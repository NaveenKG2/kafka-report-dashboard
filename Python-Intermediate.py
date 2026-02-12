import pandas as pd

data = {'prodID': ['101', '102', '103', '104', '104'], 'prodname': ['X', 'Y', 'Z', 'X', 'W'], 'profit': ['2738', '2727', '3497', '7347', '3743']}
df = pd.DataFrame(data, index=['one','two','three','four','five'])
print(df['prodname'][3])

