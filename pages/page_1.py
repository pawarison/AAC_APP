import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import streamlit as st
from st_aggrid import AgGrid
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    layout="wide",page_title = "Market Tracking Indicator"
)

# ----------------------------------------------------------------
# ---------------- Google Sheet AMQS Session ----------------
gc = gspread.service_account('credential.json')
amqs_sheet = gc.open_by_key('1lqxTEL4hYOs3Tyd19o9XLpZT8e6RrGjB0GXJWxywlis')

# ---- get all AMQS sheet ----
# tradelog_sheet = amqs_sheet.get_worksheet(0)
# pivot_data_sheet = amqs_sheet.get_worksheet(1)
# equity_sheet = amqs_sheet.get_worksheet(2)
benchmark_sheet = amqs_sheet.get_worksheet(3)

@st.cache_data()
def load_data():
    benchmark_data = benchmark_sheet.get_all_records()
    return benchmark_data

benchmark_data = load_data()

benchmark = pd.DataFrame(benchmark_data)
benchmark.set_index('Date',inplace=True)
benchmark['NDX13WHLwma'] = benchmark['NDX13WHLwma'].replace('',np.nan).astype(float)
benchmark['SPX13WHLwma'] = benchmark['SPX13WHLwma'].replace('',np.nan).astype(float)

NDX13WHL_color = np.where(benchmark['NDX13WHL']>benchmark['NDX13WHLwma'],'green','#ff7814')
SPX13WHL_color = np.where(benchmark['SPX13WHL']>benchmark['SPX13WHLwma'],'green','#ff7814')


df_3mChange = benchmark[['NASDAQ','SPX','NDXE','SPXEW']].pct_change(60)
df_3mChange['ndx_spread'] = df_3mChange['NASDAQ'] - df_3mChange['NDXE']
df_3mChange['spx_spread'] = df_3mChange['SPX'] - df_3mChange['SPXEW']

 
benchmark['NDX26W_HL'] = (benchmark['NDX26WHI']/benchmark['NDX26WLO'])
benchmark.replace([np.inf, -np.inf], 0, inplace=True)
benchmark['NDX26W_HL'] =  benchmark['NDX26W_HL'].rolling(5).mean().fillna(method='ffill')

