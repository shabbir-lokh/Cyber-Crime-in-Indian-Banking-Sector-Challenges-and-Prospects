from django.shortcuts import render
import sqlite3
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder,StandardScaler
import tensorflow as tf
import numpy as np

# Create your views here.
def login(request):
    return render(request,'UserApp/Login.html')
def register(request):
    return render(request,'UserApp/register.html')

def Userction(request):
    username=request.POST.get('username')
    password=request.POST.get('password')
    con = sqlite3.connect("banking.db")
    cur=con.cursor()
    cur.execute("select *  from user where username='"+username+"'and password='"+password+"'")
    data=cur.fetchone()
    if data is not None:
        request.session['user']=data[2]
        request.session['userid']=data[0]
        return render(request,'UserApp/UserHome.html')
    else:
        context={'data':'Login Failed ....!!'}
        return render(request,'UserApp/Login.html',context)
def UserHome(request):
    return render(request,'UserApp/UserHome.html')

def RegAction(request):
    name=request.POST['name']
    email=request.POST['email']
    mobile=request.POST['mobile']
    address=request.POST['address']
    username=request.POST['username']
    password=request.POST['password']

    con = sqlite3.connect("banking.db")
    cur=con.cursor()
    #cur.execute("CREATE TABLE user (ID INTEGER PRIMARY KEY AUTOINCREMENT,name varchar(100),email varchar(100),mobile varchar(100),address varchar(100) ,username varchar(100),password varchar(100))")
    con.commit()
    cur.execute("select * from user where email='"+email+"'")
    d=cur.fetchone()
    if d is None:
        i=cur.execute("insert into user values(null,'"+name+"','"+email+"','"+mobile+"','"+address+"','"+username+"','"+password+"')")
        con.commit()
        con.close()
        if i == 0:
            context = {'data': 'Registration Failed...!!'}
            return render(request,'UserApp/register.html',context)
        else:
            context = {'data': 'Registration Successful...!!'}
            return render(request,'UserApp/register.html',context)
    else:
        context={'data':'Email Already Exist...!!'}
        return render(request,'UserApp/register.html',context)


def DetectFraud(request):
    path = "Dataset/cybercrime_banking.csv"
    df2 = pd.read_csv(path)
    df2.dropna(inplace=True)

    a = 0
    Transaction_Type = ""
    for d in df2['Transaction_Type'].unique():
        Transaction_Type += "<option value=" + str(a) + ">" + d + "</option>"
        a += 1
    Transaction_Type += ""

    b = 0
    Device_Used = ""
    for s in df2['Device_Used'].unique():
        Device_Used += "<option value="+str(b)+">" + s + "</option>"
        b += 1
    Device_Used += ""

    c = 0
    Location = ""
    for s in df2['Location'].unique():
        Location += "<option value=" + str(c) + ">" + s + "</option>"
        c += 1
    Location += ""
    d = 0
    Bank_Name = ""
    for s in df2['Bank_Name'].unique():
        Bank_Name += "<option value=" + str(d) + ">" + s + "</option>"
        d += 1
    Bank_Name += ""

    f = 0
    Challenges = ""
    for s in df2['Challenges'].unique():
        Challenges += "<option value=" + str(f) + ">" + s + "</option>"
        f += 1
    Challenges += ""

    g = 0
    Prospects = ""
    for s in df2['Prospects'].unique():
        Prospects += "<option value=" + str(g) + ">" + s + "</option>"
        g += 1
    Prospects += ""

    context={"Prospects":Prospects,"Challenges":Challenges,"Transaction_Type":Transaction_Type,"Device_Used":Device_Used,"Location":Location,"Bank_Name":Bank_Name}
    return render(request,'UserApp/DetectFraud.html',context)



def PredAction(request):
    g=request.POST['amount']
    a=request.POST['Transaction_Type']
    m=request.POST['Fraudulent']
    d=request.POST['Device_Used']
    lt=request.POST['Location']
    Lg=request.POST['Bank_Name']
    Cha = request.POST['Challenges']
    Pros = request.POST['Prospects']

    da = g + "," + a + "," + m + "," + d + "," + lt + "," + Lg + "," + Cha+ "," + Pros
    inputt = 'Transaction_Amount,Transaction_Type,Fraudulent,Device_Used,Location,Bank_Name,Challenges,Prospects\n'
    inputt += da + "\n"

    f = open("Dataset/test.txt", "w")
    f.write(inputt)
    f.close()

    test = pd.read_csv("Dataset/test.txt")

    test_data = test.values[:, 0:8]

   # Load the trained model
    loaded_model = tf.keras.models.load_model('Model/ANN_Cybercrime.h5')

    test_data = np.array(test_data).reshape(1, -1)  # Reshape for ANN
    prediction = loaded_model.predict(test_data)
    p = np.argmax(prediction, axis=1)[0]

    output=""
    if p==0:
        output="Data Breach"
    elif p == 1:
        output = "Non-Fraud"
    elif p == 2:
        output = "DDoS Attacks"
    elif p == 3:
        output = "Phishing"
    elif p == 4:
        output = "Ransomware"
    elif p == 5:
        output = "Malware"
    else:
        output = "Insider Threats"
    context={"data":output}
    return render(request, 'UserApp/PredictedData.html', context)

