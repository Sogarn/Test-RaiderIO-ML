# server name
player_server = "Shadow Council"
# list of player names
player_names = ["Hevensrath","Hevensword","Hevensdemon","Hevensreaper","Hevensnature","Hevenlystorm"]
# number of weeks to look back
week_count = 4

import json, requests, numpy as np, scipy.stats, math
from datetime import datetime, timezone

# function for converting individual performance into a normal distribution percentage
def calculateZValue(individual_stat, group_stat):
    group_average = np.average(group_stat)
    group_deviation = np.std(group_stat)
    return (individual_stat - group_average) / group_deviation

# actual api checks and analysis
def main(server, player, weeks_to_check):
    # fix potential spaces in server name
    server = server.replace(" ", "%20")

    # generate query string
    query_string = "https://raider.io/api/v1/characters/profile?region=us&realm=" + server + "&name=" + player + "&fields=mythic_plus_recent_runs"
    query_response = requests.get(query_string)

    # make sure we have a valid response
    if query_response.ok:
        query_data = json.loads(query_response.text)
        # store recent run data
        all_recent_runs = query_data['mythic_plus_recent_runs']
        run_IDs = []
        # to store key levels
        key_levels = []
        # to store number of chests (0 chest is deplete, 1 is timing, 2 is 2 chest etc)
        chest_count = []
        # get the current date and time in utc time
        current_dt = datetime.now(timezone.utc)
        # iterate through recent runs
        for recent_run in all_recent_runs:
            # get the run date and time
            run_dt = recent_run['completed_at']
            # convert run date and time to datetime object with utc timezone
            run_dt = datetime.strptime(run_dt[:-5], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
            # only add runs within the week threshold after rounding up
            week_difference = math.floor((current_dt - run_dt).days / 7)
            if (week_difference <= weeks_to_check):
                # store run ID
                run_IDs.append(recent_run['keystone_run_id'])
                key_levels.append(recent_run['mythic_level'])
                chest_count.append(recent_run['num_keystone_upgrades'])
        # calculate how many runs there were
        run_count = len(run_IDs)
        # store player ilvl deviations from party
        player_ilvl_stdevs = []
        # store player rating deviations from party
        player_rating_stdevs = []
        # to store player ilvls
        player_ilvls = []
        # to store player ratings
        player_ratings = []
        # to store group ilvls
        group_ilvls = []
        # to store group ratings
        group_ratings = []
        # iterate through ids if we have at least two runs
        if (run_count > 1):
            for id in run_IDs:
                # subquery to then seach each individual run
                subquery_string = "https://raider.io/api/v1/mythic-plus/run-details?season=season-tww-1&id=" + str(id)
                subquery_response = requests.get(subquery_string)
                # with valid response
                if subquery_response.ok:
                    subquery_data = json.loads(subquery_response.text)
                    # iterate through 5 players
                    for roster_data in subquery_data['roster']:
                        name = roster_data['character']['name']
                        ilvl = float(roster_data['items']['item_level_equipped'])
                        rating = float(roster_data['ranks']['score'])
                        # check if ilvl is greater than zero
                        if (ilvl > 0):
                            # if name matches, store seperately
                            if (name == player):
                                player_ilvls.append(ilvl)
                            else:
                                group_ilvls.append(ilvl)
                        # check if rating is greater than zero
                        if (rating > 0):
                            # if name matches, store seperately
                            if (name == player):
                                player_ratings.append(rating)
                            else:
                                group_ratings.append(rating)
                # stat collection
                # get average player ilvl over past 10 runs
                player_average_ilvl = np.average(player_ilvls)
                # get average player rating over past 10 runs
                player_average_rating = np.average(player_ratings)
                # store player standard deviations
                player_ilvl_stdevs.append(calculateZValue(player_average_ilvl, group_ilvls))
                player_rating_stdevs.append(calculateZValue(player_average_rating, group_ratings))
            # output
            print(f"Player {player} past {run_count} runs stats over the past {week_count} weeks:")
            average_player_ilvl_stdev = np.average(player_ilvl_stdevs)
            average_player_rating_stdev = np.average(player_rating_stdevs)
            average_key_level = np.average(key_levels)
            key_timing_percentage = (1 - (chest_count.count(0) / len(chest_count))) * 100
            average_chests = np.average(chest_count)
            # output basic key stats
            print(f"Average key level: {average_key_level:.1f}")
            print(f"Key timing percentage: {key_timing_percentage:.1f}%")
            print(f"Average number of chests: {average_chests:.1f}")
            # convert deviations to a normal distribution percentage
            player_ilvl_percentage = scipy.stats.norm.cdf(average_player_ilvl_stdev) * 100
            print(f"On average, {player}'s ilvl was in the {player_ilvl_percentage:.1f} percentile of their groups.")
            # convert deviations to a normal distribution percentage
            player_rating_percentage = scipy.stats.norm.cdf(average_player_rating_stdev) * 100
            print(f"On average, {player}'s io rating was in the {player_rating_percentage:.1f} percentile of their groups.")
        # if no valid runs
        else:
            print(f"Player {player} does not have enough valid runs in the past {weeks_to_check} weeks.")

for name in player_names:
    # blank line
    print()
    # run main function
    main(player_server, name, week_count)