benchmark['SPX26W_HL'] = (benchmark['SPX26WHI']/benchmark['SPX26WLO'])
benchmark.replace([np.inf, -np.inf], 0, inplace=True)
benchmark['SPX26W_HL'] = benchmark['SPX26W_HL'].rolling(5).mean().fillna(method='ffill')
# ----------------------------------------------------------------  
# ----- benchmark tracking Chart Plot -----
def benchmark_fig(flag='', flag2=''):

    ndx_fig = make_subplots(rows=2, cols=1,shared_xaxes=True,vertical_spacing=0.1,
                            row_width=[0.9,1],subplot_titles=(flag, flag2 ))
    
    # ---------- panel 1 ----------
    if flag == 'NASDAQ100':                        
        ndx_fig.append_trace(go.Scatter(mode='lines+markers',marker_color=NDX13WHL_color, 
                                x=benchmark.index, y = benchmark['NASDAQ'], name = 'NASDAQ100',
                                line=dict(width = 2, color='rgb(55, 83, 109)' ),
                                legendgroup=f"group 1",  # this can be any string, not just "group"
                                legendgrouptitle_text=f"Panel 1",
                                ), row=1, col=1)
    else:
        pass

    if flag == 'S&P500': 
        ndx_fig.append_trace(go.Scatter(mode='lines+markers',marker_color=SPX13WHL_color, 
                                x=benchmark.index, y = benchmark['SPX'], name = 'S&P500',
                                line=dict(width = 2, color='rgb(55, 83, 109)' ),
                                legendgroup=f"group 1",  # this can be any string, not just "group"
                                legendgrouptitle_text=f"Panel 1",
                                ), row=1, col=1)
    else:
        pass

    # ---------- panel 2 ----------
    if flag2 == 'NDX 3-m Return, MarketCap-Weight VS Equal-weight':                        
        ndx_fig.append_trace(go.Scatter(mode='lines', 
                                x=df_3mChange.index, y = df_3mChange['NASDAQ'], name = 'NDX 3m return',
                                line=dict(width = 2, color='#DE3163' ),
                                legendgroup=f"group 2",  # this can be any string, not just "group"
                                legendgrouptitle_text=f"Panel 2",
                                ), row=2, col=1)
        ndx_fig.append_trace(go.Scatter(mode='lines', 
                                x=df_3mChange.index, y = df_3mChange['NDXE'], name = 'NDXE 3m return',
                                line=dict(width = 2, color='rgb(55, 83, 109)' ),
                                legendgroup=f"group 2",  # this can be any string, not just "group"
                                legendgrouptitle_text=f"Panel 2",
                                ), row=2, col=1)
        ndx_fig.append_trace(go.Bar( 
                                x=df_3mChange.index, y = df_3mChange['ndx_spread'], name = 'Spread',
                                marker_color='lightslategray',
                                legendgroup=f"group 2",  # this can be any string, not just "group"
                                legendgrouptitle_text=f"Panel 2",
                                ), row=2, col=1)
    else:
        pass

    if flag2 == 'SPX 3-m Return, MarketCap-Weight VS Equal-weight': 
        ndx_fig.append_trace(go.Scatter(mode='lines', 
                                x=df_3mChange.index, y = df_3mChange['SPX'], name = 'SPX 3m return',
                                line=dict(width = 2, color='#DE3163' ),
                                legendgroup=f"group 2",  # this can be any string, not just "group"
                                legendgrouptitle_text=f"Panel 2",), row=2, col=1)
        ndx_fig.append_trace(go.Scatter(mode='lines', 
                                x=df_3mChange.index, y = df_3mChange['SPXEW'], name = 'SPXEW 3m return',
                                line=dict(width = 2, color='rgb(55, 83, 109)' ),
                                legendgroup=f"group 2",  # this can be any string, not just "group"
                                legendgrouptitle_text=f"Panel 2",
                                ), row=2, col=1)
        ndx_fig.append_trace(go.Bar( 
                                x=df_3mChange.index, y = df_3mChange['spx_spread'], name = 'Spread',
                                marker_color='lightslategray',
                                legendgroup=f"group 2",  # this can be any string, not just "group"
                                legendgrouptitle_text=f"Panel 2",
                                ), row=2, col=1)
    else:
        pass

    if flag2 == 'Cboe IndexOption VS EquityOption P/C Ratio': 
        ndx_fig.append_trace(go.Scatter(mode='lines', 
                                x=benchmark.index, y = benchmark['CBOEPCE'], name = 'IndexOption P/C Ratio',
                                line=dict(width = 2, color='#DE3163' ),
                                legendgroup=f"group 2",  # this can be any string, not just "group"
                                legendgrouptitle_text=f"Panel 2",), row=2, col=1)
        ndx_fig.append_trace(go.Scatter(mode='lines', 
                                x=benchmark.index, y = benchmark['CBOEPCI'], name = 'EquityOption P/C Ratio',
                                line=dict(width = 2, color='rgb(55, 83, 109)' ),
                                legendgroup=f"group 2",  # this can be any string, not just "group"
                                legendgrouptitle_text=f"Panel 2",
                                ), row=2, col=1)
        ndx_fig.add_hline(y=1, row=2, line_width=1, line_dash="dash")
    else:
        pass

    if flag2 == 'NDX, 3m NHNL Ratio': 
        ndx_fig.append_trace(go.Scatter(mode='lines', 
                                x=benchmark.index, y = benchmark['NDX26W_HL'], name = 'NDX 3m NHNL Ratio',
                                line=dict(width = 2, color='#DE3163' ),
                                legendgroup=f"group 2",  # this can be any string, not just "group"
                                legendgrouptitle_text=f"Panel 2",), row=2, col=1)
        ndx_fig.add_hline(y=1, row=2, line_width=1, line_dash="dash")
    else:
        pass

    if flag2 == 'SPX, 3m NHNL Ratio': 
        ndx_fig.append_trace(go.Scatter(mode='lines', 
                                x=benchmark.index, y = benchmark['SPX26W_HL'], name = 'NDX 3m NHNL Ratio',
                                line=dict(width = 2, color='#DE3163' ),
                                legendgroup=f"group 2",  # this can be any string, not just "group"
                                legendgrouptitle_text=f"Panel 2",), row=2, col=1)
        ndx_fig.add_hline(y=1, row=2, line_width=1, line_dash="dash")
    else:
        pass

    # ---------- fig config ----------
    ndx_fig.update_layout( title = 'Index Analysis',
        yaxis_title = 'Price',  
    )
    ndx_fig.update_xaxes(showspikes=True, spikecolor="orange", spikesnap="cursor", spikemode="across", spikethickness=2 )
    ndx_fig.update_yaxes(showspikes=True, spikecolor="orange", spikesnap="cursor", spikemode="across", spikethickness=2 )
    ndx_fig.update_layout(hovermode='x unified',height=900) 

    return ndx_fig

tabs = st.tabs(["Index Analysis","Sector Analysis"])
with tabs[0]:
    cols = st.columns(2)
    with cols[0]:
        market_option = st.selectbox(
            'Select Market',
            ('NASDAQ100', 'S&P500'))
    with cols[1]:        
        metric_option = st.selectbox(
            'Select metric',
            ('NDX 3-m Return, MarketCap-Weight VS Equal-weight', 'SPX 3-m Return, MarketCap-Weight VS Equal-weight',
            'Cboe IndexOption VS EquityOption P/C Ratio',
            'NDX, 3m NHNL Ratio','SPX, 3m NHNL Ratio'))

    market_fig = benchmark_fig(flag=market_option, flag2=metric_option)
    st.plotly_chart(market_fig, theme="streamlit", use_container_width=True)