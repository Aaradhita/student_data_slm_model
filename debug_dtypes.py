import pandas as pd

file = 'student_dataset.xlsx'
df = pd.read_excel(file)
print('original dtypes:')
print(df.dtypes)
result = df.copy()
for col in df.columns:
    if df[col].dtype != object:
        print('col', col, 'dtype', df[col].dtype)
result = result.applymap(lambda x: '' if pd.isna(x) else str(x))
print('after applymap dtypes:')
print(result.dtypes)
print('sample value', result.iloc[0,0], type(result.iloc[0,0]))
# try writing
try:
    result.to_excel('test_out.xlsx', index=False)
    print('write succeeded')
except Exception as e:
    print('write error', e)
    print(result.dtypes)
