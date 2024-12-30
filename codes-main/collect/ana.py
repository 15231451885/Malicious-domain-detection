import os
import pandas as pd
import json

data_dict = {'data': [], 'datetime': []}

data_2 = []#统计来源的字典数组
exclude = set(['__pycache__'])
for root,dirs,filenames in os.walk(os.path.join(os.path.expanduser("~"), "%s" % "mytest".lower()),topdown=True):
    dirs[:] = [d for d in dirs if d not in exclude]
    print(filenames)
    print(root)

#数据总量，按时间统计
for filename in sorted(filenames):
    csv_data = pd.read_csv(root+'/'+filename,names=["addr","type","source"])
    csv_df = pd.DataFrame(csv_data)
    csv_df = csv_df["addr"]
    csv_df.drop_duplicates(inplace=True)
    print(csv_df.shape[0])
    ftime=filename[:-4]
    data_dict["data"].append(csv_df.shape[0])
    data_dict["datetime"].append(ftime)
with open(os.path.join(os.path.join(os.path.expanduser("~"), "%s" % "anadata".lower()),"data.json"),'w') as dump_f:
    json.dump(data_dict,dump_f)

df = pd.DataFrame(columns = ["source", 0])
#按来源统计数据量
for filename in sorted(filenames):
    csv_data = pd.read_csv(root+'/'+filename,names=["addr","type","source"])
    csv_df = pd.DataFrame(csv_data)
    csv_df.drop_duplicates(inplace=True)
    print(csv_df.shape[0])

    csv_df = csv_df.groupby('source').size()#按来源分组并计数
    csv_df = csv_df.reset_index()#添加索引
    csv_df =csv_df.drop(csv_df[csv_df[0]<1000].index)
    csv_df = csv_df.reset_index(drop=True)
    for i in range(csv_df.shape[0]):
        flag=0
        for j in range(df.shape[0]):
            if df.iloc[j,0]==csv_df.iloc[i,0]:
                df.iloc[j,1]+=csv_df.iloc[i,1]
                flag=1
        if flag==0:
            t=csv_df.iloc[[i]]
            df=df.append(t)
            pass
        # data_dict2 = {'data': [], 'source': []}#新增了一个字典统计来源
        # data_dict2["source"].append(csv_df.iloc[i,0])
        # data_dict2["data"].append(float(csv_df.iloc[i,1]))
        # data_2.append(data_dict2)
df.rename(columns = {0 : "num"},inplace=True)
data_2={col:df[col].tolist() for col in df.columns}
l=len(data_2["num"])
for i in range(l):
    data_2["num"][i]=int(data_2["num"][i])
with open(os.path.join(os.path.join(os.path.expanduser("~"), "%s" % "anadata".lower()),"data2.json"),'w') as dump_f:
    json.dump(data_2,dump_f)
