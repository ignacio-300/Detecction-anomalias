# -*- coding: utf-8 -*-
"""anomaly-detection-Ignacio.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1v1hr0bzeP5vdaYtMWcrHp0DAEwhrYZa2
"""

!nvidia-smi

!pip install h5py
!pip install typing-extensions
!pip install wheel

!pip uninstall keras
!pip uninstall tensorflow

!pip install gdown
!pip install keras
#!pip install tensorflow-gpu
!pip install tensorflow==2.7.0

# Commented out IPython magic to ensure Python compatibility.


import numpy as np
import tensorflow as tf
from tensorflow import keras
import pandas as pd
import seaborn as sns
from pylab import rcParams
import matplotlib.pyplot as plt
from matplotlib import rc
from pandas.plotting import register_matplotlib_converters
from sklearn.preprocessing import StandardScaler

# %matplotlib inline
# %config InlineBackend.figure_format='retina'

register_matplotlib_converters()
sns.set(style='whitegrid', palette='muted', font_scale=1.5)

rcParams['figure.figsize'] = 22, 10

RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)
#tf.random.set_seed(RANDOM_SEED)

TimeSeries = pd.read_csv('/content/MRNA(1).csv', parse_dates=['Date'], index_col='Date')

TimeSeries.head()

plt.plot(TimeSeries.Close, label='close price')
plt.legend();

train_size = int(len(TimeSeries) * 0.8)#% de entrenamiento/Validación
test_size = len(TimeSeries) - train_size
train, test = TimeSeries.iloc[0:train_size], TimeSeries.iloc[train_size:len(TimeSeries)]
print(train.shape, test.shape)



escala = StandardScaler() #escalamos todos los precios de 0-1 para facilitar el aprendizaje de la red neuronal
escala = escala.fit(train[['Close']])

train['Close'] = escala.transform(train[['Close']])
test['Close'] = escala.transform(test[['Close']])

def create_dataset(X, y, time_steps=1):
    Xs, ys = [], []
    for i in range(len(X) - time_steps):
        v = X.iloc[i:(i + time_steps)].values
        Xs.append(v)        
        ys.append(y.iloc[i + time_steps])
    return np.array(Xs), np.array(ys)

VentanaTiempo = 64

# reshape to [samples, time_steps, n_features]

X_train, y_train = create_dataset(train[['Close']], train.Close, VentanaTiempo)
X_test, y_test = create_dataset(test[['Close']], test.Close, VentanaTiempo)

#X_t=X_train.reshape(851,30)
print(X_train.shape)
print(X_test.shape)

model = keras.Sequential()
model.add(keras.layers.LSTM(
    units=32, 
    input_shape=(X_train.shape[1], X_train.shape[2]), return_sequences=False))
model.add(keras.layers.Dropout(rate=0.2))
model.add(keras.layers.RepeatVector(n=X_train.shape[1]))
model.add(keras.layers.LSTM(units=64, return_sequences=True)) 
model.add(keras.layers.Dropout(rate=0.2))
model.add(keras.layers.TimeDistributed(keras.layers.Dense(1)))
model.compile(loss='mae', optimizer='adam')

model.summary()

history = model.fit(
    X_train, y_train,
    epochs=50,
    batch_size=16,
    validation_split=0.1,
    shuffle=False
)

plt.plot(history.history['loss'], label='train')
plt.plot(history.history['val_loss'], label='test')
plt.legend();

X_train_pred = model.predict(X_train)

train_mae_loss = np.mean(np.abs(X_train_pred - X_train), axis=1)

sns.distplot(train_mae_loss, bins=50, kde=True);

X_test_pred = model.predict(X_test)

test_mae_loss = np.mean(np.abs(X_test_pred - X_test), axis=1)

TIME_STEPS

print(test)

THRESHOLD = 1
test_score_df=[]
test_score_df = pd.DataFrame(index=test[VentanaTiempo:].index)
test_score_df['loss'] = test_mae_loss
test_score_df['threshold'] = THRESHOLD
test_score_df['anomaly'] = test_score_df.loss > test_score_df.threshold
test_score_df['Close'] = test[VentanaTiempo:].Close

plt.plot(test_score_df.index, test_score_df.loss, label='loss')
plt.plot(test_score_df.index, test_score_df.threshold, label='threshold')
plt.xticks(rotation=25)
plt.legend();

anomalies = test_score_df[test_score_df.anomaly == True]
anomalies

plt.plot(
  test[VentanaTiempo:].index,
  escala.inverse_transform(test[['Close']][VentanaTiempo:]), 
  label='Close price'
);

sns.scatterplot(
  anomalies.index,
  escala.inverse_transform(anomalies[['Close']]).ravel(),
  color=sns.color_palette()[3],
  s=52,
  label='anomaly'
)
plt.xticks(rotation=25)
plt.legend();