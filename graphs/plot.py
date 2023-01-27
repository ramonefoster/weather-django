import pandas as pd
import sqlite3
from plotly.offline import plot
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
db_dir = BASE_DIR / 'db.sqlite3'
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except:
        return None

def read_data(year, month, whole_year):
    conn = create_connection(db_dir)
    cur = conn.cursor()
    if whole_year:        
        cur.execute(f"""SELECT date,time,temperature,humidity,wind_speed,wind_dir,wind_angle,bar,solar_rad, 
        uv_dose, wind_val FROM W{year} WHERE date BETWEEN '{year}-01-01' AND '{year}-12-31' 
        """)
    else:        
        cur.execute(f"""SELECT date,time,temperature,humidity,wind_speed,wind_dir,wind_angle,bar,solar_rad, 
        uv_dose, wind_val FROM W{year} WHERE date BETWEEN '{year}-{month}-01' AND '{year}-{month}-31' 
        """)

    rows = cur.fetchall()
    df = pd.DataFrame( [[ij for ij in i] for i in rows] )
    df.rename(columns={0: 'Date', 1: 'Time', 2: 'Temperature', 3: 'Humidity', 4:'Wind-speed',
     5:'Wind-direction', 6: 'Wind-angle', 7:'Bar', 8:'Solar-radiation', 9:'Uv-dose', 10: 'Wind-strength'}, inplace=True)  

    df["Datetime"] = df['Date'].astype(str) +" "+ df["Time"]
    df['Datetime'] = pd.to_datetime(df['Datetime'], format='%Y-%m-%d %H:%M')  
    
    return df

def plot_wind(year, month, whole_year): 
    df = read_data(year,month, whole_year)   
    df = df.replace({'---': np.nan})
    df['Wind-angle'] = df['Wind-angle'].astype(float)
    grp = df.groupby(["Wind-direction","Wind-strength","Wind-angle"]).size()\
            .reset_index(name="frequency").sort_values(['Wind-angle'], ascending=[1])

    fig = px.bar_polar(grp, r="frequency", theta="Wind-angle",
                    color="Wind-strength", template="plotly_dark",
                    labels={"Wind-strength": "Wind Speed in Km/h"}, direction='clockwise',
                    color_discrete_sequence= px.colors.sequential.Plasma_r)


    #Turn graph object into local plotly graph
    plotly_plot_obj = plot({'data': fig}, output_type='div')

    return plotly_plot_obj

def plot_general(year, month, element, whole_year):
    element_units = {'Temperature': '°C', 'Wind-speed': 'km/h', 'Solar-radiation': 'W/m²', 'Bar': 'mmhg', 'Humidity': '%', 'Uv-dose': ''}
    unit = element_units[element]
    print(unit)
    df = read_data(year, month, whole_year)    
    ndf = df.replace({'---': np.nan})
    ndf[element] = ndf[element].astype(float)
    mean = round(ndf[element].mean(), ndigits=2)

    ndf = ndf.sort_values(['Datetime', element], ascending=[1,1])
    fig = px.line(ndf, x='Datetime', y=element)
    fig.update_xaxes(rangeslider_visible=True)
    fig.add_hline(y=mean, line_width=1, line_color="red", line_dash="dot",
                    annotation_text=f"{mean}{unit}", 
                    annotation_position="top right", annotation=dict(font_size=15, font_family="Arial", font_color='red'))

    #Turn graph object into local plotly graph
    plotly_plot_obj = plot({'data': fig}, output_type='div')

    return plotly_plot_obj