import streamlit as st
import pandas as pd
from DBconnect import get_database_session
from json import loads
from pathlib import Path

st.write("Test File")
df=pd.read_csv(Path("./extras/stock_info.csv"), encoding='utf8')
st.table(df)
result = df.to_json(orient="records")
st.write(result)

# test = poms_db()
# client=test.get_client()
# st.write("Hi : ",client.list_database_names())

test = get_database_session()
st.write("Databases details: ",test.list_database_names())

pims_db = test["pims_db"]
st.write("POMS collection details: ",pims_db.list_collection_names())

stock_table = pims_db['stock_table']
if not stock_table.count_documents({}):
    stock_table.insert_many(loads(result))
    # st.write(type(loads(result)))
st.write("Stock table row count: ",stock_table.count_documents({}))

test_frommongo = pd.DataFrame(list(stock_table.find({},{"_id": 0})))
st.table(test_frommongo)

# Update a value

# if stock_table.count_documents({'stock':'Bread'}):
#     st.write(stock_table.find({'stock':'Bread'})[0])
    
stock_table.update_one(
    { 'stock' : 'Bread'},
    {
      '$set' : { 'quantity' : 7 }  
    } 
)