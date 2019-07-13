import numpy as np
import pandas as pd
import random
import os

class county(object):
    def __init__(self, fips, init_self_increase, \
        report_num, increase_count, b_value, a_value):
        self.fips = fips
        self.last_increase = init_self_increase
        self.report_num = report_num
        self.increase_count = increase_count
        self.b_value = b_value
        self.a_value = a_value

    def _get_self_increase(self):
        # linear increasing in a county itself
        mu = 1.0
        sigma = 0.2
        increase = random.normalvariate(mu, sigma) * self.last_increase  
        return increase

    def update(self, neighbor_influence): 
        # consist of two parts: self increase and neighbor influence
        # return total increase
        if self.report_num <= 0:
            return 0
        self_increase = self._get_self_increase()
        self_coeff = random.normalvariate(0.5, 0.1)
        neighbor_coeff = 1-self_coeff
        total_increase = np.rint(self_increase*self_coeff + \
                                        neighbor_influence*neighbor_coeff)
        #if random.random() < 0.1:
        #    self.report_num -= total_increase
        #else:
        #    self.report_num += total_increase
        if random.random() < self.b_value**(self.increase_count/self.a_value):
            self.report_num += total_increase
        else:
            total_increase = random.normalvariate(0.0,0.4) * total_increase
            self.report_num -= total_increase
        if total_increase > 0:
            self.increase_count += 1
        else:
            self.increase_count -= 0
        return total_increase

def _get_neighbor_influence(last_increases, neighbors, relation):
    # return a dict: fips: neighbor increase
    all_fips = list(last_increases.keys())
    neighbor_influence = dict()
    for fips in all_fips:
        #coeff*relation
        influence = 0.0
        neighbor_fips = neighbors[fips]
        for n_fips in neighbor_fips:
            coeff = random.normalvariate(0.3,0.1)
            influence += relation[fips][n_fips]*coeff*last_increases[n_fips]
        influence = np.rint(influence)
        neighbor_influence[fips] = influence
    return neighbor_influence

def simulate(init_increases, init_reports, neighbors, \
    relation, increase_count, a_value, b_value):
    # init_increases: a dict: fips to init_increases
    counties = []
    last_increase = init_increases.copy()
    all_fips = list(init_increases.keys())
    for fips in all_fips:
        counties.append(county(fips, init_increases[fips], init_reports[fips], 
                        increase_count[fips], a_value[fips], b_value[fips]))
    simulate_years = 30
    results = [] # each entry is the result of a year, stored in a dict
    for _ in range(simulate_years):
        # simulate one year
        neighbor_influence = _get_neighbor_influence(last_increase, \
            neighbors, relation)
        result = dict()
        for i in range(len(counties)):
            fips = counties[i].fips
            increase = counties[i].update(neighbor_influence[fips])
            last_increase[fips] = increase
            result[fips] = counties[i].report_num
        results.append(result)
    return results

def load_data(substance_name):
    init_increases = dict()
    init_reports = dict()
    neighbor = dict()
    relations = dict()
    increase_count = dict()
    a_value = dict()
    b_value = dict()
    increase_data = np.load('data/pos/'+substance_name+'_init_increase.npy')
    report_data = np.load('data/pos/'+substance_name+'_init_report.npy')
    relation_data = np.load('relations.npy')
    neighbor_data = np.load('neighbor.npy')
    increase_count_data = np.load('increase_count.npy')
    a_value_data = np.load('a_value.npy')
    b_value_data = np.load('b_value.npy')
    all_fips = _get_fips()
    for i in range(len(all_fips)):
        fips = all_fips[i]
        init_increases[fips] = increase_data[i] 
        init_reports[fips] = report_data[i]
        increase_count[fips] = increase_count_data[i]
        a_value[fips] = a_value_data[i]
        b_value[fips] = b_value_data[i]
        dict_tmp = dict()
        list_tmp = []
        for j in range(len(all_fips)):
            dict_tmp[all_fips[j]] = relation_data[i][j]
            if neighbor_data[i][j] == 1:
                list_tmp.append(all_fips[j])
        relations[fips] = dict_tmp
        neighbor[fips] = list_tmp
    return init_increases, init_reports, neighbor, relations, \
    increase_count, a_value, b_value


def write_result(substacne_name, results):
    all_fips = sorted(list(results[0].keys()))
    result_npy = []
    for fips in all_fips:
        for i in range(len(results)):
            result_npy.append(results[i][fips])
    result_npy = np.array(result_npy)
    result_npy = np.reshape(result_npy, [len(all_fips), -1])
    if not os.path.exists('results/prob2/pos/'):
        os.makedirs('results/prob2/pos')
    np.save('results/prob2/pos/'+substacne_name+'.npy' , result_npy)

def _get_fips():
    data = pd.read_csv('MCM_NFLIS_Data.csv')
    fips = sorted(list(set(data['FIPS_Combined'])))
    return fips

def _get_substances():
    substance_file = open('substances_to_deal.txt')
    for line in substance_file:
        substances = line.split(' ')
    return substances

if __name__ == '__main__':
    substances = _get_substances()[:-1]
    for substance in substances:
        init_increases, init_reports, neighbors, relation, \
        increase_count, a_value, b_value = load_data(substance)
        results = simulate(init_increases, init_reports, \
            neighbors, relation, increase_count, a_value, b_value)
        write_result(substance, results)
        print(substance)
    #test()
    