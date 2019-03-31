import matplotlib.pyplot as plt
import mpld3 as mp
import businessLogic as bl
import pandas as pd
import json
import numpy as np
from bson.json_util import dumps,loads


def calculate(R_df,colection):

  phy=R_df[R_df['subsector']=='Physical']
  org=R_df[R_df['subsector']=='Organisational']
  tech=R_df[R_df['subsector']=='Technical']
  phycid=phy.cid.unique()
  orgcid=org.cid.unique()
  techcid=tech.cid.unique()

  subs=['Physical','Organisational','Technical']
  host,base,colection,user,pwd=bl.mongoInit(colection)
  ## userid,survey,company  should be passed from UI with API
  ##userid='588'
  ##company='ITH'
  ##survey='Quater 1'

  x=df=pd.DataFrame()
  for sub in subs:
    subdf=R_df[R_df['subsector']==sub]
    subcid=subdf.cid.unique()

    for i in subcid:
      #  print("i value is ", i, sub)
        subscore=subdf[subdf.cid==i].qscore.sum()/len(subdf[subdf.cid==i].index)
        df=subdf[subdf.cid==i]
        df['cscore']=subscore
        x=pd.concat([df, x], ignore_index=True)
       # print(subcid)

  df=x.sort_values(['cid']) # df has mean values of cscore i.e category score in R1
 # print(df)
  return df


def pie(df):

    pieR1=df[df['sector']=='R1']['avgsectscore'].unique()
    pieR1= round(float(pieR1),2)

    pieR2=df[df['sector']=='R2']['avgsectscore'].unique()
    pieR2= round(float(pieR2),2)

    pieR3=df[df['sector']=='R3']['avgsectscore'].unique()
    pieR3= round(float(pieR3),2)

    pieR4=df[df['sector']=='R4']['avgsectscore'].unique()
    pieR4= round(float(pieR4),2)

    data = json.dumps({'R1': pieR1, 'R2': pieR2, 'R3':pieR3, 'R4':pieR4})
    return data


def bar(df):

    barR1=[]
    barR1.append(round(float(df[(df['sector']=='R1') & (df['subsector']=='Physical')]['subsector_avg'].unique()),2))
    barR1.append(round(float(df[(df['sector']=='R1') & (df['subsector']=='Organisational')]['subsector_avg'].unique()),2))
    barR1.append(round(float(df[(df['sector']=='R1') & (df['subsector']=='Technical')]['subsector_avg'].unique()),2))

    barR2=[]
    barR2.append(round(float(df[(df['sector']=='R2') & (df['subsector']=='Physical')]['subsector_avg'].unique()),2))
    barR2.append(round(float(df[(df['sector']=='R2') & (df['subsector']=='Organisational')]['subsector_avg'].unique()),2))
    barR2.append(round(float(df[(df['sector']=='R2') & (df['subsector']=='Technical')]['subsector_avg'].unique()),2))

    barR3=[]
    barR3.append(round(float(df[(df['sector']=='R3') & (df['subsector']=='Physical')]['subsector_avg'].unique()),2))
    barR3.append(round(float(df[(df['sector']=='R3') & (df['subsector']=='Organisational')]['subsector_avg'].unique()),2))
    barR3.append(round(float(df[(df['sector']=='R3') & (df['subsector']=='Technical')]['subsector_avg'].unique()),2))

    barR4=[]
    barR4.append(round(float(df[(df['sector']=='R4') & (df['subsector']=='Physical')]['subsector_avg'].unique()),2))
    barR4.append(round(float(df[(df['sector']=='R4') & (df['subsector']=='Organisational')]['subsector_avg'].unique()),2))
    barR4.append(round(float(df[(df['sector']=='R4') & (df['subsector']=='Technical')]['subsector_avg'].unique()),2))

    data = json.dumps({'R1': barR1, 'R2': barR2, 'R3':barR3, 'R4':barR4})
    return data

def radar(df):

    set1=set2=set3=[]
    set1=[ round(float(df[(df['sector']=='R1') & (df['subsector']=='Physical')]['subsector_avg'].unique()),2),
           round(float(df[(df['sector']=='R2') & (df['subsector']=='Physical')]['subsector_avg'].unique()),2),
           round(float(df[(df['sector']=='R3') & (df['subsector']=='Physical')]['subsector_avg'].unique()),2),
           round(float(df[(df['sector']=='R4') & (df['subsector']=='Physical')]['subsector_avg'].unique()),2)]

    set2=[ round(float(df[(df['sector']=='R1') & (df['subsector']=='Organisational')]['subsector_avg'].unique()),2),
           round(float(df[(df['sector']=='R2') & (df['subsector']=='Organisational')]['subsector_avg'].unique()),2),
           round(float(df[(df['sector']=='R3') & (df['subsector']=='Organisational')]['subsector_avg'].unique()),2),
           round(float(df[(df['sector']=='R4') & (df['subsector']=='Organisational')]['subsector_avg'].unique()),2)]

    set3=[ round(float(df[(df['sector']=='R1') & (df['subsector']=='Technical')]['subsector_avg'].unique()),2),
           round(float(df[(df['sector']=='R2') & (df['subsector']=='Technical')]['subsector_avg'].unique()),2),
           round(float(df[(df['sector']=='R3') & (df['subsector']=='Technical')]['subsector_avg'].unique()),2),
           round(float(df[(df['sector']=='R4') & (df['subsector']=='Technical')]['subsector_avg'].unique()),2)]

    data = json.dumps({'Physical': set1, 'Organisational': set2, 'Technical':set3 })
    return data

def radarBySector(df,sectors):
   set=[]
   setlabel=[]
   for sec in sectors:

       df1=df[df['sector']==sec]
       clist=df1.cid.unique()
       for i in clist:
           x=df1[df1['cid']==i]
           set.append(x['cscore'].unique())
           setlabel.append(x['cname'].unique())
           set=np.array(set).tolist()
           setlabel=np.array(setlabel).tolist()
           merged_list = []
           for l in set:
             merged_list += l
           merged_label = []
           for j in setlabel:
             merged_label += j
       if sec == 'R1':
         set1=merged_list
         label1=  merged_label
       elif sec == 'R2':
         set2=merged_list
         label2=  merged_label
       elif sec == 'R3':
         set3=merged_list
         label3=  merged_label
       elif sec == 'R4':
         set4=merged_list
         label4=  merged_label
       set=[]
       setlabel=[]

   data= [
           {"sector":"R1","labels":label1,"score":set1},
           {"sector":"R2","labels":label2,"score":set2},
           {"sector":"R3","labels":label3,"score":set3},
           {"sector":"R4","labels":label4,"score":set4}
         ]
   return dumps(data)



def radarAllSectors(df,sectors):
    set=[]
    setlabel=[]
    clist=df.cid.unique()
    for i in clist:
        x=df[df['cid']==i]

        set.append(x['cscore'].unique())
        setlabel.append(x['cname'].unique())
        set=np.array(set).tolist()
        setlabel=np.array(setlabel).tolist()
        merged_list = []
        for l in set:
          merged_list += l
        merged_label = []
        for j in setlabel:
          merged_label += j

    set=merged_list
    labels=  merged_label


    data = {
             "category":labels,
             "scores":set
        }


    return dumps(data)
