from typing import OrderedDict
from decouple import config
from helperfunctions import compileCoords, findFrequency, spreadData, translateGen
from Pokemon import Pokemon
import plotly.graph_objects as go
import streamlit as st
import requests as req
import altair as alt
import pandas as pd
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
   ["Homepage", "Comparisons", "Rank", "Analysis","Locations"]
)

# Page 1 - Comparisons
if sidebar_selectbox == "Comparisons":

    # Dictionary that maintains order of inserted key-values: {pokemon_id: pokemon_name}
    ordered_pokemon = OrderedDict()
    if pokemon_names_response.status_code == 200:
        for i in range(1, len(pokemon_names_response.json())):
            ordered_pokemon[pokemon_names_response.json()[str(i)]["id"]] = pokemon_names_response.json()[str(i)]["name"]
    else:
        st.error("API Error: Unable to validate API request at this moment.")

    # List of pokemon names for select box
    list_of_names = []
    for i in ordered_pokemon:
        list_of_names.append(ordered_pokemon[i])

    # Generate Interactive Graph of every pokemon
    if pokemon_stats_response.status_code == 200:
        df = pd.DataFrame.from_dict(pokemon_stats_response.json())
        df = df.drop(columns=['form'])
        df = df.drop_duplicates()
        df = df.rename(columns={"pokemon_name":"Name", "pokemon_id": "ID", "base_stamina": "Base Stamina",
        "base_attack": "Base Attack", "base_defense": "Base Defense"})
        df.insert(0, 'ID', df.pop('ID'))
        df.insert(0, 'Name', df.pop('Name'))
    else:
        st.error("API Error: Unable to validate API request at this moment.")

    # Search Box(s) for pokemon to locate specific stats

    # Initiate Columns
    cols = st.columns(2)

    # Select Dropdown 1
    poke_one = cols[0].selectbox(label="Option 1", options=list_of_names)
    # Select Dropdown 2
    poke_two = cols[1].selectbox(label="Option 2", options=list_of_names)
    
    # Graph variables
    poke_one_stats = [0,0,0]
    poke_two_stats = [0,0,0]

    # Helper method to fill graph variables 
    spreadData(poke_one_stats, df, poke_one)
    spreadData(poke_two_stats, df, poke_two)

    cols[0].write("Stamina ({}) - Attack ({}) - Defense ({})".format(poke_one_stats[0],poke_one_stats[1],poke_one_stats[2]))
    cols[1].write("Stamina ({}) - Attack ({}) - Defense ({})".format(poke_two_stats[0],poke_two_stats[1],poke_two_stats[2]))

    # Empty Space
    cols[0].text("")
    cols[0].text("")
    cols[0].text("")
    cols[1].text("")
    cols[1].text("")
    cols[1].text("")

    # Empty Space
    st.text("")
    st.text("")

    # Draw Radar Chart
    with st.expander("Radar Comparison Chart"):

        exp_cols = st.columns(2)

        colorpick1 = exp_cols[0].color_picker('Option 1 Line Color', '#fa8072')
        colorpick2 = exp_cols[1].color_picker('Option 2 Line Color', '#ADD8E6')

        # Radar Chart
        categories = ['Stamina', 'Attack', 'Defense']
        fig = go.Figure()
        
        # Data set 1
        fig.add_trace(go.Scatterpolar(
        r=poke_one_stats, # <-- Data 
        theta=categories,
        fill='toself',
        name='Product A',
        line={'color': colorpick1, 'dash': 'solid'}
        ))

        # Data set 2
        fig.add_trace(go.Scatterpolar(
        r=poke_two_stats, # <-- Data
        theta=categories,
        fill='toself',
        name='Product B',
        line= {'color': colorpick2, 'dash': 'solid'}
        ))

        fig.update_layout(
            polar=dict(
            radialaxis=dict(
            visible=True,
            range=[0, max(max(poke_one_stats), max(poke_two_stats))], # <-- Resize based on max of both selections
            linecolor="#000000"
        )),
        showlegend=False
        )

        st.write(fig)
    
    # Empty Space
    st.text("")
    st.text("")
    st.text("")
    st.text("")

    # Select Slider
    lowerBound, upperBound = st.select_slider('Select the generation(s) of pokemon you want to view in the interactive table.', 
    options=['1', '2', '3', '4', '5', '6', '7', '8'],
    value=('1', '8'))

    # Make chart responsive to bar
    result = translateGen(lowerBound, upperBound)
    df = df[(df['ID'] >= result[0]) & (df['ID'] <= result[1])]

    # Empty Space
    st.text("")
    st.text("")

    # Draw Interactive Graph
    st.write("Base Stats")
    st.dataframe(df)

