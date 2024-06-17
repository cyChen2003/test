import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel, AutoConfig
from dataset import MyDataset
import os
os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"
# os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

class RegressiveTransformer(nn.Module):
    def __init__(self):
        super(RegressiveTransformer, self).__init__()
        model_path = "BAAI/bge-large-zh-v1.5"
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModel.from_pretrained(model_path,output_hidden_states=True)
        self.config = AutoConfig.from_pretrained(model_path)
        self.transformerEncoder = nn.TransformerEncoder(nn.TransformerEncoderLayer(d_model=self.config.hidden_size, nhead=8), num_layers=3)
        self.prediction_layer = nn.Linear(self.config.hidden_size, 1)
        self.embedding = nn.Embedding(11, self.config.hidden_size)
    def forward(self, encode_inputs , workYear, job_tag):
        #批处理的情况下，encode_inputs是一个字典
        input_ids = encode_inputs['input_ids']
        attention_mask = encode_inputs['attention_mask']
        outputs = []
        for i in range(len(input_ids)):
            tmp_output = self.model(input_ids[i], attention_mask=attention_mask[i])
            outputs.append(tmp_output)
        #转换成tensor
        outputs = torch.stack(outputs)
        last_hidden_state = outputs[0][:, 0]
        workYear = self.embedding(workYear)
        output_job_tag = []
        for i in range(len(job_tag)):
            tmp_output = self.model(job_tag[i]['input_ids'], attention_mask=job_tag[i]['attention_mask'])
            output_job_tag.append(tmp_output)
        job_tag = torch.stack(output_job_tag)
        #取平均job_tag平均
        job_tag = torch.mean(job_tag, dim=-2)
        job_tag = job_tag.unsqueeze(0)
        hidden_state = torch.cat([last_hidden_state, workYear, job_tag], dim=-2)
        hidden_state = self.transformerEncoder(hidden_state)
        hidden_state = self.prediction_layer(hidden_state)
        #取平均值作为输出
        hidden_state = torch.mean(hidden_state, dim=-1)
        return hidden_state
if __name__ == '__main__':
    data = MyDataset('../data/job_v1.csv')
    #分成训练集和测试集
    train_data, test_data = torch.utils.data.random_split(data, [int(len(data)*0.8), len(data)-int(len(data)*0.8)])
    train_loader = torch.utils.data.DataLoader(train_data, batch_size=3, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_data, batch_size=3, shuffle=False)
    model = RegressiveTransformer()
    # model = model.to('cuda')
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)
    for epoch in range(10):
        model.train()
        for i, (encode_inputs, workYear, job_tag, targets) in enumerate(train_loader):
            optimizer.zero_grad()
            # #将数据放到cuda上
            # encode_inputs = {k: v.to('cuda') for k, v in encode_inputs.items()}
            # workYear = workYear.to('cuda')
            # job_tag = [{k: v.to('cuda') for k, v in job_tag.items()}]
            # targets = targets.to('cuda')

            outputs = model(encode_inputs, workYear, job_tag)
            loss = criterion(outputs, targets.float())
            loss.backward()
            optimizer.step()
            if i % 10 == 0:
                print(f'epoch:{epoch}, step:{i}, loss:{loss.item()}')
        model.eval()
        with torch.no_grad():
            for i, (encode_inputs, workYear, job_tag, targets) in enumerate(test_loader):
                outputs = model(encode_inputs, workYear, job_tag)
                loss = criterion(outputs, targets.float())
                if i % 10 == 0:
                    print(f'epoch:{epoch}, step:{i}, loss:{loss.item()}')
