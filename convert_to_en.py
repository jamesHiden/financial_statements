import pandas as pd
from num2words import num2words
from word2number import w2n
import jalali
import re

def bs_to_en(df):
    df.columns = df.columns.astype(str)
    for i,j in enumerate(df['شرح']):
        if j == 'دارایی‌ها' or j == 'دارايي‌ها':
            df['شرح'][i] = 'Assets'
        elif j == 'دریافتنی‌‌های غیرتجاری':
            df['شرح'][i] = 'No Trade Receivables'
        elif j == 'پرداختنی‌های غیرتجاری':
            df['شرح'][i] = 'No Trade Payables'
        elif j == 'پیش‌دریافت‌های غیرجاری':
            df['شرح'][i] = 'Non-Current Advances Received'
        elif j == 'دارايی‌های غیرجاری' or j == 'دارایی‌‌های غیرجاری' or j == 'دارايي‌هاي غيرجاري':
            df['شرح'][i] = 'Non-Current Assets'
        elif j == 'دارایی‌های ثابت مشهود' or j == 'دارايي‌هاي ثابت مشهود':
            df['شرح'][i] = 'Tangible Fixed Assets'
        elif j == 'سرمایه‌گذاری در املاک' or j == 'سرمايه‌گذاري در املاک':
            df['شرح'][i] = 'Investment in Properties'
        elif j == 'دارایی‌های نامشهود' or j == 'دارايي‌هاي نامشهود':
            df['شرح'][i] = 'Intangible Assets'
        elif j == 'سرمایه‌گذاری‌های بلندمدت' or j == 'سرمايه‌گذاري‌هاي بلندمدت':
            df['شرح'][i] = 'Long-Term Investments'
        elif j == 'دریافتنی‌های بلندمدت' or j == 'دریافتنی‌‌های بلندمدت' or j == 'دريافتني‌هاي بلندمدت':
            df['شرح'][i] = 'Long-Term Receivables'
        elif j == 'دارايي ماليات انتقالي':
            df['شرح'][i] = 'tax moved Assets'
        elif j == 'سایر دارایی‌ها' or j == 'ساير دارايي‌ها':
            df['شرح'][i] = 'Other Assets'
        elif j == 'جمع دارایی‌های غیرجاری' or j == 'جمع دارايي‌هاي غيرجاري':
            df['شرح'][i] = 'Total Non-Current Assets'
        elif j == 'دارایی‌های جاری' or j == 'دارایی‌‌های جاری' or j == 'دارايي‌هاي جاري':
            df['شرح'][i] = 'Current Assets'
        elif j == 'سفارشات و پیش‌پرداخت‌ها' or j == 'پیش پرداخت‌ها و سفارشات' or j == 'سفارشات و پيش‌پرداخت‌ها':
            df['شرح'][i] = 'Orders and Prepayments'
        elif j == 'موجودی مواد و کالا' or j == 'موجودي مواد و کالا':
            df['شرح'][i] = 'Inventory'
        elif j == 'دریافتنی‌های تجاری و سایر دریافتنی‌ها' or j == 'دریافتنی‌‌های تجاری' or j == 'دريافتني‌هاي تجاري و ساير دريافتني‌ها':
            df['شرح'][i] = 'Trade and Other Receivables'
        elif j == 'سرمایه‌گذاری‌های کوتاه‌مدت' or j == 'سرمایه‌گذاری‌‌های کوتاه مدت' or j == 'سرمايه‌گذاري‌هاي کوتاه‌مدت' or j == 'سرمایه‌گذاری‌‌های کوتاه‌مدت':
            df['شرح'][i] = 'Short-Term Investments'
        elif j == 'موجودی نقد' or j == 'موجودي نقد':
            df['شرح'][i] = 'Cash and Cash Equivalents'
        elif j == 'دارایی‌های نگهداری شده برای فروش' or j == 'دارايي‌هاي نگهداري شده براي فروش':
            df['شرح'][i] = 'Assets Held for Sale'
        elif j == 'جمع دارایی‌های جاری' or j == 'جمع دارايي‌هاي جاري':
            df['شرح'][i] = 'Total Current Assets'
        elif j == 'جمع دارایی‌ها' or j == 'جمع دارايي‌ها':
            df['شرح'][i] = 'Total Assets'
        elif j == 'حقوق مالکانه و بدهی‌ها' or j == 'بدهی‌ها و حقوق صاحبان سهام' or j == 'حقوق مالکانه و بدهي‌ها':
            df['شرح'][i] = 'Equity and Liabilities'
        elif j == 'حقوق مالکانه' or j == 'حقوق صاحبان سهام':
            df['شرح'][i] = 'Equity'
        elif j == 'سرمايه' or j == 'سرمایه':
            df['شرح'][i] = 'Capital'
        elif j == 'افزایش سرمایه در جریان' or j == 'افزایش (کاهش) سرمایه در جریان' or j == 'افزايش سرمايه در جريان':
            df['شرح'][i] = 'Capital Increase in Progress'
        elif j == 'صرف سهام' or j == 'صرف (کسر) سهام':
            df['شرح'][i] = 'Treasury Share'
        elif j == 'صرف سهام خزانه':
            df['شرح'][i] = 'treasury Shares'
        elif j == 'اندوخته قانونی' or j == 'اندوخته قانوني':
            df['شرح'][i] = 'Legal Reserve'
        elif j == 'ساير اندوخته‌ها' or j == 'سایر اندوخته‌ها':
            df['شرح'][i] = 'Other Reserves'
        elif j == 'مازاد تجدیدارزيابی دارایی‌ها' or j == 'مازاد تجدید ارزیابی دارایی‌ها' or j == 'مازاد تجديدارزيابي دارايي‌ها':
            df['شرح'][i] = 'Revaluation Surplus'
        elif j == 'تفاوت تسعیر ارز عملیات خارجی' or j == 'تفاوت تسعیر ناشی از تبدیل به واحد پول گزارشگری' or j == 'تفاوت تسعير ارز عمليات خارجي':
            df['شرح'][i] = 'Foreign Operations Exchange Differences'
        elif j == 'سود (زيان) انباشته' or j == 'سود (زیان) انباشته' or j == 'سود(زيان) انباشته':
            df['شرح'][i] = 'Retained Earnings (Loss)'
        elif j == 'سهام خزانه':
            df['شرح'][i] = 'Treasury Shares'
        elif j == 'جمع حقوق مالکانه' or j == 'جمع حقوق صاحبان سهام':
            df['شرح'][i] = 'Total Equity'
        elif j == 'بدهی‌ها' or j == 'بدهي‌ها':
            df['شرح'][i] = 'Liabilities'
        elif j == 'بدهی‌های غیرجاری' or j == 'بدهي‌هاي غيرجاري':
            df['شرح'][i] = 'Non-Current Liabilities'
        elif j == 'پرداختنی‌های بلندمدت' or j == 'پرداختني‌هاي بلندمدت':
            df['شرح'][i] = 'Long-Term Payables'
        elif j == 'تسهیلات مالی بلندمدت' or j == 'تسهيلات مالي بلندمدت':
            df['شرح'][i] = 'Long-Term Financial Facilities'
        elif j == 'بدهي ماليات انتقالي':
            df['شرح'][i] = 'Tax Moved Liabilities'
        elif j == 'ذخیره مزایای پایان خدمت کارکنان' or j == 'ذخيره مزاياي پايان خدمت کارکنان':
            df['شرح'][i] = 'Employees End of Service Benefits Provision'
        elif j == 'جمع بدهی‌های غیرجاری' or j == 'جمع بدهي‌هاي غيرجاري':
            df['شرح'][i] = 'Total Non-Current Liabilities'
        elif j == 'بدهی‌های جاری' or j == 'بدهي‌هاي جاري':
            df['شرح'][i] = 'Current Liabilities'
        elif j == 'پرداختنی‌های تجاری و سایر پرداختنی‌ها' or j == 'پرداختنی‌های تجاری' or j == 'پرداختني‌هاي تجاري و ساير پرداختني‌ها':
            df['شرح'][i] = 'Trade and Other Payables'
        elif j == 'مالیات پرداختنی' or j == 'ماليات پرداختني':
            df['شرح'][i] = 'Tax Payable'
        elif j == 'سود سهام پرداختنی' or j == 'سود سهام پرداختني':
            df['شرح'][i] = 'Dividends Payable'
        elif j == 'تسهیلات مالی' or j == 'تسهيلات مالي':
            df['شرح'][i] = 'Short-Term Financial Facilities'
        elif j == 'ذخایر' or j == 'ذخاير':
            df['شرح'][i] = 'Provisions'
        elif j == 'پیش‌دریافت‌ها' or j == 'پیش‌دریافت‌های جاری' or j == 'پيش‌دريافت‌ها':
            df['شرح'][i] = 'Advances Received'
        elif j == 'جمع بدهی‌های جاری' or j == 'جمع بدهي‌هاي جاري':
            df['شرح'][i] = 'Total Current Liabilities'
        elif j == 'جمع بدهی‌ها' or j == 'جمع بدهي‌ها':
            df['شرح'][i] = 'Total Liabilities'
        elif j == 'جمع حقوق مالکانه و بدهی‌ها' or j == 'جمع بدهی‌ها و حقوق صاحبان سهام' or j == 'جمع حقوق مالکانه و بدهي‌ها':
            df['شرح'][i] = 'Total Equity and Liabilities'
        elif j == 'بدهی‌های ‌مرتبط ‌با دارایی‌های نگهداری‌‌شده برای ‌فروش' or j == 'بدهی‌های مرتبط با دارایی‌های نگهداری شده برای فروش' or j == 'بدهي‌هاي ‌مرتبط ‌با دارايي‌هاي نگهداري‌‌شده براي ‌فروش':
            df['شرح'][i] = 'Liabilities Related to Assets Held for Sale'
        elif j == 'مازاد تجدید ارزیابی دارایی‌های نگهداری شده برای فروش' or j == 'مازاد تجدید ارزیابی دارایی‌های غیرجاری نگهداری شده برای فروش':
            df['شرح'][i] = 'Revaluation Surplus of Assets Held for Sale'
        elif j == 'اندوخته تسعیر ارز دارایی‌ها و بدهی‌های شرکت‌های دولتی' or j == 'اندوخته تسعير ارز دارايي‌ها و بدهي‌هاي شرکت‌هاي دولتي':
            df['شرح'][i] = 'Foreign Operations Exchange Differences Reserve'
            
    # df.drop(0,axis=0,inplace=True)
    df.fillna(0,inplace=True)
    df_col = []

    for i in df.columns:
        if i.__contains__('/'):
            df_col.append(jalali.Persian(re.findall('\w\w\w\w/\w\w/\w\w',i)[0]).gregorian_string())
            d = df[i].map(lambda x:(str(x).replace(',','').replace(')','').replace('(','-')))
            df[i] = d.map(lambda x: w2n.word_to_num(num2words(x).replace(',','')))
        elif i == 'شرح':
            df_col.append('Description')
        # elif i == 'درصد تغییر' or i == 'درصد تغییرات':
        #     df_col.append('Percentage Change')
        else:
            df = df.drop(i,axis=1)
    # print(df_col)

    df.columns = df_col
    return df

