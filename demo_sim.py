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
# NUM_K = 3
# NUM_USER = 7
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

#返回两个用户所评电影相同的比例,最后一个参数kind表示：当为uciduid时，返回（交集/ucid集）,默认返回（交集/并集）
def getSameRate(uidOne, uidTwo, userratings, *kind):
    setOne = set(userratings[uidOne])
    setTwo = set(userratings[uidTwo])
    sameSet = setOne & setTwo
    allSet = setOne | setTwo
    if kind == "uciduid":
        return float(len(sameSet)) / len(setOne)
    return float(len(sameSet)) / len(allSet)
        
    
#从评分集合中挑选k个起始点,返回选出的集合
def chooseKInitCenter(numk, usernum, userratings):
    userCenters = {}
    userIds = []
    #随机挑选k个用户
    n = 0 
    while len(userIds) < numk :
        tempId = randint(1, usernum)
        n += 1
        if tempId not in userIds :
            stats = True #记录此点是否可用
            #对于已经存在的每一个中心点，都和新选取的中心点计算相同相似度
            for ucid in userIds:
                #如果相似度大于0.2，则放弃该点
                if getSameRate(ucid, tempId, userratings) >= 0.2:
                    stats = False
                    break
            #如果显示可用，就加入到中心点列表中
            if stats:
                userIds.append(tempId)
    #设置userCenters
    for ucid in userIds:
        userCenters[ucid] = userratings[ucid]
    print n
    return userCenters

#在得到初始点集合(是用户集，不是评分集)，以及所有用户评分集合的基础上，用相似度进行聚类
def getUsersClusters(usernum, movienum, usercenters, userratings):
    start = time.time()
    clusters = {}
    #所有初始中心结点的id
    userCenterIds = usercenters.keys()
    #初始化k个聚类内为空列表
    for ucid in userCenterIds:
        clusters[ucid] = []
    #循环遍历每一个用户
    for uid in range(1, usernum+1):
        # print "uid\t", uid
        #设置哨兵点
        maxSameRate = -1
        #计算uid和每个ucid的相似度，并取相似度最大的那一个ucid作为聚类号
        for ucid in userCenterIds:
            #存储ucid的所有评分电影id
            sameMidRate = getSameRate(ucid, uid, userratings, "uciduid")
            # print "ucid\t", ucid, "\tsamemidRate\t", sameMidRate
            if sameMidRate > maxSameRate:
                (maxSameRate, maxSameUcid) = (sameMidRate, ucid)
        #划入距离最短的聚类
        # print "maxSameUcid", maxSameUcid
        # print "---"
        clusters[maxSameUcid].append(uid)
    print u'聚类',time.time() - start
    return clusters

#重新计算每个聚类的中心，用每个聚类的中间点（按评论电影的多少来排序）作为代表中心
def getAverageCenters(userratings, clusters):
    start = time.time()
    userNewCenters = {}
    #循环k个中心点
    for ucid in clusters:
        #获取当前中心点内所有用户以及其评论过的电影数量，并排序
        userMidLenSet = {}
        for uid in clusters[ucid]:
            userMidLenSet[uid] = len(userratings[uid])
        tempSortedSet = sorted(userMidLenSet.items(), key=lambda item:item[1], reverse=False)
        userNewCenterId = tempSortedSet[len(clusters[ucid]) / 2][0]
        userNewCenters[userNewCenterId] = userratings[userNewCenterId]
    print u'平均', time.time() - start
    return userNewCenters
        
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
    ratingsDetail = loadRatingsDetail(FILEPATH_100k_ratings) #FILEPATH_test,FILEPATH_100k_ratings
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
        averageCenters = getAverageCenters(ratingsDetail, clustersDetail)
        if userCentersDetail == averageCenters: 
            break
        else:
            userCentersDetail = averageCenters
            n += 1

    timeUsed = time.time() - start
    print u"用时 %s 秒." % timeUsed