import json

with open("/media/nithin/E:/Project/djangosam/samplesite/templates/new2015batch.json","r") as fs:
    res=json.load(fs)

class_ranks={}
sem_ranks={}
lookup_for_sem={}
def assign_ranks(d):
    for branch in res:
        lookup_for_class={}
        rank={}
        for usn in res[branch]:
            rank[usn]=float(res[branch][usn]["CGPA"])
            sem_ranks[usn]=float(res[branch][usn]["CGPA"])
        for i,val in enumerate(sorted(set(rank.values()),reverse=True)):
                lookup_for_class[val]=i+1
        for usn in rank:
            rank[usn]=lookup_for_class[rank[usn]]
        class_ranks.update(rank)
    for i,val in enumerate(sorted(set(sem_ranks.values()),reverse=True)):
        lookup_for_sem[val]=i+1
    for usn in sem_ranks:
        sem_ranks[usn]=lookup_for_sem[sem_ranks[usn]]
assign_ranks(res)
print(lookup_for_sem)
for branch in res:
    for usn in res[branch]:
        res[branch][usn]["ClassRank"]=str(class_ranks[usn])
        res[branch][usn]["SemRank"]=str(sem_ranks[usn])
with open("/media/nithin/E:/Project/djangosam/samplesite/templates/new2015batch.json","w") as kp:
    json.dump(res,kp)

        
    

