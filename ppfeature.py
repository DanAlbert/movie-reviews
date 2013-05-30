def get_vocab():
    vocab = []
    with open('vocabulary.txt', 'r') as vocab_file:
        vocab = vocab_file.read().split('\n')

    return [word for word in vocab if word != '']


def main():
    vocab = get_vocab()
    with open('training.txt', 'w') as output_file:
        output_file.write('%s\n' % ','.join(vocab))
        with open('raw.train.txt', 'r') as training_file:
            for review in training_file:
                words = review.split(' ')
                features = []
                for word in vocab:
                    if word in words:
                        features.append('1')
                    else:
                        features.append('0')
                output_file.write('%s\n' % ','.join(features))


if __name__ == '__main__':
    main()
