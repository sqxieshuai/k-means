# -*- coding: utf-8 -*-

import os
import time
from random import randint
from math import sqrt
from hashlib import md5

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
NUM_K = 30
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

#返回两个用户所评电影相同的比例,返回（交集/并集）
def getSameRate(uidOne, uidTwo, userratings):
    setOne = set(userratings[uidOne])
    setTwo = set(userratings[uidTwo])
    sameSet = setOne & setTwo
    allSet = setOne | setTwo
    return float(len(sameSet)) / len(allSet)
        
    
#从评分集合中挑选k个起始点,返回每个选出的ucid中的uid列表
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
                #如果相似度大于0.3，则放弃该点
                if getSameRate(ucid, tempId, userratings) >= 0.3:
                    stats = False
                    break
            #如果显示可用，就加入到中心点列表中
            if stats:
                userIds.append(tempId)
    #设置userCenters
    for ucid in userIds:
        userCenters[ucid] = userratings[ucid].keys()  #此处返回的中心点，只包含其评分的mid，不包含mid对应的评分值
    print n
    return userCenters

#在得到初始点集合(是用户集，不是评分集)，以及所有用户评分集合的基础上，用相似度进行聚类，在进行聚类的过程中，不考虑评分值，值考虑用户间评过分的mid的相同率
def getUsersClusters(usernum, movienum, usercenters, userratings):
    start = time.time()
    clusters = {}
    #所有初始中心结点的id
    userCenterIds = usercenters.keys() #所有的ucid
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
            #存储ucid的所有评分电影id
            ucidSet = set(usercenters[ucid])
            uidSet = set(userratings[uid])
            sameSet = ucidSet & uidSet
            allSet = ucidSet | uidSet
            sameMidRate = float(len(sameSet)) / len(allSet)
            # print "ucid\t", ucid, "\tsamemidRate\t", sameMidRate
            if sameMidRate >= maxSameRate:
                (maxSameRate, maxSameUcid) = (sameMidRate, ucid)
        #划入与中心点最相似的聚类中
        # print "maxSameUcid", maxSameUcid
        # print "---"sssss
        clusters[maxSameUcid].append(uid)  #聚类结果是ucid和其对应的uid
    print u'聚类',time.time() - start
    return clusters

#tempSortedSet = sorted(userMidLenSet.items(), key=lambda item:item[1], reverse=False)
#重新计算每个聚类的中心
def getAverageCenters(userratings, clusters):
    start = time.time()
    userNewCenters = {}
    #循环k个中心点
    for ucid in clusters:
        userNewCenters[ucid] = []
        #每个电影id在此聚类中心出现的次数
        tempMidNum = {}
        # #聚类内用户的数量
        # clusterLength = float(len(clusters[ucid]))
        #遍历聚类ucid内的每个用户
        for uid in clusters[ucid]:
            #遍历用户的每个评过分的电影id
            for mid in userratings[uid]:
                #将此聚类内，此电影id出现的次数+1
                tempMidNum[mid] = tempMidNum[mid] + 1 if tempMidNum.has_key(mid) else 1
        # for mid in tempMidNum:
        #     #计算每个电影出现的均值
        #     tempMidNum[mid] /= clusterLength
        tempMidNum = sorted(tempMidNum.items(), key=lambda item:item[1], reverse=True)[0:len(tempMidNum)/4 + 1]
        for item in tempMidNum:
            userNewCenters[ucid].append(item[0])  #返回的结果是ucid和其对应的聚类中出现频率排在前25%的mid
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
    while True and n<40:
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
    print u"生成聚类总用时 %s 秒." % timeUsed

    for ucid in sorted(clustersDetail.keys()):
        print ucid,'\t',len(clustersDetail[ucid])

    clustersUcidList = sorted(clustersDetail.keys())
    print sorted(clustersUcidList)
    for i in range(len(clustersUcidList)):
        for j in range(i+1, len(clustersUcidList)):
            ucidi = clustersUcidList[i]
            ucidj = clustersUcidList[j]
            # print ucidi,ucidj,getSameRate(ucidi, ucidj, averageCenters)
            if getSameRate(ucidi, ucidj, averageCenters) > 0.3:
                clustersDetail[ucidj] += clustersDetail[ucidi]
                del clustersDetail[ucidi]
                averageCenters = getAverageCenters(ratingsDetail, clustersDetail)
                break
    
    for ucid in sorted(clustersDetail.keys()):
        print ucid,'\t',len(clustersDetail[ucid])
