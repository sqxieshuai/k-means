# -*- coding: utf-8 -*-

import os
import time
from random import randint
from math import sqrt


PATH_DATA_FOLDER = "D:\MovieLens\Data".replace("\\", "/")
PATH_HERE = os.path.abspath("").replace("\\", "/")

#ml-100k folder
FILEPATH_100k_users = PATH_DATA_FOLDER + "/ml-100k/u.user"
FILEPATH_100k_ratings = PATH_DATA_FOLDER + "/ml-100k/u.data"
FILEPATH_100k_movies = PATH_DATA_FOLDER + "/ml-100k/u.item"

#ml-1M folder
FILEPATH_1M_users = PATH_DATA_FOLDER + "/ml-1M/users.dat"
FILEPATH_1M_ratings = PATH_DATA_FOLDER + "/ml-1M/ratings.dat"
FILEPATH_1M_movies = PATH_DATA_FOLDER + "/ml-1M/movies.dat"

#ml-10M folder
FILEPATH_10M_tags = PATH_DATA_FOLDER + "/ml-10M/tags.dat"
FILEPATH_10M_ratings = PATH_DATA_FOLDER + "/ml-10M/ratings.dat"
FILEPATH_10M_movies = PATH_DATA_FOLDER + "/ml-10M/movies.dat"

#const numbers 
NUM_K = 5
NUM_USER = 943  #943,6040,71567
NUM_MOVIE = 1682  #1682,3952,65133

#小数据test
# FILEPATH_test = PATH_HERE + '/demo.txt'
# NUM_K = 2
# NUM_USER = 4
# NUM_MOVIE = 6

#'\t','::','::'

#从文件内读取数据到内存,同时对数据进行预处理，并规格化，返回“用户-电影评分”集合
def loadRatingsDetail(ratingDataFilepath):
    ratings = {}
    fp = open(ratingDataFilepath, "r")
    for line in fp.readlines():
        (userId, movieId, rating) = line.strip().split("\t")[0:3]
        ratings.setdefault(int(userId), {})
        ratings[int(userId)][int(movieId)] = float(rating)
    fp.close()
    return ratings

#计算一个向量的模,保留三位小数
def getNorm(uid, userratings):
    temp = 0
    for val in userratings[uid].values():
        temp += pow(val, 2)
    temp = round(sqrt(temp), 3)
    return temp

#从评分集合中挑选k个起始点,返回选出的集合
def chooseKInitCenter(numk, usernum, userratings):
    userCenters = {}
    userIdNorms = {} #存储中心点的模
    userIds = []
    #随机挑选k个用户
    while len(userIds) < numk :
        tempId = randint(1, usernum)
        if tempId not in userIds :
            stats = True #记录此点是否可用
            #对于已经存在的每一个中心点，都和新选取的中心点计算余弦相似度
            #如果任意一个大于阀值（0.6），就放弃新选取的点
            for ucid in userIds:
                #计算余弦相似度，先计算分子
                temp1 = 0 #余弦相似度的分子
                for mid in userratings[ucid]:
                    temp1 += userratings[ucid][mid] * userratings[tempId].get(mid, 0)
                #计算分母，分别计算两个向量的模
                #先计算中心点的模
                try:
                    temp2 = userIdNorms[ucid]
                except KeyError:
                    temp2 = getNorm(ucid, userratings)
                    userIdNorms[ucid] = temp2
                #再计算新选点的模
                temp3 = getNorm(tempId, userratings)
                #计算余弦值
                cosValue = round(temp1/(temp2*temp3), 3)
                #如果出现相似度比较大的情况，则放弃该点
                if cosValue >= 0.6:
                    break
            #如果显示可用，就加入到中心点列表中
            if stats:
                userIds.append(tempId)
    #设置userCenters
    for ucid in userIds:
        userCenters[ucid] = userratings[ucid]
    return userCenters

#在得到初始点集合(是用户集，不是评分集)，以及所有用户评分集合的基础上，用欧式距离进行聚类
def getUsersClusters(usernum, movienum, usercenters, userratings):
    start = time.time()
    clusters = {}
    #所有初始结点的id
    userCenterIds = usercenters.keys()
    #初始化k个聚类内为空列表
    for ucid in userCenterIds:
        clusters[ucid] = []
    #循环遍历每一个用户
    for uid in range(1, usernum+1):
        #存储uid的所有评分
        uidRating = userratings[uid]
        #设置哨兵比较点
        minLenUcid = -1
        maxLen = float("inf")
        #计算uid和每个ucid的距离，并取距离最短的那一个ucid作为聚类号
        for ucid in userCenterIds:
            #存储ucid的所有评分
            ucidRating = usercenters[ucid]
            tempLen = 0
            #求uid和ucid的欧式距离
            for mid in ucidRating.keys():
                tempLen += pow(ucidRating[mid] - uidRating.get(mid, 0), 2)
            for mid in (set(uidRating)-set(ucidRating)):
                tempLen += pow(uidRating[mid], 2)
            if sqrt(tempLen) < maxLen:
                (maxLen, minLenUcid) = (sqrt(tempLen), ucid)
        #划入距离最短的聚类
        clusters[minLenUcid].append(uid)
    print u'聚类',time.time() - start
    return clusters

#重新计算每个聚类的中心
def getAverageCenters(movienum, ratingsDetail, usercenters, clusters):
    start = time.time()
    averageCenters = {}
    #循环k个中心点
    for ucid in usercenters.keys():
        #初始化第i个中心点内，对所有电影的平均得分为0
        tempUserRatings = {}
        for i in range(1, movienum+1):
            tempUserRatings[i] = 0.0
        #循环遍历第i个中心点内的所有用户
        for uid in clusters[ucid]:
            #遍历该用户的所有评分，将tempUserRatings中对应的项增加该评分
            for mid in ratingsDetail[uid].keys():
                tempUserRatings[mid] += ratingsDetail[uid][mid]
        #计算平均得分
        tempLen = len(clusters[ucid])
        for mid in tempUserRatings.keys():
            tempUserRatings[mid] = round(tempUserRatings[mid]/tempLen, 3)
        averageCenters[ucid] = tempUserRatings
    print u'平均', time.time() - start
    return averageCenters
        
#k-means算法步骤
#1.获取数据
#2.取k个起始点
#3.用欧式距离进行聚类
#4.算每个聚类的平均中心
#5.重复3,4步骤，直到聚类中心不再变化

#优化步骤
#

if __name__ == '__main__':
    start = time.time()
    #获得用户对电影的评分
    ratingsDetail = loadRatingsDetail(FILEPATH_100k_ratings)
    #选取初始k个中心点
    userCentersDetail = chooseKInitCenter(NUM_K, NUM_USER, ratingsDetail)
    #当平均中心点不等于上一次的中心点时，进行循环
    print userCentersDetail.keys()
    
    n = 1
    while True:
        clustersDetail = getUsersClusters(NUM_USER, NUM_MOVIE, userCentersDetail, ratingsDetail)
        print u"第%s次计算结果：\n聚类编号-类内元素个数:" % n
        for ucid in sorted(clustersDetail.keys()):
            print ucid,'\t',len(clustersDetail[ucid])
        print '********************'
        averageCenters = getAverageCenters(NUM_MOVIE, ratingsDetail, userCentersDetail, clustersDetail)
        if userCentersDetail == averageCenters: 
            break
        else:
            userCentersDetail = averageCenters
            n += 1

    timeUsed = time.time() - start
    print u"用时 %s 秒." % timeUsed