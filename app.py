import os
import streamlit as st
import pandas as pd
from io import StringIO
import zipfile
import uuid


uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
     # To read file as bytes:
    uniq = uuid.uuid4().hex
    name = uploaded_file.name.split(".")[0] 
    with zipfile.ZipFile(uploaded_file,"r") as z:
        z.extractall(f"./uploaded/{name}_{uniq}/")

    dataArray=[]
    for root, dirnames, filenames in os.walk(f"./uploaded/{name}_{uniq}/"):
        data = dict()
        if "user.csv" in filenames:
            folderName = root.split("/")
            data["participant"] = name
            data["Des-row"] = int(folderName[-1][8])
            
            # location
            df_temp = pd.read_csv(os.path.join(root,"location choice.csv")).to_dict()
            data["Zone Elapsed Time"] = df_temp["Elapsed Time"][0]
            data["Zone"] = df_temp["Zone"][0]
            data["Postcode"] = df_temp["Postcode"][0]
            data["Selected Location"] = df_temp["Selected Location"][0]
            # vehicle
            df_temp = pd.read_csv(os.path.join(root,"vehicle choice.csv")).to_dict()
            data["Vehicle Elapsed Time"] = df_temp["Elapsed Time"][0]
            data["Vehicle Choice"] = df_temp["Vehicle Choice"][0]
            # payment
            df_temp = pd.read_csv(os.path.join(root,"payment.csv")).to_dict()
            data["Payment Elapsed Time"] = df_temp["Elapsed Time"][0]
            data["Payment Option"] = df_temp["Payment Option"][0]
            
            # options
            df_temp = pd.read_csv(os.path.join(root,"options.csv")).to_dict(orient="records")
            
            data["Chat Elapsed Time"] = df_temp[0]["Elapsed Time"]
            data["Chat With Operator"] = df_temp[0]["Selected State"]
            
            data["CD Elapsed Time"] = df_temp[1]["Elapsed Time"]
            data["Change Destination"] = df_temp[1]["Selected State"]
            data["RTD Elapsed Time"] = df_temp[2]["Elapsed Time"]
            data["Real-Time Display"] = df_temp[2]["Selected State"]
            
            if len(df_temp) > 3:
                data["Chat2 Elapsed Time"] = df_temp[3]["Elapsed Time"]
                data["Chat2 With Operator"] = df_temp[3]["Selected State"]
            else:
                data["Chat2 Elapsed Time"] = ""
                data["Chat2 With Operator"] = ""
            dataArray.append(data)
    
    df = pd.DataFrame(dataArray)
    df_new = df.sort_values(by=["Des-row"]).reset_index().drop(columns=["index"])
    name = df_new.to_dict()["participant"][0]
    final_filename = name+"_final_data.xlsx"
    df_new.to_excel(final_filename,index=False)

    with open(final_filename, 'rb') as my_file:
        st.download_button(label = 'Download', data = my_file, file_name = final_filename, mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
