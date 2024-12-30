import os
import pandas as pd
import re

import tld
import math
import numpy as np
import pickle
import string
from collections import defaultdict, Counter

# dgaTLD_list = ["cf", "recipes", "email", "ml", "gq", "fit", "cn", "ga", "rest", "tk"]
hmm_add = r"./static/hmm_matrix.csv"
gib_add = r"./static/gib_model.pki"
gramfile_add = r"./static/n_gram_rank_freq.txt"
private_tld_file = r"./static/private_tld.txt"
hmm_prob_threshold = -120



accepted_chars = 'abcdefghijklmnopqrstuvwxyz '
pos = dict([(char, idx) for idx, char in enumerate(accepted_chars)])
def get_name(url):
    """
    用python自带库进行域名提取
    :param url: url
    :return: 二级域名，顶级域名
    """
    url = url.strip(string.punctuation)
    try:
        TLD = tld.get_tld(url, as_object=True, fix_protocol=True)
        SLD = tld.get_tld(url, as_object=True, fix_protocol=True).domain

    except Exception as e:
        na_list = url.split(".")
        TLD = na_list[-1]
        SLD = na_list[-2]
    return str(TLD), str(SLD)

def load_gramdict_privatetld():
    """
    加载n元排序字典
    :return: 字典
    """
    rank_dict = dict()
    with open(gramfile_add, 'r') as f:
        for line in f:
            cat, gram, freq, rank = line.strip().split(',')
            rank_dict[gram] = int(rank)
    pritld_list = list()
    with open(private_tld_file, 'r') as f:
        pritld_list = set(line.strip() for line in f)
    return rank_dict, pritld_list

def cal_ent_gni_cer(SLD):
    """
    计算香农熵, Gini值, 字符错误的分类
    :param url:
    :return:
    """
    f_len = float(len(SLD))
    count = Counter(i for i in SLD).most_common()  # unigram frequency
    ent = -sum(float(j / f_len) * (math.log(float(j / f_len), 2)) for i, j in count)  # shannon entropy
    gni = 1 - sum(float(j / f_len) * float(j / f_len) for i, j in count)
    cer = 1 - max(float(j/ f_len) for i, j in count)
    return ent, gni, cer


def cal_rep_letter(SLD):
    """
    计算字符串中重复出现的字母个数
    :param SLD: 字符串
    :return: 重复字母个数
    """
    count = Counter(i for i in SLD if i.isalpha()).most_common()
    sum_n = 0
    for letter, cnt in count:
        if cnt > 1:
            sum_n += 1
    return sum_n
def cal_gib(SLD):
    """
    计算gib标签
    :param SLD:
    :return: 1: 正常 0: 异常
    """
    gib_model = pickle.load(open(gib_add, 'rb'))
    mat = gib_model['mat']
    threshold = gib_model['thresh']

    log_prob = 0.0
    transition_ct = 0
    SLD = re.sub("[^a-z]", "", SLD)
    gram2 = [SLD[i:i + 2] for i in range(len(SLD) - 1)]
    for a, b in gram2:
        log_prob += mat[pos[a]][pos[b]]
        transition_ct += 1
    # The exponentiation translates from log probs to probs.
    prob = math.exp(log_prob / (transition_ct or 1))
    return int(prob > threshold)

def cal_hmm_prob(url):
    """
    计算成文概率, 结果越小越异常
    :param url:
    :return: 概率
    """
    hmm_dic = defaultdict(lambda: defaultdict(float))
    with open(hmm_add, 'r') as f:
        for line in f.readlines():
            key1, key2, value = line.rstrip().split('\t')  # key1 can be '' so rstrip() only
            value = float(value)
            hmm_dic[key1][key2] = value
    url = '^' + url.strip('.') + '$'
    gram2 = [url[i:i+2] for i in range(len(url)-1)]
    prob = hmm_dic[''][gram2[0]]

    for i in range(len(gram2)-1):
        prob *= hmm_dic[gram2[i]][gram2[i+1]]
    if prob < math.e ** hmm_prob_threshold:
        prob = -999
    return prob

