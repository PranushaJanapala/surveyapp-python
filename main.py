from flask import Flask, request, render_template,jsonify
import requests
import businessLogic as bl
import os
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from shutil import copyfile
import chartsLogic as cl
from flask_mail import Mail, Message
import warnings
import time
import json
import numpy as np
import functools as ft
from bson import json_util
import xlrd
import pprint
import sqlalchemy
import matplotlib.pyplot as plt
import xlwt
from xlwt import Workbook

import base64
warnings.filterwarnings("ignore")
import smtplib
from flask_cors import CORS
from bson.json_util import dumps,loads

sectors=['R1','R2','R3','R4']
subsectors=['Physical','Organisational','Technical']
df=pd.DataFrame()
app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
cors = CORS(app)

@app.route('/')
def login():


    return "<u><b>Login Page</u></b>"
## Redirect to login page

@app.route('/questionsUpload', methods=['GET','POST'])
def questionsUpload():
    survey = request.args.get('survey')
    company = request.args.get('company')
    file = request.files['file']
    #file = xlrd.open_workbook("C:/Users/headway/PycharmProjects/untitled/questions.xlsx")
    df = pd.read_excel(file)

    #df.pop('category_id')

    list=df['category_name'].unique()
    cn=1
    print(df.columns)
    for i in list:
        df.loc[df['category_name'] == i, 'category_id'] = cn
        cn+=1

    df.category_id=df.category_id.astype(int)

    #print(df)
    #Getting timestamp
    backup=bl.getTimeStamp()
    
    #code pending for taking backup of this json
    jFile= 'C:/Users/v.subramani/Documents/WRKDIR/SurveyApp/surveyPython/db.json'
    jsonFile= 'C:/Users/v.subramani/Documents/WRKDIR/SurveyApp/surveyPython/db_{}.json'.format(backup)
    copyfile(jFile, jsonFile)

    #Parsing and divding into sector chunks of data from excel
    df_R1 = df[df['sector']=='R1']
    df_R2 = df[df['sector']=='R2']
    df_R3 = df[df['sector']=='R3']
    df_R4 = df[df['sector']=='R4']
    
    #initialize Mongo DB details or can be taken from a config file in future
    host='localhost'
    database='Surveyapp'
    collection='questions'
    user='root'
    pwd='Blackpearl'
    
    
    #update the db.json file with related info
    bl.parseDF(df_R1,df_R2,df_R3,df_R4,jsonFile,survey,company)
    
    #push json to mongo
    bl.pushMongoDB(host,database,collection,jsonFile,user,pwd,survey,company)
    
    #function to clean the workspace and close all handlers and files
    #bl.cleanup()
    
    return 'Upload Done -- replace this with web page'


@app.route('/usersUpload', methods=['GET','POST'])
def usersUpload():
    survey = request.args.get('survey')
    company = request.args.get('company')
    file = request.files['file']
    #file = xlrd.open_workbook("C:/Users/headway/PycharmProjects/untitled/user_details.xlsx")
    df = pd.read_excel(file)

    # Getting timestamp
    backup = bl.getTimeStamp()

    # code pending for taking backup of this json
    jFile = 'C:/Users/v.subramani/Documents/WRKDIR/SurveyApp/surveyPython/users.json'
    jsonFile = 'C:/Users/v.subramani/Documents/WRKDIR/SurveyApp/surveyPython/users_{}.json'.format(backup)
    copyfile(jFile, jsonFile)

    # Parsing and divding into sector chunks of data from excel
    #df_username = df[df['username']]


    # initialize Mongo DB details or can be taken from a config file in future
    host = 'localhost'
    database = 'Surveyapp'
    collection = 'userdetails'
    user = 'root'
    pwd = 'Blackpearl'

    # update the db.json file with related info
    bl.parseDFusers(df, jsonFile, survey, company)

    # push json to mongo
    bl.pushMongoDB(host, database, collection, jsonFile, user, pwd, survey, company)

    # function to clean the workspace and close all handlers and files
    # bl.cleanup()

    return 'Upload Done -- replace this with web page'

@app.route('/companyNames', methods=['GET', 'POST'])
def companyNames():
    companies_list = list(bl.getcompanynames())
    print(companies_list)
    return json.dumps(companies_list)

@app.route('/companySurveyNames', methods=['GET', 'POST'])
def companySurveyNames():
    company = request.args.get('company')
    #company = "company3"
    companysurveynames=list(bl.getcompanysurveynames(company))
    return json.dumps(companysurveynames)

