
# coding: utf-8

# In[47]:


import pandas as pd
import numpy as np


# In[48]:


def compute_corr(data1, data2, name1, name2):
    if type(data2[name2][0]) == type('ate'):
        return 0.0
    data = pd.merge(data1, data2, on='FIPS_Combined')
    tmp1 = data[name1]
    tmp2 = data[name2]
    corr = tmp1.corr(tmp2, method='pearson')
    if corr != corr:
        return 0.0
    return corr


# In[49]:


def trans(name, y):
    if y < 2013:
        t = pd.read_csv('tmp.csv')
    else:
        t = pd.read_csv('tmp1.csv')
    t.columns = ['a','b']
    return list(t['b'][t.a==name])[0]


# In[50]:


factors = set()
factor_raws = set()
report_data = pd.read_csv('trend_use.csv')
for y in range(2010,2017):
    print('year:',y)
    data2 = pd.read_csv('new_'+str(y)[2:]+'.csv')
    cols = list(data2.columns)
    for i in range(1, len(cols)):
        tmp_data = data2[[cols[0],cols[i]]]
        corr = compute_corr(report_data, tmp_data, 'NA_trend', cols[i])
        #print(corr)
        if np.abs(corr) > 0.75:
            info = trans(cols[i], y)
            #print(info, corr)
            factors.add(info[info.find(';')+2:info.find('-')-1])
            factor_raws.add((cols[i],y))
print(factors)
print(factor_raws)


# In[22]:


import random
def kmeans(data, k, threhold):
    # random select k initial points
    centers = []
    for i in range(k):
        index = random.randint(0, data.shape[0]-1)
        centers.append(data[index])
    count = 0
    while(True):
        l2_distances = []
        for i in range(k):
            l2_distance = np.linalg.norm(data-centers[i], axis=1)
            l2_distances.append(np.expand_dims(l2_distance,axis=-1))
        l2_distances = np.concatenate(l2_distances, axis=1)
        classify_result = np.argmin(l2_distances, axis=1)
        error = 0.0
        for i in range(k):
            class_data = data[classify_result==i]
            if class_data.shape[0] != 0:
                new_center = np.mean(class_data, axis=0)
                error += np.linalg.norm(centers[i] - new_center)
                centers[i] = new_center
        count += 1
        #print("Iteration:%d, Error:%f" %(count, error))
        if error < threhold:
            break
    #print(centers)
    return classify_result


# In[23]:


import numpy as np
import pandas as pd
tmp_data = pd.read_csv('MCM_NFLIS_Data.csv')
all_fips = sorted(list(set(tmp_data['FIPS_Combined'])))
class_features = []
for big_class in factors:
    features = []
    #count=0
    for factor_raw in factor_raws:
        info = trans(factor_raw[0], factor_raw[1])
        info = info[info.find(';')+2:info.find('-')-1]
        if info == big_class:
            #count+=1
            raw_data = pd.read_csv('new_'+str(factor_raw[1])[2:]+'.csv')
            tmp_list = []
            for fips in all_fips:
                tmp_list.append(np.array(raw_data[factor_raw[0]]\
                    [raw_data.FIPS_Combined == fips]))
            tmp_list = np.concatenate(tmp_list)
            #print(tmp_list.shape)
            if tmp_list.shape[0] == 461:
                features.append(tmp_list)
    features = np.stack(features).T
    print(features.shape)
    class_features.append(features)


# In[24]:


report_num_data = pd.read_csv('trend_use.csv')
report_num_np = []
for fips in all_fips:
    report_num_np.append(np.sum(report_num_data['NA_trend']\
        [report_num_data.FIPS_Combined==fips]))
report_num_np = np.array(report_num_np)


# In[46]:


class_num = 5
#for i in range(class_num):
b_value = np.zeros(report_num_np.shape)
for feature_ind in range(len(class_features)):
    classify = kmeans(class_features[feature_ind], class_num, 1e-7)
    scores = []
    for i in range(class_num):
        class_score = np.mean(report_num_np[classify==i])
        print(class_score)
        scores.append(class_score)
    arg_index = np.argsort(np.array(scores))
    for i in range(class_num):
        b_value[classify==i] += arg_index[i]
print(b_value)
np.save('b_value.npy', b_value/np.max(b_value))

