# Mirrors the notebook's "Inferencing using Flask API" cells against the forwarded backend URL.
import sys, json, requests, pandas as pd
model_root_url = sys.argv[1]
model_url = model_root_url + "/v1/predict"
model_batch_url = model_root_url + "/v1/predictbatch"
print("model_root_url:", model_root_url)
payload = {
  "Product_Weight": 12.66,
  "Product_Sugar_Content": "Low Sugar",
  "Product_Allocated_Area": 0.027,
  "Product_MRP": 117.08,
  "Store_Size": "Medium",
  "Store_Location_City_Type": "Tier 2",
  "Store_Type": "Supermarket Type2",
  "Product_Id_char": "FD",
  "Store_Age_Years": 16,
  "Product_Type_Category": "Non Perishables"
}
response = requests.post(model_url, json=payload)
print("SINGLE status:", response.status_code)
print("SINGLE json:", response.json())
batch_dataset = pd.read_csv("deploy/Batch_Data_SuperKart.csv")
batch_input = {'file': batch_dataset.to_csv(header=True, index=False).encode('utf-8')}
response = requests.post(model_batch_url, files=batch_input)
print("BATCH response:", response)
print("BATCH text:", response.text)
