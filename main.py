from typing import OrderedDict
from decouple import config
from helperfunctions import compileCoords, findFrequency
import plotly.graph_objects as go
import streamlit as st
import requests as req
import altair as alt
import pandas as pd
import numpy as np
import time

# Current Time
now = time.time()

# Page Layout
st.set_page_config(layout="centered", page_title="PokemonGo Helper", initial_sidebar_state="expanded")

# Page Title
st.title("PokemonGo Helper")

# Api endpoints + headers(api key)
pokemon_names_url = "https://pokemon-go1.p.rapidapi.com/pokemon_names.json"
pokemon_stats_url = "https://pokemon-go1.p.rapidapi.com/pokemon_stats.json"
pokemon_types_url = "https://pokemon-go1.p.rapidapi.com/pokemon_types.json"
pokemon_london_map_url = "https://londonpogomap.com/pokestop.php?time=%s" % int(now)
pokemon_nyc_map_url = "https://nycpokemap.com/pokestop.php?time=%s" % int(now)
pokemon_syd_map_url = "https://sydneypogomap.com/pokestop.php?time=%s" % int(now)
headers = {"X-RapidAPI-Key": config("API_KEY")}

# Requests
pokemon_names_response = req.request("GET", pokemon_names_url, headers=headers) # Search
pokemon_stats_response = req.request("GET", pokemon_stats_url, headers=headers) # Search 
pokemon_types_response = req.request("GET", pokemon_types_url, headers=headers) # Analysis

# Navigation Bar (Side)
sidebar_selectbox = st.sidebar.selectbox(
   "Select:",
   ["Homepage", "Search", "Analysis","Locations"]
)

# Page 1 - Search
if sidebar_selectbox == "Search":

# Dictionary that maintains order of inserted key-values: {pokemon_id: pokemon_name}
    ordered_pokemon = OrderedDict()
    for i in range(1, len(pokemon_names_response.json())):
        ordered_pokemon[pokemon_names_response.json()[str(i)]["id"]] = pokemon_names_response.json()[str(i)]["name"]
    

# List of pokemon names for select box
    list_of_names = []
    for i in ordered_pokemon:
        list_of_names.append(ordered_pokemon[i])

# Generate Interactive Graph of every pokemon
    df = pd.DataFrame.from_dict(pokemon_stats_response.json())
    df = df.drop(columns=['form'])
    df = df.drop_duplicates()
    df = df.rename(columns={"pokemon_name":"Name", "pokemon_id": "ID"})
    df.insert(0, 'ID', df.pop('ID'))
    df.insert(0, 'Name', df.pop('Name'))

# Search Box(s) for pokemon to locate specific stats

    poke_one = st.selectbox(label="pokemon1", options=list_of_names)
    poke_two = st.selectbox(label="pokemon2", options=list_of_names)
    
    poke_one_stats = [0,0,0]
    poke_two_stats = [0,0,0]

    poke_one_row = df.loc[df['Name'] == poke_one]
    poke_two_row = df.loc[df['Name'] == poke_two]

    # Input DataSet 1
    poke_one_stats[0] = poke_one_row.iloc[0]['base_stamina']
    poke_one_stats[1] = poke_one_row.iloc[0]['base_attack']
    poke_one_stats[2] = poke_one_row.iloc[0]['base_defense']
    
    # Input DataSet 2
    poke_two_stats[0] = poke_two_row.iloc[0]['base_stamina']
    poke_two_stats[1] = poke_two_row.iloc[0]['base_attack']
    poke_two_stats[2] = poke_two_row.iloc[0]['base_defense']

    # Radar Chart
    categories = ['Stamina', 'Attack', 'Defense']
    fig = go.Figure()
    
    # Data set 1
    fig.add_trace(go.Scatterpolar(
      r=poke_one_stats, # <-- Data 
      theta=categories,
      fill='toself',
      name='Product A'
    ))

    # Data set 2
    fig.add_trace(go.Scatterpolar(
      r=poke_two_stats, # <-- Data
      theta=categories,
      fill='toself',
      name='Product A'
    ))

    fig.update_layout(
        polar=dict(
        radialaxis=dict(
        visible=True,
        range=[0, 500],
        # NEEDS CHANGE
        # Change of colors - https://plotly.com/python-api-reference/generated/plotly.graph_objects.Layout.html
    )),
    showlegend=False
    )
    # Draw Radar Chart
    st.write(fig)

    # Draw Interactive Graph
    st.dataframe(df)


