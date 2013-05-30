def get_stop_words():
    stop_words = []
    with open('stoplist.txt', 'r') as stop_list:
        for line in stop_list:
            word = line.strip()
            stop_words.append(word)

    return stop_words


def get_uncommon_words():
    all_words = {}
    with open('raw.train.txt', 'r') as training_data:
        all_data = training_data.read()
        for word in all_data.split(' '):
            if word in all_words:
                all_words[word] += 1
            else:
                all_words[word] = 1

    with open('raw.test.txt', 'r') as training_data:
        all_data = training_data.read()
        for word in all_data.split(' '):
            if word in all_words:
                all_words[word] += 1
            else:
                all_words[word] = 1

    uncommon_words = []
    for word, count in all_words.items():
        if count <= 3:
            uncommon_words.append(word)

    return uncommon_words


def main():
    stop_words = get_stop_words()
    uncommon_words = get_uncommon_words()
    clean_words = stop_words
    clean_words.extend(uncommon_words)

    with open('vocabulary.txt', 'w') as output_file:
        with open('raw.vocabulary.txt', 'r') as raw_vocab_file:
            for line in raw_vocab_file:
                word = line.strip()
                if word not in clean_words:
                    output_file.write(line)


if __name__ == '__main__':
    main()
