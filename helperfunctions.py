def compileCoords(mapJson):
    list_of_coords = []
    for i in range(1, 76):
        new_loc = dict()
        new_loc["lat"] = mapJson["invasions"][i]["lat"]
        new_loc["lon"] = mapJson["invasions"][i]["lng"]
        list_of_coords.append(new_loc)
            
    return list_of_coords

def findFrequency(mapJson):
    pokemon_type_dist = dict()
    for i in mapJson:
        type_dict = i['type']
        for j in range(len(type_dict)):
            try:
                pokemon_type_dist[type_dict[j]] = pokemon_type_dist[type_dict[j]] + 1
            except:
                pokemon_type_dist[type_dict[j]] = 1
    return pokemon_type_dist

def spreadData(graph_data, df, poke_selection):

    poke_row = df.loc[df['Name'] == poke_selection]
    graph_data[0] = poke_row.iloc[0]['Base Stamina']
    graph_data[1] = poke_row.iloc[0]['Base Attack']
    graph_data[2] = poke_row.iloc[0]['Base Defense']


def translateGen(val1, val2):
    result = [0, 0]

    generations = {
    "1" : [1, 151], 
    "2" : [152, 251], 
    "3" : [252, 386],
    "4" : [387, 493],
    "5" : [494, 649],
    "6" : [650, 721],
    "7" : [722, 809],
    "8" : [810, 906]}

    val1_range = generations[val1]
    val2_range = generations[val2]

    result[0] = val1_range[0]
    result[1] = val2_range[1]

    return result
