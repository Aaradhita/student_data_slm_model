import pandas as pd
print('pandas version', pd.__version__)
print('has applymap?', hasattr(pd.DataFrame, 'applymap'))
df = pd.DataFrame({'a':[1,2]})
print(df, type(df))
print('call applymap', df.applymap(lambda x: x*2))