def cf_to_en(df):
    df.columns = df.columns.astype(str)
    for i,j in enumerate(df['شرح']):
        if j == 'جریان­‌های نقدی حاصل از فعالیت‌های عملیاتی:' or j == 'جريان­هاي نقدي حاصل از فعاليت‌هاي عملياتي:':
            df['شرح'][i] = 'Operating Activities'
        elif j == 'نقد حاصل از عملیات' or j == 'نقد حاصل از عمليات':
            df['شرح'][i] = 'Net Income'
        elif j == 'پرداخت‌های نقدی بابت مالیات بر درآمد' or j == 'پرداخت‌هاي نقدي بابت ماليات بر درآمد':
            df['شرح'][i] = 'Cash payments for income taxes'
        elif j == 'جریان ‌خالص ‌ورود‌ (خروج) ‌نقد حاصل از فعالیت‌های ‌عملیاتی' or j == 'جريان ‌خالص ‌ورود‌ (خروج) ‌نقد حاصل از فعاليت‌هاي ‌عملياتي':
            df['شرح'][i] = 'Net cash provided by (used in) operating activities'
        elif j == 'جریان‌­های نقدی حاصل از فعالیت‌های سرمایه‌گذاری:' or j == 'جريان­هاي نقدي حاصل از فعاليت‌هاي سرمايه‌گذاري:':
            df['شرح'][i] = 'Cash flows from investing activities'
        elif j == 'دریافت‌های نقدی حاصل از فروش دارایی‌های ثابت مشهود' or j == 'دريافت‌هاي نقدي حاصل از فروش دارايي‌هاي ثابت مشهود':
            df['شرح'][i] = 'Cash receipts from the sale of tangible fixed assets'
        elif j == 'پرداخت‌های نقدی برای خرید دارایی‌های ثابت مشهود' or j == 'پرداخت‌هاي نقدي براي خريد دارايي‌هاي ثابت مشهود':
            df['شرح'][i] = 'Cash payments for the purchase of tangible fixed assets'
        elif j == 'دریافت‌های نقدی حاصل از فروش دارایی‌های نگهداری‌شده برای فروش' or j == 'دريافت‌هاي نقدي حاصل از فروش دارايي‌هاي غيرجاري نگهداري‌شده براي فروش':
            df['شرح'][i] = 'Cash receipts from the sale of held-for-sale assets'
        elif j == 'دریافت‌های نقدی حاصل از فروش دارایی‌های نامشهود' or j == 'دريافت‌هاي نقدي حاصل از فروش دارايي‌هاي نامشهود':
            df['شرح'][i] = 'Cash receipts from the sale of intangible assets'
        elif j == 'پرداخت‌های نقدی برای خرید دارایی‌های نامشهود' or j == 'پرداخت‌هاي نقدي براي خريد دارايي‌هاي نامشهود':
            df['شرح'][i] = 'Cash payments for the purchase of intangible assets'
        elif j == 'دریافت‌های نقدی حاصل از فروش سرمايه‌گذاری‌های بلندمدت' or j == 'دريافت‌هاي نقدي حاصل از فروش سرمايه‌گذاري‌هاي بلندمدت':
            df['شرح'][i] = 'Cash receipts from the sale of long-term investments'
        elif j == 'پرداخت‌های نقدی برای تحصیل سرمايه‌گذاری‌های بلندمدت' or j == 'پرداخت‌هاي نقدي براي تحصيل سرمايه‌گذاري‌هاي بلندمدت':
            df['شرح'][i] = 'Cash payments for long-term investments'
        elif j == 'دریافت‌های نقدی حاصل از فروش سرمایه‌گذاری در املاک' or j == 'دريافت‌هاي نقدي حاصل از فروش سرمايه‌گذاري در املاک':
            df['شرح'][i] = 'Cash receipts from the sale of real estate investments'
        elif j == 'پرداخت‌های نقدی برای تحصیل سرمایه‌گذاری در املاک' or j == 'پرداخت‌هاي نقدي براي تحصيل سرمايه‌گذاري‌ در املاک':
            df['شرح'][i] = 'Cash payments for real estate investments'
        elif j == 'دریافت‌های نقدی حاصل از فروش سرمايه‌گذاری‌های کوتاه‌مدت' or j == 'دريافت‌هاي نقدي حاصل از فروش سرمايه‌گذاري‌هاي کوتاه‌مدت':
            df['شرح'][i] = 'Cash receipts from the sale of short-term investments'
        elif j == 'پرداخت‌های نقدی برای تحصیل سرمایه‌گذاری‌های کوتاه‌مدت' or j == 'پرداخت‌هاي نقدي براي تحصيل سرمايه‌گذاري‌هاي کوتاه‌مدت':
            df['شرح'][i] = 'Cash payments for short-term investments'
        elif j == 'پرداخت های نقدی بابت تسهیلات اعطایی به دیگران' or j == 'پرداخت‌هاي نقدي بابت تسهيلات اعطايي به ديگران':
            df['شرح'][i] = 'Cash payments for loans granted to others'
        elif j == 'دریافت‌های نقدی حاصل از استرداد تسهیلات اعطایی به دیگران' or j == 'دريافت‌هاي نقدي حاصل از استرداد تسهيلات اعطايي به ديگران':
            df['شرح'][i] = 'Cash receipts from the repayment of loans granted to others'
        elif j == 'دریافت‌های نقدی حاصل از سود تسهیلات اعطایی به دیگران' or j == 'دريافت‌هاي نقدي حاصل از سود تسهيلات اعطايي به ديگران':
            df['شرح'][i] = 'Cash receipts from interest on loans granted to others'
        elif j == 'دریافت‌های نقدی حاصل از سود‌ سهام' or j == 'دريافت‌هاي نقدي حاصل از سود‌ سهام':
            df['شرح'][i] = 'Cash receipts from dividend income'
        elif j == 'دریافت‌های نقدی حاصل از سود سایر سرمایه‌گذاری‌ها' or j == 'دريافت‌هاي نقدي حاصل از سود ساير سرمايه‌گذاري‌ها':
            df['شرح'][i] = 'Cash receipts from other investment income'
        elif j == 'جريان خالص ورود (خروج) نقد حاصل از فعاليت‌های سرمایه‌گذاری' or j == 'جريان خالص ورود (خروج) نقد حاصل از فعاليت‌هاي سرمايه‌گذاري':
            df['شرح'][i] = 'Net cash provided by (used in) investing activities'
        elif j == 'جريان خالص ورود (خروج) نقد قبل از فعالیت‌های تامین مالی' or j == 'جريان خالص ورود (خروج) نقد قبل از فعاليت‌هاي تامين مالي':
            df['شرح'][i] = 'Net cash provided by (used in) operating activities before financing activities'
        elif j == 'جریان­‌های نقدی حاصل از فعالیت‌های تامین مالی:' or j == 'جريان­هاي نقدي حاصل از فعاليت‌هاي تامين مالي:':
            df['شرح'][i] = 'Cash flows from financing activities'
        elif j == 'دریافت‌های نقدی حاصل از افزايش سرمايه' or j == 'دريافت‌هاي نقدي حاصل از افزايش سرمايه':
            df['شرح'][i] = 'Cash receipts from capital contributions'
        elif j == 'دریافت‌های نقدی حاصل از صرف سهام' or j == 'دريافت‌هاي نقدي حاصل از صرف سهام':
            df['شرح'][i] = 'Cash receipts from the sale of shares'
        elif j == 'دریافت‌های نقدی حاصل از فروش سهام خزانه' or j == 'دريافت‌هاي نقدي حاصل از فروش سهام خزانه':
            df['شرح'][i] = 'Cash receipts from the sale of treasury shares'
        elif j == 'پرداخت‌های نقدی برای خرید سهام خزانه' or j == 'پرداخت‌هاي نقدي براي خريد سهام خزانه':
            df['شرح'][i] = 'Cash payments for the purchase of treasury shares'
        elif j == 'دریافت‌های نقدی حاصل از تسهيلات' or j == 'دريافت‌هاي نقدي حاصل از تسهيلات':
            df['شرح'][i] = 'Cash receipts from facilities'
        elif j == 'پرداخت‌های نقدی بابت اصل تسهيلات' or j == 'پرداخت‌هاي نقدي بابت اصل تسهيلات':
            df['شرح'][i] = 'Cash payments for principal of facilities'
        elif j == 'پرداخت‌های نقدی بابت سود تسهيلات' or j == 'پرداخت‌هاي نقدي بابت سود تسهيلات':
            df['شرح'][i] = 'Cash payments for interest on facilities'
        elif j == 'دریافت‌های نقدی حاصل از انتشار اوراق مشارکت' or j == 'دريافت‌هاي نقدي حاصل از انتشار اوراق مشارکت':
            df['شرح'][i] = 'Cash receipts from the issuance of participation certelificates'
        elif j == 'پرداخت‌های نقدی بابت اصل اوراق مشارکت' or j == 'پرداخت‌هاي نقدي بابت اصل اوراق مشارکت':
            df['شرح'][i] = 'Cash payments for principal of participation certelificates'
        elif j == 'پرداخت‌های نقدی بابت سود اوراق مشارکت' or j == 'پرداخت‌هاي نقدي بابت سود اوراق مشارکت':
            df['شرح'][i] = 'Cash payments for interest on participation certelificates'
        elif j == 'دریافت‌های نقدی حاصل از انتشار اوراق خرید دین' or j == 'دريافت‌هاي نقدي حاصل از انتشار اوراق خريد دين':
            df['شرح'][i] = 'Cash receipts from the issuance of sukuk'
        elif j == 'پرداخت‌های نقدی بابت اصل اوراق خرید دین' or j == 'پرداخت‌هاي نقدي بابت اصل اوراق خريد دين':
            df['شرح'][i] = 'Cash payments for principal of sukuk'
        elif j == 'پرداخت‌های نقدی بابت سود اوراق خرید دین' or j == 'پرداخت‌هاي نقدي بابت سود اوراق خريد دين':
            df['شرح'][i] = 'Cash payments for profit/interest on sukuk'
        elif j == 'پرداخت‌های نقدی بابت اصل اقساط اجاره سرمایه‌ای' or j == 'پرداخت‌هاي نقدي بابت اصل اقساط اجاره سرمايه‌اي':
            df['شرح'][i] = 'Cash payments for principal of capital lease installments'
        elif j == 'پرداخت‌های نقدی بابت سود اجاره سرمایه‌ای' or j == 'پرداخت‌هاي نقدي بابت سود اجاره سرمايه‌اي':
            df['شرح'][i] = 'Cash payments for rental interest on capital lease'
        elif j == 'پرداخت‌های نقدی بابت سود سهام' or j == 'پرداخت‌هاي نقدي بابت سود سهام':
            df['شرح'][i] = 'Cash payments for dividend income on shares'
        elif j == 'جريان خالص ورود (خروج) نقد حاصل از فعالیت‌های تامين مالی' or j == 'جريان خالص ورود (خروج) نقد حاصل از فعاليت‌هاي تامين مالي':
            df['شرح'][i] = 'Net cash provided by (used in) financing activities'
        elif j == 'خالص افزايش (کاهش) در موجودی نقد' or j == 'خالص افزايش (کاهش) در موجودي نقد':
            df['شرح'][i] = 'Net increase (decrease) in cash balance'
        elif j == 'مانده موجودی نقد در ابتدای سال' or j == 'مانده موجودي نقد در ابتداي سال':
            df['شرح'][i] = 'Cash balance at the beginning of the year'
        elif j == 'تاثير تغييرات نرخ ارز' or j == 'تاثير تغييرات نرخ ارز':
            df['شرح'][i] = 'Effects of exchange rate changes'
        elif j == 'مانده موجودي نقد در پايان سال' or j == 'مانده موجودی نقد در پايان سال':
            df['شرح'][i] = 'Cash balance at the end of the year'
        elif j == 'معاملات غیرنقدی' or j == 'معاملات غيرنقدي':
            df['شرح'][i] = 'Non-cash transactions'
    # df.drop(0,axis=0,inplace=True)
    df.fillna(0,inplace=True)
    df_col = []

    # if True not in ['/' in df.columns[i] for i in range(len(df.columns))]:
    #     df.columns = df.loc[0]
    for i in df.columns:
        if i.__contains__('/'):
            df_col.append(jalali.Persian(re.findall('\w\w\w\w/\w\w/\w\w',i)[0]).gregorian_string())
            d = df[i].map(lambda x:(str(x).replace(',','').replace(')','').replace('(','-')))
            df[i] = d.map(lambda x: w2n.word_to_num(num2words(x).replace(',','')))
        elif i == 'شرح':
            df_col.append('Description')
        # elif i == 'درصد تغییر' or i == 'درصد تغییرات':
        #     df_col.append('Percentage Change')
        else:
            df = df.drop(i,axis=1)
    # print(df_col)

    df.columns = df_col
    return df

