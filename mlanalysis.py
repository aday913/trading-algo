from sklearn.model_selection import cross_val_score, cross_val_predict, LeaveOneOut
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix
from sklearn.svm import SVC
from random import seed
import matplotlib.pyplot as plt
import numpy as np
import logging
import pandas
import csv
import os

class MLAnalysis(object):
    '''
    Basic class that will allow for all the analysis necessary
    Input parameters:
    filename: the .csv file name/path that the class will be analyzing
    LOO: boolean for whether the analysis should use LOOCV (default is no)
    '''

    def __init__(self, filename, LOO=False, classCol='Class', 
                    droppedCols=['Class', 'Image', 'Date'],
                    plot=False,
                    debug=False):
        if debug:
            logging.basicConfig(level=logging.DEBUG,
                                format='%(name)s: %(message)s')
        else:
            logging.basicConfig(level=logging.INFO,
                                format='%(name)s: %(message)s')
        np.random.seed(1234)
        self.plot = plot
        self.loo = LeaveOneOut()
        self.filename = filename
        self.LOO = LOO
        self.classCol = classCol
        self.droppedCols = droppedCols
        self.X, self.Y, self.numCols = self.formatData(self.filename)
        self.accuracy = 0.0
        self.bestType = None
        self.bestModel = None
        self.bestParams = None

    def getAccuracy(self):
        return self.accuracy
    
    def getModel(self):
        return self.bestModel

    def formatData(self, filename):
        '''
        Given a .csv file, the function parses the file into input data (x)
        and class data (y)
        '''
        dataset = pandas.read_csv(filename, header=0)
        dataFrame = pandas.DataFrame(dataset)

        y = dataFrame[self.classCol]
        x = dataFrame.drop(columns=self.droppedCols)
        numCols = list(x.columns)
        numCols = len(numCols)
        x = x.values
        return x, y, numCols
    
    def runRF(self):
        '''
        The main method for random forest machine learning analysis
        '''
        x = self.X
        y = self.Y
        params = self.optimizeRF(x, y, maxF=self.numCols)
        bestModel = RandomForestClassifier(
            n_estimators=params[1], max_features=params[2])
        bestScalerType = params[-1]
        if bestScalerType == 'StandardScaler':
            bestX = StandardScaler().fit(x).transform(x)
        elif bestScalerType == 'MinMaxScaler':
            bestX = MinMaxScaler().fit(x).transform(x)
        else:
            bestX = x
        
        if self.plot:
            if self.LOO:
                prediction = cross_val_predict(bestModel, bestX, y, cv=self.loo)
            else:
                prediction = cross_val_predict(bestModel, bestX, y, cv=3)
            confusion = confusion_matrix(y, prediction)

            self.plot_confusion_matrix(confusion, 
            title='RF, {}, {:2f}'.format(self.filename, params[0]))
        
        if params[0] > self.accuracy:
            self.accuracy = params[0]
            self.bestType = 'Random Forest'
            self.bestParams = params
            self.bestModel = bestModel
    
    def runSVM(self):
        '''
        The main method for random forest machine learning analysis
        '''
        x = self.X
        y = self.Y
        params = self.optimizeSVM(x, y, maxF=self.numCols)
        bestModel = SVC(kernel=params[1], gamma=params[2], C=params[3])
        bestScalerType = params[-1]
        if bestScalerType == 'StandardScaler':
            bestX = StandardScaler().fit(x).transform(x)
        elif bestScalerType == 'MinMaxScaler':
            bestX = MinMaxScaler().fit(x).transform(x)
        else:
            bestX = x
        
        if self.plot:
            if self.LOO:
                prediction = cross_val_predict(bestModel, bestX, y, cv=self.loo)
            else:
                prediction = cross_val_predict(bestModel, bestX, y, cv=3)
            confusion = confusion_matrix(y, prediction)

            self.plot_confusion_matrix(confusion, 
            title='RF, {}, {:2f}'.format(self.filename, params[0]))
        
        self.accuracy = params[0]

    def plot_confusion_matrix(self, cm, title='Confusion matrix', 
                            cmap=plt.cm.Blues):
        '''
        Given an input confusion matrix, the function will plot the confusion 
        matrix using a colormap visualization
        '''
        plt.figure()
        plt.imshow(cm, interpolation='nearest', cmap=cmap)
        plt.title(title)
        plt.colorbar()
        plt.tight_layout()
        plt.ylabel('True label')
        plt.xlabel('Predicted label')
        fileName = title + '.png'
        plt.show()

    def createSVM(self, kernel, gamma, C):
        '''
        Given a kernel type, gamme value, and c value, the function will return
        a SVM model that can be called elsewhere in the script
        '''

        if kernel not in ['linear', 'rbf', 'poly']:
            # We just need to check that the kernel type is acceptable
            print('Kernel type not allowed, must be linear, rbf, or poly')
            return None
        logging.debug(' Creating SVM model: {} kernel, {} gamma, {} C'.format(
                                                                kernel, 
                                                                gamma, 
                                                                C))
        model = SVC(kernel=kernel, gamma=gamma, C=C)
        return model

    def optimizeSVM(self, X, Y, kernels=['rbf', 'linear']):
        '''
        Given X and y data, the function will optimize the kernel type, gamma
        value, and c value best suited to maximizing the model accuracy
        Returns [bestScore, bestKernel, bestG, bestC, bestScaler]
        '''

        sscaler = StandardScaler()
        mscaler = MinMaxScaler()

        sscaler.fit(X)
        mscaler.fit(X)

        sx = sscaler.transform(X)
        mx = mscaler.transform(X)

        dependents = [sx, mx]
        dependentNames = ['StandardScaler', 'MinMaxScaler']

        logging.debug('Tyring to optimize SVM model...')

        bestkernel = None
        bestG = None
        bestC = None
        bestI = None
        bestScore = 0.00

        # We use multiple for loops to iterate over different values for 
        # the SVM parameters in order to optimize them
        for i in range(0, 2):
            for kernel in kernels:
                for c in [.001, .01, .1, 1, 10, 100]:
                    for gamma in [.001, .01, .1, 1, 10, 100]:
                        model = createSVM(kernel, gamma, c)
                        x = dependents[i]
                        # score = cross_val_score(model, x, Y, cv=3).mean()
                        score = cross_val_score(model, x, Y, cv=self.loo).mean()
                        if score > bestScore:
                            bestkernel = kernel
                            bestG = gamma
                            bestC = c
                            bestI = i
                            bestScore = score

        logging.debug('Best score: {}'.format(bestScore))
        logging.debug('Best gamma: {}'.format(bestG))
        logging.debug('Best C: {}'.format(bestC))
        logging.debug('Best Scaler: {}'.format(dependentNames[bestI]))
        logging.debug('Best Kernel Type: {}'.format(bestkernel))
        
        # Return a list containing the top accuracy and the optimized params:
        return [bestScore, bestkernel, bestG, bestC, dependentNames[bestI]]

    def createKNN(self, K, weight):
        '''
        Given a K-neighbor value, the function will return
        a KNN model that can be called elsewhere in the script
        '''
        logging.debug(' Creating a KNN model: {} neighbors and {} weight'.format(
                                                                    K, weight))
        model = KNeighborsClassifier(n_neighbors=K, weights=weight)
        return model

    def optimizeKNN(self, X, Y, maxK=10):
        '''
        Given X and y data, the function will optimize the K-neighbor and 
        weight best suited to maximizing the KNN model accuracy
        Returns [bestScore, bestK, bestWeight, bestScaler]
        '''

        logging.debug('Trying to optimize KNN model...')

        sscaler = StandardScaler()
        mscaler = MinMaxScaler()

        sscaler.fit(X)
        mscaler.fit(X)

        sx = sscaler.transform(X)
        mx = mscaler.transform(X)

        dependents = [X, sx, mx]
        dependentNames = ['None', 'StandardScaler', 'MinMaxScaler']

        # For this model, we just need to use 2 for loops to optimize the 
        # number of neighbors and weight type 
        
        # We set up variables that will be optimized:
        bestK = None
        bestWeight = None
        bestI = None
        bestScore = 0.0

        # Our outer loop will optimize K value, while the inner one will
        # optimize weight type
        for i in range(0, 3):
            for n in range(1, maxK):
                for weight in ['uniform', 'distance']:
                    model = createKNN(n, weight)
                    x = dependents[i]
                    # score = cross_val_score(model, x, Y, cv=3).mean()
                    score = cross_val_score(model, x, Y, cv=self.loo).mean()
                    if score > bestScore:
                        bestK = n
                        bestWeight = weight
                        bestI = i
                        bestScore = score
        
        logging.debug('Best score: {}'.format(bestScore))
        logging.debug('Best K: {}'.format(bestK))
        logging.debug('Best Scaler: {}'.format(dependentNames[bestI]))
        logging.debug('Best Weight Type: {}'.format(bestWeight))
        
        # Return a list containing the top accuracy and the optimized params:
        return [bestScore, bestK, bestWeight, dependentNames[bestI]]

    def createRF(self, n_estimators, max_features):
        '''
        Given a n_estimators value, the function will return
        a Random forest model that can be called elsewhere in the script
        '''
        logging.debug(' Creating RF model: {} n_est, {} max_feat'.format(
                                                    n_estimators, 
                                                    max_features))
        model = RandomForestClassifier(
            n_estimators=n_estimators, max_features=max_features)
        return model

    def optimizeRF(self, X, Y, maxN=10, maxF=30):
        '''
        Given X and y data, the function will optimize the n_estimator and 
        max_feature best suited to maximizing the RF model accuracy
        Returns [bestScore, bestN, bestMF, bestScaler]
        '''
        logging.debug('Trying to optimize RF model...')

        sscaler = StandardScaler()
        mscaler = MinMaxScaler()

        sscaler.fit(X)
        mscaler.fit(X)

        sx = sscaler.transform(X)
        mx = mscaler.transform(X)

        dependents = [X, sx, mx]
        dependentNames = ['None', 'StandardScaler', 'MinMaxScaler']

        # For this model, we just need to use 2 for loops to optimize the 
        # number of neighbors and weight type 
        
        # We set up variables that will be optimized:
        bestN = None
        bestMF = None
        bestI = None
        bestScore = 0.0

        # Our outer loop will optimize K value, while the inner one will
        # optimize weight type
        for i in range(0, 3):
            for n in range(1, maxN):
                for mf in range(1, maxF):
                    model = self.createRF(n, mf)
                    x = dependents[i]
                    if self.LOO:
                        score = cross_val_score(model, x, Y, cv=self.loo).mean()
                    else:
                        score = cross_val_score(model, x, Y, cv=3).mean()
                    if score > bestScore:
                        bestN = n
                        bestMF = mf
                        bestI = i
                        bestScore = score
        
        logging.debug('Best score: {}'.format(bestScore))
        logging.debug('Best N: {}'.format(bestN))
        logging.debug('Best Scaler: {}'.format(dependentNames[bestI]))
        logging.debug('Best MF: {}'.format(bestMF))
        
        # Return a list containing the top accuracy and the optimized params:
        return [bestScore, bestN, bestMF, dependentNames[bestI]]

    
        
if __name__ == '__main__':
    logging.info('Running NK-MachineLearning-Classification.py as main')


    # THIS FOR LOOP IS FOR OPTIMIZING MODELS FOR INDIVIDUAL DATASETS
    # for file in [r'DataFiles\2.21.21_BC.csv',
    #             r'DataFiles\2.21.21_BC_NoNTC.csv',]:

    #     analysis = MLAnalysis(file, LOO=True, debug=True)
    #     print(analysis.getAccuracy())