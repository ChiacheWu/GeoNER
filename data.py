import sys, pickle, os, random
import numpy as np
import re

## tags, BIO
# tag2label = {"O": 0,
#              "B-PER": 1, "I-PER": 2,
#              "B-LOC": 3, "I-LOC": 4,
#              "B-ORG": 5, "I-ORG": 6,
#              }


# 数据名称，研究区域，研究内容，研究方法
tag2label = {
    "O": 0,
    "B-DATA": 1, "I-DATA": 2,
    "B-AREA": 3, "I-AREA": 4,
    "B-CONTENT": 5, "I-CONTENT": 6,
    "B-METHOD": 7, "I-METHOD": 8,
}

ann2tag = {
    "area": "AREA",
    "contents": "CONTENT",
    "data": "DATA",
    "method": "METHOD",
}

split_char = '\t'


def ann2data(ann_path, file_name):
    data = ""
    with open(ann_path, 'r', encoding='utf-8') as f:
        ann_txt = f.read()

        word_ind = 0

        while word_ind < len(ann_txt):
            annotated_stk = []
            tag = []
            if ann_txt[word_ind] == '[' and (ann_txt[word_ind + 1] == '@' or '$'):
                # 记录标记词
                # 开始符：[ @
                # 结束符：* ]
                word_ind += 2  # 跳过 [ @

                # VC#.net程序语言#method
                while ann_txt[word_ind] != '*' and ann_txt[word_ind + 1] != ']':
                    annotated_stk.append(ann_txt[word_ind])
                    word_ind += 1

                while annotated_stk[-1] != '#':
                    tag.insert(0, annotated_stk[-1])
                    annotated_stk.pop()

                annotated_stk.pop()  # pop '#'
                tag = ''.join(tag)

                data += f"{annotated_stk[0]}\tB-{ann2tag[tag]}\n"
                for word in ''.join(annotated_stk[1:]):
                    data += f"{word}\tI-{ann2tag[tag]}\n"

                word_ind += 2   # 跳过 * ]

            else:
                if ann_txt[word_ind] == ('。' or '！' or '!'):
                    data += str(ann_txt[word_ind]) + f'{split_char}O\n'
                    data += '\n'  # read_corpus
                else:
                    data += str(ann_txt[word_ind]) + f'{split_char}O\n'
                word_ind += 1

        print(ann_path)

        ann_path_list = re.split("\\\|/", ann_path)

        save_dir = '\\'.join(ann_path_list[:-1])
        save_pth = os.path.join(save_dir, file_name)
        if not os.path.exists(save_dir):
            os.file(save_dir)
        print(save_pth)
        with open(save_pth, 'w', encoding='utf-8') as fw:
            fw.write(data)
        # print(data)


def read_corpus(corpus_path):
    """

    read corpus and return the list of samples
    :param corpus_path:
    :return: data
    """
    data = []
    with open(corpus_path, encoding='utf-8') as fr:
        lines = fr.readlines()
    sent_, tag_ = [], []
    for line in lines:
        if line != '\n':
            print(line)
            [char, label] = line.strip('\n').split(split_char)
            # [char, label] = line.split(split_char)
            sent_.append(char)
            tag_.append(label)
        elif len(sent_):
            data.append((sent_, tag_))
            sent_, tag_ = [], []

    return data


def vocab_build(vocab_path, corpus_path, min_count):
    """

    删除低频 word，为每个 word 编码 id
    :param vocab_path:
    :param corpus_path:
    :param min_count:
    :return:
    """
    data = read_corpus(corpus_path)
    word2id = {}
    for sent_, tag_ in data:
        for word in sent_:
            if word.isdigit():
                word = '<NUM>'
            elif ('\u0041' <= word <= '\u005a') or ('\u0061' <= word <= '\u007a'):
                word = '<ENG>'
            if word not in word2id:
                word2id[word] = [len(word2id) + 1, 1]
            else:
                word2id[word][1] += 1
    low_freq_words = []
    for word, [word_id, word_freq] in word2id.items():
        if word_freq < min_count and word != '<NUM>' and word != '<ENG>':
            low_freq_words.append(word)
    for word in low_freq_words:
        del word2id[word]

    new_id = 1
    for word in word2id.keys():
        word2id[word] = new_id
        new_id += 1
    word2id['<UNK>'] = new_id
    word2id['<PAD>'] = 0

    print(len(word2id))
    with open(vocab_path, 'wb') as fw:
        pickle.dump(word2id, fw)


def sentence2id(sent, word2id):
    """

    word_id => sentence id (list)
    :param sent:
    :param word2id:
    :return:
    """
    sentence_id = []
    for word in sent:
        if word.isdigit():
            word = '<NUM>'
        elif ('\u0041' <= word <= '\u005a') or ('\u0061' <= word <= '\u007a'):
            word = '<ENG>'
        if word not in word2id:
            word = '<UNK>'
        sentence_id.append(word2id[word])
    return sentence_id


def read_dictionary(vocab_path):
    """

    :param vocab_path:
    :return:
    """

    # vocab_build(vocab_path, corpus_path, min_count)
    # vocab_build(vocab_path, corpus_path, 5)
    vocab_path = os.path.join(vocab_path)
    with open(vocab_path, 'rb') as fr:
        word2id = pickle.load(fr)
    print('vocab_size:', len(word2id))
    return word2id


def random_embedding(vocab, embedding_dim):
    """

    word embedding
    :param vocab:
    :param embedding_dim:
    :return:
    """
    embedding_mat = np.random.uniform(-0.25, 0.25, (len(vocab), embedding_dim))
    embedding_mat = np.float32(embedding_mat)
    return embedding_mat


def pad_sequences(sequences, pad_mark=0):
    """

    对齐
    :param sequences:
    :param pad_mark:
    :return:
    """
    max_len = max(map(lambda x: len(x), sequences))
    seq_list, seq_len_list = [], []
    for seq in sequences:
        seq = list(seq)
        seq_ = seq[:max_len] + [pad_mark] * max(max_len - len(seq), 0)
        seq_list.append(seq_)
        seq_len_list.append(min(len(seq), max_len))
    return seq_list, seq_len_list


def batch_yield(data, batch_size, vocab, tag2label, shuffle=False):
    """

    :param data:
    :param batch_size:
    :param vocab:
    :param tag2label:
    :param shuffle:
    :return:
    """
    if shuffle:
        random.shuffle(data)

    seqs, labels = [], []
    for (sent_, tag_) in data:
        sent_ = sentence2id(sent_, vocab)
        label_ = [tag2label[tag] for tag in tag_]

        if len(seqs) == batch_size:
            yield seqs, labels
            seqs, labels = [], []

        seqs.append(sent_)
        labels.append(label_)

    if len(seqs) != 0:
        yield seqs, labels


if __name__ == "__main__":
    ann_path = "./ner_data/original/abstract2.txt.ann"
    ann2data(ann_path, "test_data")

