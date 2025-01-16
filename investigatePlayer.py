player_server = "Shadow Council"
player_name = "Zevvo"

import json, requests, numpy as np, scipy.stats

# fix potential spaces in server name
player_server = player_server.replace(" ", "%20")
# default runs picked up by raider io
run_count = 10

# generate query string
query_string = "https://raider.io/api/v1/characters/profile?region=us&realm=" + player_server + "&name=" + player_name + "&fields=mythic_plus_recent_runs"
query_response = requests.get(query_string)

# make sure we have a valid response
if query_response.ok:
    query_data = json.loads(query_response.text)
    # get the most recent run ids to check them out
    run_IDs = [0] * run_count
    for x in range(run_count):
        # store run ID
        run_IDs[x] = query_data['mythic_plus_recent_runs'][x]['keystone_run_id']
    
    # store player ilvl deviations from party
    player_stdevs = []
    # should iterate 10 times
    for id in run_IDs:
        # subquery to then seach each individual run
        subquery_string = "https://raider.io/api/v1/mythic-plus/run-details?season=season-tww-1&id=" + str(id)
        subquery_response = requests.get(subquery_string)
        # with valid response
        if subquery_response.ok:
            subquery_data = json.loads(subquery_response.text)
            # to store group ilvls
            group_ilvl = []
            # iterate through 5 players
            for roster_data in subquery_data['roster']:
                name = roster_data['character']['name']
                ilvl = roster_data['items']['item_level_equipped']
                # if name matches, store seperately
                if (name == player_name):
                    player_ilvl = ilvl
                else:
                    group_ilvl.append(ilvl)
            # stat collection
            group_average = np.average(group_ilvl)
            group_deviation = np.std(group_ilvl)
            player_stdevs.append((player_ilvl - group_average) / group_deviation)
    # output
    print("Player: " + player_name)
    average_player_stdev = np.average(player_stdevs)
    # convert deviations to a normal distribution percentage
    player_percentage = int(scipy.stats.norm.cdf(average_player_stdev) * 100)
    print("On average, over the past 10 runs " + player_name + "'s ilvl was in the " + str(player_percentage) + "th percentile of their group.")