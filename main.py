import pandas as pd
import os
from rename_fa_to_en import rename_to_en
from codal_api import get_info
from convert_to_en import bs_to_en, cf_to_en, is_to_en
from num2words import num2words
from word2number import w2n
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

base_dir = os.path.dirname(os.path.abspath)
symbols = ['فاراک', 'شپدیس', 'شتران', 'شپنا', 'شستا']
for symbol in symbols:
    get_info(symbols)
    rename_to_en(symbol)
    dst_dir = os.path.join(base_dir,'csv_files', symbol)

    file_dir = f"C:/Users/new user/Downloads/{symbol}"
    if not os.path.isdir(dst_dir):
        os.makedirs(dst_dir)
    dirs = os.listdir(file_dir)

    for file in dirs:
        if file[-14:] == 'notAudited.xls':
            if (file.replace('notAudited', 'Audited') in dirs) or (file.replace('notAudited', 'notAudited_modified') in dirs):
                continue
        if file[-23:] == 'notAudited_modified.xls' and file.replace('notAudited_modified', 'Audited') in dirs:
            continue

        try:
            data = pd.read_html(f'{file_dir}/{file}')
            for df in data:
                if 'جمع دارایی‌های جاری' in df.values or 'جمع دارايي‌هاي جاري' in df.values:
                    df.to_csv(f'{dst_dir}/{file}_bs.csv',index=False)
                    
                elif 'نقد حاصل از عملیات' in df.values or 'نقد حاصل از عمليات' in df.values or 'جریان­‌های نقدی حاصل از فعالیت‌های تامین مالی' in df.values:
                    df.to_csv(f'{dst_dir}/{file}_cf.csv',index=False)
                    
                elif 'سود (زیان) پایه هر سهم' in df.values or 'سود (زيان) پايه هر سهم' in df.values or 'درآمد سود سهام' in df.values:
                    df.to_csv(f'{dst_dir}/{file}_is.csv',index=False)

        except:
            print("We could not read the file>>>>>>>>>>> ",file)
            pass

        bs_path = os.path.join(dst_dir,'balance_sheet')
        cf_path = os.path.join(dst_dir,'cash_flow')
        is_path = os.path.join(dst_dir,'income_statement')

        if not os.path.isdir(bs_path):
            os.mkdir(bs_path)
        if not os.path.isdir(cf_path):
            os.mkdir(cf_path)
        if not os.path.isdir(is_path):
            os.mkdir(is_path)

        dirs = os.listdir(dst_dir)

        for file in dirs:
            if '.csv' not in file:
                continue
            data = pd.read_csv(f'{dst_dir}/{file}')
            if type(data.columns) == tuple:
                col_names = []
                [col_names.append(data.columns[i][0]) for i in range(len(data.columns))]
                data.columns = col_names
                
            if True not in ['/' in data.columns[i] for i in range(len(data.columns))]:
                data.columns = data.loc[0]
                data.rename(columns={data.columns[0]:'شرح'},inplace=True)
                
            data.drop(0,axis=0,inplace=True)
            data.reset_index(drop=True, inplace=True)
            if file[-6:]=='bs.csv':
                if len(data.columns)>5:
                    try:
                        if 'درصد  تغییرات' in data.columns:
                            data1 = data.loc[0:,'شرح':'درصد  تغییرات']
                        elif 'درصد تغییرات' in data.columns:
                            data1 = data.loc[0:,'شرح':'درصد تغییرات']
                        data1 = data1[data1['شرح'].notna()]
                        data2 = data.loc[0:,'شرح.1':]
                        data2.columns = data1.columns
                        x = pd.concat([data1, data2]).reset_index(drop=True)
                        bs_to_en(x).to_csv(f"{bs_path}/{file[:-11]}.csv", index=False)
                        os.remove(f'{dst_dir}/{file}')
                    except:
                        print("We could not extract Balance Sheet from this file: ",file)
                        pass
                else:
                    try:
                        bs_to_en(data).to_csv(f"{bs_path}/{file[:-11]}.csv", index=False)
                        os.remove(f'{dst_dir}/{file}')
                    except:
                        print('We could not extract Cash Flow from this file: ',file)
                        
            elif file[-6:]=='cf.csv':
                try:
                    cf_to_en(data).to_csv(f"{cf_path}/{file[:-11]}.csv", index=False)
                    os.remove(f'{dst_dir}/{file}')
                except:
                    print(file)
                    
            elif file[-6:]=='is.csv':
                try:
                    is_to_en(data).to_csv(f"{is_path}/{file[:-11]}.csv", index=False)
                    os.remove(f'{dst_dir}/{file}')
                except:
                    print('We could not extract Income Statement from this file: ',file)