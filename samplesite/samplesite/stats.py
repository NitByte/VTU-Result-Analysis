import json
import pandas as pd
import statistics
from tabulate import tabulate
import operator
from django.shortcuts import HttpResponse,render

def studGrade(request):
    branch=request.GET["branch"]
    year=request.GET["year"]
    grade=request.GET["grade"]
    with open("templates/new20"+year+"batch.json") as fp:
        res=json.load(fp)
    branch_name=res[branch]
    subjects={}
    count={}
    for usn in branch_name:
        for subs in branch_name[usn]["Subjects"]:
            if subs not in subjects:
                subjects[subs]=branch_name[usn]["Subjects"][subs]["SubjectName"]
    grade_studs={}
    for sub,name in subjects.items():
        grade_studs[name]={}
    for sub,name in subjects.items():
        for usn in branch_name:
            try:
                if branch_name[usn]["Subjects"][sub]["GradeLetter"]==grade:
                    grade_studs[name][branch_name[usn]["Name"]]={}
                    grade_studs[name][branch_name[usn]["Name"]]["Total"]=branch_name[usn]["Subjects"][sub]["Total"]
                    grade_studs[name][branch_name[usn]["Name"]]["Internal"]=branch_name[usn]["Subjects"][sub]["Internal"]
                    grade_studs[name][branch_name[usn]["Name"]]["External"]=branch_name[usn]["Subjects"][sub]["External"]
                    grade_studs[name][branch_name[usn]["Name"]]["GradePoints"]=branch_name[usn]["Subjects"][sub]["GradePoints"]
                    grade_studs[name][branch_name[usn]["Name"]]["GradeLetter"]=branch_name[usn]["Subjects"][sub]["GradeLetter"]                 
            except:
                pass
    for sub in grade_studs:
        count[sub]=len(grade_studs[sub])
    print(count)
    return render(request,"gradestats.html",{'gradestats':grade_studs,'subjects':subjects,'count':count})

def classStats(request):
    branch=request.GET["branch"]
    year=request.GET["year"]
    with open("templates/new20"+year+"batch.json") as fp:
        res=json.load(fp)
    branch_name=res[branch]
    subjects={}

    for usn in branch_name:
        for subs in branch_name[usn]["Subjects"]:
            if subs not in subjects:
                subjects[subs]=branch_name[usn]["Subjects"][subs]["SubjectName"]

    stats={}
    sub_dict={}
    sub_stats={}

    for usn in branch_name:
        stats[usn]={}
        stats[usn]["Name"]=branch_name[usn]["Name"]
        stats[usn]["SGPA"]=branch_name[usn]["CGPA"]
        for subs in branch_name[usn]["Subjects"]:
            stats[usn][subs]=branch_name[usn]["Subjects"][subs]["Total"]
    
    for sub in subjects:
        sub_dict[sub]=[]

    for usn in branch_name:
        for subs in branch_name[usn]["Subjects"]:
            sub_dict[subs].append(branch_name[usn]["Subjects"][subs]["GradeLetter"])

    df=pd.DataFrame(stats).transpose()
    columns = [column for column in df.columns if column!="Name" and column!="SGPA"]
    s=df["Name"]
    c=df["SGPA"].astype('float32')
    df=df[columns].astype('float32')
    df["Name"]=s
    df["SGPA"]=c

    sub_stats["Average"]={}
    sub_stats["Count"]={}
    sub_stats["Maximum"]={}
    sub_stats["Minimun"]={}
    sub_stats["Quantile"]={}
    sub_stats["StandardDeviation"]={}
    sub_stats["Variance"]={}
    sub_stats["Fails"]={}
    sub_stats["Pass%"]={}
    sub_stats["Above90"]={}
    for sub in columns:
        sub_stats["Count"][sub]=df[sub].count()
        sub_stats["Average"][sub]=round(df[sub].mean(),2)
        sub_stats["Maximum"][sub]=df[sub].max()
        sub_stats["Minimun"][sub]=df[sub].min()
        sub_stats["Quantile"][sub]=df[sub].quantile()
        if sub_stats["Count"][sub]!=1:
            sub_stats["StandardDeviation"][sub]=round(df[sub].std(),2)
        else:
            sub_stats["StandardDeviation"][sub]=0
        if sub_stats["Count"][sub]!=1:
            sub_stats["Variance"][sub]=round(df[sub].var(),2)
        else:
            sub_stats["Variance"][sub]=0
        sub_stats["Fails"][sub]=sub_dict[sub].count('F')
        sub_stats["Pass%"][sub]=round(((len(sub_dict[sub])-sub_dict[sub].count('F'))/len(sub_dict[sub]))*100,2)
        sub_stats["Above90"][sub]=sub_dict[sub].count('S+')     
    return render(request,"classstats.html",{'sub_stats':sub_stats,'subjects':subjects})

