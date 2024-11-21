
from snowflake.snowpark.context import get_active_session
import streamlit as st
import ast
session = get_active_session()

prompt = """Please write an email or text promoting a new plan that will save customers total costs. 
Also resolve the customer issue based on the ticket category. 
If the contact_preference is text message, write text message response in less than 25 words. 
If the contact_preference is email, write email response in maximum 100 words.
Write only email or text message response based on the contact_preference for every customer.
"""

ticket_categories = ['Roaming fees', 'Slow data speed', 'Lost phone', 'Add new line', 'Closing account']

st.subheader("Auto-generate custom emails or text messages")

with st.container():
    with st.expander("Enter customer request and select LLM", expanded=True):
        customer_request = st.text_area('Request',"""Dear customer service, I am requesting the closure of my account linked to this email effective June 2024. I have been satisfied with the service but will no longer need it. Please confirm receipt and let me know if there are any additional steps I need to take. Thank you for your attention.""")
    
        with st.container():
            left_col, right_col = st.columns(2)
            with left_col:
                selected_preference = st.selectbox('Select contact preference', ('Text message', 'Email'))
            with right_col:
                selected_llm = st.selectbox('Select LLM',('llama3-8b', 'mistral-7b', 'mistral-large', 'SUPPORT_MESSAGES_FINETUNED_MISTRAL_7B',))

with st.container():
    _,mid_col,_ = st.columns([.4,.3,.3])
    with mid_col:
        generate_template = st.button('Generate messages ⚡',type="primary")

with st.container():
    if generate_template:
        category_sql = f"""
        select snowflake.cortex.classify_text('{customer_request}', {ticket_categories}) as ticket_category
        """
        df_category = session.sql(category_sql).to_pandas().iloc[0]['TICKET_CATEGORY']
        df_category_dict = ast.literal_eval(df_category)
        st.subheader("Ticket category")
        st.write(df_category_dict['label'])

        message_sql = f"""
        select snowflake.cortex.complete('{selected_llm}',concat('{prompt}', '{customer_request}', '{selected_preference}')) as custom_message
        """
        df_message = session.sql(message_sql).to_pandas().iloc[0]['CUSTOM_MESSAGE']
        st.subheader(selected_preference)
        st.write(df_message)