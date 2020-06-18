from sklearn.feature_extraction.text import CountVectorizer  
from sklearn.feature_extraction.text import TfidfTransformer  
import jieba
import numpy as np
import ipdb

# 每个文件取的关键词个数
__count = 10

def tf_idf(data_lib):
  # 先分词
  for i in range(len(data_lib)):
    data_lib[i] = " ".join(jieba.cut_for_search(data_lib[i]))

  # 计算tf-idf值
  vectorizer = CountVectorizer()
  X = vectorizer.fit_transform(data_lib)
  word = vectorizer.get_feature_names()
  transformer = TfidfTransformer()  
  tfidf = transformer.fit_transform(X)

  # 对tf-idf作处理，每个文件只取一部分，然后合成关键词表
  matrix = tfidf.A
  np_word = np.array(word)
  score_list = []
  for vector in matrix:
    line = np.vstack((vector,np_word))
    # 按照分数从大到小排序
    line = line[:,line[0].argsort()[::-1]]
    # 只要前十个最大的
    line = line[:,:__count]
    score_list.append(line)
  
  # 生成最终单词表
  word = []
  for socre in score_list:
    for tag in socre[1]:
      if tag not in word:
        word.append(tag)
  
  # 生成最后的分数向量
  final_score = []
  for score in score_list:
    one_score = [0] * len(word)
    for i in range(score.shape[1]):
      try:
        location = word.index(score[1][i])
        one_score[location] = score[0][i]
      except ValueError:
        print("ERROR")
        continue
    final_score.append(one_score)

  # 每个文件的分数向量
  final_score = np.array(final_score).astype("float")
  # 必须是一个可逆矩阵才行
  while True:
    # 随机加密矩阵
    encrypt_matrix = np.random.randint(0,2,(len(word),len(word)))
    try:
      # 解密矩阵
      decrypt_matrix = np.linalg.inv(encrypt_matrix)
    except np.linalg.LinAlgError:
      continue
    break

  # 加密分数向量
  encrypt_score = np.dot(final_score,encrypt_matrix)

  return word,encrypt_score.tolist(),encrypt_matrix.tolist(),decrypt_matrix.tolist()