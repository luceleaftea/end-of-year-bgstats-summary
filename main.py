import json
from pathlib import Path

path = Path(__file__).parent / "./year.bgsplay"
with path.open(newline='') as jsonfile:
    year_json = json.load(jsonfile)

    # Calculate self / anonymous ids
    self_id = year_json['userInfo']['meRefId']
    anonymous_id = None
    for player in year_json['players']:
        if player['isAnonymous']:
            anonymous_id = player['id']

    # Setup stat variables
    total_plays = len(year_json['plays'])
    friends_played_with = len(year_json['players']) - 2 # subtract 2 to account for self and anonymous player
    unique_games = len(year_json['games'])
    unique_locations = len(year_json['locations'])
    unique_days_played_on = set()
    estimated_time_played = 0
    new_games_played = 0

    # Setup Game Dictionary
    game_dict = {}

    for game in year_json['games']:


        game['plays'] = 0
        game['unique_players'] = set()
        game['unique_locations'] = set()
        game['first_time'] = False
        game['average_play_time'] = (game['minPlayTime'] + game['maxPlayTime']) / 2

        game_dict[game['id']] = game

    # Parse data from plays
    for play in year_json['plays']:
        if play['ignored']:
            continue

        game = game_dict[play['gameRefId']]

        game['plays'] += 1

        locationId = play.get('locationRefId')
        if locationId is not None:
            game['unique_locations'].add(locationId)

        date = play['playDate'].split(' ')[0]
        unique_days_played_on.add(date)

        for player in play['playerScores']:
            if player['playerRefId'] != anonymous_id:
                game['unique_players'].add(player['playerRefId'])

            if player['playerRefId'] == self_id and player['newPlayer']:
                game['first_time'] = True

    # Calculate estimated time and new game count
    for game in game_dict.values():
        game['total_time_played'] = game['plays'] * game['average_play_time']
        estimated_time_played += game['total_time_played']

        if game['first_time']:
            new_games_played += 1

    # Print text results
    output_text = ""

    output_text += f"Total Plays: {total_plays}\n\n"
    output_text += f"Friends Played With: {friends_played_with}\n\n"
    output_text += f"Unique Games: {unique_games}\n\n"
    output_text += f"Unique Locations: {unique_locations}\n\n"
    output_text += f"New Games Played: {new_games_played}\n\n"
    output_text += f"Estimated Time Played: {round(estimated_time_played / 60)} hours\n\n"
    output_text += f"Days Played On: {len(unique_days_played_on)}\n\n"

    output_text += "| Game | Time | Plays | Locations | Friends Played With | First Time? |\n"
    output_text += "| --- | --- | --- | --- | --- | --- |\n"

    game_list = list(game_dict.values())
    game_list.sort(key=lambda value: -value['plays'])

    for game in game_list:
        # skips any expansions that got included
        if game['plays'] == 0:
            continue

        # subtract 1 from unique_players to account for self (anonymous should already have been filtered out)
        output_text += f"| {game['name']} | {round(game['total_time_played'] / 60)} | {game['plays']} | {len(game['unique_locations'])} | {len(game['unique_players']) - 1} | {'✓' if game['first_time'] else ''} |\n"


    print(output_text)