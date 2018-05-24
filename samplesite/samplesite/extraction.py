from django.shortcuts import HttpResponse,render
import pandas as pd
import requests
from tabulate import tabulate
import bs4 as bs
import json
import numpy as np

def fetch_result(request):
    branches=['is','cs','me','ec','cv','te','im','bt','ee']
    base_usn="1mv"
    year=request.GET['year']
    types=request.GET['type']
    print(year,types)
    result={}
    
    def assign_ranks(d):
        all_ranks={}
        for branch in d:
            lookup={}
            rank={}
            for usn in d[branch]:
                rank[usn]=float(d[branch][usn]["CGPA"])
            for i,val in enumerate(sorted(set(rank.values()),reverse=True)):
                    lookup[val]=i+1
            for usn in rank:
                rank[usn]=lookup[rank[usn]]
            all_ranks.update(rank)
        return all_ranks

    def assign_grade_and_points(reval_total):
        total = int(reval_total)
        if 100 >=total >= 90:
            return "10", "S+"
        elif 89 >= total >= 80:
            return "9", "S"
        elif 79 >= total >= 70:
            return "8", "A"
        elif 69 >= total >= 60:
            return "7", "B"
        elif 59 >= total >= 50:
            return "6", "C"
        elif 49 >= total >= 45:
            return "5", "D"
        else:
            return "4", "E"

    def calc_sgpa(points, credit):
        points = np.array(points)
        credit = np.array(credit)
        sgpa = '%.2f' % ((sum(points * credit) / sum(credit * 10)) * 10)
        return sgpa

    def regular():
        i=0
        backlog={'17':'1','16':'3','15':'5'}
        def form_df(usn,branch):
            headers={}
            headers['User-Agent']='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
            payload={'lns':usn}
            req=requests.post("http://results.vtu.ac.in/vitaviresultcbcs/resultpage.php",data=payload,params=headers)
            soup=bs.BeautifulSoup(req.text,"lxml")
            name=soup.find("div",class_="table-responsive").find_all("td")[-1].text.split(":")[-1].strip()
            print(usn)
            try:
                if soup.find("div",attrs={'style':"text-align:center;padding:5px;"}).b.text.split(":")[-1].strip()==backlog[year]:
                    table=soup.find("div","divTable")
                    i+=1
                    rows=table.find_all('div',class_="divTableRow")
                    table=[]
                    for row in rows:
                        record=str(row.text).split('\n')
                        record=record[1:-1]
                        table.append(record)      
                    df=pd.DataFrame(table[1:],columns=table[0])
                    df=df.set_index(df['Subject Code'])
                    df=df[table[0][1:]]
                    head=table[0]
                    print(tabulate(df,headers=head,numalign="left", tablefmt="fancy_grid"))
                    result[branch][usn]={}
                    result[branch][usn]["Name"]=name
                    result[branch][usn]["Subjects"]={}
                    for row in df.itertuples():
                        result[branch][usn]["Subjects"][row[0]]={}
                        result[branch][usn]["Subjects"][row[0]]["SubjectName"]=row[1]
                        result[branch][usn]["Subjects"][row[0]]["Internal"]=str(row[2])
                        result[branch][usn]["Subjects"][row[0]]["External"]=str(row[3])
                        result[branch][usn]["Subjects"][row[0]]["Total"]=row[4]
                        result[branch][usn]["Subjects"][row[0]]["Result"]=row[5]
                else:
                    pass
            except:
                pass

        for branch in branches:
            result[branch]={}
            if branch not in ["cs","me","ec","ee"]:
                for num in range(1,70):
                    usn=base_usn+year+branch+str(num).zfill(3)
                    form_df(usn,branch)

                for num in range(1,70):
                    usn=base_usn+str(int(year)-1)+branch+str(num).zfill(3)
                    form_df(usn,branch)

                for num in range(400,420):
                    usn=base_usn+str(int(year)+1)+branch+str(num)
                    form_df(usn,branch)

                for num in range(400,420):
                    usn=base_usn+str(int(year))+branch+str(num)
                    form_df(usn,branch) 
            else:
                for num in range(1,160):
                    usn=base_usn+year+branch+str(num).zfill(3)
                    form_df(usn,branch)

                for num in range(1,160):
                    usn=base_usn+str(int(year)-1)+branch+str(num).zfill(3)
                    form_df(usn,branch)

                for num in range(400,440):
                    usn=base_usn+str(int(year)+1)+branch+str(num)
                    form_df(usn,branch)

                for num in range(400,440):
                    usn=base_usn+str(int(year))+branch+str(num)
                    form_df(usn,branch) 

        for branch in result:
            for usn in result[branch]:
                points=[]
                credit=[]
                for sub in result[branch][usn]["Subjects"]:
                    if result[branch][usn]["Subjects"][sub]["Result"] !="P":
                        result[branch][usn]["Subjects"][sub]["GradeLetter"] = "F"
                        result[branch][usn]["Subjects"][sub]["GradePoints"] = "0"
                    else:
                        tot = result[branch][usn]["Subjects"][sub]["Total"]
                        grade_points, grade_letter = assign_grade_and_points(tot)
                        result[branch][usn]["Subjects"][sub]["GradeLetter"] = grade_letter
                        result[branch][usn]["Subjects"][sub]["GradePoints"] = grade_points
                    if sub[-3]=='L':
                        result[branch][usn]["Subjects"][sub]["Credits"]='2'
                    elif len(sub)==7:
                        result[branch][usn]["Subjects"][sub]["Credits"]='3'
                    else:
                        result[branch][usn]["Subjects"][sub]["Credits"]='4'
                    points.append(int(result[branch][usn]["Subjects"][sub]["GradePoints"]))
                    credit.append(int(result[branch][usn]["Subjects"][sub]["Credits"]))
                    
                result[branch][usn]['CGPA']=calc_sgpa(points,credit)

        all_rank=assign_ranks(result)
        for branch in result:
            for usn in result[branch]:
                result[branch][usn]["Rank"]=all_rank[usn]
        with open("templates/20"+year+"batch.json","w+") as fp:
            json.dump(result,fp)

    def update():
        with open("templates/20"+year+"batch.json", "r") as fp:
            res = json.load(fp)

        with open("templates/reval20"+year+"batch.json", "r") as rp:
            reval = json.load(rp)

        for branch in reval:
            for usn in reval[branch]:
                for sub in reval[branch][usn]["Subjects"]:
                    if sub in res[branch][usn]["Subjects"]:
                        new_external = reval[branch][usn]["Subjects"][sub]["RVMarks"]
                        result = reval[branch][usn]["Subjects"][sub]["Result"]
                        reval[branch][usn]["Subjects"][sub]["External"] = new_external
                        res[branch][usn]["Subjects"][sub]["OldTotal"]=res[branch][usn]["Subjects"][sub]["Total"] 
                        res[branch][usn]["Subjects"][sub]["Total"] = str(
                            int(new_external) + int(res[branch][usn]["Subjects"][sub]["Internal"]))
                        if result == "F":
                            res[branch][usn]["Subjects"][sub]["GradeLetter"] = "F"
                            res[branch][usn]["Subjects"][sub]["GradePoints"] = "0"
                        else:
                            tot = res[branch][usn]["Subjects"][sub]["Total"]
                            grade_points, grade_letter = assign_grade_and_points(tot)
                            res[branch][usn]["Subjects"][sub]["GradeLetter"] = grade_letter
                            res[branch][usn]["Subjects"][sub]["GradePoints"] = grade_points

        for branch in reval:
            for usn in reval[branch]:
                points=[]
                credit=[]
                for sub in res[branch][usn]["Subjects"]:
                    points.append(int(res[branch][usn]["Subjects"][sub]["GradePoints"]))
                    credit.append(int(res[branch][usn]["Subjects"][sub]["Credits"]))
                res[branch][usn]["OldSGPA"]=res[branch][usn]["CGPA"]
                res[branch][usn]["CGPA"]=calc_sgpa(points,credit)
            for usn in res[branch]:
                for sub in res[branch][usn]["Subjects"]:
                    if "OldTotal" in res[branch][usn]["Subjects"][sub]:
                        pass
                    else:
                        res[branch][usn]["Subjects"][sub]["OldTotal"]="N/A"


        with open("templates/new20"+year+"batch.json","w+") as wp:
            json.dump(res,wp)

    def reval():
        with open("templates/20"+year+"batch.json") as js:
            res=json.load(js)

        sub_reval={}
        url="http://results.vtu.ac.in/vitavirevalresultcbcs/resultpage.php"
        headers={}
        headers['User-Agent']='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
        i=0
        for branch in res:
            sub_reval[branch]={}
            for usns in res[branch]:  
                usn={'lns':usns}    
                req=requests.post(url,params=headers,data=usn)
                i+=1
                print(i,res[branch][usns]["Name"])
                soup=bs.BeautifulSoup(req.text,'lxml')
                try:
                    rows=soup.find_all('div',class_="divTableRow")
                    rows=rows[0:-1]
                    table=[]
                    for row in rows:
                        record=str(row.text).split('\n')
                        record=record[1:-1]
                        table.append(record)      
                    df=pd.DataFrame(table[1:],columns=table[0])
                    df=df.set_index(df['Subject Code'])
                    df=df[table[0][1:]]
                    df=df.drop("Subject Code", axis=0,errors="ignore")
                    df[["RV Marks","Old Marks"]]=df[["RV Marks","Old Marks"]].astype(int)
                    df["Marks Increased"]=df["RV Marks"]-df["Old Marks"]
                    head=table[0]
                    head.append("Marks Increased")
                    sub_reval[branch][usns]={}
                    sub_reval[branch][usns]["Name"]=res[branch][usns]["Name"]
                    sub_reval[branch][usns]["Subjects"]={}
                    print(tabulate(df,headers=head,numalign="left", tablefmt="fancy_grid"))
                    for row in df.itertuples():
                        sub_reval[branch][usns]["Subjects"][row[0]]={}
                        sub_reval[branch][usns]["Subjects"][row[0]]["SubjectName"]=row[1]
                        sub_reval[branch][usns]["Subjects"][row[0]]["RVMarks"]=str(row[2])
                        sub_reval[branch][usns]["Subjects"][row[0]]["OldMarks"]=str(row[3])
                        sub_reval[branch][usns]["Subjects"][row[0]]["InternalMarks"]=row[4]
                        sub_reval[branch][usns]["Subjects"][row[0]]["Result"]=row[5]
                        sub_reval[branch][usns]["Subjects"][row[0]]["MarksIncreased"]=str(row[6])
                except:
                    pass
        with open("templates/reval20"+year+"batch.json",'w+') as fp:
            json.dump(sub_reval,fp)
    if types=='Regular':
        regular()
    else:
        reval()
        update()

    return HttpResponse("Fetched "+i+" results")

    