def SVM_get_feature(url):
    gram_rank_dict, private_tld = load_gramdict_privatetld()
    TLD, SLD = get_name(url)

    # 17. 是否包含私人域名#
    has_private_tld = 0
    for tld in private_tld:
        if tld in url:
            has_private_tld = 1
            name_list = tld.split('.')
            TLD = name_list[-1]
            SLD = name_list[-2]

    url = SLD + "." + TLD
    # 1. 香农熵#
    entropy = cal_ent_gni_cer(TLD)[0]
    # 2. SLD长度#
    f_len = float(len(SLD))
    # 3. 香农熵与SLD长度比#
    ent_flen = entropy / f_len
    # 4. SLD中元音占比#
    vowel_ratio = len(re.findall(r"a|e|i|o|u", SLD)) / f_len
    # 5. SLD中数字占比#
    digit_ratio = len(re.findall(r"[0-9]", SLD)) / f_len
    # 6. SLD中重复字母占比#
    repeat_letter = cal_rep_letter(SLD) / f_len
    # 7. SLD连续数字占比#
    dig_list = re.findall(r"[0-9]{2,}", url)
    dig_len = [len(dig) for dig in dig_list]
    consec_digit = sum(dig_len) / f_len
    # 8. SLD连续辅音占比#
    con_list = re.findall(r"[b|c|d|f|g|h|j|k|l|m|n|p|q|r|s|t|v|w|x|y|z]{2,}", url)
    con_len = [len(con) for con in con_list]
    consec_consonant = sum(con_len) / f_len
    # 9. gib成文检测#
    gib_value = cal_gib(SLD)
    # 10. hmm成文检测#
    hmm_log_prob = cal_hmm_prob(SLD)

    main_domain = '$' + SLD + '$'
    gram2 = [main_domain[i:i + 2] for i in range(len(main_domain) - 1)]
    gram3 = [main_domain[i:i + 3] for i in range(len(main_domain) - 2)]
    gram1_rank = [gram_rank_dict[i] if i in gram_rank_dict else 0 for i in main_domain[1:-1]]
    gram2_rank = [gram_rank_dict[''.join(i)] if ''.join(i) in gram_rank_dict else 0 for i in gram2]
    gram3_rank = [gram_rank_dict[''.join(i)] if ''.join(i) in gram_rank_dict else 0 for i in gram3]

    # 11. 一元排序均值#
    avg_gram1_rank = np.mean(gram1_rank)
    # 12. 二元排序均值#
    avg_gram2_rank = np.mean(gram2_rank)
    # 13. 三元排序均值#
    avg_gram3_rank = np.mean(gram3_rank)
    # 14. 一元排序标准差#
    std_gram1_rank = np.std(gram1_rank)
    # 15. 二元排序标准差#
    std_gram2_rank = np.std(gram2_rank)
    # 16. 三元排序标准差#
    std_gram3_rank = np.std(gram3_rank)

    feature = [entropy, f_len, ent_flen, vowel_ratio, digit_ratio, repeat_letter, consec_digit, consec_consonant,
               gib_value,hmm_log_prob, avg_gram1_rank, avg_gram2_rank, avg_gram3_rank, std_gram1_rank, std_gram2_rank,
               std_gram3_rank, has_private_tld]

    return feature


exclude = set(['__pycache__'])
f=[]
for root, dirs, filenames in os.walk(os.path.join(os.path.expanduser("~"), "%s" % "mytest".lower()), topdown=True):
    dirs[:] = [d for d in dirs if d not in exclude]
    print(filenames)
    print(root)
for filename in sorted(filenames):
    csv_data = pd.read_csv(root + '/' + filename, names=["addr", "type", "source"])
    csv_df = pd.DataFrame(csv_data)
    csv_df = csv_df["addr"]
    csv_df.drop_duplicates(inplace=True)
    print(csv_df.shape[0])
    csv_df.reset_index(drop=True, inplace=True)
    for i in range(csv_df.shape[0]):
        if re.match(r"\A\d+\.\d+\.\d+\.\d+", csv_df[i]):
            csv_df.drop(index=i, inplace=True)
            continue
        f=SVM_get_feature(csv_df[i])
        print(f)
    print(csv_df.shape[0])
