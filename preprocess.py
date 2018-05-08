import scipy.io as sio
import numpy as np
import pickle
from scipy.sparse import hstack, vstack, coo_matrix, csr_matrix

def load_data(path):
    data = sio.loadmat(path)
    if path == "LandmineData.mat":
        X = data["feature"]
        Y = data["label"]
    elif path == "emails.mat":
        X = data["X"]
        Y = data["Y"]
    return [X, Y]

def preprocess_landmine(X, Y):
    """
    X_train: first column is tid, followed by features
    Y_train: labels
    """
    print("landmine")
    n_train = 160 # number of samples per task
    k = X.shape[1] # number of tasks
    dim = X[0][0].shape[1]
    X_train = np.array([]).reshape(0, dim + 1)
    Y_train = np.array([]).reshape(0, 1)
    X_test = np.array([]).reshape(0, dim + 1)
    Y_test = np.array([]).reshape(0, 1)
    
    for n in range(k):
        n_samples = X[0][n].shape[0]
        mask_tmp = np.random.permutation(n_samples)
        mask_train = mask_tmp[:n_train]
        mask_test = mask_tmp[n_train:]

        tmp = np.zeros((n_train, 1))
        tmp.fill(n)
        X_tmp = np.concatenate((tmp, X[0][n][mask_train]), axis=1)
        X_train = np.concatenate((X_train, X_tmp), axis=0)
        Y_train = np.concatenate((Y_train, Y[0][n][mask_train]))

        tmp = np.zeros((n_samples - n_train, 1))
        tmp.fill(n)
        X_tmp = np.concatenate((tmp, X[0][n][mask_test]), axis=1)
        X_test = np.concatenate((X_test, X_tmp), axis=0)
        Y_test = np.concatenate((Y_test, Y[0][n][mask_test]))
    
    #shuffle data
    shuffle = np.random.permutation(X_train.shape[0])
    X_train = X_train[shuffle]
    Y_train = Y_train[shuffle]
    return [X_train, Y_train, X_test, Y_test, k, dim + 1]

def preprocess_landmine_unbalanced(X, Y):
    """
    X_train: first column is tid, followed by features
    Y_train: labels
    """
    print("landmine")
    k = X.shape[1] # number of tasks
    dim = X[0][0].shape[1]
    X_train = np.array([]).reshape(0, dim + 1)
    Y_train = np.array([]).reshape(0, 1)
    
    for n in range(k):
        if n < k/2:
            n_train = 400
        else:
            n_train = 20
        n_samples = X[0][n].shape[0]
        mask = np.random.permutation(n_samples)[:n_train]
        tmp = np.zeros((n_train, 1))
        tmp.fill(n)
        X_tmp = np.concatenate((tmp, X[0][n][mask]), axis=1)
        X_train = np.concatenate((X_train, X_tmp), axis=0)
        Y_train = np.concatenate((Y_train, Y[0][n][mask]))
    
    #shuffle data
    shuffle = np.random.permutation(X_train.shape[0])
    X_train = X_train[shuffle]
    Y_train = Y_train[shuffle]
    return [X_train, Y_train, k, dim + 1]

def preprocess_landmine_coldstart(X, Y):
    """
    X_train: first column is tid, followed by features
    Y_train: labels
    """
    print("landmine coldstart")
    n_train = 160 # number of samples per task
    k = X.shape[1] # number of tasks
    dim = X[0][0].shape[1]
    X_train_warm = np.array([]).reshape(0, dim + 1)
    Y_train_warm = np.array([]).reshape(0, 1)
    X_train_cold = np.array([]).reshape(0, dim + 1)
    Y_train_cold = np.array([]).reshape(0, 1)
    X_test = np.array([]).reshape(0, dim + 1)
    Y_test = np.array([]).reshape(0, 1)
    
    for n in range(k):
        n_samples = X[0][n].shape[0]
        mask_tmp = np.random.permutation(n_samples)
        mask_train = mask_tmp[:n_train]
        mask_test = mask_tmp[n_train:]

        tmp = np.zeros((n_train, 1))
        tmp.fill(n)
        X_tmp = np.concatenate((tmp, X[0][n][mask_train]), axis=1)
        p = np.random.binomial(1, 0.5)
        if n < 0.8 * k and p:
            X_train_warm = np.concatenate((X_train_warm, X_tmp), axis=0)
            Y_train_warm = np.concatenate((Y_train_warm, Y[0][n][mask_train]))
        else:
            X_train_cold = np.concatenate((X_train_cold, X_tmp), axis=0)
            Y_train_cold = np.concatenate((Y_train_cold, Y[0][n][mask_train]))
        
        tmp = np.zeros((n_samples - n_train, 1))
        tmp.fill(n)
        X_tmp = np.concatenate((tmp, X[0][n][mask_test]), axis=1)
        X_test = np.concatenate((X_test, X_tmp), axis=0)
        Y_test = np.concatenate((Y_test, Y[0][n][mask_test]))
    
    #shuffle data
    shuffle = np.random.permutation(X_train_warm.shape[0])
    X_train_warm = X_train_warm[shuffle]
    Y_train_warm = Y_train_warm[shuffle]
    shuffle = np.random.permutation(X_train_cold.shape[0])
    X_train_cold = X_train_cold[shuffle]
    Y_train_cold = Y_train_cold[shuffle]
    return [np.concatenate((X_train_warm, X_train_cold), axis=0),
            np.concatenate((Y_train_warm, Y_train_cold), axis=0),
            X_test, Y_test, k, dim + 1]