# Page 2 - Analysis
elif sidebar_selectbox == "Analysis":

# Line Chart of trend of stats
    line_graph_data = dict()
    for i in range(len(pokemon_types_response.json())):
        type_dict = pokemon_types_response.json()[i]['type']
        stam = pokemon_stats_response.json()[i]['base_stamina']
        att = pokemon_stats_response.json()[i]['base_attack']
        defs = pokemon_stats_response.json()[i]['base_defense']
        for j in range(len(type_dict)):
            try:
                stat_arr = line_graph_data[type_dict[j]]
                stat_arr[0] = stat_arr[0] + int(stam)
                stat_arr[1] = stat_arr[1] + int(att)
                stat_arr[2] = stat_arr[2] + int(defs)
            except:
                line_graph_data[type_dict[j]] = [stam,att,defs]

    pokemon_type_dist = findFrequency(pokemon_types_response.json())
    line_graph_types = []
    for key in line_graph_data:
        new_type = dict()
        stats = line_graph_data[key]
        new_type["Type"] = key
        new_type["Stamina"] = str(stats[0] // pokemon_type_dist[key]) 
        new_type["Attack"] = str(stats[1] // pokemon_type_dist[key])
        new_type["Defense"] = str(stats[2] // pokemon_type_dist[key])
        line_graph_types.append(new_type)

    line_df = pd.DataFrame(line_graph_types)

    stat_option = st.selectbox(
     'Which Base Stat would you like to view?',
     ('Stamina', 'Attack', 'Defense'))

    st.altair_chart(alt.Chart(line_df).mark_line().encode(alt.X('Type'), alt.Y('{}'.format(stat_option)))) 

    # Bar Chart of Types Frequency
    pokemon_type_dist = findFrequency(pokemon_types_response.json())

    # Dictionary pokemon_type_dist now holds = {type: freq}
    # Convert to dictionary with {type: type_name, freq, freq_val}

    bar_chart_data = []
    for val in pokemon_type_dist:
        newType = dict()
        newType["Type"] = val
        newType["Frequency"] = pokemon_type_dist[val]
        bar_chart_data.append(newType)
        type_df = pd.DataFrame(bar_chart_data)

    st.write("Pokemon Type Frequency Distribution")

    chart = (alt.Chart(type_df).mark_bar().encode(alt.X("Type"), alt.Y("Frequency"),alt.Color("Type"), alt.Tooltip(["Type", "Frequency"]),).interactive())
    st.altair_chart(chart)

# Page 3 - Locations
elif sidebar_selectbox == "Locations":

    # Description
    st.write("PokeStops and Gyms of Popular Spoofing locations")

    # Location Dropdown
    location_option = st.selectbox(
     'What spoofing location would you like to view?',
     ('London', 'NYC', 'Sydney'))

    # Map chart - LONDON
    if location_option == 'London':
        # Request
        pokemon_london_map_response = req.request("GET", pokemon_london_map_url) 
        if pokemon_london_map_response.status_code == 200:
            london_df = pd.DataFrame(compileCoords(pokemon_london_map_response.json()))
            st.map(london_df)
        else:
            st.error("API Error: Unable to validate API request at this moment.")

    # Map chart - NYC
    elif location_option == 'NYC':
        # Request
        pokemon_nyc_map_response = req.request("GET", pokemon_nyc_map_url)
        if pokemon_nyc_map_response.status_code == 200:
            nyc_df = pd.DataFrame(compileCoords(pokemon_nyc_map_response.json()))
            st.map(nyc_df)
        else:
            st.error("API Error: Unable to validate API request at this moment.")

    # Map Chart - Sydney
    elif location_option == 'Sydney':
        # Request
        pokemon_syd_map_response = req.request("GET", pokemon_syd_map_url)

        if pokemon_syd_map_response.status_code == 200:
            syd_df = pd.DataFrame(compileCoords(pokemon_syd_map_response.json()))
            st.map(syd_df)
        else:
            st.error("API Error: Unable to validate API request at this moment.")
    
    # Invalid Location Entry
    else:
        st.error("Error: Invalid location option was selected.")

# Page 1 - Home Page        
else:
    st.write("Home Page")





