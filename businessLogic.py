import json
import smtplib
import sqlalchemy
from pymongo import MongoClient
from bson.json_util import dumps,loads
from flask import render_template
import pymongo
import pprint

# access row by row and update the json file
def parseDF(df_R1,df_R2,df_R3,df_R4,jsonFile,survey,company):
    with open(jsonFile) as json_data:
        js = json.load(json_data)

    #updating surveyName and CompanyName
    js["survey"]=survey
    js["company"]=company

    #updating qid, cid & questions to json file

    R1_phy=df_R1[df_R1['subsector']=='Physical']
    for index, row in R1_phy.iterrows():
      js["R1"]["Physical"].append({'qid':row["qid"], 'question': row["question"], 'cid': row["category_id"],  'cname': row["category_name"], 'nist': row["NIST FUNCTION"], 'cat_reference': row["category_Reference"], 'cat_explanation': row["category_Reference_Explanation"]  })

    R1_org=df_R1[df_R1['subsector']=='Organisational']
    for index, row in R1_org.iterrows():
      js["R1"]["Organisational"].append({'qid':row["qid"], 'question': row["question"], 'cid': row["category_id"],  'cname': row["category_name"], 'nist': row["NIST FUNCTION"], 'cat_reference': row["category_Reference"], 'cat_explanation': row["category_Reference_Explanation"]  })

    R1_tec=df_R1[df_R1['subsector']=='Technical']
    for index, row in R1_tec.iterrows():
      js["R1"]["Technical"].append({'qid':row["qid"], 'question': row["question"], 'cid': row["category_id"],  'cname': row["category_name"], 'nist': row["NIST FUNCTION"], 'cat_reference': row["category_Reference"], 'cat_explanation': row["category_Reference_Explanation"]  })


    R2_phy=df_R2[df_R2['subsector']=='Physical']
    for index, row in R2_phy.iterrows():
      js["R2"]["Physical"].append({'qid':row["qid"], 'question': row["question"], 'cid': row["category_id"],  'cname': row["category_name"], 'nist': row["NIST FUNCTION"], 'cat_reference': row["category_Reference"], 'cat_explanation': row["category_Reference_Explanation"]  })

    R2_org=df_R2[df_R2['subsector']=='Organisational']
    for index, row in R2_org.iterrows():
      js["R2"]["Organisational"].append({'qid':row["qid"], 'question': row["question"], 'cid': row["category_id"],  'cname': row["category_name"], 'nist': row["NIST FUNCTION"], 'cat_reference': row["category_Reference"], 'cat_explanation': row["category_Reference_Explanation"]  })

    R2_tec=df_R2[df_R2['subsector']=='Technical']
    for index, row in R2_tec.iterrows():
      js["R2"]["Technical"].append({'qid':row["qid"], 'question': row["question"], 'cid': row["category_id"],  'cname': row["category_name"], 'nist': row["NIST FUNCTION"], 'cat_reference': row["category_Reference"], 'cat_explanation': row["category_Reference_Explanation"]  })


    R3_phy=df_R3[df_R3['subsector']=='Physical']
    for index, row in R3_phy.iterrows():
      js["R3"]["Physical"].append({'qid':row["qid"], 'question': row["question"], 'cid': row["category_id"],  'cname': row["category_name"], 'nist': row["NIST FUNCTION"], 'cat_reference': row["category_Reference"], 'cat_explanation': row["category_Reference_Explanation"]  })

    R3_org=df_R3[df_R3['subsector']=='Organisational']
    for index, row in R3_org.iterrows():
      js["R3"]["Organisational"].append({'qid':row["qid"], 'question': row["question"], 'cid': row["category_id"],  'cname': row["category_name"], 'nist': row["NIST FUNCTION"], 'cat_reference': row["category_Reference"], 'cat_explanation': row["category_Reference_Explanation"]  })

    R3_tec=df_R3[df_R3['subsector']=='Technical']
    for index, row in R3_tec.iterrows():
      js["R3"]["Technical"].append({'qid':row["qid"], 'question': row["question"], 'cid': row["category_id"],  'cname': row["category_name"], 'nist': row["NIST FUNCTION"], 'cat_reference': row["category_Reference"], 'cat_explanation': row["category_Reference_Explanation"]  })


    R4_phy=df_R4[df_R4['subsector']=='Physical']
    for index, row in R4_phy.iterrows():
      js["R4"]["Physical"].append({'qid':row["qid"], 'question': row["question"], 'cid': row["category_id"],  'cname': row["category_name"], 'nist': row["NIST FUNCTION"], 'cat_reference': row["category_Reference"], 'cat_explanation': row["category_Reference_Explanation"]  })

    R4_org=df_R4[df_R4['subsector']=='Organisational']
    for index, row in R4_org.iterrows():
      js["R4"]["Organisational"].append({'qid':row["qid"], 'question': row["question"], 'cid': row["category_id"],  'cname': row["category_name"], 'nist': row["NIST FUNCTION"], 'cat_reference': row["category_Reference"], 'cat_explanation': row["category_Reference_Explanation"]  })

    R4_tec=df_R4[df_R4['subsector']=='Technical']
    for index, row in R4_tec.iterrows():
      js["R4"]["Technical"].append({'qid':row["qid"], 'question': row["question"], 'cid': row["category_id"],  'cname': row["category_name"], 'nist': row["NIST FUNCTION"], 'cat_reference': row["category_Reference"], 'cat_explanation': row["category_Reference_Explanation"]  })

    with open(jsonFile, 'w') as outfile:
      json.dump(js, outfile)