def preprocess_emails(X, Y):
    """
    X_train: first column is tid, followed by features
    Y_train: labels
    """
    print("emails")
    n_train = 100 # number of samples per task
    k = X.shape[1] # number of tasks
    dim = X[0][0].shape[1]
    X_train = np.array([]).reshape(0, dim + 1)
    Y_train = np.array([]).reshape(0, 1)
    X_test = np.array([]).reshape(0, dim + 1)
    Y_test = np.array([]).reshape(0, 1)
    
    for n in range(k):
        n_samples = X[0][n].shape[0]
        mask_tmp = np.random.permutation(n_samples)
        mask_train = mask_tmp[:n_train]
        mask_test = mask_tmp[n_train:]
        
        tmp = np.zeros((n_train, 1))
        tmp.fill(n)
        X_tmp = hstack([coo_matrix(tmp), X[0][n][mask_train]])
        X_train = vstack([X_train, X_tmp])
        Y_train = np.concatenate((Y_train, Y[0][n][mask_train]))

        tmp = np.zeros((n_samples - n_train, 1))
        tmp.fill(n)
        X_tmp = hstack([coo_matrix(tmp), X[0][n][mask_test]])
        X_test = vstack([X_test, X_tmp])
        Y_test = np.concatenate((Y_test, Y[0][n][mask_test]))
    
    #shuffle data
    shuffle = np.random.permutation(X_train.shape[0])
    X_train = coo_matrix(X_train.todense()[shuffle])
    Y_train = Y_train[shuffle]
    return [X_train, Y_train, X_test, Y_test, k, dim + 1]

def preprocess_music(X, Y):
    print("music")
    n_train = 200 # number of samples per task
    n_test = 10
    k = len(X)
    dim = X[0][0].shape[1]

    X_train = np.array([]).reshape(0, dim + 1)
    Y_train = np.array([]).reshape(0, 1)
    X_test = np.array([]).reshape(0, dim + 1)
    Y_test = np.array([]).reshape(0, 1)
    
    for n in range(k):
        n_samples = X[n].shape[0]
        Y_tmp = Y[n].todense().reshape(n_samples, 1)
        mask_tmp = np.random.permutation(n_samples)
        mask_train = mask_tmp[:n_train]
        mask_test = mask_tmp[n_train:n_train + n_test]
        
        tmp = np.zeros((n_train, 1))
        tmp.fill(n)
        X_tmp = hstack([csr_matrix(tmp), X[n][mask_train]])
        X_train = vstack([X_train, X_tmp])
        Y_train = np.concatenate((Y_train, Y_tmp[mask_train]))

        tmp = np.zeros((n_test, 1))
        tmp.fill(n)
        X_tmp = hstack([csr_matrix(tmp), X[n][mask_test]])
        X_test = vstack([X_test, X_tmp])
        Y_test = np.concatenate((Y_test, Y_tmp[mask_test]))
    
    return [X_train, Y_train, X_test, Y_test, k, dim + 1]

if __name__ == "__main__":
    # [X, Y] = load_data("LandmineData.mat")
    # [X_train, Y_train, X_test, Y_test, k, fea] = preprocess_landmine(X, Y)
    # with open("landmine.p", "wb") as f:
    #     pickle.dump([X_train, Y_train, X_test, Y_test, k, fea], f)

    # [X, Y] = load_data("LandmineData.mat")
    # [X, Y, k, fea] = preprocess_landmine_unbalanced(X, Y)
    # with open("landmine_unbalanced.p", "wb") as f:
    #     pickle.dump([X, Y, k, fea], f)

    # [X, Y] = load_data("LandmineData.mat")
    # [X_train, Y_train, X_test, Y_test, k, fea] = preprocess_landmine_coldstart(X, Y)
    # with open("landmine_coldstart.p", "wb") as f:
    #     pickle.dump([X_train, Y_train, X_test, Y_test, k, fea], f)

    # [X, Y] = load_data("emails.mat")
    # [X_train, Y_train, X_test, Y_test, k, fea] = preprocess_emails(X, Y)
    # with open("emails.p", "wb") as f:
    #     pickle.dump([X_train, Y_train, X_test, Y_test, k, fea], f)

    with open("data.data", "rb") as f:
        X = pickle.load(f)
    with open("gt.data", "rb") as f:
        Y = pickle.load(f)
    [X_train, Y_train, X_test, Y_test, k, fea] = preprocess_music(X, Y)
    with open("music.p", "wb") as f:
        pickle.dump([X_train, Y_train, X_test, Y_test, k, fea], f)

    print("X.shape", X_train.shape)
    print("Y.shape", Y_train.shape)
    print(k, fea)
