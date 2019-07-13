
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd 

data = pd.read_csv('MCM_NFLIS_Data.csv')

# data
# RangeIndex: 24062 entries, 0 to 24061
# Data columns(total 10 columns):
# YYYY                      24062 non-null int64
# State                     24062 non-null object
# COUNTY                    24062 non-null object
# FIPS_State                24062 non-null int64
# FIPS_County               24062 non-null int64
# FIPS_Combined             24062 non-null int64
# SubstanceName             24062 non-null object
# DrugReports               24062 non-null int64
# TotalDrugReportsCounty    24062 non-null int64
# TotalDrugReportsState     24062 non-null int64
# dtypes: int64(7), object(3)
# 
import scipy.stats as stats
import matplotlib.pyplot as plt
state = sorted(list(set(data['State'])))
year = sorted(list(set(data['YYYY'])))

fips = sorted(list(set(data['FIPS_Combined'])))
he_list = []
na_list = []
for i in range(len(fips)):
    f = fips[i]
    if i % 20 == 0:
        print(i)
    y_he = []
    y_na = []
    for y in year:
        y_he.append(np.sum(data['DrugReports'][(data.SubstanceName=='Heroin')\
         & (data.FIPS_Combined==f) & (data.YYYY==y)]))
        y_na.append(np.sum(data['DrugReports'][(data.SubstanceName!='Heroin')\
         & (data.FIPS_Combined==f) & (data.YYYY==y)]))
    y_he = np.array(y_he)
    y_na = np.array(y_na)
    he_list.append(y_he)
    na_list.append(y_na)

print('done first')


# In[171]:


def relate(a, b):
    #c = a / np.max(a)
    #d = b / np.max(b)
    #return np.linalg.norm(c-d)
    a_sub = a[1:]-a[:-1]
    b_sub = b[1:]-b[:-1]
    fenzi = a_sub @ b_sub
    fenmu = np.linalg.norm(a_sub) * np.linalg.norm(b_sub)
    return fenzi / fenmu
    
def fips_to_name(data, a):
    name = data['State'][data.FIPS_Combined==a]
    name = list(name)[0]
    name += ',' + list(data['COUNTY'][data.FIPS_Combined==a])[0]
    return name
count = 0
for i in range(len(na_list)):
    for j in range(len(na_list)):
        if i != j:
            #if np.sum(na_list[i]) > 5 and np.sum(na_list[j]) > 5:
            re = relate(na_list[i], na_list[j])
            if re > 0.97:
                plt.plot(year, na_list[i], marker='o', \
                    label=fips_to_name(data,fips[i]))
                plt.plot(year, na_list[j], marker='x', \
                    label=fips_to_name(data,fips[j]))
                plt.legend()
                plt.title(str(re))
                plt.show()
                count+=1
print(count)


# In[114]:


state = sorted(list(set(data.State)))
drug = sorted(list(set(data.SubstanceName)))
drug.remove('Heroin')
count = 0
#result_file = open('start_county.txt', 'w')
to_deal = []
for s in state:
    #for d in drug:
    for d in sorted(list(set(data['SubstanceName'][data.State==s]))):
        drug_trend = []
        for y in year:
            drug_trend.append(np.sum(data['DrugReports'][(data.State==s) \
                & (data.YYYY==y) & (data.SubstanceName==d)]))
        
        '''
        if drug_trend[0] == 0:
            county = sorted(list(set(data['COUNTY'][data.State==s])))
            tmp = np.array(drug_trend)
            if np.sum(tmp) == 0:
                print(s+','+d+': Never reported.')
                #content = s+','+d+': Never reported.\n'
                #result_file.write(content)
            else:
                first_appear = []
                y = np.array(year)[np.greater(tmp, 0)][0]
                for c in county:
                    if np.sum(data['DrugReports'][(data.State==s)\
                     & (data.YYYY==y) & (data.SubstanceName==d)\
                      & (data.COUNTY==c)]) > 0:
                        first_appear.append(c)
                #content = s+','+d+' first reported in '+str(y)+' in '\
                +str(first_appear)+'.\n'
                #result_file.write(content)
            #print(str(s)+','+str(d))
            #plt.plot(year, drug_trend, label=fips_to_name(data,fips[i]))
            #plt.legend()
            #plt.title(str(s)+','+str(d))
            #plt.show()
        else:
        '''

        if drug_trend[0] > 0:
            to_deal.append((s,d))
print(to_deal)
tmpp = []
for deal in to_deal:
    tmpp.append(deal[1])
tmpp = set(tmpp)
print(tmpp)


# In[70]:


count = 0
relations = []
for i in range(len(na_list)):
    for j in range(len(na_list)):
        if i != j:
            #if np.sum(na_list[i]) > 5 and np.sum(na_list[j]) > 5:
            re = relate(na_list[i], na_list[j])
            relations.append(re)
        else:
            relations.append(0.0)
print(len(relations))


# In[73]:


relations = np.array(relations)
relations = np.reshape(relations, [len(fips), len(fips)])
np.save('relations.npy', relations)


# In[75]:


a = np.load('relations.npy')
print(a)


# In[155]:


coordinates = np.load('../data_processed/new_coor.npy')
distances = []
for i in range(coordinates.shape[0]):
    for j in range(coordinates.shape[0]):
        distances.append(np.linalg.norm(coordinates[i]-coordinates[j]))
distances = np.array(distances)
distances = np.reshape(distances, [coordinates.shape[0], coordinates.shape[0]])
print(distances)


# In[164]:


threshold = np.mean(np.sort(distances)[:,10])
neighbor = np.less(distances, threshold).astype(np.int32)
neighbor -= np.eye(neighbor.shape[0], dtype=np.int32)
#np.save('neighbor.npy', neighbor)
print(np.where(np.greater(np.sort(distances)[:,1],2)))


# In[166]:


need_deal = tmpp
print(need_deal)
for d in need_deal:
    init_increase = []
    init_report = []
    y2 = year[-1]
    y1 = year[-2]
    for f in fips:
        report1 = np.sum(data['DrugReports'][(data.FIPS_Combined==f) \
            & (data.SubstanceName==d) & (data.YYYY==y1)])
        report2 = np.sum(data['DrugReports'][(data.FIPS_Combined==f) \
            & (data.SubstanceName==d) & (data.YYYY==y2)])
        if len(list(data['DrugReports'][(data.FIPS_Combined==f) \
            & (data.SubstanceName==d) & (data.YYYY==y1)])) > 1:
            print(error)
        init_increase.append(report2-report1)
        init_report.append(report2)
    init_increase = np.array(init_increase)
    init_report = np.array(init_report)
    np.save('data/pos/'+d+'_init_increase.npy', init_increase)
    np.save('data/pos/'+d+'_init_report.npy', init_report)
    

# In[167]:


deal_file = open('substances_to_deal.txt', 'w')
for d in need_deal:
    deal_file.write(d+' ')