def parseDFusers(df_username,jsonFile,survey,company):
    with open(jsonFile) as json_data:
        js = json.load(json_data)

    #updating surveyName and CompanyName
    js["survey"]=survey
    js["company"]=company

    #updating qid, cid & questions to json file

    for index, row in df_username.iterrows():
      js["users"].append({'username': row["username"], 'email': row["email"], 'role': row["role"], 'department': row["department"], 'userid': index+1, 'activateSurvey': "False", 'isValid': "False", 'password': ""})


    with open(jsonFile, 'w') as outfile:
      json.dump(js, outfile)




# Establishes connection to MongoDB specified collection
def mongoConnect(host,base,colection,user,pwd):

    client = MongoClient(host, 27017)
    db = client[base]
    col = db[colection]
    return col,db


# load json to questions collection
def pushMongoDB(host,database,collection,jsonFile,user,pwd,survey,company):

    col,db = mongoConnect(host,database,collection,user,pwd)
    #check if same survey & comany names alreaday exists in database.. if yes, delte the existing entry in database
    col.remove({"survey":survey,"company":company})

    #inserting the json file as document into datbase
    with open(jsonFile) as f:
      data = json.load(f)
    col.insert(data)


def getTimeStamp():
    import calendar
    import time
    return calendar.timegm(time.gmtime())



def getMails(survey,company,department):
    col, db = mongoConnect("localhost", "Surveyapp", "userdetails", "user", "pwd")
    mail_list= []
    json_response = list(col.find({"company": company, "survey": survey}, {"users": 1.0, "_id": 0}))
    for i in json_response:
        for attribute, value in i.items():
            for val in value:
                if val['department']== department:
                    mail_list.append(val['email'])
    return mail_list


def sqlConnect():
    database_username = 'root'
    database_password = 'root'
    database_ip       = 'localhost'
    database_name     = 'surveyapp'
    auth_plugin = 'mysql_native_password'
    db = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(database_username, database_password,database_ip, database_name, auth_plugin))
    return db

def activateSurvey(survey,company,department):
    db=sqlConnect()
    # SELECT email  FROM bkbase.userdetails where survey='BKSurvey' and company='CGI' and department ='adv' and isValid='False' and surveyActive='True'
    db.engine.execute("UPDATE userdetails set activateSurvey='True' where survey='"+survey+ "' and company='"+company + "' and department ='"+department+"' and activateSurvey='False'")

