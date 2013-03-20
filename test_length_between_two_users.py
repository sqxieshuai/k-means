# -*- coding: utf-8 -*-

import time

a = {}
b = {}

for i in range(0, 100000, 2):
    a.setdefault(i,i)

for i in range(0, 100000, 4):
    b.setdefault(i, i)

for i in range(1011, 50111, 3):
    b.setdefault(i, i)

start = time.time()
lens = 0
n = 0
for i in range(100000):
    lens += pow(a.get(i, 0) - b.get(i, 0), 2)
    n += 1
print lens,n
print "用时 %s 秒" % (time.time() - start)
print "---------------------------"

start = time.time()
lens = 0
n = 0
for i in a:
    lens += pow(a[i] - b.get(i, 0), 2)
    n += 1
for i in set(b) - set(a):
    lens += pow(b[i], 2)
    n += 1
print lens,n
print "用时 %s 秒" % (time.time() - start)

'''
之前算法计算用户距离的时候，要遍历所有的电影id，然后逐一取值，相减，平方
优化之后，只取有评分的项进行计算，大大减少计算次数
'''