@app.route('/departmentNames', methods=['GET', 'POST'])
def departmentNames():
    company = request.args.get('company')
    survey = request.args.get('survey')
    #company = "company3"
    #survey = "survey3"
    departmentnames=list(bl.getdepartmentnames(company, survey))
    return json.dumps(departmentnames)

@app.route('/releaseSurvey', methods=['GET', 'POST'])
def releaseSurvey():
    survey = request.args.get('survey')
    company = request.args.get('company')
    department = request.args.get('department')
    #url = request.args.get('url')

    #survey = "survey"
    #company = "company"
    #department = 'Deco'
    # bl.activateSurvey(survey,company,department)
    #mail_list=["vigneshsubramani28@gmail.com"]
    mail_list=list(bl.getMails(survey,company,department))
    sendmail(survey,company,mail_list)
    return 'sent email'

@app.route('/surveyQuestions', methods=['GET', 'POST'])
def surveyQuestions():
    survey = request.args.get('survey')
    company = request.args.get('company')
    sector = request.args.get('sector')
    subsector = request.args.get('subsector')
    cname = request.args.get('cname')
    #survey = "survey"
    #company = "company"
    #sector = "R1"
    #subsector = "Physical"
    #cname = "abc"
    questions = bl.displayquestions(survey,company,sector,subsector,cname)
    return json.dumps(questions, default=json_util.default)


@app.route('/categories', methods=['GET', 'POST'])
def categories():
    survey = request.args.get('survey')
    company = request.args.get('company')
    sector = request.args.get('sector')
    subsector = request.args.get('subsector')
    #survey = "survey"
    #company = "company"
    #sector = "R1"
    #subsector = "Physical"
    count = bl.getcategory(survey,company,sector,subsector)
    print(count)
    return json.dumps(count, default=json_util.default)



@app.route('/getAllPie', methods=['GET'])
def getAllPie():

    dataframe = request.args.get('dataframe')
    df=pd.read_excel(dataframe)
    data=cl.pie(df)
    return data


@app.route('/getAllBar', methods=['GET'])
def getAllBar():

    dataframe = request.args.get('dataframe')
    df=pd.read_excel(dataframe)
    data=cl.bar(df)
    return data



@app.route('/validation', methods=['GET', 'POST'])
def validation():
    survey = request.args.get('survey')
    company = request.args.get('company')
    email = request.args.get('email')
    #survey = "survey"
    #company = "company"
    #email = "pranushajanapaa@gmail.com"
    return bl.validate(survey,company,email)


@app.route('/Registration', methods=['GET', 'POST'])
def Registration():
    survey = request.args.get('survey')
    company = request.args.get('company')
    email = request.args.get('email')
    username =  request.args.get('username')
    password =  request.args.get('password')
    #survey = "survey"
    #company = "company"
    #email = "pranushajanapala@gmail.com"
    #username = "pranusha"
    #password = "pwd"
    return bl.register(survey,company,email,username,password)

@app.route('/getAllRadar', methods=['GET'])
def getAllRadar():

    dataframe = request.args.get('dataframe')
    df=pd.read_excel(dataframe)
    data=cl.radar(df)
    return data




@app.route('/userResponse', methods=['GET', 'POST'])
def userResponse():
    data = request.get_json()
    return bl.userResponseload(data)

@app.route('/saveResponse', methods=['GET', 'POST'])
def saveResponse():
    data = request.get_json()
    return bl.saveUserResponse(data)


@app.route('/getAllRadarBySector', methods=['GET'])
def getAllRadarBySector():

    dataframe = request.args.get('dataframe')
    df=pd.read_excel(dataframe)
    data=cl.radarBySector(df,sectors)
    return data


@app.route('/getSingleRadarAllSectors', methods=['GET'])
def getSingleRadarAllSectors():

    survey = request.args.get('survey')
    company = request.args.get('company')
    userid= request.args.get('userid')
    r = requests.get("http://127.0.0.1:5000/chartsOne?survey={}&company={}&userid={}".format(survey,company,userid))
    jsonres=r.json()
    df=pd.DataFrame(jsonres)
    df=df.sort_values(['sector','cid','subsector'])

    data=cl.radarAllSectors(df,sectors)
    return data