def pushSurvey(mail_list):
    for mail in mail_list:
        sender = 'root@ith.com'
        receivers = mail

        message = """ 
        
        MAIL BODY ## MAIL BODY ## MAIL BODY  
        Click on the below link to take SURVEY
        
        http://survey.com:5000
                
        """

        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receivers, message)
        print("Successfully sent email")

def getSurveyDetails(userid,survey,company,host,base,colection,user,pwd,sector):
   col,db=mongoConnect(host,base,colection,user,pwd)
   uid='%s' % userid
   uid=uid.strip("'")
   query = [{'$match':{'userid':uid}},{'$unwind' : "$rows" }, { '$match' : { "rows.sector" : { '$eq' : sector} }} ]

   document = col.aggregate(query)
   return document

def getSurveyDetailsAll(survey,company,host,base,colection,user,pwd,sector):
   col=mongoConnect(host,base,colection,user,pwd)
   survey='%s' % survey
   survey=survey.strip("'")
   company='%s' % company
   company=company.strip("'")
   query = [{ '$match':{ 'survey':survey,'company':company}} , {'$unwind' : "$rows" },{ '$match' : { "rows.sector" : {'$eq' : sector} } }]
   document = col.aggregate(query)
   return document


def getSurveyDetailsByDept(survey,company,host,base,colection,user,pwd,sector,dept):
   col=mongoConnect(host,base,colection,user,pwd)
   survey='%s' % survey
   survey=survey.strip("'")
   company='%s' % company
   company=company.strip("'")
   dept='%s' % dept
   dept=dept.strip("'")
   query = [{ '$match':{ 'survey':survey,'company':company,'department':dept}} , {'$unwind' : "$rows" },{ '$match' : { "rows.sector" : {'$eq' : sector} } }]
   document = col.aggregate(query)
   return document

def mongoInit(colection):
    host='localhost'
    base='Surveyapp'
    user='root'
    pwd='root'
    return host,base,colection,user,pwd

def getcompanynames():
    col, db = mongoConnect("localhost", "Surveyapp", "userdetails", "user", "pwd")
    company = []
    json_response = list(col.find())
    for i in json_response:
        for attribute, value in i.items():
            if attribute == "company":
                company.append(value)
    return company


def getcompanysurveynames(company):
    col, db = mongoConnect("localhost", "Surveyapp", "userdetails", "user", "pwd")
    surveys = []
    json_response = list(col.find())
    for i in json_response:
        for attribute, value in i.items():
            if value == company:
                surveys.append(i['survey'])
    return surveys

def getdepartmentnames(company,survey):
    col, db = mongoConnect("localhost", "Surveyapp", "userdetails", "user", "pwd")
    department_list = []
    json_response = list(col.find({"company": company, "survey": survey},{"users": 1.0, "_id": 0}))
    for i in json_response:
        for attribute, value in i.items():
            for val in value:
                department_list.append(val['department'])
        department_list = list(dict.fromkeys(department_list))
    return department_list

def displayquestions(survey,company,sector,subsector,cname):
    #cid = category[8:]
    #print(cid)
    col,db = mongoConnect("localhost", "Surveyapp", "questions", "user", "pwd")
    questions = []
    cname_key = sector + "." + subsector
    json_response = list(col.find({"survey": survey,"company": company},{cname_key: 1.0, "_id": 0}))
    for i in json_response:
        for attribute, value in i.items():
            for attr, val in value.items():
                for v in val:
                    if v['cname'] == cname:
                        questions.append(v)
    return questions

