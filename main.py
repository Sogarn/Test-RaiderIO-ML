import json
import requests
import os.path
from fastai.tabular.all import *


# gather more data
def gatherdata():
    # where to start the runs
    run_number = 14500230
    # where to save csv
    csv_location = r"C:\Users\Filipe\Documents\runData.csv"
    # how many queries in a row
    max_queries = 450

    # check if file exists, if it does not then make header row
    if not os.path.exists(csv_location):
        data_file = open(csv_location, "x")
        data_file.write("run_number,key_level,dungeon,affix,ilvl,spec,io_score,chests\n")
        data_file.close()

    # open file to prepare appending
    data_file = open(csv_location, "a")

    for x in range (1, max_queries):
        # generate query string
        query_string = "https://raider.io/api/v1/mythic-plus/run-details?season=season-df-1&id=" + str(run_number + x)

        query_response = requests.get(query_string)
        # make sure we have a valid response
        if query_response.ok:
            query_data = json.loads(query_response.text)

            # data we are storing
            # dungeon short name (dungeon->short name)
            dungeon = str(query_data['dungeon']['short_name'])
            # key level (mythic_level)
            key_level = str(query_data['mythic_level'])
            # num chests (num_chests)
            chests = str(query_data['num_chests'])
            # fortified vs tyrannical affixes
            affix = str(query_data['weekly_modifiers'][0]['name'])

            # store player team info temporarily
            roster = query_data['roster']

            # iterate through roster to fill in data, first few entries stay the same
            for player in roster:
                data_file.write(f"{run_number+x},{key_level},{dungeon},{affix},"
                                f"{str(player['items']['item_level_equipped'])},"
                                f"{str(player['character']['spec']['name'])} {str(player['character']['class']['name'])},"
                                f"{str(player['ranks']['score'])},"
                                f"{chests}\n")
    # close file
    data_file.close()
    pass


# gather data
gatherdata()
