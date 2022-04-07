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
