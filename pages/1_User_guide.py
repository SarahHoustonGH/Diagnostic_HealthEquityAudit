import streamlit as st

st.title(f'User Guide')

# Define the header and main text
intro_text = (
    "This Streamlit app allows you to visualize results produced by the HSMA5 Health Equity Audit for CDCs."
    "Please select your modality and demographic of interest in the panel on the left"
)

# Display the header and main text using markdown
st.markdown(intro_text)

st.markdown(
    """
    ### Add how to guide
    ## Add limitations
    ## Add data sources
    
"""
)