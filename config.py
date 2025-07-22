from itertools import combinations

from enum import StrEnum

class BALL(StrEnum):
    red25 = "红球25码"
    red20 = "红球20码"
    red12 = "红球12码"
    red10 = "红球10码"
    red3 = "红球三胆"
    red2 = "红球双胆"
    red1 = "红球独胆"
    redk6 = "红球杀六"
    redk3 = "红球杀三"
    tali2 = "凤尾两码"
    head2 = "龙头两码"
    blue5 = "蓝球定五"
    blue3 = "蓝球定三"
    bluek5 = "蓝球杀五"
    blue6 = "蓝球定六"
    blue2 = "蓝球定二"
    blue1 = "蓝球定一"
    bluek3 = "蓝球杀三"



def summation(seq):
    return sum([int(i) for i in seq.split(",")])

def interval(seq):
    seqs = [int(i) for i in seq.split(",")]
    return seqs[-1] - seqs[0]

def AC(seq,length):
    combs = combinations([int(i) for i in seq.split(",")],2)
    difflist = []
    for com in combs:
        difflist.append(abs(com[1] - com[0]))
    return len(set(difflist)) - length - 1

def zone_ratio(seq,type):
    if type == 1:
        boundry = [11,23]
    else:
        boundry = [12,25]
    resdict = {1:0,2:0,3:0}
    for num in seq.split(","):
        if int(num) <= boundry[0]:
            resdict[1] += 1
        elif int(num) >= boundry[1]:
            resdict[3] += 1
        else:
            resdict[2] += 1
    return ":".join([str(j) for j in list(resdict.values())])

def odd_ratio(seq):
    resdict = {1:0,0:0}
    for num in seq.split(","):
        if int(num) % 2 == 0:
            resdict[0] += 1
        else:
            resdict[1] += 1
    return ":".join([str(j) for j in list(resdict.values())]) 


def remainder(seq):
    res = [str(int(i) % 3).zfill(2) for i in seq.split(",")]
    return ",".join(res)

def composite(seq):
    res = 0
    for sub in seq.split(","):
     res += int(sub[0])
     res += int(sub[1])
    return res    


dlt_schema_count_dict = {
    "红球25码":5,
    "红球20码":5,
    "红球10码":5,
    "红球三胆":3,
    "红球双胆":2,
    "红球独胆":1,
    "红球杀六":6,
    "红球杀三":3,
    "蓝球定六":6,
    "蓝球定二":2,
    "蓝球定一":1,
    "蓝球杀三":3
}


ssq_schema_count_dict = {
    "红球25码":6,
    "红球20码":6,
    "红球12码":6,
    "红球三胆":3,
    "红球双胆":2,
    "红球独胆":1,
    "红球杀六":6,
    "红球杀三":3,
    "凤尾两码":1,
    "龙头两码":1,
    "蓝球定五":1,
    "蓝球定三":1,
    "蓝球杀五":5
}



def call_hit(row):
    pr = row["numbers"].split(",")
    if "红" in row["schema"]:
        tr = row["rsequence"].split(",")
        if "杀" not in row["schema"]:
            return len(set(tr).intersection(set(pr)))
        else:
            return len([i for i in pr if i not in tr])
    elif "凤" in row["schema"]:
        if row["rsequence"].endswith(row["numbers"]):
            return 1
        else:
            return 0
    elif "龙" in row["schema"]:
        if row["rsequence"].startswith(row["numbers"]):
            return 1
        else:
            return 0   
    else:
        tr = row["bsequence"].split(",")
        if "杀" not in row["schema"]:
            return len(set(tr).intersection(set(pr)))
        else:
            return len([i for i in pr if i not in tr])

srschema12 = "红球12码"
srschema25 = "红球25码"
srschema20 = "红球20码"
srschematop2 = "龙头两码"
srschematail2 = "凤尾两码"
srschema3 = "红球三胆"
srschemak3 = "红球杀三"
srschemak6 = "红球杀六"
srschema4 = "红球四码"
srschema1 = "红球独胆"
srschema2 = "红球双胆"

sbschema5 = "蓝球定五"
sbschema3 = "蓝球定三"
sbschemak5 = "蓝球杀五"

drschema10 = "红球10码"
drschema25 = "红球25码"
drschema20 = "红球20码"
drschema3 = "红球三胆"
drschema2 = "红球双胆"
drschema1 = "红球独胆"
drschemak3 = "红球杀三"
drschemak6 = "红球杀六"

dbschema6 = "蓝球定六"
dbschema2 = "蓝球定二"
dbschema1 = "蓝球定一"
dbschemak3 = "蓝球杀三"