def is_to_en(df):
    df.columns = df.columns.astype(str)
    for i,j in enumerate(df['شرح']):
        if j == 'سود (زیان) خالص':
            df['شرح'][i] ='Net profit (loss)'
        elif j == 'درآمدهای عملیاتی':
            df['شرح'][i] ='Operating revenues'
        elif j == 'درآمد سود سهام':
            df['شرح'][i] ='Dividend income'
        elif j == 'درآمد سود تضمین شده':
            df['شرح'][i] ='Guaranteed profit income'
        elif j == 'سود (زیان) فروش سرمایه گذاری ها':
            df['شرح'][i] ='Gain (loss) from sale of investments'
        elif j == 'سود (زیان) تغییر ارزش سرمایه گذاری در اوراق بهادار':
            df['شرح'][i] ='Gain (loss) from change in fair value of securities'
        elif j == 'سایر درآمدهای عملیاتی':
            df['شرح'][i] ='Other operating income'
        elif j == 'جمع درآمدهای عملیاتی':
            df['شرح'][i] ='Total operating revenues'
        elif j == 'هزینه های عملیاتی':
            df['شرح'][i] ='Operating expenses'
        elif j == 'هزینه‌های فروش، اداری و عمومی' or j == 'هزينه‏‌هاى فروش، ادارى و عمومى':
            df['شرح'][i] ='Selling, general, and administrative expenses'
        elif j == 'سایر هزینه‌های عملیاتی':
            df['شرح'][i] ='Other operating expenses'
        elif j == 'جمع هزینه های عملیاتی':
            df['شرح'][i] ='Total operating expenses'
        elif j == 'سود (زیان) عملیاتی':
            df['شرح'][i] ='Operating profit (loss)'
        elif j == 'هزینه‌های مالی':
            df['شرح'][i] ='Financial expenses'
        elif j == 'سایر درآمدها و هزینه‌های غیرعملیاتی' or j == 'سایر درآمدها و هزینه‌های غیرعملیاتی- درآمد سرمایه‌گذاری‌ها':
            df['شرح'][i] ='Other non-operating income and expenses'
        elif j == 'سود (زیان) عملیات در حال تداوم قبل از مالیات' or j == 'سود (زيان) عمليات در حال تداوم قبل از ماليات':
            df['شرح'][i] ='Continuing operations profit (loss) before tax'
        elif j == 'مالیات بر درآمد' or j == 'هزینه مالیات بر درآمد:':
            df['شرح'][i] ='Income tax'
        elif j == 'سود (زیان) خالص عملیات در حال تداوم' or j == 'سود (زيان) خالص عمليات در حال تداوم':
            df['شرح'][i] ='Net income (loss) from continuing operations'
        elif j == 'سود (زیان) عملیات متوقف ‌شده پس از اثر مالیاتی':
            df['شرح'][i] ='Discontinued operations profit (loss) after tax'
        elif j == 'سود (زیان) خالص':
            df['شرح'][i] ='Net profit (loss)'
        elif j == 'سود (زیان) پایه هر سهم' or j == 'سود (زيان) پايه هر سهم':
            df['شرح'][i] ='Earnings (loss) per share'
        elif j == 'سود (زیان) پایه هر سهم ناشی از عملیات در حال تداوم- عملیاتی':
            df['شرح'][i] ='Basic earnings (loss) per share from continuing operations - Operating'
        elif j == 'سود (زیان) پایه هر سهم ناشی از عملیات در حال تداوم- غیرعملیاتی':
            df['شرح'][i] ='Basic earnings (loss) per share from continuing operations - Non-operating'
        elif j == 'سود (زیان) پایه هر سهم ناشی از عملیات متوقف ‌شده':
            df['شرح'][i] ='Basic earnings (loss) per share from discontinued operations'
        elif j == 'سود (زیان) پایه هر سهم':
            df['شرح'][i] = 'Basic earnings (loss) per share'
        elif j == 'سود (زیان) تقلیل یافته هر سهم':
            df['شرح'][i] = 'Diluted earnings (loss) per share'
        elif j == 'سود (زیان) تقلیل یافته هر سهم ناشی از عملیات در حال تداوم- عملیاتی':
            df['شرح'][i] = 'Diluted earnings (loss) per share from continuing operations - Operating'
        elif j == 'سود (زیان) تقلیل یافته هر سهم ناشی از عملیات در حال تداوم- غیرعملیاتی':
            df['شرح'][i] = 'Diluted earnings (loss) per share from continuing operations - Non-operating'
        elif j == 'سود (زیان) تقلیل یافته هر سهم ناشی از عملیات متوقف‌ شده':
            df['شرح'][i] = 'Diluted earnings (loss) per share from discontinued operations'
        elif j == 'سود (زیان) تقلیل یافته هر سهم':
            df['شرح'][i] = 'Diluted earnings (loss) per share'
        elif j == 'گردش حساب سود (زیان) انباشته':
            df['شرح'][i] = 'Accumulated retained earnings'
        elif j == 'سود (زیان) خالص' or j == 'سود (زيان) خالص':
            df['شرح'][i] = 'Net profit (loss)'
        elif j == 'سود (زیان) انباشته ابتدای دوره':
            df['شرح'][i] = 'Beginning retained earnings'
        elif j == 'تعدیلات سنواتی':
            df['شرح'][i] = 'Periodic adjustments'
        elif j == 'سود (زیان) انباشته ابتدای دوره تعدیل‌شده':
            df['شرح'][i] = 'Adjusted beginning retained earnings'
        elif j == 'سود سهام‌ مصوب':
            df['شرح'][i] = 'Approved dividend'
        elif j == 'تغییرات سرمایه از محل سود (زیان) انباشته':
            df['شرح'][i] = 'Capital changes from retained earnings'
        elif j == 'سود (زیان) انباشته ابتدای دوره تخصیص نیافته':
            df['شرح'][i] = 'Unappropriated retained earnings at the beginning of the period'
        elif j == 'انتقال از سایر اقلام حقوق صاحبان سهام':
            df['شرح'][i] = 'Transfer from other equity items'
        elif j == 'سود قابل تخصیص':
            df['شرح'][i] = 'Retained earnings available for allocation'
        elif j == 'انتقال به اندوخته‌ قانوني‌':
            df['شرح'][i] = 'Transfer to legal reserves'
        elif j == 'انتقال به سایر اندوخته‌ها':
            df['شرح'][i] = 'Transfer to other reserves'
        elif j == 'سود (زیان) انباشته‌ پايان‌ دوره':
            df['شرح'][i] = 'Retained earnings at the end of the period'
        elif j == 'سود (زیان) خالص هر سهم- ریال' or j == 'سود (زیان) خالص هر سهم– ریال':
            df['شرح'][i] = 'Net earnings (loss) per share - Iranian rials'
        elif j == 'سرمایه':
            df['شرح'][i] = 'Capital'
        elif j == 'بهاى تمام شده درآمدهای عملیاتی':
            df['شرح'][i] = 'Cost of goods sold for operating income'
        elif j == 'سود (زيان) ناخالص':
            df['شرح'][i] = 'Gross profit (loss)'
        elif j == 'هزینه کاهش ارزش دریافتنی‌‏ها (هزینه استثنایی)':
            df['شرح'][i] = 'Impairment of receivables (extraordinary expense)'
        elif j == 'ساير درآمدها':
            df['شرح'][i] = 'Other incomes'
        elif j == 'سایر هزینه‌ها':
            df['شرح'][i] = 'Other expenses'
        elif j == 'سود (زيان) عملياتي':
            df['شرح'][i] = 'Operating profit (loss)'
        elif j == 'هزينه‏‌هاى مالى':
            df['شرح'][i] = 'Financial expenses'
        elif j == 'سایر درآمدها و هزینه‌های غیرعملیاتی- اقلام متفرقه':
            df['شرح'][i] = 'Other non-operating income - Miscellaneous items'
        elif j == 'سال جاری':
            df['شرح'][i] = 'Current year'
        elif j == 'سال‌های قبل':
            df['شرح'][i] = 'Prior years'
        elif j == 'عملیات متوقف شده:':
            df['شرح'][i] = 'Discontinued operations'
        elif j == 'سود (زیان) خالص عملیات متوقف شده':
            df['شرح'][i] = 'Net profit (loss) from discontinued operations'
        elif j == 'عملیاتی (ریال)':
            df['شرح'][i] = '(Operational in Rials)'
        elif j == 'غیرعملیاتی (ریال)':
            df['شرح'][i] = '(Non-operational in Rials)'
        elif j == 'ناشی از عملیات در حال تداوم':
            df['شرح'][i] = 'Attributable to continuing operations'
        elif j == 'ناشی از عملیات متوقف شده':
            df['شرح'][i] = 'Attributable to discontinued operations'
        elif j == 'عملیات در حال تداوم:':
            df['شرح'][i] = 'Continuing operations'
        

    # df.drop(0,axis=0,inplace=True)
    df.fillna(0,inplace=True)
    df_col = []

    # if True not in ['/' in df.columns[i] for i in range(len(df.columns))]:
    #     df.columns = df.loc[0]
    for i in df.columns:
        if i.__contains__('/'):
            df_col.append(jalali.Persian(re.findall('\w\w\w\w/\w\w/\w\w',i)[0]).gregorian_string())
            d = df[i].map(lambda x:(str(x).replace(',','').replace(')','').replace('(','-')))
            df[i] = d.map(lambda x: w2n.word_to_num(num2words(x).replace(',','')))
        elif i == 'شرح':
            df_col.append('Description')
        # elif i == 'درصد تغییر' or i == 'درصد تغییرات':
        #     df_col.append('Percentage Change')
        else:
            df = df.drop(i,axis=1)
    # print(df_col)

    df.columns = df_col
    return df
