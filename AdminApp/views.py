from django.shortcuts import render
import pandas as pd
from sklearn.model_selection import train_test_split
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler


# Create your views here.
def index(request):
    return render(request,'index.html')

def AdminAction(request):
    uname=request.POST['username']
    passw=request.POST['password']
    if uname == 'Admin' and passw == 'Admin':
        return render(request,'AdminApp/AdminHome.html')
    else:
        context={'msg':'Admin Login Failed..!!'}
        return render(request,'AdminApp/index.html',context)

def AdminHome(request):
    return render(request,'AdminApp/AdminHome.html')

global data
def Upload(request):
    # global data
    # data=pd.read_csv("Dataset/sobar-72.csv", encoding='unicode_escape')
    # context={'data':data,'msg':'Dataset Loaded Successfully..!!'}
    return render(request,'AdminApp/Upload.html')
global df
def UploadAction(request):
    global df
    if request.method == 'POST':
        file = request.FILES['dataset']
        df = pd.read_csv(file)
        columns = df.columns.tolist()
        rows = df.head(10).values.tolist()
        context = {'columns': columns, 'rows': rows}
        return render(request, 'AdminApp/ViewDataset.html', context)

global X,  X_train, X_test, y_train, y_test,mappings
def preprocess(request):
    global df,X, X_train, X_test, y_train, y_test,mappings

    # Preprocessing
    df_cleaned = df.drop(columns=["Transaction_ID", "Customer_ID", "IP_Address", "Time_of_Transaction"])
    categorical_cols = ["Transaction_Type", "Device_Used", "Location", "Bank_Name", "Challenges", "Prospects",
                        "Cybercrime_Type"]
    mappings = {}

    for col in categorical_cols:
        unique_values = df_cleaned[col].unique()
        mappings[col] = {value: idx for idx, value in enumerate(unique_values)}
        df_cleaned[col] = df_cleaned[col].map(mappings[col])

    scaler = MinMaxScaler()
    df_cleaned[["Transaction_Amount"]] = scaler.fit_transform(df_cleaned[["Transaction_Amount"]])

    # Split features and target
    X = df_cleaned.drop(columns=["Cybercrime_Type"])
    y = df_cleaned["Cybercrime_Type"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Convert to NumPy arrays
    X_train = np.array(X_train)
    X_test = np.array(X_test)
    y_train = np.array(y_train)
    y_test = np.array(y_test)
    context={'data':str(len(df)),'train':str(len(X_train)), 'test':str(len(y_test))}
    return render(request, "AdminApp/Preprocess.html", context)

global adaacc,ada_model
def runANN(request):
    global X, y, X_train, X_test, y_train, y_test

    model = Sequential([
        Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dense(len(mappings["Cybercrime_Type"]), activation='softmax')
    ])
    # Compile model
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    # Train model
    history = model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test))
    # Save model
    model.save("Model/ANN_Cybercrime.h5")
    train_acc = history.history['acc'][-1]
    print(f"Model Accuracy: {train_acc * 100:.2f}%")
    context={'data':'Artificial Neural Network Model Generated Successfully..!!', 'acc': f"Model Accuracy: {train_acc * 100:.2f}%"}
    return render(request, "AdminApp/Algorithms.html", context)