def getcategory(survey,company,sector,subsector):
    cname_list=[]
    col,db = mongoConnect("localhost", "Surveyapp", "questions", "user", "pwd")
    cname_key = sector + "." + subsector + ".cname"
    json_response = col.find({"survey" : survey,"company" : company},{ cname_key : 1.0, "_id" : 0})
    for i in json_response:
        for attribute, value in i.items():
            for attr, val in value.items():
                for li in val:
                    cname_list.append(li['cname'])
    cname_list = list(dict.fromkeys(cname_list))
    #cid_list.sort()
    return cname_list


def validate(survey,company,email):
    col, db = mongoConnect("localhost", "Surveyapp", "userdetails", "user", "pwd")
    doc = list(col.find({"company": company, "survey": survey}, {"users": 0}))
    id = ""
    msg = ""
    for i in doc:
        id = i['_id']
        
    json_response = list(col.find({"company": company, "survey": survey}, {"users": 1.0, "_id": 0}))
    for i in json_response:
        for attribute, value in i.items():
            
            for val in value:
                if val['email'] == email:
                    if val['isValid'] == "False":
                        col.update({"_id": id, "users.email": email}, {"$set": {"users.$.isValid": "True"}})
                        return render_template('validatescreen.html')
                        msg = "done"
                    else:
                        return render_template('validatedscreen.html')
                        msg = "done"

    if msg == "":
        return "not a valid user to take survey"

def register(survey,company,email,username,password):
    col, db = mongoConnect("localhost", "Surveyapp", "userdetails", "user", "pwd")
    doc = list(col.find({"company": company, "survey": survey}, {"users": 0}))
    id = ""
    msg = ""
    for i in doc:
        id = i['_id']
    json_response = list(col.find({"company": company, "survey": survey}, {"users": 1.0, "_id": 0}))
    for i in json_response:
        for attribute, value in i.items():
            for val in value:
                if val['email'] == email:
                    if val['password'] == "":
                        response = col.update({"_id": id, "users.email": email}, {"$set": {"users.$.password": password, "users.$.username": username}})
                        print(response)
                        msg = "done"
                        return json.dumps({"status": '200', "message": "Registration is completed"})

                    else:
                        msg = "done"
                        return json.dumps({"status": '404', "message": "This email id is already registered."})

    if msg == "":
        return json.dumps({"status": '404', "message": "Not a valid user for registration"})



def userResponseload(data):
    col, db = mongoConnect("localhost", "Surveyapp", "users", "user", "pwd")
    ids = []
    keys = ["emailid","survey","company"]
    find_keys = dict((k, data[k]) for k in keys if k in data)
    #existing_doc = list(col.find({"emailid": check_emailid}))
    p = col.find(find_keys)
    for ppp in col.find(find_keys):
        ids.append(ppp["_id"])
    pp = loads(dumps(p))
    if pp!=[]:
        for id in ids:
            print(id)
            col.remove({"_id": id})
        #col.delete_one(existing_doc)
        col.insert(data)
        return "delete and insert"
    else:
        col.insert(data)
        return "document is inserted"

def saveUserResponse(data):
    print("done")

def userLogin(data, jsonFile):
    col, db = mongoConnect("localhost", "Surveyapp", "userdetails", "user", "pwd")
    print(data['email'])
    print(data['password'])
    with open(jsonFile) as json_data:
        js = json.load(json_data)
    jsonresponse = col.find({"users.email": data['email']}, {"_id": 0, "users": 0})
    survey = ""
    company = ""
    response = ""
    for i in jsonresponse:
        company = (i['company'])
        survey = (i['survey'])
    js["survey"] = survey
    js["company"] = company
    jsonresponses = col.find({"survey": survey, "company":company, "users.email": data['email']}, {"users": 1.0, "_id": 0})
    for j in jsonresponses:
        for k, l in j.items():
            for m in l:
                if m['email'] == data['email']:
                    print("yes")
                    js["users"].append(m)
                    js["isValid"] = m['isValid']
                    if m['role'] == "Admin":
                        js["isAdmin"] = "true"
                        print(js)

    return "done"
