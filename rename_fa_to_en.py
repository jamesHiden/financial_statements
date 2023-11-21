import os
import re, jalali

def rename_to_en(symbol):
    path = f"C:/Users/new user/Downloads/{symbol}"
    dirs = os.listdir(path)

    for file in dirs:
        try:
            # print(file)
            period = jalali.Persian(re.findall('\w\w\w\w-\w\w-\w\w',file)[1]).gregorian_string()
            p = jalali.Gregorian(period).persian_string()
            if p.__contains__('12'):
                quarter = 'Q4'
            elif p.__contains__('-9-'):
                quarter = 'Q3'
            elif p.__contains__('-6-'):
                quarter = 'Q2'
            else:
                quarter = 'Q1'
            if file.__contains__('حسابرسی نشده'):
                if file.__contains__('اصلاحیه'):
                    Title = 'notAudited_modified'
                else:
                    Title = 'notAudited'
            elif file.__contains__('حسابرسی شده'):
                if file.__contains__('اصلاحیه'):
                    Title = 'Audited_modified'
                else:
                    Title = 'Audited'
            if file.__contains__('تلفیقی'):
                Title+='_Integrated'
            dst = f'{p}_{quarter}_{Title}.xls'
            if os.path.isfile(os.path.join(path,dst)):
                os.remove(os.path.join(path,dst))
            os.rename(os.path.join(path,file),os.path.join(path,dst))
        except:
            print(file,'*******')