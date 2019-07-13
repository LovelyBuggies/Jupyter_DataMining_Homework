
# coding: utf-8

# In[6]:


import numpy as np
import os
import pandas as pd 
import matplotlib.pyplot as plt
data = pd.read_csv('../MCM_NFLIS_Data.csv')
all_fips = sorted(list(set(data['FIPS_Combined'])))
files = os.listdir('./')
files = [f for f in files if f[-4:] == '.npy']
print(files)


# In[7]:


def fips_to_name(data, a):
    name = data['State'][data.FIPS_Combined==a]
    name = list(name)[0]
    name += ',' + list(data['COUNTY'][data.FIPS_Combined==a])[0]
    return name


# In[37]:


year = list(range(2000,2018))
for ind in range(len(files)):
    result = np.load(files[ind])
    for i in range(len(all_fips)): 
        if np.sum(np.abs(result[i])) > 0:
            to_plot = list(result[i])
            to_plot.reverse()
            ori = []
            d = files[ind][:-4]
            f = all_fips[i]
            for y in list(range(2010,2018)):
                ori.append(np.sum(data['DrugReports'][(data.SubstanceName==d) \
                    & (data.FIPS_Combined==f) & (data.YYYY==y)]))
            to_plot = to_plot + ori
            #print(to_plot)
            plt.plot(year, to_plot, marker='o', label=d)
            plt.legend()
            plt.title(fips_to_name(data, f))
            plt.show()


# In[79]:


year = list(range(2010,2048))
for ind in range(len(files)):
    result = np.load('pos/'+files[ind])
    for i in range(len(all_fips)): 
        if np.max(np.abs(result[i])) > 20:
            to_plot = list(result[i])
            ori = []
            d = files[ind][:-4]
            f = all_fips[i]
            for y in list(range(2010,2018)):
                ori.append(np.sum(data['DrugReports'][(data.SubstanceName==d) \
                    & (data.FIPS_Combined==f) & (data.YYYY==y)]))
            to_plot = ori + to_plot
            #print(to_plot)
            plt.plot(year, to_plot, marker='o', label=d)
            plt.legend()
            plt.title(fips_to_name(data, f))
            plt.show()


# In[78]:


year = list(range(2010,2048))
for ind in range(len(files)):
    result = np.load('prob2/pos/'+files[ind])
    for i in range(len(all_fips)): 
        if np.max(np.abs(result[i])) > 20:
            to_plot = list(result[i])
            ori = []
            d = files[ind][:-4]
            f = all_fips[i]
            for y in list(range(2010,2018)):
                ori.append(np.sum(data['DrugReports'][(data.SubstanceName==d) \
                    & (data.FIPS_Combined==f) & (data.YYYY==y)]))
            to_plot = ori + to_plot
            #print(to_plot)
            plt.plot(year, to_plot, marker='o', label=d)
            plt.legend()
            plt.title(fips_to_name(data, f))
            plt.show()


# In[63]:


states = [51,39,42,21,54]
file_write = open('start_county1.txt', 'w')
for ind in range(len(files)):
    result = np.load(files[ind])
    for state in states:
        first_year = 2010
        county_list = []
        for j in range(10):
            for i in range(len(all_fips)):
                if all_fips[i] // 1000 == state:
                    if j == 0 and result[i][j] <= 0:
                        first_year = 2009
                        county_list.append(fips_to_name(data, all_fips[i]))
                    elif j > 0 and j < 9:
                        if result[i][j] > 0 and result[i][j+1] <= 0:
                            if first_year != 2009 - j:
                                first_year = 2009 - j
                                county_list = [fips_to_name(data, all_fips[i])]
                            else:
                                county_list.append(fips_to_name(data, all_fips[i]))
                    else:
                        if result[i][j] > 0:
                            if first_year != 1998:
                                first_year = 1998
                                county_list = [fips_to_name(data, all_fips[i])]
                            else:
                                county_list.append(fips_to_name(data, all_fips[i]))
        
        file_write.write(str(state)+','+files[ind][:-4]+' first reported in '\
            +str(first_year)+' in '+str(county_list)+'\n')


# In[86]:


year = list(range(2010,2038))
count = 0
for ind in range(len(files)):
    result = np.load('pos/'+files[ind])[:,:20]
    for i in range(len(all_fips)): 
        #if np.sum(np.abs(result[i])) > 20:
        if np.max(np.abs(result[i])) > 500:
            to_plot = list(result[i])
            ori = []
            d = files[ind][:-4]
            f = all_fips[i]
            for y in list(range(2010,2018)):
                ori.append(np.sum(data['DrugReports'][(data.SubstanceName==d) \
                    & (data.FIPS_Combined==f) & (data.YYYY==y)]))
            to_plot = ori + to_plot
            #print(to_plot)
            #plt.plot(year, to_plot, marker='o', label=d)
            #plt.legend()
            #plt.title(fips_to_name(data, f))
            #plt.show()
            print(d, fips_to_name(data, f), np.where(result[i]>500)[0][0]+2010)
print(count)