def branchStats(request):
    year=request.GET["year"]
    with open("templates/new20"+year+"batch.json") as fp:
        res=json.load(fp)
    branch_name=res["cs"]
    subjects={}

    for usn in branch_name:
        for subs in branch_name[usn]["Subjects"]:
            if subs not in subjects:
                subjects[subs]=branch_name[usn]["Subjects"][subs]["SubjectName"]
    branchtuple=[]
    tableDict={}
    rankdict={}
    ranks={}
    sgpas=[]
    result=[]
    tableDict["CGPAS"]={}
    tableDict["Fails"]={}
    for branch in res:
        sgpas=[]
        result=[]
        for usn in res[branch]:
            sgpas.append(res[branch][usn]["CGPA"])
            for sub in res[branch][usn]["Subjects"]:
                if res[branch][usn]["Subjects"][sub]["GradeLetter"]=='F':
                    result.append('F')
                    break
        tableDict["CGPAS"][branch]=sgpas
        tableDict["Fails"][branch]=result
    branchStats={}
    branchStats["No Of Students"]={}
    branchStats["Max SGPA"]={}
    branchStats["Min SGPA"]={}
    branchStats["No Of Students Failed"]={}
    branchStats["Above 9 SGPA"]={}
    branchStats["Below 4 SGPA"]={}
    branchStats["Pass%"]={}
    branchStats["Average SGPA"]={}
    branchStats["Variance"]={}
    branchStats["Branch Rank"]={}
    for branch in res:
        branchtuple.append(branch)
        totalStuds=len(res[branch])
        branchStats["No Of Students"][branch]=totalStuds
        branchStats["Max SGPA"][branch]=max(tableDict["CGPAS"][branch])
        branchStats["Min SGPA"][branch]=min(tableDict["CGPAS"][branch])
        branchStats["Variance"][branch]=round(statistics.variance(map(float,tableDict["CGPAS"][branch])),2)
        fail=len(tableDict["Fails"][branch])
        branchStats["No Of Students Failed"][branch]=fail
        avgsgpa=round(statistics.mean(map(float,tableDict["CGPAS"][branch])),2)
        branchStats["Average SGPA"][branch]=avgsgpa
        ranks[branch]=avgsgpa
        branchStats["Above 9 SGPA"][branch]=len([x for x in tableDict["CGPAS"][branch] if float(x) >=9.0])
        branchStats["Below 4 SGPA"][branch]=len([x for x in tableDict["CGPAS"][branch] if float(x) <=4.0])
        branchStats["Pass%"][branch]=round(((totalStuds-fail)/totalStuds)*100,2)
    ranktuple=sorted(ranks.items(),key=operator.itemgetter(1),reverse=True)
    for rank,tup in enumerate(ranktuple):
        rankdict[tup[0]]=rank+1
    for branch in branchtuple:
        branchStats["Branch Rank"][branch]=rankdict[branch]
    return render(request,'branchstats.html',{"branchStats":branchStats})

