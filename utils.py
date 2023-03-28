import logging, sys, argparse


def str2bool(v):
    # copy from StackOverflow
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_entity(tag_seq, char_seq):
    DATA = get_DATA_entity(tag_seq, char_seq)
    AREA = get_AREA_entity(tag_seq, char_seq)
    CONTENT = get_CONTENT_entity(tag_seq, char_seq)
    METHOD = get_METHOD_entity(tag_seq, char_seq)

    return DATA, AREA, CONTENT, METHOD


def get_DATA_entity(tag_seq, char_seq):
    length = len(char_seq)
    DATA = []
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-DATA':
            if 'data' in locals().keys():
                DATA.append(data)
                del data
            data = char
            if i+1 == length:
                DATA.append(data)
        if tag == 'I-DATA':
            data += char
            if i+1 == length:
                DATA.append(data)
        if tag not in ['I-DATA', 'B-DATA']:
            if 'data' in locals().keys():
                DATA.append(data)
                del data
            continue
    return DATA


def get_AREA_entity(tag_seq, char_seq):
    length = len(char_seq)
    AREA = []
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-AREA':
            if 'area' in locals().keys():
                AREA.append(area)
                del area
            area = char
            if i+1 == length:
                AREA.append(area)
        if tag == 'I-AREA':
            area += char
            if i+1 == length:
                AREA.append(area)
        if tag not in ['I-AREA', 'B-AREA']:
            if 'area' in locals().keys():
                AREA.append(area)
                del area
            continue
    return AREA


def get_CONTENT_entity(tag_seq, char_seq):
    length = len(char_seq)
    CONTENT = []
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-CONTENT':
            if 'content' in locals().keys():
                CONTENT.append(content)
                del content
            content = char
            if i+1 == length:
                CONTENT.append(content)
        if tag == 'I-CONTENT':
            content += char
            if i+1 == length:
                CONTENT.append(content)
        if tag not in ['I-CONTENT', 'B-CONTENT']:
            if 'content' in locals().keys():
                CONTENT.append(content)
                del content
            continue
    return CONTENT


def get_METHOD_entity(tag_seq, char_seq):
    length = len(char_seq)
    METHOD = []
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-METHOD':
            if 'method' in locals().keys():
                METHOD.append(method)
                del method
            method = char
            if i+1 == length:
                METHOD.append(method)
        if tag == 'I-METHOD':
            method += char
            if i+1 == length:
                METHOD.append(method)
        if tag not in ['I-METHOD', 'B-METHOD']:
            if 'method' in locals().keys():
                METHOD.append(method)
                del method
            continue
    return METHOD


def get_logger(filename):
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    handler = logging.FileHandler(filename)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
    logging.getLogger().addHandler(handler)
    return logger