@app.route('/upload', methods=['GET', 'POST'])
def upload():
    folder_name = request.form['superhero']
    '''
    # this is to verify that folder to upload to exists.
    if os.path.isdir(os.path.join(APP_ROOT, 'files/{}'.format(folder_name))):
        print("folder exist")
    '''
    target = os.path.join(APP_ROOT, 'files/{}'.format(folder_name))
    print(target)
    if not os.path.isdir(target):
        os.mkdir(target)
    print(request.files.getlist("file"))
    for upload in request.files.getlist("file"):
        print(upload)
        print("{} is the file name".format(upload.filename))
        filename = upload.filename
        # This is to verify files are supported

        destination = "/".join([target, filename])
        print("Accept incoming file:", filename)
        print("Save it to:", destination)
        upload.save(destination)

    # return send_from_directory("images", filename, as_attachment=True)
    return render_template("complete.html", image_name=filename)




############################################################################################################################################
############################################################################################################################################

@app.route('/chartsAll', methods=['GET'])
def chartsAll():
    import time
    import xlwt
    from xlwt import Workbook
    survey = request.args.get('survey')
    company = request.args.get('company')
    host,base,colection,dbuser,pwd=bl.mongoInit('users')

    df=pd.DataFrame(columns=['sector','subsector','cid','qid','qscore','qconfidence'])
    for sector in sectors:
        document= bl.getSurveyDetailsAll(survey,company,host,base,colection,dbuser,pwd,sector)

        for i in document:
            df=df.append({'sector': i['rows']['sector'],'subsector':i['rows']['subsector'],'cid':i['rows']['cid'],'cname':i['rows']['cname'],'qid':i['rows']['qid'],'qscore':i['rows']['qscore'], 'qconfidence':i['rows']['qconfidence']},ignore_index=True)
    df=df.sort_values(['sector','subsector'])


    df['qconfidence'] = df['qconfidence'].astype(int)
    df['qscore'] = df['qscore'].astype(int)

    R1_df=df[df['sector']=='R1']
    R2_df=df[df['sector']=='R2']
    R3_df=df[df['sector']=='R3']
    R4_df=df[df['sector']=='R4']

    R1_df=cl.calculate(R1_df,colection)
    R2_df=cl.calculate(R2_df,colection)
    R3_df=cl.calculate(R3_df,colection)
    R4_df=cl.calculate(R4_df,colection)

    framelist=[R1_df,R2_df,R3_df,R4_df]
    mf=pd.DataFrame(columns=R1_df.columns.values)
    for i in framelist:
        phy=i[i['subsector']=='Physical']
        org=i[i['subsector']=='Organisational']
        tech=i[i['subsector']=='Technical']

        i['avgsectscore']=(phy.iloc[0]['cscore']+org.iloc[0]['cscore']+tech.iloc[0]['cscore'])/3
        mf=mf.append(i)
        mf.index = pd.RangeIndex(len(mf.index))

        avgR1_phy=mf[(mf['subsector']=='Physical') & (mf['sector']=='R1')].qscore.sum()/len(mf[(mf['subsector']=='Physical') & (mf['sector']=='R1')])

    avgR1_phy=mf[(mf['subsector']=='Physical') & (mf['sector']=='R1')].qscore.sum()/len(mf[(mf['subsector']=='Physical') & (mf['sector']=='R1')])
    avgR1_org=mf[(mf['subsector']=='Organisational') & (mf['sector']=='R1')].qscore.sum()/len(mf[(mf['subsector']=='Organisational') & (mf['sector']=='R1')])
    avgR1_tech=mf[(mf['subsector']=='Technical') & (mf['sector']=='R1')].qscore.sum()/len(mf[(mf['subsector']=='Technical') & (mf['sector']=='R1')])

    avgR2_phy=mf[(mf['subsector']=='Physical') & (mf['sector']=='R2')].qscore.sum()/len(mf[(mf['subsector']=='Physical') & (mf['sector']=='R2')])
    avgR2_org=mf[(mf['subsector']=='Organisational') & (mf['sector']=='R2')].qscore.sum()/len(mf[(mf['subsector']=='Organisational') & (mf['sector']=='R2')])
    avgR2_tech=mf[(mf['subsector']=='Technical') & (mf['sector']=='R2')].qscore.sum()/len(mf[(mf['subsector']=='Technical') & (mf['sector']=='R2')])

    avgR3_phy=mf[(mf['subsector']=='Physical') & (mf['sector']=='R3')].qscore.sum()/len(mf[(mf['subsector']=='Physical') & (mf['sector']=='R3')])
    avgR3_org=mf[(mf['subsector']=='Organisational') & (mf['sector']=='R3')].qscore.sum()/len(mf[(mf['subsector']=='Organisational') & (mf['sector']=='R3')])
    avgR3_tech=mf[(mf['subsector']=='Technical') & (mf['sector']=='R3')].qscore.sum()/len(mf[(mf['subsector']=='Technical') & (mf['sector']=='R3')])

    avgR4_phy=mf[(mf['subsector']=='Physical') & (mf['sector']=='R4')].qscore.sum()/len(mf[(mf['subsector']=='Physical') & (mf['sector']=='R4')])
    avgR4_org=mf[(mf['subsector']=='Organisational') & (mf['sector']=='R4')].qscore.sum()/len(mf[(mf['subsector']=='Organisational') & (mf['sector']=='R4')])
    avgR4_tech=mf[(mf['subsector']=='Technical') & (mf['sector']=='R4')].qscore.sum()/len(mf[(mf['subsector']=='Technical') & (mf['sector']=='R4')])



   # mf[(mf['subsector']=='Physical') & (mf['sector']=='R1')]['subsector_avg']=avgR1_phy
   ## mf['subsector_avg'] = np.where(  (mf['subsector']=='Physical') & (mf['sector']=='R1'))

    filter1 = mf[(mf['subsector']=='Physical') & (mf['sector']=='R1')]
    filter1['subsector_avg']=avgR1_phy

    filter2 = mf[(mf['subsector']=='Organisational') & (mf['sector']=='R1')]
    filter2['subsector_avg']=avgR1_org

    filter3 = mf[(mf['subsector']=='Technical') & (mf['sector']=='R1')]
    filter3['subsector_avg']=avgR1_tech

    filter4 = mf[(mf['subsector']=='Physical') & (mf['sector']=='R2')]
    filter4['subsector_avg']=avgR2_phy

    filter5 = mf[(mf['subsector']=='Organisational') & (mf['sector']=='R2')]
    filter5['subsector_avg']=avgR2_org

    filter6 = mf[(mf['subsector']=='Technical') & (mf['sector']=='R2')]
    filter6['subsector_avg']=avgR2_tech

    filter7 = mf[(mf['subsector']=='Physical') & (mf['sector']=='R3')]
    filter7['subsector_avg']=avgR3_phy

    filter8 = mf[(mf['subsector']=='Organisational') & (mf['sector']=='R3')]
    filter8['subsector_avg']=avgR3_org

    filter9 = mf[(mf['subsector']=='Technical') & (mf['sector']=='R3')]
    filter9['subsector_avg']=avgR3_tech

    filter10 = mf[(mf['subsector']=='Physical') & (mf['sector']=='R4')]
    filter10['subsector_avg']=avgR4_phy

    filter11 = mf[(mf['subsector']=='Organisational') & (mf['sector']=='R4')]
    filter11['subsector_avg']=avgR4_org

    filter12 = mf[(mf['subsector']=='Technical') & (mf['sector']=='R4')]
    filter12['subsector_avg']=avgR4_tech

    dfs=[filter1,filter2,filter3,filter4,filter5,filter6,filter7,filter8,filter9,filter10,filter11,filter12]
    df=pd.concat(dfs)

    time=int(time.time())
    uniqId=545 ## Sent from UI later.. can be admin userid
    fileName='dataframe_{}.xlsx'.format(time)
    wb = Workbook()
    sheet1 = wb.add_sheet('Sheet 1')
    wb.save(fileName)

    writer = ExcelWriter(fileName)
    df.to_excel(writer,'Sheet1',index=False)
    writer.save()

    return fileName



