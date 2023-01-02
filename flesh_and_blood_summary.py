import json
from pathlib import Path

def flesh_and_blood_summary(path: Path):
    with path.open(newline='') as jsonfile:
        year_json = json.load(jsonfile)

        # Calculate self / anonymous ids
        self_id = year_json['userInfo']['meRefId']
        anonymous_id = None
        for player in year_json['players']:
            if player['isAnonymous']:
                anonymous_id = player['id']

        # Setup stat variables
        game_formats = {}
        # blitz = {
        #     'heroes': {},
        #     'plays': 0,
        #     'times_went_first': 0,
        #     'wins': 0,
        #     'losses': 0,
        #     'ties': 0,
        #     'wins_when_first': 0,
        # }

        # Parse data from plays
        for play in year_json['plays']:
            if play['ignored']:
                continue

            # Get game format object to use
            game_format = play.get('board')

            if game_format is None:
                print("Missing format for game " + play['uuid'])
                continue

            game_format_stats = game_formats.get(game_format)

            if game_format_stats is None:
                game_format_stats = {
                    'heroes': {},
                    'plays': 0,
                    'times_went_first': 0,
                    'wins': 0,
                    'losses': 0,
                    'ties': 0,
                    'wins_when_first': 0,
                }
                game_formats[game_format] = game_format_stats

            # Calculate stats
            game_format_stats['plays'] += 1

            winner_exists = False
            self_role = None
            self_start_player = False
            self_won = False
            heroes_played_against = set()

            for player in play['playerScores']:
                role = player.get('role')
                hero = game_format_stats['heroes'].get(role)

                if hero is None:
                    hero = {
                        'played_as': 0,
                        'times_went_first_as': 0,
                        'wins_as': 0,
                        'losses_as': 0,
                        'ties_as': 0,
                        'wins_when_first_as': 0,
                        'played_against': 0,
                        'times_went_first_against': 0,
                        'wins_against': 0,
                        'losses_against': 0,
                        'ties_against': 0,
                        'wins_when_first_against': 0,
                    }

                    game_format_stats['heroes'][role] = hero

                if player['winner']:
                    winner_exists = True

                # Player is me
                if player['playerRefId'] == self_id:
                    self_role = role
                    hero['played_as'] += 1

                    if player['startPlayer']:
                        self_start_player = True
                        game_format_stats['times_went_first'] += 1
                        hero['times_went_first_as'] += 1
                    if player['winner']:
                        self_won = True
                        game_format_stats['wins'] += 1
                        hero['wins_as'] += 1
                    if player['startPlayer'] and player['winner']:
                        game_format_stats['wins_when_first'] += 1
                        hero['wins_when_first_as'] += 1
                # Player is not me
                else:
                    heroes_played_against.add(role)

                    if player['winner']:
                        game_format_stats['losses'] += 1
                        hero['losses_against'] += 1

            for hero_against in heroes_played_against:
                hero_object = game_format_stats['heroes'].get(hero_against)
                hero_object['played_against'] += 1

                if self_start_player:
                    hero_object['times_went_first_against'] += 1
                if self_won:
                    hero_object['wins_against'] += 1
                if self_start_player and self_won:
                    hero_object['wins_when_first_against'] += 1

            if not winner_exists:
                game_format_stats['ties'] += 1

                game_format_stats['heroes'].get(self_role)['ties_as'] += 1
                for hero in heroes_played_against:
                    game_format_stats['heroes'].get(hero)['ties_against'] += 1
            elif not self_won:
                game_format_stats['heroes'].get(self_role)['losses_as'] += 1

    # Print results
    output_text = ""

    for game_format_name in sorted(game_formats):
        output_text += create_format_results_table(game_format_name, game_formats[game_format_name])
        output_text += "\n"

    print(output_text)

def create_format_results_table(format_name, format_object):
    output_text = ""

    win_percent = round(format_object['wins'] / format_object['plays'] * 100, 2) if format_object['plays'] > 0 else 0.0
    win_percent_when_first = round(format_object['wins_when_first'] / format_object['times_went_first'] * 100, 2) if format_object['times_went_first'] > 0 else 0.0

    output_text += f"### {format_name}\n"

    output_text += f"#### Overall\n"
    output_text += "| Plays | Wins | Losses | Ties | Win Percentage | Times Went First | Wins When First Player | Win % When First Player |\n"
    output_text += "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
    output_text += f"| {format_object['plays']} | {format_object['wins']} | {format_object['losses']} | {format_object['ties']} | {win_percent}% | {format_object['times_went_first']} | {format_object['wins_when_first']} | {win_percent_when_first}% |\n"
    output_text += "\n"

    output_text += f"#### Hero Stats As\n"
    output_text += "| Hero | Plays | Wins | Losses | Ties | Win Percentage | Times Went First | Wins When First Player | Win % When First Player |\n"
    output_text += "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"

    for hero in sorted(format_object['heroes']):
        hero_object = format_object['heroes'][hero]

        plays = hero_object['played_as']

        if plays == 0:
            continue

        times_went_first = hero_object['times_went_first_as']
        wins = hero_object['wins_as']
        losses = hero_object['losses_as']
        ties = hero_object['ties_as']
        win_percent = round(wins / plays * 100, 2) if plays > 0 else 0.0
        wins_when_first = hero_object['wins_when_first_as']
        win_percent_when_first = round(wins_when_first / times_went_first * 100, 2) if times_went_first > 0 else 0.0

        output_text += f"| {hero} | {plays} | {wins} | {losses} | {ties} | {win_percent}% | {times_went_first} | {wins_when_first} | {win_percent_when_first}% |\n"

    output_text += "\n"

    output_text += f"#### Hero Stats Against\n"
    output_text += "| Hero | Plays | Wins | Losses | Ties | Win Percentage | Times Went First | Wins When First Player | Win % When First Player |\n"
    output_text += "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"

    for hero in sorted(format_object['heroes']):
        hero_object = format_object['heroes'][hero]

        plays = hero_object['played_against']

        if plays == 0:
                continue

        times_went_first = hero_object['times_went_first_against']
        wins = hero_object['wins_against']
        losses = hero_object['losses_against']
        ties = hero_object['ties_against']
        win_percent = round(wins / plays * 100, 2) if plays > 0 else 0.0
        wins_when_first = hero_object['wins_when_first_against']
        win_percent_when_first = round(wins_when_first / times_went_first * 100, 2) if times_went_first > 0 else 0.0

        output_text += f"| {hero} | {plays} | {wins} | {losses} | {ties} | {win_percent}% | {times_went_first} | {wins_when_first} | {win_percent_when_first}% |\n"

    output_text += "\n"

    return output_text