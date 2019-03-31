import pandas as pd
import businessLogic as bl
import sys, os
from shutil import copyfile

survey = sys.argv[1]
company = sys.argv[2]
filename = sys.argv[3]

#Needs to be updated from config file
path='C:/Users/bhara/Desktop/workspace'

filepath=os.path.join(path, filename)

#Getting timestamp
backup=bl.getTimeStamp()

#code pending for taking backup of this json
jFile= 'C:/Users/bhara/Desktop/workspace/db.json'
jsonFile= 'C:/Users/bhara/Desktop/workspace/db_{}.json'.format(backup)
copyfile(jFile, jsonFile)

# Parsing excel data
xl = pd.read_excel(path+'/'+filename)

#Parsing and divding into sector chunks of data from excel
df_R1 = xl[xl['sector']=='R1']
df_R2 = xl[xl['sector']=='R2']
df_R3 = xl[xl['sector']=='R3']
df_R4 = xl[xl['sector']=='R4']

#initialize Mongo DB details or can be taken from a config file in future
host='localhost'
database='BKBASE'
collection='questions'
user='root'
pwd='Blackpearl'


#update the db.json file with related info
bl.parseDF(df_R1,df_R2,df_R3,df_R4,jsonFile,survey,company)

#push json to mongo
bl.pushMongoDB(host,database,collection,jsonFile,user,pwd,survey,company)

#function to clean the workspace and close all handlers and files
#bl.cleanup()