############################################################################################################################################
############################################################################################################################################







@app.route('/chartsOne', methods=['GET'])
def chartsOne():

    survey = request.args.get('survey')
    company = request.args.get('company')
    userid= request.args.get('userid')
    host,base,colection,dbuser,pwd=bl.mongoInit('users')


    df=pd.DataFrame(columns=['sector','subsector','cid','qid','qscore','qconfidence'])
    for sector in sectors:
        document= bl.getSurveyDetails(userid,survey,company,host,base,colection,dbuser,pwd,sector)
        for i in document:
            df=df.append({'sector': i['rows']['sector'],'subsector':i['rows']['subsector'],'cid':i['rows']['cid'],'cname':i['rows']['cname'],'qid':i['rows']['qid'],'qscore':i['rows']['qscore'], 'qconfidence':i['rows']['qconfidence']},ignore_index=True)
    df=df.sort_values(['sector','subsector'])


    df['qconfidence'] = df['qconfidence'].astype(int)
    df['qscore'] = df['qscore'].astype(int)


    R1_df=df[df['sector']=='R1']
    R2_df=df[df['sector']=='R2']
    R3_df=df[df['sector']=='R3']
    R4_df=df[df['sector']=='R4']

    R1_df=cl.calculate(R1_df,colection)
    R2_df=cl.calculate(R2_df,colection)
    R3_df=cl.calculate(R3_df,colection)
    R4_df=cl.calculate(R4_df,colection)

    framelist=[R1_df,R2_df,R3_df,R4_df]
    mf=pd.DataFrame(columns=R1_df.columns.values)
    for i in framelist:
        phy=i[i['subsector']=='Physical']
        org=i[i['subsector']=='Organisational']
        tech=i[i['subsector']=='Technical']

        i['avgsectscore']=(phy.iloc[0]['cscore']+org.iloc[0]['cscore']+tech.iloc[0]['cscore'])/3
        mf=mf.append(i)
        mf.index = pd.RangeIndex(len(mf.index))

        avgR1_phy=mf[(mf['subsector']=='Physical') & (mf['sector']=='R1')].qscore.sum()/len(mf[(mf['subsector']=='Physical') & (mf['sector']=='R1')])

    avgR1_phy=mf[(mf['subsector']=='Physical') & (mf['sector']=='R1')].qscore.sum()/len(mf[(mf['subsector']=='Physical') & (mf['sector']=='R1')])
    avgR1_org=mf[(mf['subsector']=='Organisational') & (mf['sector']=='R1')].qscore.sum()/len(mf[(mf['subsector']=='Organisational') & (mf['sector']=='R1')])
    avgR1_tech=mf[(mf['subsector']=='Technical') & (mf['sector']=='R1')].qscore.sum()/len(mf[(mf['subsector']=='Technical') & (mf['sector']=='R1')])

    avgR2_phy=mf[(mf['subsector']=='Physical') & (mf['sector']=='R2')].qscore.sum()/len(mf[(mf['subsector']=='Physical') & (mf['sector']=='R2')])
    avgR2_org=mf[(mf['subsector']=='Organisational') & (mf['sector']=='R2')].qscore.sum()/len(mf[(mf['subsector']=='Organisational') & (mf['sector']=='R2')])
    avgR2_tech=mf[(mf['subsector']=='Technical') & (mf['sector']=='R2')].qscore.sum()/len(mf[(mf['subsector']=='Technical') & (mf['sector']=='R2')])

    avgR3_phy=mf[(mf['subsector']=='Physical') & (mf['sector']=='R3')].qscore.sum()/len(mf[(mf['subsector']=='Physical') & (mf['sector']=='R3')])
    avgR3_org=mf[(mf['subsector']=='Organisational') & (mf['sector']=='R3')].qscore.sum()/len(mf[(mf['subsector']=='Organisational') & (mf['sector']=='R3')])
    avgR3_tech=mf[(mf['subsector']=='Technical') & (mf['sector']=='R3')].qscore.sum()/len(mf[(mf['subsector']=='Technical') & (mf['sector']=='R3')])

    avgR4_phy=mf[(mf['subsector']=='Physical') & (mf['sector']=='R4')].qscore.sum()/len(mf[(mf['subsector']=='Physical') & (mf['sector']=='R4')])
    avgR4_org=mf[(mf['subsector']=='Organisational') & (mf['sector']=='R4')].qscore.sum()/len(mf[(mf['subsector']=='Organisational') & (mf['sector']=='R4')])
    avgR4_tech=mf[(mf['subsector']=='Technical') & (mf['sector']=='R4')].qscore.sum()/len(mf[(mf['subsector']=='Technical') & (mf['sector']=='R4')])



   # mf[(mf['subsector']=='Physical') & (mf['sector']=='R1')]['subsector_avg']=avgR1_phy
   ## mf['subsector_avg'] = np.where(  (mf['subsector']=='Physical') & (mf['sector']=='R1'))

    filter1 = mf[(mf['subsector']=='Physical') & (mf['sector']=='R1')]
    filter1['subsector_avg']=avgR1_phy

    filter2 = mf[(mf['subsector']=='Organisational') & (mf['sector']=='R1')]
    filter2['subsector_avg']=avgR1_org

    filter3 = mf[(mf['subsector']=='Technical') & (mf['sector']=='R1')]
    filter3['subsector_avg']=avgR1_tech

    filter4 = mf[(mf['subsector']=='Physical') & (mf['sector']=='R2')]
    filter4['subsector_avg']=avgR2_phy

    filter5 = mf[(mf['subsector']=='Organisational') & (mf['sector']=='R2')]
    filter5['subsector_avg']=avgR2_org

    filter6 = mf[(mf['subsector']=='Technical') & (mf['sector']=='R2')]
    filter6['subsector_avg']=avgR2_tech

    filter7 = mf[(mf['subsector']=='Physical') & (mf['sector']=='R3')]
    filter7['subsector_avg']=avgR3_phy

    filter8 = mf[(mf['subsector']=='Organisational') & (mf['sector']=='R3')]
    filter8['subsector_avg']=avgR3_org

    filter9 = mf[(mf['subsector']=='Technical') & (mf['sector']=='R3')]
    filter9['subsector_avg']=avgR3_tech

    filter10 = mf[(mf['subsector']=='Physical') & (mf['sector']=='R4')]
    filter10['subsector_avg']=avgR4_phy

    filter11 = mf[(mf['subsector']=='Organisational') & (mf['sector']=='R4')]
    filter11['subsector_avg']=avgR4_org

    filter12 = mf[(mf['subsector']=='Technical') & (mf['sector']=='R4')]
    filter12['subsector_avg']=avgR4_tech

    dfs=[filter1,filter2,filter3,filter4,filter5,filter6,filter7,filter8,filter9,filter10,filter11,filter12]
    df=pd.concat(dfs)

    js=df.to_json()
    print(df)

    return js






