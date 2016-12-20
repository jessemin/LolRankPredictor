from sklearn.svm import SVC
from sklearn.svm import SVR
from sklearn.ensemble import AdaBoostClassifier

"""
Class : Predictor
==============================================================================
Train
Predict given x values that are array of array of vectors
"""
class Predictor(object):

    # initialize the MMR Predictor
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y
        self.classifier = None
        self.learner_name = None

    def setLearner(self, learner_name, m_c_strategy, loss):
        if learner_name == 'svm':
            self.learner = SVC(decision_function_shape=m_c_strategy)
        elif learner_name == 'ada':
            self.learner = AdaBoostClassifier(n_estimators=57)
            self.learner.classes = [i for i in range(1, 26)]
            self.learner.n_classes = 25
        elif learner_name == 'svr':
            self.learner = SVR()

        self.learner_name = learner_name

    def learn(self):
        self.learner.fit(self.X, self.Y)

    def predict(self, testX):
        return self.learner.predict(testX)

    def score(self, testX, trueY):
        return self.learner.score(testX, trueY)

    def predictAndGetError(self, testX, trueY):
        pred_y = self.predict(testX)

        if self.learner_name == 'svr':
            pred_y = [max(min(int(round(y)), 25), 1) for y in pred_y]
        count = 0
        total_count = len(testX)

        for i in range(0, total_count):
            if pred_y[i] != trueY[i]:
                count += 1
        return float(count) / total_count
