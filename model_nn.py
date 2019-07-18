from keras.models import Model
from keras.layers import Dense, Input, ReLU, Activation
from keras.optimizers import Adam

def sp500_estimate_nn(stockdata,Tk,epochs):
    # Load X and Y data
    Y = stockdata.dfr[Tk].dropna()
    X = stockdata.X['SPY']

    # Intersect X and Y
    intersect = Y.index.intersection(X.index)
    Y = Y[intersect].values
    X = X.loc[intersect].values

    # Parameterize neural network
    inp = Input((1,))
    xlayer = Dense(9, activation='relu')(inp)
    xlayer = Dense(25, activation='relu')(xlayer)
    xlayer = Dense(25, activation='relu')(xlayer)
    yout = Dense(1, activation='linear')(xlayer)

    # Estimate model
    model = Model(inp, yout)
    model.compile(loss='mse', optimizer=Adam(lr=0.001))
    model.fit(X,Y,epochs=epochs, verbose=1, batch_size=10000)

    return model

# import matplotlib.pyplot as plt
# #
# # from getstockdata import getstockdata
# # stockdata = getstockdata('data/sp500_6stocks.pkl')  #stockdata = getstockdata('data/sp500_505stocks.pkl')
# # Tk = 'BAC'
# #
# # y_nn = model.predict(x_grid)
# #
# # plt.scatter(X,Y,s=2)
# # plt.plot(x_grid,y_nn)
# # plt.show()
# #
# # import sys
# # sys.exit('done')