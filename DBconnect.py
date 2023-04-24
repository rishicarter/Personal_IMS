from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import streamlit as st

username = st.secrets['DB_USERNAME']
password = st.secrets['DB_PASSWORD']

uri = f"mongodb+srv://{username}:{password}@cluster0.r9atf7b.mongodb.net/poms_db?retryWrites=true&w=majority"


@st.cache_resource
def get_database_session():
    session = MongoClient(uri, server_api=ServerApi('1'))
    return session

# class poms_db:
    
#     def __init__(self) -> None:
#         # Create a new client and connect to the server
#         self.client = MongoClient(uri, server_api=ServerApi('1'))
#     def get_client(self) -> MongoClient:
#         return self.client
    
#     def test_connect_db(self):
#         # Send a ping to confirm a successful connection
#         try:
#             with st.spinner('Waiting for ping...'):
#                 self.client.admin.command('ping')
#             st.success("Pinged your deployment. You successfully connected to MongoDB!")
#         except Exception as e:
#             st.error(e)
            
    # todo: CRUD handling functions
