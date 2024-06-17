import json
import os
import pandas as pd
from pandas import DataFrame
from typing import List

data_standard = {
    'jobId': '',
    'job_name': '',
    'job_tag': [],
    'districtString': '',
    'workYear': '',
    'degreeString': '',
    'industryType': '',
    'companyTypeString': '',
    'companySizeString': '',
    'companyName': '',
    'jobDescribe': '',
    'jobSalaryMin': '',
}
def preprocess(data_path):
    # 读取jsonl文件
    with open(data_path, 'r', encoding='utf-8') as f:
        data = f.readlines()
    # 解析jsonl文件
    data = [json.loads(line) for line in data]
    data_standard = []
    for i in range(len(data)):
        standard_dict = data_standard.copy()
        try:
            standard_dict = {
                # jobId设为Key
                'jobId': data[i]['jobId'],
                'job_name': data[i]['jobName'],
                'job_tag': data[i]['jobTags'],
                'districtString': data[i]['jobAreaLevelDetail']['districtString'] if 'jobAreaLevelDetail' in data[i] and 'districtString' in data[i]['jobAreaLevelDetail'] else '',
                'workYear': data[i]['workYear'] if 'workYear' in data[i] else '',
                'degreeString': data[i]['degreeString'] if 'degreeString' in data[i] else '',
                'industryType': data[i]['industryType1Str'] if 'industryType1Str' in data[i] else '',
                'companyTypeString': data[i]['companyTypeString'] if 'companyTypeString' in data[i] else '',
                'companySizeString': data[i]['companySizeString'] if 'companySizeString' in data[i] else '',
                'companyName': data[i]['companyName'] if 'companyName' in data[i] else '',
                'jobDescribe': data[i]['jobDescribe'] if 'jobDescribe' in data[i] else '',
                'jobSalaryMin': data[i]['jobSalaryMin'],
            }
        except Exception as e:
            #哪个字段出错了，则置为空
            print(f"the {i}th data has error {e}")
        data_standard.append(standard_dict)
    #以data_standard中的jobId为Key，去重
    data_standard = {data['jobId']: data for data in data_standard}.values()
    return data_standard
if __name__ == '__main__':
    data_path = 'job_v1.jsonl'
    data_standard = preprocess(data_path)
    #保存到csv文件中
    data_standard = pd.DataFrame(data_standard)
    data_standard.to_csv('job_v1.csv',index=False,encoding='utf-8')