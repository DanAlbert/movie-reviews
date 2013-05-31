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


class ReviewList(list):
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
        self.probabilities = {'pos': {}, 'neg': {}}
        self.p_pos = 0
        self.p_neg = 0

    def train(self, training_data):
        for feature in training_data.feature_names:
            total = float(len(training_data.reviews))
            num_pos = 0
            num_pos_with_feat = 0
            num_neg_with_feat = 0
            num_pos_no_feat = 0
            num_neg_no_feat = 0
            num_feat_present = 0
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
                if feat_present:
                    num_feat_present += 1
                if review.label == 'pos':
                    num_pos += 1
                if review.label == 'pos':
                    if feat_present:
                        num_pos_with_feat += 1
                    else:
                        num_pos_no_feat += 1
                if review.label == 'neg':
                    if feat_present:
                        num_neg_with_feat += 1
                    else:
                        num_neg_no_feat += 1

            #p = float(num_pos_with_feat) / float(num_feat_present)

            #p = (float(num_pos_with_feat) + 1) / (float(num_feat_present) + 2)
            #self.probabilities['pos'][feature] = p
            #p = (float(num_neg_with_feat) + 1) / (float(num_feat_present) + 2)
            #self.probabilities['neg'][feature] = p

            num_neg = float(total - num_pos)
            #print 'total %d' % total
            #print 'num_pos %d' % num_pos
            #print 'num_pos_with_feat %d' % num_pos_with_feat
            #print 'num_feat_present %d' % num_feat_present
            #print 'num_neg %d' % num_neg
            #print 'num_pos_no_feat %d' % num_pos_no_feat
            #print 'num_neg_no_feat %d' % num_neg_no_feat

            p = {
                True: (float(num_pos_with_feat) + 1) / (float(num_pos) + 2),
                False: (float(num_pos_no_feat) + 1) / (float(num_pos) + 2),
            }
            self.probabilities['pos'][feature] = p
            p = {
                True: (float(num_neg_with_feat) + 1) / (float(num_neg) + 2),
                False: (float(num_neg_no_feat) + 1) / (float(num_neg) + 2),
            }
            self.probabilities['neg'][feature] = p

            self.p_pos = float(num_pos) / total
            self.p_neg = float(num_neg) / total

        #print 'probabilities:'
        #print self.probabilities

    def classify(self, review):
        pos_prod = 1.0
        neg_prod = 1.0
        for feature, value in review.features.items():
            if value:
                pos_prod *= self.probabilities['pos'][feature][True]
                neg_prod *= self.probabilities['neg'][feature][True]
            else:
                pos_prod *= self.probabilities['pos'][feature][False]
                neg_prod *= self.probabilities['neg'][feature][False]
        p_pos = self.p_pos * pos_prod
        p_neg = self.p_neg * neg_prod
        #print 'p_pos: %f p_neg: %f' % (p_pos, p_neg)
        if p_pos > p_neg:
            print 'pos'
        elif p_pos < p_neg:
            print 'neg'
        else:
            print 'unknown'


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

    for review in test_reviews.reviews:
        classifier.classify(review)


def usage():
    print 'usage: python classifier.py TRAINING_DATA_FILE TRAINING_LABEL_FILE',
    print 'TESTING_DATA_FILE TESTING_LABEL_FILE'


if __name__ == '__main__':
    main()