# Page 2 - Rank
elif sidebar_selectbox == "Rank":

    # Generate Interactive Graph of every pokemon
    if pokemon_stats_response.status_code == 200:
        newdf = pd.DataFrame.from_dict(pokemon_stats_response.json())
        newdf = newdf.drop(columns=['form'])
        newdf = newdf.drop_duplicates()
        newdf = newdf.rename(columns={"pokemon_name":"Pokemon", "pokemon_id": "ID",
        "base_attack": "Base Attack", "base_defense": "Base Defense", "base_stamina": "Base Stamina"})
        newdf.insert(0, 'ID', newdf.pop('ID'))
        newdf.insert(0, 'Pokemon', newdf.pop('Pokemon'))
    else:
        st.error("API Error: Unable to validate API request at this moment.")

    # Dictionary that maintains order of inserted key-values: {pokemon_id: pokemon_name}
    ordered_pokemon = OrderedDict()
    if pokemon_names_response.status_code == 200:
        for i in range(1, len(pokemon_names_response.json())):
            ordered_pokemon[pokemon_names_response.json()[str(i)]["id"]] = pokemon_names_response.json()[str(i)]["name"]
    else:
        st.error("API Error: Unable to validate API request at this moment.")

    # List of pokemon names for select box
    list_of_pokes = []
    for i in ordered_pokemon:
        list_of_pokes.append(ordered_pokemon[i])
    
    poke_choice = st.selectbox(label="Pokemon Name" ,options=list_of_pokes)

    input_cols = st.columns(3)
    val2 = input_cols[1].number_input(label="Attack",min_value=0,max_value=15)
    val3 = input_cols[2].number_input(label="Defense",min_value=0,max_value=15)
    val1 = input_cols[0].number_input(label="Stamina",min_value=0,max_value=15)

    poke = Pokemon(poke_choice, val2, val3, val1, newdf)

    poke.get_selected_info()
    poke.find_nearest_level_great()
    poke.find_nearest_cpm()
    poke.find_statproduct()
    poke.sortby_statproduct()
    poke.find_user_choice_rank()

    poke_dict = {
        "Pokemon": [poke.name], 
        "Attack":[int(poke.attack)], 
        "Defense":[int(poke.defense)],
        "Stamina":[int(poke.stamina)],  
        "Optimal Level":[round(poke.level)], 
        "Rank": [poke.rank], 
        "CP":[poke.CP]
    }

    result_df = pd.DataFrame(poke_dict)

    st.text("")
    st.text("")
    st.text("")

    st.write(result_df)

# Page 3 - Analysis
elif sidebar_selectbox == "Analysis":

    # Information Box

    st.info("Wait times for checkbox options on average are longer than other components.")

    # Empty space
    st.text("")
    st.text("")
    st.text("")

    st.write("Select a box to view the stat distribution among pokemon types.")
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

    line_cols = st.columns(3)

    sta_box = line_cols[0].checkbox('By Stamina')
    att_box = line_cols[1].checkbox('By Attack')
    def_box = line_cols[2].checkbox('By Defense')

    if sta_box:
        st.altair_chart(alt.Chart(line_df).mark_line().encode(alt.X('Type'), alt.Y('Stamina')))
    if att_box:
        st.altair_chart(alt.Chart(line_df).mark_line().encode(alt.X('Type'), alt.Y('Attack')))
    if def_box:
        st.altair_chart(alt.Chart(line_df).mark_line().encode(alt.X('Type'), alt.Y('Defense'))) 

    # Empty line space
    st.text("")
    st.text("")
    st.text("")

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

    chart = (alt.Chart(type_df).mark_bar().encode(alt.X("Type"), alt.Y("Frequency"),alt.Color("Type"), alt.Tooltip(["Type", "Frequency"]),).interactive())
    
    with st.expander("Pokemon Type Frequency"):
        st.altair_chart(chart)

