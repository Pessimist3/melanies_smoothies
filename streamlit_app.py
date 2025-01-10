# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col, when_matched
import requests
import pandas

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"),col("SEARCH_ON"))
# st.dataframe(data=my_dataframe, use_container_width=True)

pd_df = my_dataframe.to_pandas()


############################################################################
# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the Fruits You'd Like in Your Yummy Drink!
    """
)

# Get the customer's name
name_on_order = st.text_input(
    "Name on Smoothie"
)
ingredients_list = st.multiselect(
    "Select up to 5 Ingredients",
    my_dataframe,
    max_selections = 5
)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        st.subheader(fruit_chosen + " Nutritional Information")
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        ingredients_string += fruit_chosen + ' '

    st.write(ingredients_string)
    
    my_insert_stmt = " insert into smoothies.public.orders(ingredients, name_on_order) values ('" + ingredients_string + "', '" + name_on_order + "')"

   # st.write(my_insert_stmt)
   # st.stop
    
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Thanks ' + name_on_order + '! Your Smoothie is ordered!', icon="✅")



