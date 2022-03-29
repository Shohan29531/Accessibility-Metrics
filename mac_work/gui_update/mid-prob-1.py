import csv

from datetime import datetime
 

X_train=[]
with open('data_train_midterm_problem1.csv', 'r', encoding="latin-1") as csvfile:
    reader = csv.reader(csvfile)
    i=0
    
    for row in reader:
        data=[]
        i=i+1
        if i==1:
            continue
        for j in range(2):  
            if(j==0):
                date = datetime.strptime(row[j], '%m-%d-%Y')
                data.append(date)
            elif(j==1):
                data.append(float(row[j]))
        X_train.append(data)  

print(X_train)