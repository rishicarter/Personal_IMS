# Imports
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from extras.DBconnect import get_database_session

# Functions ---------------
# @st.cache_data
def get_quantity_from_choice(df,choice):
    return df[df['stock']==choice]['quantity'].values[0]
def get_category_from_choice(df,choice):
    return df[df['stock']==choice]['category'].values[0]

def refresh_data(comp=st):
    col1,col2=comp.columns(2)
    col1.success('Data Added Successfully!!')
    with col2:
        with st.spinner('Refreshing data...'):
            # time.sleep(1)
            st.experimental_rerun()

#--------------------------

# App Config
st.set_page_config(
    page_title="IMS App",
    page_icon="🍗",
    layout="centered",
    initial_sidebar_state='expanded',
    menu_items={
        'About': "# App to organise, manage and plan stock requirements!"
    }
)

########################################################
# Handling DB actions
with st.spinner('Wait for DB Connection...'):
    client = get_database_session()
# if isinstance(stock_table_session, int) or not stock_table_session.server_info()['ok']:
# st.write(stock_table_session.server_info())
if isinstance(client, int) or not client.server_info()['ok']:
    # TODO manual entry
    pass

stock_table = client.pims_db.stock_table

########################################################

# App Brief
st.title('Personal Food Stock Management System!')
st.subheader('App to organise, manage and plan food stock requirements.')

# TODO: File handling using data_upload.py
# filepath='./stock_info.csv'
# filepath=os.path.abspath('stock_info.csv')
# main_df=pd.read_csv(filepath, encoding="utf8")

main_df=pd.DataFrame(list(stock_table.find({}, {'_id':0})))

# TODO: Remove duplicacy in df

# Sidebar Filtering
df_categories=main_df['category'].unique()
selected_categories=st.sidebar.multiselect("Filter the Categories", df_categories)
df=main_df.copy()
if selected_categories:
    df=df[df['category'].isin(selected_categories)].reset_index(drop=True)
# df_table=st.dataframe(df)

# Data Viz
viz_container=st.container()
plt.style.use('dark_background')
fig_viz,ax_viz=plt.subplots()
ax_viz=sns.barplot(data=df,x='stock',y='quantity',hue='category',dodge=False)
for i in ax_viz.containers:
    ax_viz.bar_label(i,)
plt.title("Items present in Stock")
plt.xticks(rotation=-80)
plt.xlabel('')
plt.ylabel("Quantity")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
viz_container.pyplot(fig_viz)
with viz_container.expander('Show Table'):
    df_table=st.dataframe(df, use_container_width=True)

# Data Add/Update
tab_update,tab_add,tab_free=st.tabs(["Update Stock","Add Stock","Full Control"])
with tab_update:
    update_container=st.container()
    with update_container:
        all_items=list(df['stock'].unique())
        col_choice,col_quant=st.columns(2)
        choice=col_choice.selectbox('Enter Stock Item',all_items,key='choice')
        old_value,new_value=get_quantity_from_choice(df,choice),0
        old_cat=get_category_from_choice(df,choice)
        if choice:
            update_quant=col_quant.number_input(f"New Quantity? (Old Value = {old_value})",
                                 min_value=0, value=old_value, key='new_value')
        col_cat_options,col_cat_val=st.columns(2)
        if update_quant:
            for i in range(len(df_categories)):
                if df_categories[i]==old_cat:
                    index_of_category=i
            update_cat_option=col_cat_options.radio('Category Type',
                                         ('Pre-existing Category','New Category'))
            if update_cat_option=='Pre-existing Category':
                update_cat_value=col_cat_val.selectbox('Category Value', 
                                                       index=index_of_category,
                                                       options=df_categories)
            elif update_cat_option=='New Category':
                update_cat_value=col_cat_val.text_input('Input Category')
        if update_cat_value and update_quant and choice:
            col_changes,col_update=st.columns(2)
            col_changes.code(f"(\n'Stock' : {choice}\n'Quantity' : {old_value} -> {update_quant}\n'Category' : {old_cat} -> {update_cat_value}\n)",
                             language='python')
            if col_update.button('Save Changes', key='update_button'):
                stock_table.update_one(
                    { 'stock' : choice},
                    {
                    '$set' : {'quantity' : update_quant,
                              'category' : update_cat_value
                              }  
                    } 
                )
                refresh_data(col_update)

# Tab for adding new items to the system.
with tab_add:
    add_container=st.container()
    with add_container:
        quant_flg,cat_flg,button_flg=True,True,True
        col_add_stock,col_add_quantity=st.columns(2)
        add_stock=col_add_stock.text_input('Stock Item name', key='add_stock', value="",
                                           placeholder='Eg: `Eggs (individual)` or `Milk`')
        quant_flg=False if add_stock else True
        add_quantity=col_add_quantity.number_input('Stock Quantity', min_value=0, disabled=quant_flg)
        cat_flg=False if add_quantity else True
        col_add_cat_radio,col_add_cat_value=st.columns(2)
        add_cat_option=col_add_cat_radio.radio('Category Type',
                                         ('Pre-existing Category','New Category'),
                                         disabled=cat_flg, key='add_cat_option')
        if add_cat_option=='Pre-existing Category':
            add_cat_value=col_add_cat_value.selectbox('Category Value', options=df_categories,
                                                      disabled=cat_flg, key='add_cat_value')
        elif add_cat_option=='New Category':
            add_cat_value=col_add_cat_value.text_input('Input Category', disabled=cat_flg)
        add_cat_value="" if cat_flg else add_cat_value
        button_flg=False if add_cat_value else True
        col_add_changes,col_add_button=st.columns(2)
        col_add_changes.code(f"(\n'Stock' : {add_stock}\n'Quantity' : {add_quantity}\n'Category' : {add_cat_value}\n)",
                             language='python')
        if col_add_button.button('Save Changes', disabled=button_flg, key='add_button'):
            # row_add = [add_stock, add_quantity, add_cat_value]
            # main_df.loc[len(df)] = row_add
            # main_df.to_csv(filepath,encoding="utf8",index=False)
            stock_table.update_one({'stock': add_stock},
                                   {'$set': {'quantity': add_quantity,
                                             'category': add_cat_value
                                             }}, upsert=True)
            quant_flg,cat_flg,button_flg=True,True,True
            refresh_data(col_add_button)
                
# Tab with full control and quick changes!
with tab_free:
    # df = st.experimental_data_editor(df, num_rows='dynamic',
    #                                  key='update_editor', use_container_width=True)
    # if st.button('Save Changes', key='free_button'):
    #     pass
    #     # df.to_csv(filepath,encoding="utf8",index=False)
    #     # refresh_data()
    st.info('Coming Soon')