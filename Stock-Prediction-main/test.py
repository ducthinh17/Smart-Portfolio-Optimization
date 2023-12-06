import investpy
import pandas as pd
import datetime as dt

from sklearn.preprocessing import MinMaxScaler

import numpy as np

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import Accuracy
from tensorflow.keras import models

import matplotlib.pyplot as plt

start = '01/06/2009'
end = dt.datetime.now().strftime("%d/%m/%Y")
test_size = 60
pre_day = 30
company = 'PLC'
crypto = 'bitcoin'
df = investpy.get_stock_historical_data(stock=company, country='VietNam', from_date=start, to_date=end)
# df = investpy.get_crypto_historical_data(crypto=crypto, from_date=start, to_date=end)

df = pd.DataFrame(df)

df['H-L'] = df['High'] - df['Low']
df['O-C'] = df['Open'] - df['Close']
ma_1 = 7
ma_2 = 14
ma_3 = 21
df[f'SMA_{ma_1}'] = df['Close'].rolling(window=ma_1).mean()
df[f'SMA_{ma_2}'] = df['Close'].rolling(window=ma_2).mean()
df[f'SMA_{ma_3}'] = df['Close'].rolling(window=ma_3).mean()
df[f'SD_{ma_1}'] = (((df['Close'] - df[f'SMA_{ma_1}'])**2).rolling(window=ma_1).sum()/ma_1)**.5
df.dropna(inplace=True)

df.to_csv(f"{company}.csv")
# df.to_csv(f"{crypto}.csv")
print("Done Loading Data")
# Process Data
scala_x = MinMaxScaler(feature_range=(0, 1))
scala_y = MinMaxScaler(feature_range=(0, 1))
cols_x = ['H-L', 'O-C', f'SMA_{ma_1}', f'SMA_{ma_2}', f'SMA_{ma_3}', f'SD_{ma_1}']
cols_y = ['Close']
scaled_data_x = scala_x.fit_transform(df[cols_x].values.reshape(-1, len(cols_x)))
scaled_data_y = scala_y.fit_transform(df[cols_y].values.reshape(-1, len(cols_y)))

x_total = []
y_total = []

for i in range(pre_day, len(df)):
    x_total.append(scaled_data_x[i-pre_day:i])
    y_total.append(scaled_data_y[i])

x_train = np.array(x_total[:len(x_total)-test_size])
x_test = np.array(x_total[len(x_total)-test_size:])
y_train = np.array(y_total[:len(y_total)-test_size])
y_test = np.array(y_total[len(y_total)-test_size:])
x_total = np.array(x_total)
print(x_total.shape)
reconstructed_model = models.load_model(f"{company}.h5")
predict_prices = reconstructed_model.predict(x_total)
predict_prices = scala_y.inverse_transform(predict_prices)


real_price = df[pre_day:]['Close'].values.reshape(-1, 1)
real_price = np.array(real_price)
real_price = real_price.reshape(real_price.shape[0], 1)
print(real_price.shape)




# Plotting the Stat
plt.style.use('dark_background')
plt.figure(figsize=(20, 16))
plt.plot(real_price, color="red", label=f"Real {company} Prices")
plt.plot(predict_prices, color="blue", label=f"Predicted {company} Prices", ls='--')
# plt.plot(real_price, color="red", label=f"Real {crypto} Prices")
# plt.plot(predict_prices, color="blue", label=f"Predicted {crypto} Prices")
plt.title(f"{company} Prices")
# plt.title(f"{crypto} Prices")
plt.xlabel("Time")
plt.ylabel("Stock Prices")
plt.ylim(bottom=0)
plt.xlim(left=0)
plt.legend()
plt.show()