############################################################################################################################################
############################################################################################################################################


@app.route('/chartsByDept', methods=['GET'])
def chartsByDept():
    import time
    import xlwt
    from xlwt import Workbook
    survey = request.args.get('survey')
    company = request.args.get('company')
    dept = request.args.get('department')
    host,base,colection,dbuser,pwd=bl.mongoInit('users')

    df=pd.DataFrame(columns=['sector','subsector','cid','qid','qscore','qconfidence'])
    for sector in sectors:
        document= bl.getSurveyDetailsByDept(survey,company,host,base,colection,dbuser,pwd,sector,dept)

        for i in document:
            df=df.append({'sector': i['rows']['sector'],'subsector':i['rows']['subsector'],'cid':i['rows']['cid'],'cname':i['rows']['cname'],'qid':i['rows']['qid'],'qscore':i['rows']['qscore'], 'qconfidence':i['rows']['qconfidence']},ignore_index=True)
    df=df.sort_values(['sector','subsector'])


    df['qconfidence'] = df['qconfidence'].astype(int)
    df['qscore'] = df['qscore'].astype(int)

    R1_df=df[df['sector']=='R1']
    R2_df=df[df['sector']=='R2']
    R3_df=df[df['sector']=='R3']
    R4_df=df[df['sector']=='R4']

    R1_df=cl.calculate(R1_df,colection)
    R2_df=cl.calculate(R2_df,colection)
    R3_df=cl.calculate(R3_df,colection)
    R4_df=cl.calculate(R4_df,colection)

    framelist=[R1_df,R2_df,R3_df,R4_df]
    mf=pd.DataFrame(columns=R1_df.columns.values)
    for i in framelist:
        phy=i[i['subsector']=='Physical']
        org=i[i['subsector']=='Organisational']
        tech=i[i['subsector']=='Technical']

        i['avgsectscore']=(phy.iloc[0]['cscore']+org.iloc[0]['cscore']+tech.iloc[0]['cscore'])/3
        mf=mf.append(i)
        mf.index = pd.RangeIndex(len(mf.index))

        avgR1_phy=mf[(mf['subsector']=='Physical') & (mf['sector']=='R1')].qscore.sum()/len(mf[(mf['subsector']=='Physical') & (mf['sector']=='R1')])

    avgR1_phy=mf[(mf['subsector']=='Physical') & (mf['sector']=='R1')].qscore.sum()/len(mf[(mf['subsector']=='Physical') & (mf['sector']=='R1')])
    avgR1_org=mf[(mf['subsector']=='Organisational') & (mf['sector']=='R1')].qscore.sum()/len(mf[(mf['subsector']=='Organisational') & (mf['sector']=='R1')])
    avgR1_tech=mf[(mf['subsector']=='Technical') & (mf['sector']=='R1')].qscore.sum()/len(mf[(mf['subsector']=='Technical') & (mf['sector']=='R1')])

    avgR2_phy=mf[(mf['subsector']=='Physical') & (mf['sector']=='R2')].qscore.sum()/len(mf[(mf['subsector']=='Physical') & (mf['sector']=='R2')])
    avgR2_org=mf[(mf['subsector']=='Organisational') & (mf['sector']=='R2')].qscore.sum()/len(mf[(mf['subsector']=='Organisational') & (mf['sector']=='R2')])
    avgR2_tech=mf[(mf['subsector']=='Technical') & (mf['sector']=='R2')].qscore.sum()/len(mf[(mf['subsector']=='Technical') & (mf['sector']=='R2')])

    avgR3_phy=mf[(mf['subsector']=='Physical') & (mf['sector']=='R3')].qscore.sum()/len(mf[(mf['subsector']=='Physical') & (mf['sector']=='R3')])
    avgR3_org=mf[(mf['subsector']=='Organisational') & (mf['sector']=='R3')].qscore.sum()/len(mf[(mf['subsector']=='Organisational') & (mf['sector']=='R3')])
    avgR3_tech=mf[(mf['subsector']=='Technical') & (mf['sector']=='R3')].qscore.sum()/len(mf[(mf['subsector']=='Technical') & (mf['sector']=='R3')])

    avgR4_phy=mf[(mf['subsector']=='Physical') & (mf['sector']=='R4')].qscore.sum()/len(mf[(mf['subsector']=='Physical') & (mf['sector']=='R4')])
    avgR4_org=mf[(mf['subsector']=='Organisational') & (mf['sector']=='R4')].qscore.sum()/len(mf[(mf['subsector']=='Organisational') & (mf['sector']=='R4')])
    avgR4_tech=mf[(mf['subsector']=='Technical') & (mf['sector']=='R4')].qscore.sum()/len(mf[(mf['subsector']=='Technical') & (mf['sector']=='R4')])



   # mf[(mf['subsector']=='Physical') & (mf['sector']=='R1')]['subsector_avg']=avgR1_phy
   ## mf['subsector_avg'] = np.where(  (mf['subsector']=='Physical') & (mf['sector']=='R1'))

    filter1 = mf[(mf['subsector']=='Physical') & (mf['sector']=='R1')]
    filter1['subsector_avg']=avgR1_phy

    filter2 = mf[(mf['subsector']=='Organisational') & (mf['sector']=='R1')]
    filter2['subsector_avg']=avgR1_org

    filter3 = mf[(mf['subsector']=='Technical') & (mf['sector']=='R1')]
    filter3['subsector_avg']=avgR1_tech

    filter4 = mf[(mf['subsector']=='Physical') & (mf['sector']=='R2')]
    filter4['subsector_avg']=avgR2_phy

    filter5 = mf[(mf['subsector']=='Organisational') & (mf['sector']=='R2')]
    filter5['subsector_avg']=avgR2_org

    filter6 = mf[(mf['subsector']=='Technical') & (mf['sector']=='R2')]
    filter6['subsector_avg']=avgR2_tech

    filter7 = mf[(mf['subsector']=='Physical') & (mf['sector']=='R3')]
    filter7['subsector_avg']=avgR3_phy

    filter8 = mf[(mf['subsector']=='Organisational') & (mf['sector']=='R3')]
    filter8['subsector_avg']=avgR3_org

    filter9 = mf[(mf['subsector']=='Technical') & (mf['sector']=='R3')]
    filter9['subsector_avg']=avgR3_tech

    filter10 = mf[(mf['subsector']=='Physical') & (mf['sector']=='R4')]
    filter10['subsector_avg']=avgR4_phy

    filter11 = mf[(mf['subsector']=='Organisational') & (mf['sector']=='R4')]
    filter11['subsector_avg']=avgR4_org

    filter12 = mf[(mf['subsector']=='Technical') & (mf['sector']=='R4')]
    filter12['subsector_avg']=avgR4_tech

    dfs=[filter1,filter2,filter3,filter4,filter5,filter6,filter7,filter8,filter9,filter10,filter11,filter12]
    df=pd.concat(dfs)

    time=int(time.time())
    uniqId=545 ## Sent from UI later.. can be admin userid
    fileName='dataframe_{}.xlsx'.format(time)
    wb = Workbook()
    sheet1 = wb.add_sheet('Sheet 1')
    wb.save(fileName)

    writer = ExcelWriter(fileName)
    df.to_excel(writer,'Sheet1',index=False)
    writer.save()

    return fileName

