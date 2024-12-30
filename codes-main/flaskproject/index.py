from flask import Flask, render_template, request
import sys
import json
import os


# path=os.path.join(os.path.expanduser("~"), "%s" % "libsvm/libsvm-3.24/python".lower())
path=os.path.join(os.path.expanduser("~"), "%s" % "static/libsvm/python".lower())
sys.path.append(path)
from preproc_3 import SVM_get_feature
from svmutil import *
from scale import scale

model= svm_load_model("model");
#
# url="baidu.com"
practical_label=[0]
# f=SVM_get_feature(url)
# f=scale("range.txt",f)
# l = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41]
# predict_pixel=[dict(zip(l,f))]
# p_label, p_acc, p_val = svm_predict(practical_label, predict_pixel, model,'-b 1');
# print(p_acc)
# print(p_val[0][0])
# print(p_label)



with open(os.path.join(os.path.join(os.path.expanduser("~"), "%s" % "anadata".lower()),"data.json"),'r') as load_f:
    data_dict = json.load(load_f)
app = Flask(__name__)

#打开文件data2.json
with open(os.path.join(os.path.join(os.path.expanduser("~"), "%s" % "anadata".lower()),"data2.json"),'r') as load_f:
    data_dict2 = json.load(load_f)
app = Flask(__name__)

@app.route('/')
def index():
    my_dict = data_dict
    my_dict2 = data_dict2
    # render_template方法:渲染模板
    # 参数1: 模板名称  参数n: 传到模板里的数据
    return render_template('hello.html',
                           my_dict=my_dict,my_dict2=my_dict2)

@app.route('/result',methods = ['POST', 'GET'])
def result():

   if request.method == 'POST':
      result = request.form
      url=result.to_dict()['Name']
      f=SVM_get_feature(url)
      f=scale("range.txt",f)
      l = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41]
      predict_pixel=[dict(zip(l,f))]
      p_label, p_acc, p_val = svm_predict(practical_label, predict_pixel, model,'-b 1');
      # print(p_acc)
      # print(p_val[0][0])
      # print(p_label)
      if p_label[0]==1:
          r="Safe"
          p=p_val[0][0]
      else:
          r="risk"
          p=p_val[0][1]
      return render_template("result.html",p = p,r=r)



if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=False)
