# 导入socket模块
import socket
import sys
import os
import threading
import time
path=os.path.join(os.path.expanduser("~"), "%s" % "static/libsvm/python".lower())
sys.path.append(path)
from preproc_3 import SVM_get_feature
from svmutil import *
from scale import scale

model= svm_load_model("model");
#
# url="baidu.com"
practical_label=[0]

class MyThread(threading.Thread):
    def run(self):
        while 1:
            # 创建tcp服务端套接字
            # 参数同客户端配置一致，这里不再重复
            tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # 设置端口号复用，让程序退出端口号立即释放，否则的话在30秒-2分钟之内这个端口是不会被释放的，这是TCP的为了保证传输可靠性的机制。
            tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

            # 给客户端绑定端口号，客户端需要知道服务器的端口号才能进行建立连接。IP地址不用设置，默认就为本机的IP地址。
            tcp_server.bind(("", 5002))

            # 设置监听
            # 128:最大等待建立连接的个数， 提示： 目前是单任务的服务端，同一时刻只能服务与一个客户端，后续使用多任务能够让服务端同时服务与多个客户端
            # 不需要让客户端进行等待建立连接
            # listen后的这个套接字只负责接收客户端连接请求，不能收发消息，收发消息使用返回的这个新套接字tcp_client来完成
            tcp_server.listen(128)

            # 等待客户端建立连接的请求, 只有客户端和服务端建立连接成功代码才会解阻塞，代码才能继续往下执行
            # 1. 专门和客户端通信的套接字： tcp_client
            # 2. 客户端的ip地址和端口号： tcp_client_address
            tcp_client, tcp_client_address = tcp_server.accept()

            # 代码执行到此说明连接建立成功
            print("客户端的ip地址和端口号:", tcp_client_address)

            # 接收客户端发送的数据, 这次接收数据的最大字节数是1024
            recv_data = tcp_client.recv(1024)

            # 对服务器发来的数据进行解码保存到变量recv_content中
            recv_content = recv_data.decode(encoding="utf-8")
            print("接收客户端的数据为:", recv_content)
            url = recv_content
            f = SVM_get_feature(url)
            f = scale("range.txt", f)
            l = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
            31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41]
            predict_pixel = [dict(zip(l, f))]
            p_label, p_acc, p_val = svm_predict(practical_label, predict_pixel, model, '-b 1');
            if p_label[0] == 1:
                r = "Safe"
                p = p_val[0][0]
                send_data = ("safe   "+"possiblity:  "+str(p)).encode(encoding="utf-8")
            else:
                r = "risk"
                p = p_val[0][1]
                send_data = ("risk   " + "possiblity:  " + str(p)).encode(encoding="utf-8")
            # 准备要发送给服务器的数据


            # 发送数据给客户端
            tcp_client.send(send_data)

            # 关闭服务与客户端的套接字， 终止和客户端通信的服务
            tcp_client.close()

            # 关闭服务端的套接字, 终止和客户端提供建立连接请求的服务 但是正常来说服务器的套接字是不需要关闭的，因为服务器需要一直运行。
            # tcp_server.close()
def test():
    while 1:
        t = MyThread()
        t.run()
if __name__ == '__main__':
    test()
