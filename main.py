from typing import OrderedDict
from decouple import config
import altair as alt
import streamlit as st
import requests as req
import pandas as pd
import numpy as np

st.title("PokemonGo Helper")

# Api endpoints + headers(api key)
pokemon_names_url = "https://pokemon-go1.p.rapidapi.com/pokemon_names.json"
pokemon_stats_url = "https://pokemon-go1.p.rapidapi.com/pokemon_stats.json"
pokemon_types_url = "https://pokemon-go1.p.rapidapi.com/pokemon_types.json"
headers = {"X-RapidAPI-Key": config("API_KEY")}

# Requests
pokemon_names_response = req.request("GET", pokemon_names_url, headers=headers)
pokemon_stats_response = req.request("GET", pokemon_stats_url, headers=headers)
pokemon_types_response = req.request("GET", pokemon_types_url, headers=headers)


# Dictionary that maintains order of inserted key-values: pokemon_id: pokemon_name
ordered_pokemon = OrderedDict()
for i in range(1, len(pokemon_names_response.json())):
    ordered_pokemon[pokemon_names_response.json()[str(i)]["id"]] = pokemon_names_response.json()[str(i)]["name"]

# List of pokemon names for select box
list_of_names = []
for i in ordered_pokemon:
    list_of_names.append(ordered_pokemon[i])

# Interactive Graph of every pokemon
df = pd.DataFrame.from_dict(pokemon_stats_response.json())
df = df.drop(columns=['form'])
df = df.drop_duplicates()
df = df.rename(columns={"pokemon_name":"name", "pokemon_id": "id"})
df.insert(0, 'id', df.pop('id'))
df.insert(0, 'name', df.pop('name'))
st.dataframe(df)

# Bar Chart of Types Frequency
pokemon_type_dist = dict()
for i in pokemon_types_response.json():
    type_dict = i['type']
    for j in range(len(type_dict)):
        try:
            pokemon_type_dist[type_dict[j]] = pokemon_type_dist[type_dict[j]] + 1
        except:
            pokemon_type_dist[type_dict[j]] = 1

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

# Select a pokemon for singular stats
st.selectbox(label="pokemon", options=list_of_names)






