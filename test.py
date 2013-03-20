# -*- coding: utf-8 -*-

import os

PATH_HERE = os.path.abspath("").replace("\\", "/")

#ml-100k folder
FILEPATH_100k_users = PATH_HERE + "/ml-100k/u.user"
FILEPATH_100k_ratings = PATH_HERE + "/ml-100k/u.data"
FILEPATH_100k_movies = PATH_HERE + "/ml-100k/u.item"

#ml-1M folder
FILEPATH_1M_users = PATH_HERE + "/ml-1M/users.dat"
FILEPATH_1M_ratings = PATH_HERE + "/ml-1M/ratings.dat"
FILEPATH_1M_movies = PATH_HERE + "/ml-1M/movies.dat"

#ml-10M folder
FILEPATH_10M_tags = PATH_HERE + "/ml-10M/tags.dat"
FILEPATH_10M_ratings = PATH_HERE + "/ml-10M/ratings.dat"
FILEPATH_10M_movies = PATH_HERE + "/ml-10M/movies.dat"


fp = open(FILEPATH_10M_ratings, 'r')
fc = []
n = 0
for line in fp.readlines():
    fc.append(int(line.strip().split("::")[1]))
    n += 1
print len(fc)
temp = sorted(set(fc))
print len(temp),temp[-10::]
print n


