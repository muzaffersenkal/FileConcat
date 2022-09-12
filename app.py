import os
import streamlit as st
import pandas as pd
from io import StringIO
import zipfile
import uuid
import py7zr

def get_only_folders(path):
    
    files = os.listdir(path)
    return list(filter(lambda x: os.path.isdir(os.path.join(path,x)), files))

def find_first_int(text): # to find block
    for i, c in enumerate(text):
        if c.isdigit():
            return i

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
     # To read file as bytes:
    uniq = uuid.uuid4().hex
    new_folder = f"./uploaded/{uniq}/"
    #name = uploaded_file.name.split(".")[0] 

    if uploaded_file.name.split(".")[-1]  == "7z":
        with py7zr.SevenZipFile(uploaded_file, mode='r') as z:
            z.extractall(new_folder)
    else:
        with zipfile.ZipFile(uploaded_file,"r") as z:
            z.extractall(new_folder)

    

    dataArray=[]

    experiments = get_only_folders(new_folder)

    for exp in experiments:
        experiment_folder = os.path.join(new_folder, exp)
        desRows = get_only_folders(experiment_folder)
        desRows = list(filter(lambda x:x.startswith("Des_row"), desRows))
    
        

        if  len(desRows) == 8:
    
            for d in desRows:
                root = os.path.join(experiment_folder, d)
                data = dict()
                
                if "user.csv" in os.listdir(root):
                    exSplit = exp.split()
                    data["fullName"] = exp
                    data["participant"] = exSplit[0]+ " " + exSplit[1] + exSplit[2]
                    
                    blockName = "".join(exSplit[-2:])
                    blockIntegerIndex = find_first_int(blockName)
                    blockName = blockName[blockIntegerIndex:]
                    data["Des-row"] = int(d.split()[-1].split("__")[0])
                    data["block"] = blockName

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

                    options = []
                    for opt in df_temp:

                        if opt["Option"] in options:
                            optName = opt["Option"]+ " Second"
                            data[optName] = opt["Selected State"]
                            data[optName + " Elapsed Time"] = opt["Elapsed Time"]
                        else:
                            optName = opt["Option"]
                            data[optName] = opt["Selected State"]
                            data[optName + " Elapsed Time"] = opt["Elapsed Time"]
                        options.append(opt["Option"])
                    dataArray.append(data)
    
    df = pd.DataFrame(dataArray)
    df_new = df.sort_values(by=["fullName","Des-row"]).reset_index().drop(columns=["index"])
    final_filename = "final_data.xlsx"
    df_new.to_excel(final_filename,index=False)

    with open(final_filename, 'rb') as my_file:
        st.download_button(label = 'Download', data = my_file, file_name = final_filename, mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
