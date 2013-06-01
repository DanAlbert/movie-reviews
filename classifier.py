import math
import sys


def get_feature_data(training_data_file):
    data = []
    with open(training_data_file, 'r') as data_file:
        lines = data_file.readlines()
        keys = [s.strip() for s in lines[0].split(',')]
        for line in lines[1:]:
            review_data = {}
            for idx, feature in enumerate(line.split(',')):
                review_data[keys[idx]] = bool(int(feature))
            data.append(review_data)
    return data


def get_label_data(label_data_file):
    with open(label_data_file, 'r') as data_file:
        return [s.strip() for s in data_file.readlines()]


class Review(object):
    def __init__(self, features, label):
        self.features = features
        self.label = label


class ReviewList(object):
    def __init__(self, features, labels):
        if len(features) != len(labels):
            raise RuntimeError('Feature and data length do not match')

        self.reviews = []
        for idx, label in enumerate(labels):
            self.reviews.append(Review(features[idx], label))

    @property
    def num_features(self):
        return len(self.reviews[0].features)

    @property
    def feature_names(self):
        return self.reviews[0].features.keys()


class Classifier(object):
    def __init__(self):
        self.probabilities = {True: {}, False: {}}
        self.p_pos = 0
        self.p_neg = 0

    def train(self, training_data):
        for feature in training_data.feature_names:
            total = float(len(training_data.reviews))

            num_pos = 0
            num_pos_with_feat = 0
            num_pos_no_feat = 0

            num_neg = 0
            num_neg_with_feat = 0
            num_neg_no_feat = 0

            """
            P(good | feat) = (P(feat | good) * P(good)) / P(feat)
            
            P(feat) = num_feat_present / total
            P(good) = num_good / total

            P(feat | good) = P(feat and good) / P(good)
            P(feat and good) = num_pos_with_feat / total
            P(feat | good) = (num_pos_with_feat / total) / (num_good / total)
            P(feat | good) = num_pos_with_feat / num_good

            P(good | feat) = (P(feat and good) / P(good) * P(good)) / P(feat)
            P(good | feat) = P(feat and good) / P(feat)
            P(good | feat) = (num_pos_with_feat / total) / (num_feat_present / total)
            P(good | feat) = num_pos_with_feat / num_feat_present
            """
            for review in training_data.reviews:
                feat_present = review.features[feature]
                if review.label == 'pos':
                    num_pos += 1
                    if feat_present:
                        num_pos_with_feat += 1
                    else:
                        num_pos_no_feat += 1
                elif review.label == 'neg':
                    num_neg += 1
                    if feat_present:
                        num_neg_with_feat += 1
                    else:
                        num_neg_no_feat += 1
                else:
                    raise RuntimeError('invalid label')

            #print 'total %d' % total
            #print 'num_pos %d' % num_pos
            #print 'num_pos_with_feat %d' % num_pos_with_feat
            #print 'num_feat_present %d' % num_feat_present
            #print 'num_neg %d' % num_neg
            #print 'num_pos_no_feat %d' % num_pos_no_feat
            #print 'num_neg_no_feat %d' % num_neg_no_feat

            self.probabilities[True][feature] = {
                True: (float(num_pos_with_feat) + 1) / (float(num_pos) + 2),
                False: (float(num_pos_no_feat) + 1) / (float(num_pos) + 2),
            }
            self.probabilities[False][feature] = {
                True: (float(num_neg_with_feat) + 1) / (float(num_neg) + 2),
                False: (float(num_neg_no_feat) + 1) / (float(num_neg) + 2),
            }

            self.p_pos = float(num_pos) / total
            self.p_neg = float(num_neg) / total

        #print 'probabilities:'
        #print self.probabilities[True]
        #print self.probabilities[False]

    def classify(self, review):
        pos_prod = math.log(1.0)
        neg_prod = math.log(1.0)
        for feature, value in review.features.items():
            pos_prod += math.log(self.probabilities[True][feature][value])
            neg_prod += math.log(self.probabilities[False][feature][value])
        #print math.log(self.p_pos), math.log(self.p_neg), pos_prod, neg_prod
        p_pos = math.log(self.p_pos) + pos_prod
        p_neg = math.log(self.p_neg) + neg_prod
        #print 'p_pos: %f p_neg: %f' % (p_pos, p_neg)
        if p_pos > p_neg:
            return 1
        elif p_pos < p_neg:
            return -1
        else:
            return 0


def classify_and_show(classifier, review_list):
    num_pos_correct = 0
    num_pos_predictions = 0
    num_neg_correct = 0
    num_neg_predictions = 0
    for idx, review in enumerate(review_list.reviews):
        result = classifier.classify(review)
        if result == 1:
            print 'pos'
        elif result == 0:
            print 'neutral'
        elif result == -1:
            print 'neg'
        else:
            raise LogicError('invalid classifier result')

        if review.label == 'pos':
            num_pos_predictions += 1
            if result == 1:
                num_pos_correct += 1
        elif review.label == 'neg':
            num_neg_predictions += 1
            if result == -1:
                num_neg_correct += 1
        else:
            raise RuntimeError('invalid label in results')

    print 'positive: %d%%' % (num_pos_correct * 100 / num_pos_predictions)
    print 'negative: %d%%' % (num_neg_correct * 100 / num_neg_predictions)


def main():
    if len(sys.argv) != 5:
        usage()
        sys.exit(-1)

    training_data_file = sys.argv[1]
    training_label_file = sys.argv[2]
    test_data_file = sys.argv[3]
    test_label_file = sys.argv[4]

    training_data = get_feature_data(training_data_file)
    training_labels = get_label_data(training_label_file)
    test_data = get_feature_data(test_data_file)
    test_labels = get_label_data(test_label_file)

    training_reviews = ReviewList(training_data, training_labels)
    test_reviews = ReviewList(test_data, test_labels)

    classifier = Classifier()
    classifier.train(training_reviews)

    print 'training data:'
    classify_and_show(classifier, training_reviews)
    print
    print 'test data:'
    classify_and_show(classifier, test_reviews)


def usage():
    print 'usage: python classifier.py TRAINING_DATA_FILE TRAINING_LABEL_FILE',
    print 'TESTING_DATA_FILE TESTING_LABEL_FILE'


if __name__ == '__main__':
    main()
