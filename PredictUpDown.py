from rank_predictor import Predictor as Predictor
from features import featureExtractor as FeatureExtractor
from statsApi import APIRequester as APIRequester

def main():
    # 1) Get Data from LOL API
    # TODO : import relevant modules and pull data as json format
    # TODO : change sample data to the real data
    #sampleAPIRequester = APIRequester(playersFile="samplePlayerData")
    inputPlayersFile = "platinum4,platinum5,gold3,gold4,gold5,diamond1,diamond2,diamond3,diamond4,diamond5,silver1,silver2,silver5"
    inputPlayersFile = "platinum5,gold3,diamond1,diamond2,diamond3,diamond4,diamond5,silver5"
    sampleAPIRequester = APIRequester(playersFiles=inputPlayersFile)
    sampleAPIRequester.writeToFiles()
    jsonData = sampleAPIRequester.readFromFile()

    X = [] #list of dictionaries
    Y = [] #list of values

    for data in jsonData:
        curRank = data.pop('curRank', None)
        prevRank = data['prevRank']
        sign = 0
        if curRank - prevRank > 0:
            sign = 1
        elif prevRank - curRank < 0:
            sign = -1
        if not curRank: #edge case where the json data is malformed
            pass
        X.append(data)
        Y.append(sign)

    #TODO: Make sure X[0] has all attrs as keys. Else, add a manual list of all feature names

    features = X[0].keys()


    # 2) Filter and add features
    f_extractor = FeatureExtractor(features)
    f_extractor.feedData(X, Y)

    f_extractor.removeSingleFeature('totalHeal')

    div_attrs = ['totalPhysicalDamageDealt', 'totalTurretsKilled', 'totalAssists', 'totalDamageDealt', 'killingSpree', 'totalPentaKills', 'totalDoubleKills', 'totalDeathsPerSession', 'totalSessionsWon', 'totalGoldEarned', 'totalTripleKills', 'totalNeutralMinionsKilled', 'totalChampionKills', 'totalMinionKills', 'totalMagicDamageDealt', 'totalQuadraKills', 'totalDamageTaken', 'totalFirstBlood']
    b = 'totalSessionsPlayed'
    def getAvg(a, b):
        return float(a)/b

    def getInverse(a):
        return 1/a

    unaryFeatures = [('totalDeathsPerSession', 'inverseDeath', getInverse)] #example : ('averagekills', 'newfeaturename', lambda a: math.pow(a, 2))

    binaryFeatures = [(attr, b, 'avg-'+attr, getAvg) for attr in div_attrs] #example : ('averagekills', 'averagedeaths', 'newname',lambda a, b : a*b)
    binaryFeatures.append(('avg-totalChampionKills', 'totalDeathsPerSession', 'kill-death-ratio', getAvg))
    featuresToRemove = ['rankedPremadeGamesPlayed', 'mostSpellsCast', 'maxLargestCriticalStrike', 'rankedSoloGamesPlayed', 'normalGamesPlayed', 'botGamesPlayed', 'totalUnrealKills'] # list of features to remove. Let's eyeball it
    featuresToRemove.extend(div_attrs)

    '''
    for (f_name, new_name, func) in unaryFeatures:
        f_extractor.addUnaryFeature(f_name, new_name, func)

    for (f1, f2, new_name, func) in binaryFeatures:
        f_extractor.addCrossFeature(f1, f2, new_name, func)

    f_extractor.removeFeatures(featuresToRemove)
    '''

    # 3) Cross Validate : 9 to 1
    f_extractor.divideData(10) # divide into 10 chunks

    totalError1, totalError3 = 0.0, 0.0
    for i in range(0, 10):
        train, test = f_extractor.getTrainTestData([i])
        train_X, train_Y = f_extractor.separateXY(train)
        test_X, test_Y = f_extractor.separateXY(test)

        predictor1 = Predictor(train_X, train_Y)
        predictor1.setLearner('svm', 'ovo', None) # only support svm for now
        predictor1.learn()
        #predictor2 = Predictor(train_X, train_Y)
        #predictor2.setLearner('svm', 'ovr', None) # only support svm for now
        #predictor2.learn()
        predictor3 = Predictor(train_X, train_Y)
        predictor3.setLearner('ada', 'ovo', 'log')
        predictor3.learn()

        print "SVM > Error Rate: " + str(predictor1.predictAndGetError(test_X, test_Y)) + " / " + str(predictor1.score(test_X, test_Y))
        totalError1 += float(predictor1.predictAndGetError(test_X, test_Y))
        #print predictor2.predictAndGetError(test_X, test_Y)
        print "Boosting > Error Rate: " + str(predictor3.predictAndGetError(test_X, test_Y)) + " / " + str(predictor3.score(test_X, test_Y))
        totalError3 += float(predictor3.predictAndGetError(test_X, test_Y))

    print "Average Error for SVM > {}".format(str(totalError1/float(10)))
    print "Average Error for Boosting > {}".format(str(totalError3/float(10)))

if __name__ == "__main__":
    main()
