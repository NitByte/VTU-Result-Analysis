import json
import pandas as pd
from django.shortcuts import HttpResponse,render

with open("templates/2015batch.json") as fp:
    res=json.load(fp)

branch_name=res["cs"]
subjects={}

for usn in branch_name:
    for subs in branch_name[usn]["Subjects"]:
        if subs not in subjects:
            subjects[subs]=branch_name[usn]["Subjects"][subs]["SubjectName"]

def studGrade(request):
    grade_studs={}
    for sub,name in subjects.items():
        grade_studs[name]={}
    for sub,name in subjects.items():
        for usn in branch_name:
            try:
                if branch_name[usn]["Subjects"][sub]["GradeLetter"]=="F":
                    grade_studs[name][branch_name[usn]["Name"]]={}
                    grade_studs[name][branch_name[usn]["Name"]]["Total"]=branch_name[usn]["Subjects"][sub]["Total"]
                    grade_studs[name][branch_name[usn]["Name"]]["Internal"]=branch_name[usn]["Subjects"][sub]["Internal"]
                    grade_studs[name][branch_name[usn]["Name"]]["External"]=branch_name[usn]["Subjects"][sub]["External"]
                    grade_studs[name][branch_name[usn]["Name"]]["GradePoints"]=branch_name[usn]["Subjects"][sub]["GradePoints"]
                    grade_studs[name][branch_name[usn]["Name"]]["GradeLetter"]=branch_name[usn]["Subjects"][sub]["GradeLetter"]
                    
            except:
                pass
    return render(request,"gradestats.html",{'gradestats':grade_studs,'subjects':subjects})

def classStats(request):
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
    print(stats)
    print(df)

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
        sub_stats["StandardDeviation"][sub]=round(df[sub].std(),2)
        sub_stats["Variance"][sub]=round(df[sub].var(),2)
        sub_stats["Fails"][sub]=sub_dict[sub].count('F')
        sub_stats["Pass%"][sub]=round(((len(sub_dict[sub])-sub_dict[sub].count('F'))/len(sub_dict[sub]))*100,2)
        sub_stats["Above90"][sub]=sub_dict[sub].count('S+')     
    # print(sub_stats)
    return render(request,"classstats.html",{'sub_stats':sub_stats,'subjects':subjects})

