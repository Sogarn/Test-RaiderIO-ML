# note this worked with an older version of raider io API

import json, requests, os.path, time, math, random
# create random number generator for skipping between sequential runs
rng = random.seed()

# decent run starts are 21,000,000 for tyrannical and 23,000,000 for fortified
# where to start the runs
run_start = 21500000
# where to save csv (User\Documents\runData.csv)
csv_location = os.path.join(os.path.expanduser('~'), 'Documents', 'runData.csv')
# how many queries per run (raider io API caps at 300 requests per minute)
queries_per_run = 150
# total number of runs
max_runs = 3

# check if file exists, if it does not then make header row
if not os.path.exists(csv_location):
    create_data_file = open(csv_location, "x")
    create_data_file.write("run_number,key_level,dungeon,affix,faction,ilvl,spec,locale,io_score,world_rank,chests\n")
    create_data_file.close()

# for more consistent progress updates
completion_checkpoint1 = queries_per_run * 0.25
completion_checkpoint2 = queries_per_run * 0.5
completion_checkpoint3 = queries_per_run * 0.75


# gather more data
def gather_data():
    # store progress booloans, once they are passed they switch to false
    checkpoint1 = True
    checkpoint2 = True
    checkpoint3 = True

    # open file to prepare appending
    data_file = open(csv_location, "a")

    for x in range(queries_per_run):
        # update run number
        run_number = run_start + x
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
        # logic to post progress checkpoints only once each
        if checkpoint1 and (x > completion_checkpoint1):
            checkpoint1 = False
            print("Current run progress is at 25%...")
        elif checkpoint2 and (x > completion_checkpoint2):
            checkpoint2 = False
            print("Current run progress is at 50%...")
        elif checkpoint3 and (x > completion_checkpoint3):
            checkpoint3 = False
            print("Current run progress is at 75%...")
    # close file
    data_file.close()
    print("Current run is complete.")
pass

current_run = 0
# Changed this to a for loop since functionally that is what it was doing anyway
for run in range(max_runs):
    # report status
    print(f"Starting run {run + 1} / {max_runs}.")
    # start timer
    start_time = time.time()
    # gather data
    gather_data()
    # update run start number and add a bit of randomness
    run_start += queries_per_run + rng.randrange(10)
    # check how much time has elapsed
    elapsed_time = math.floor(time.time() - start_time)
    # do not exceed one run per minute just to be safe (and make sure we are not about to be done)
    if ((run + 1) < max_runs) and (elapsed_time < 60):
        print(f"Waiting for {60 - elapsed_time} seconds...")
        time.sleep(60 - elapsed_time)
print("All runs complete!")
