import torch
import torch.nn as nn
import pandas as pd
from transformers import AutoTokenizer, AutoModel, AutoConfig
import os
import ast
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
class MyDataset(torch.utils.data.Dataset):
    def __init__(self, path):
        #读取csv数据
        self.data = pd.read_csv(path, encoding='utf-8')
        #将第二列job_tag单独取出来
        self.job_tag = self.data['job_tag'].values
        self.targets = self.data['jobSalaryMin'].values
        self.workYear = self.data['workYear'].values
        #将其他的列保存为data
        self.data = self.data.drop(columns=['job_tag', 'jobSalaryMin','jobId','workYear']).values
        #self.data为除了job_tag和targets的所有列
        self.tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-large-zh-v1.5")
    def __len__(self):
        return len(self.data)
    def __getitem__(self, idx):
        #将data[idx]转换成list
        data = self.data[idx].tolist()
        #如有空值，填充为“无”
        for i in range(len(data)):
            if pd.isnull(data[i]):
                data[i] = '无'

        inputs = self.tokenizer(data, padding="max_length",truncation=True, return_tensors='pt', max_length=512)

        workYear = torch.tensor([int(self.workYear[idx])])
        targets = torch.tensor([self.targets[idx]])

        job_tag = ast.literal_eval(self.job_tag[idx])
        #取job_tag的前三个标签,如果不足三个，填充为“无”
        while len(job_tag) < 3:
            job_tag.append('无')
        job_tag = job_tag[0:3]
        job_tag = self.tokenizer(job_tag, padding="max_length",truncation=True, return_tensors='pt', max_length=128)
        return inputs, workYear,  job_tag, targets

# if __name__ == '__main__':
#     dataset = MyDataset('../data/job_v1.csv')
#     print(dataset[0])