############################################################################################################################################





############################################################################################################################################
############################################################################################################################################


@app.route('/getSinglePie', methods=['GET'])
def getSinglePie():

    survey = request.args.get('survey')
    company = request.args.get('company')
    userid= request.args.get('userid')
    print(survey,company,userid)
    #r = requests.get("http://127.0.0.1:5000/chartsOne?survey='Quarter%201'&company='ITH'&userid='588'")
    r = requests.get("http://127.0.0.1:5000/chartsOne?survey={}&company={}&userid={}".format(survey,company,userid))


    jsonres=r.json()
    df=pd.DataFrame(jsonres)

    data=cl.pie(df)
    return data


@app.route('/getSingleBar', methods=['GET'])
def getSingleBar():

    survey = request.args.get('survey')
    company = request.args.get('company')
    userid= request.args.get('userid')

    r = requests.get("http://127.0.0.1:5000/chartsOne?survey={}&company={}&userid={}".format(survey,company,userid))
    jsonres=r.json()
    df=pd.DataFrame(jsonres)

    data=cl.bar(df)
    return data


@app.route('/getSingleRadar', methods=['GET'])
def getSingleRadar():

    survey = request.args.get('survey')
    company = request.args.get('company')
    userid= request.args.get('userid')

    r = requests.get("http://127.0.0.1:5000/chartsOne?survey={}&company={}&userid={}".format(survey,company,userid))
    jsonres=r.json()
    df=pd.DataFrame(jsonres)

    data=cl.radar(df)
    return data




