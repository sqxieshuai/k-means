# -*- coding: utf-8 -*-

import os
import time
from random import sample
from operator import itemgetter
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
# FILEPATH_100k_ratings = PATH_HERE + '/demo.txt'
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

#从评分集合中挑选k个起始点,返回选出的集合
def chooseKInitCenter(numk, usernum, userratings):
    userCenters = {}
    userIds = sample(range(1,usernum+1), numk)
    for uid in userIds:
        userCenters[uid] = userratings[uid]
    return userCenters

#在得到初始点集合(是用户集，不是评分集)，以及所有用户评分集合的基础上，用欧式距离进行聚类
def getUsersClusters(numk, usernum, movienum, usercenters, userratings):
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
        for ucid in userCenterIds:
            #存储ucid的所有评分
            ucidRating = usercenters[ucid]
            tempLen = 0
            #遍历所有电影编号，求uid和ucid的欧式距离
            for i in range(1, movienum+1):
                tempLen += pow(ucidRating.get(i, 0) - uidRating.get(i, 0), 2)
            if sqrt(tempLen) < maxLen:
                (maxLen, minLenUcid) = (sqrt(tempLen), ucid)
        #划入聚类
        clusters[minLenUcid].append(uid)
    return clusters

#重新计算个个聚类的中心
def getAverageCenters(movienum, ratingsDetail,  usercenters, clusters):
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
    return averageCenters
        

#1.获取数据
#2.取k个起始点
#3.用欧式距离进行聚类
#4.算每个聚类的平均中心
#5.重复3,4,5步骤，直到聚类中心不再变化

for i in range(1):
    start = time.time()
    #获得用户对电影的评分
    ratingsDetail = loadRatingsDetail(FILEPATH_100k_ratings)
    #选取初始k个中心点
    userCentersDetail = chooseKInitCenter(NUM_K, NUM_USER, ratingsDetail)
    #当平均中心点不等于上一次的中心点时，进行循环
    n = 1
    while True:
        clustersDetail = getUsersClusters(NUM_K, NUM_USER, NUM_MOVIE, userCentersDetail, ratingsDetail)
        print "第%s次计算结果：\n聚类编号-类内元素个数:" % n
        for ucid in sorted(clustersDetail.keys()):
            print ucid,'\t',len(clustersDetail[ucid])
        print '********************'
        averageCenters = getAverageCenters(NUM_MOVIE, ratingsDetail, userCentersDetail, clustersDetail)
        if userCentersDetail == averageCenters:
            break
        else:
            userCentersDetail = averageCenters
            n += 1
    
    #小数据test
    # print "用户评分:"
    # for uid in sorted(ratingsDetail.keys()):
    #     print uid, ratingsDetail[uid]
    # print '********************************'
    # print "初始中心点:"
    # for ucid in sorted(userCentersDetail.keys()):
    #     print ucid, sorted(userCentersDetail[ucid].items())
    # print '********************************'
    # print "聚类:"
    # for ucid in sorted(clustersDetail.keys()):
    #     print ucid, clustersDetail[ucid]
    # print '********************************'
    # print "平均中心点:"
    # for ucid in sorted(averageCenters.keys()):
    #     print ucid, sorted(averageCenters[ucid].items())

    
    # print sorted(userCentersDetail[userCentersDetail.keys()[0]].items())

    timeUsed = time.time() - start
    print "用时 %s 秒." % timeUsed
