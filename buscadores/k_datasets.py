import kaggle
import pandas as pd
import time

k = kaggle.api
k.authenticate()

df = pd.read_csv('./datasets_kaggle.csv')

novo_df = []

for index, row in df.iterrows():
    try:
        f = k.dataset_list_files(row['ref']).to_dict().get('datasetFiles','')
        linha = row.copy()
    
        if f:
            for file in f:
                file_name = file['name']
                linha['file_name'] = file_name
    
        novo_df.append(linha)
            
        time.sleep(2)
    except Exception as e:
        print(f"Error processing {row['ref']}: {e}")
        break
    
novo_df = pd.DataFrame(novo_df)
novo_df.to_csv('./datasets_kaggle_2.csv', index=False)