@app.route('/getSingleRadarBySector', methods=['GET'])
def getSingleRadarBySector():

    survey = request.args.get('survey')
    company = request.args.get('company')
    userid= request.args.get('userid')
#    sector= request.args.get('sector')

    r = requests.get("http://127.0.0.1:5000/chartsOne?survey={}&company={}&userid={}".format(survey,company,userid))
    jsonres=r.json()
    df=pd.DataFrame(jsonres)

    data=cl.radarBySector(df,sectors)
    return data


@app.route('/getSingleTable', methods=['GET'])
def getSingleTable():

    survey = request.args.get('survey')
    company = request.args.get('company')
    userid= request.args.get('userid')
    r = requests.get("http://127.0.0.1:5000/chartsOne?survey={}&company={}&userid={}".format(survey,company,userid))
    jsonres=r.json()
    df=pd.DataFrame(jsonres)
    df=df.sort_values(['sector','cid','subsector'])
    df=df[df['sector']=='R1']



    data=dumps(df)
    return data







@app.route('/temp', methods=['GET', 'POST'])
def temp():
   file = request.files['file']
   df = pd.read_excel(file)
   #print(df)
   return 'done'

def sendmails(survey,company,department,email):
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'pranushajanapala@gmail.com'
    app.config['MAIL_PASSWORD'] = 'sreerama1234'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_DEFAULT_SENDER'] = 'pranushajanapala@gmail.com'
    mail=Mail(app)
    for addr in email:
        mails = ' '.join(addr)
        print("BK")
        #print(company,survey,addr)
        msg = Message("Survey Request", recipients=mails)
        msg.body = "Dear member,\n" \
                   "" \
                   "" \
                   "you have been picked for taking the survey by $company and the link is a follows below." \
                   "http://localhost:3001/validation?company={}&survey={}&email={}".format(company, survey, mails[0])

        mail.send(msg)


@app.route('/userlogin', methods=['GET', 'POST'])
def userlogin():
    data = request.get_json()
    jsonFile = 'C:/Users/headway/PycharmProjects/untitled/sessionTemplate.json'
    bl.userLogin(data, jsonFile)
    return "nothing"


def sendmail(survey,company,mails):
    to = mails
    gmail_user = 'pranushajanapala@gmail.com'
    gmail_pwd = 'sreerama1234'
    smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(gmail_user,gmail_pwd)

    for mail in to:

        subject ="Survey Request".format(mail)
        smtpserver.login(gmail_user, gmail_pwd)
        header = "cfhj"
        msg = "Dear member,\n" \
                   "\n" \
                   "\n" \
                   "you have been picked for taking the survey by {} and the link is a follows below.\n"\
                   "http://localhost:5000/validation?company={}&survey={}&email={}".format(company, company, survey, mail)
        smtpserver.sendmail(gmail_user, mail, msg, header

                            )

    smtpserver.close()





if __name__ == '__main__':
    app.run(debug=True)
