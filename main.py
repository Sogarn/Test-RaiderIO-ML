import json
import requests
import os.path
import time
import math

# decent run starts are 21,000,000 for tyrannical and 23,000,000 for fortified
# where to start the runs
run_start = 23000000
# where to save csv (User\Documents\runData.csv)
csv_location = os.path.join(os.path.expanduser('~'), 'Documents', 'runData.csv')
# how many queries per run (raider io API caps at 300 requests per minute)
queries_per_run = 150
# total number of queries
max_queries = 2100

# check if file exists, if it does not then make header row
if not os.path.exists(csv_location):
    data_file = open(csv_location, "x")
    data_file.write("run_number,key_level,dungeon,affix,faction,ilvl,spec,locale,io_score,world_rank,chests\n")
    data_file.close()

# gather more data
def gather_data():

    # open file to prepare appending
    data_file = open(csv_location, "a")

    for x in range (queries_per_run):
        run_number = run_start + x
        # print(f"Processing run {run_number}")
        # generate query string
        query_string = "https://raider.io/api/v1/mythic-plus/run-details?season=season-df-1&id=" + str(run_number)

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
            # run_number, key_level, dungeon, affix, faction, ilvl, spec, locale, io_score, world_rank, chests
            for player in roster:
                data_file.write(f"{run_number},{key_level},{dungeon},{affix},"
                                f"{str(player['character']['faction'])},"
                                f"{str(player['items']['item_level_equipped'])},"
                                f"{str(player['character']['spec']['name'])} {str(player['character']['class']['name'])},"
                                f"{str(player['character']['realm']['locale'])},"
                                f"{str(player['ranks']['score'])},"
                                f"{str(player['ranks']['world'])},"
                                f"{chests}\n")
    # close file
    data_file.close()
pass


current_queries = 0
print(f"Batch processing started...")
while current_queries < max_queries:
    print(f"{current_queries} / {max_queries} runs complete...")
    # start timer
    start_time = time.time()
    # gather data
    gather_data()
    # update run start number
    run_start += queries_per_run
    # update number of queries
    current_queries += queries_per_run
    # check to see that we are not done before doing time check
    if current_queries < max_queries:
        # check how much time has elapsed
        elapsed_time = math.floor(time.time() - start_time)
        # do not exceed one run per minute just to be safe
        if elapsed_time < 60:
            print(f"Waiting for {60 - elapsed_time} seconds...")
            time.sleep(60 - elapsed_time)
print("All runs complete!")
