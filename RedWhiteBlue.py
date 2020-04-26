import datetime as dt
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import yfinance as yf
import os

yf.pdr_override()
plt.style.use('seaborn')

end_date = dt.datetime.now().date()
start_date = str(end_date + dt.timedelta(days=-3 * 365))
end_date = str(dt.datetime.now().date())

ticker ='AAPL'

ema_used = [3, 5, 8, 10, 12, 15, 30, 35, 40, 45, 50, 60]
pos = 0
num = 0
percentchange = []

try:
    df = pdr.get_data_yahoo(ticker, start_date, end_date)

    for ema in ema_used:
        df['Ema_' + str(ema)] = round(df.iloc[:, 4].ewm(span=ema, adjust=False).mean(), 2)

    df['Buy'] = 'nan'
    df['Sell'] = 'nan'
    df['Profit'] = 'nan'
    pos = 0
    num = 0
    cost = 4 # 2 USD per transaction (sell + buy)
    percentchange = []

    for i in df.index:
        cmin = min(df["Ema_3"][i], df["Ema_5"][i], df["Ema_8"][i], df["Ema_10"][i], df["Ema_12"][i], df["Ema_15"][i], )
        cmax = max(df["Ema_30"][i], df["Ema_35"][i], df["Ema_40"][i], df["Ema_45"][i], df["Ema_50"][i],
                   df["Ema_60"][i], )

        close = df.loc[i, 'Adj Close']

        if (cmin > cmax):
            # print("Red White Blue")
            if (pos == 0):
                bp = close
                pos = 1
                # print("Buying now at " + str(bp))
                df.loc[i, 'Buy'] = bp

        elif (cmin < cmax):
            # print("Blue White Red")
            if (pos == 1):
                pos = 0
                sp = close
                # print("Selling now at " + str(sp))
                df.loc[i, 'Sell'] = sp
                df.loc[i, 'Profit'] = sp - bp - cost
                pc = (sp / bp - 1) * 100
                percentchange.append(pc)
        if (num == df['Adj Close'].count() - 1 and pos == 1):
            pos = 0
            sp = close
            # print("Selling now at " + str(sp))
            df.loc[i, 'Sell'] = sp
            df.loc[i, 'Profit'] = sp - bp - cost
            pc = (sp / bp - 1) * 100
            percentchange.append(pc)
        num += 1

    gains = 0
    ng = 0
    losses = 0
    nl = 0
    totalR = 1

    for i in percentchange:
        if (i > 0):
            gains += i
            ng += 1
        else:
            losses += i
            nl += 1
        totalR = totalR * ((i / 100) + 1)

    totalR = round((totalR - 1) * 100, 2)

    plt.plot(df['Adj Close'], color='black')

    idx = 0
    while idx <= 5:
        plt.plot(df['Ema_' + str(ema_used[idx])], color = 'red')
        plt.plot(df['Ema_' + str(ema_used[idx+6])], color='blue')
        idx+=1

    xmin, xmax, ymin, ymax = plt.axis()

    df['buy_to_show'] = None
    df['sell_to_show'] = None

    for i in df.index:
        price = df['Buy'][i]
        if price != 'nan':
            df.loc[i, 'buy_to_show'] = price + (ymax - price) / 2
        price = df['Sell'][i]
        if price != 'nan':
            df.loc[i, 'sell_to_show'] = price + (ymax - price) / 2

    plt.scatter(df.index, df['buy_to_show'], marker ='o', color='green')
    plt.scatter(df.index, df['sell_to_show'], marker='x', color='red')

    for a, b, s, c in zip(df.index, df['Buy'], df['Sell'], df['Profit']):
        if b != 'nan':
            buy = str(round(b, 2))
            print(str('Buy: ' + str(a.date()) + ' ' + buy))
            plt.annotate(buy, xy=(a, b + (ymax - b) / 2))
        if s != 'nan':
            profit = str(round(s, 2)) + ' profit: ' + str(round(c, 2))
            print('Sell: ' + str(a.date()) + ' ' + profit)
            plt.annotate(profit, xy=(a, s + (ymax - s) / 2))

    plt.title('Results for ' + ticker + ' going back to ' + str(df.index[0].date()) +
              ', Sample size: ' + str(ng + nl) + ' trades, ' + 'Total return: ' + str(totalR) + '%')
    # mng = plt.get_current_fig_manager()
    # mng.window.state("zoomed")
    plt.show()
    df.to_csv('stock_data.csv')
except Exception as ex:
    print('Error:', ex)