# Page 4 - Locations
elif sidebar_selectbox == "Locations":

    # Description
    st.markdown("### PokeStops and Gyms of Popular Spoofing locations")

    # Location Dropdown
    location_option = st.radio(
     'Which spoofing location would you like to view?',
     ('London', 'NYC', 'Sydney'))

    # Map chart - LONDON
    if location_option == 'London':
        # Request
        pokemon_london_map_response = req.request("GET", pokemon_london_map_url) 
        if pokemon_london_map_response.status_code == 200:
            try:
                london_df = pd.DataFrame(compileCoords(pokemon_london_map_response.json()))
                st.map(london_df)
            except:
                st.error("Error: API is currently returning an array of empty coordinates. Try again at a later time.")
        else:
            st.error("API Error: Unable to validate API request at this moment.")

    # Map chart - NYC
    elif location_option == 'NYC':
        # Request
        pokemon_nyc_map_response = req.request("GET", pokemon_nyc_map_url)
        if pokemon_nyc_map_response.status_code == 200:
            try:
                nyc_df = pd.DataFrame(compileCoords(pokemon_nyc_map_response.json()))
                st.map(nyc_df)
            except:
                st.error("Error: API is currently returning an array of empty coordinates. Try again at a later time.")
        else:
            st.error("API Error: Unable to validate API request at this moment.")

    # Map Chart - Sydney
    elif location_option == 'Sydney':
        # Request
        pokemon_syd_map_response = req.request("GET", pokemon_syd_map_url)
        if pokemon_syd_map_response.status_code == 200:
            try:
                syd_df = pd.DataFrame(compileCoords(pokemon_syd_map_response.json()))
                st.map(syd_df)
            except:
                st.error("Error: API is currently returning an array of empty coordinates. Try again at a later time.")
        else:
            st.error("API Error: Unable to validate API request at this moment.")
    
    # Invalid Location Entry
    else:
        st.error("Error: Invalid location option was selected.")

# Page 1 - Home Page        
else:
    intro_p1 = """## If you want access to an in-depth description of what this site has to offer - \n ## Accept the terms and conditions below.\n ## Otherwise, you're just going in ***blind***, bro."""
    
    intro = st.empty()
    intro.markdown(intro_p1)
    placeholder = st.empty()
    cols = placeholder.columns(1)
    terms = cols[0].button("Accept Terms & Conditions")
    if terms:
        intro.empty()
        placeholder.empty()
        st.success("Psst, come on in. The gangs all here...")
        st.markdown("## Welcome to PokemonGo Helper")
        st.markdown("#### Heres a quick breakdown of what each page has to offer. Use the side bar to navigate them.")
        st.markdown("### Comparisons")
        st.markdown("##### Head to this page to compare *two* different Pokemons stats on an awesome radar chart that you can style to your liking and as well as an interactive table to view all nine hundred pokemon.")
        st.markdown("### Rank")
        st.markdown("##### A quick way to find out what rank your pokemon is out of the ***4096*** possible permutations.")
        st.markdown("### Analysis")
        st.markdown("##### *Fancy* charts, for *fancy* people, that like *fancy* statistics.")
        st.markdown("### Locations")
        st.markdown("##### We all know that everyone cheats at Pokemon Go. I mean, who has time to go outside anymore? Here are some of the most popular spoofing locations we could find.")


            

    
    




