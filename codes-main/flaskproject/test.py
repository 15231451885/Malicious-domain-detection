import sys
import os
path=os.path.join(os.path.expanduser("~"), "%s" % "libsvm/libsvm-3.24/python".lower())
sys.path.append(path)
from preproc_3 import SVM_get_feature
from svmutil import *
from scale import scale
print("result:")
model= svm_load_model("model");
sv=model.get_SV()
url="baidu.com"
practical_label=[0]
f=SVM_get_feature(url)
f=scale("range.txt",f)
l = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41]
predict_pixel=[dict(zip(l,f))]
p_label, p_acc, p_val = svm_predict(practical_label, predict_pixel, model,'-b 1');
print(p_acc)
print(p_val[0][0])
print(p_label)

