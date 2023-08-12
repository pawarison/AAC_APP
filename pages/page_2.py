import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import streamlit as st
from st_aggrid import AgGrid,ColumnsAutoSizeMode
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

st.set_page_config( 
    layout="wide"
)
from utility import *
equity_df = read_parquet_gcs(path = 'gs://aac_bucket/equity_df.parquet', to_pandas=True)
tradelog_df = read_parquet_gcs(path = 'gs://aac_bucket/tradelog_df.parquet', to_pandas=True)


# ----------------------------------------------------------------
# ---- Calculate Equity Curve for AMQS ----
equity_curve = equity_df.copy()
equity_curve['portfolio_equity'] = equity_df['Current Equity 1']+equity_df['Current Equity 2']
equity_curve = equity_curve.set_index('Date').pct_change()
equity_curve = (1+equity_curve).cumprod()

# ---- Open position table ----
holding = tradelog_df.copy()
holding = holding[(holding['Order Status']=='Open')] 
holding['PnL %'] = (holding['Current Value $']/holding['Start Value $'])-1
holding = holding[['Date', 'Order Status','Stock','PnL %']]
holding['PnL %'] = (holding['PnL %'].astype(float).round(4))*100

# ----------------------------------------------------------------
# ---- Calculate Donut Chart ----

tradelog_df = tradelog_df[(tradelog_df['Order Status']=='Open')&(tradelog_df['Stock']!='Dummy')]
tradelog_df['Start Value $'] = tradelog_df['Start Value $'].astype(float)
tradelog_df['Current Value $'] = tradelog_df['Current Value $'].astype(float)

tradelog_group = tradelog_df.groupby('strategy')[['Start Value $']].sum() 

# --- Equity Holding ---
ndx_log = tradelog_group.loc[1].values 
ndx_log = ndx_log[0]
sp_log = tradelog_group.loc[2].values  
sp_log = sp_log[0]
# --- Cash ---
equity_dollar = equity_df.copy()
equity_dollar = equity_dollar.iloc[-1]
e_ndx = equity_dollar.loc['Current Equity 1'] 
e_sp = equity_dollar.loc['Current Equity 2'] 
current_cash = (e_ndx+e_sp) - (ndx_log+sp_log)


# ----------------------------------------------------------------
# ------------ Graph Session ------------
# ----- Equity Curve -----
fig = go.Figure()
fig.add_trace(go.Scatter(x=equity_curve.index, y = equity_curve['Current Equity 1'], name = 'Strategy 1',
                        line=dict(width = 1, color='lightslategray',dash='dash')))

fig.add_trace(go.Scatter(x=equity_curve.index, y = equity_curve['Current Equity 2'], name = 'Strategy 2',
                        line=dict(width = 1, color='lightslategray',dash='dash')))

fig.add_trace(go.Scatter(x=equity_curve.index, y = equity_curve['portfolio_equity'], name = 'Portfolio',
                        line=dict(width = 2, color='#DE3163')))

fig.update_layout( 
    title = 'AMQS Cumulative Return', 
    xaxis_title = 'Dates',  
    yaxis_title = 'Return',  
)
fig.update_xaxes(showspikes=True, spikecolor="orange", spikesnap="cursor", spikemode="across", spikethickness=2 )
fig.update_yaxes(showspikes=True, spikecolor="orange", spikesnap="cursor", spikemode="across", spikethickness=2 )
fig.update_layout(hovermode='x unified') 

# ----------------------------------------------------------------  
# ----- Donut Chart Plot -----
labels = ['Strategy 1', 'Strategy 2', 'Cash' ]
values = [ndx_log, sp_log, current_cash]

colors = [ '#DE3163','#FFBF00','lightslategray']
donut = go.Figure(data = go.Pie(values = values, 
                          labels = labels, hole = 0.5,
                          title = 'Portfolio Holding',
                          marker_colors = colors
                 ))
donut.update_traces(
                    hoverinfo='label+percent',
                    textinfo='percent', 
                    textfont_size=15,
                   )

 

tabs = st.tabs([ "Overall Performance"])

with tabs[0]:

    st.header("Overall Performance")
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    cols = st.columns(2)
    with cols[0]:
        AgGrid(holding, columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS, 
                        fit_columns_on_grid_load=True, height=500)
    with cols[1]:
        st.plotly_chart(donut, theme="streamlit", use_container_width=True)

    st.header("Keys Metric")


    st.header("Simulation")