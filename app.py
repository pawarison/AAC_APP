import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import streamlit as st
from st_aggrid import AgGrid
import plotly.graph_objects as go
import warnings
from st_pages import Page, show_pages, add_page_title,show_pages_from_config
warnings.filterwarnings('ignore')

st.set_page_config(page_title='Custom Sidebar Name',
    layout="wide" ,
    initial_sidebar_state = 'auto'
)
st.header("Welcome! 👋")
st.write('Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
         Vivamus imperdiet lacus nulla, vitae faucibus erat cursus ut.\
            Nullam quam lorem, semper eu nulla sit amet, pharetra viverra mi.\
             Donec suscipit ligula metus, nec venenatis orci pellentesque et.\
             Quisque ac sem eros. Duis non tellus vel est dictum interdum.\
             Nam pulvinar mattis rhoncus.\
         In sit amet ante ut odio scelerisque ullamcorper.')

 
markdown = """
Web App URL: <https://geotemplate.streamlit.app>
GitHub Repository: <https://github.com/giswqs/streamlit-multipage-template>
"""

 
st.title("Algoritmic-Alchemist")
 

st.header("Instructions")

show_pages(
    [
        Page("app.py", "Home", "🏠"),
        Page("pages/page_1.py", "Market Tracking Indicator", "🗺 "),
        Page("pages/page_2.py", "AMS Realtime Performance", "📈"),
    ]
)