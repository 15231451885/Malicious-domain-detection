

def MaxMinNormalization(x,Max,Min):

    x = (x - Min) / (Max - Min);
    return x;
def scale(file,l):
    with open(file) as f:
        f.readline()
        f.readline()
        i=0
        for line in f.readlines():
            line=line.strip()
            index,Min,Max=line.split(' ')
            l[i]=MaxMinNormalization(l[i],float(Max),float(Min))
            i=i+1
    return l

