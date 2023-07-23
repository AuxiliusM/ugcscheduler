from csv import DictReader

BYEWEEK_TEAM_NAME = 'Bye'


def load_win_dict(filename: str):
    with open(filename, 'r') as f:
        lines = [l.replace(' ', '') for l in f]  # cleanup
        reader = DictReader(lines, delimiter='\t')
        win_dict = {}
        for row in reader:
            played = []
            win_count = 0

            count = 1
            while str(count) in row:
                key = str(count)
                match_res = row[key]

                if match_res == 'W':
                    win_count += 1
                elif match_res == 'B':
                    win_count += 1
                
                team = row['Opp'+key]
                if team != '':
                    played.append(team)

                count += 1

            win_dict[row['Clan']] = {'wins': win_count, 'played': played}

        found_teams = win_dict.keys()
        for _, data in win_dict.items():
            # filter out all dropped teams, bc they are not included as clan name
            data['played'] = [t for t in data['played'] if t in found_teams]

        if len(win_dict.keys()) % 2 == 0:
            for _, data in win_dict.items():
                # handles edge case if additional team joined late or dropped out
                # if that is the case bye weeks might have happend, but should not be
                # used for scheduling anymore
                while data['played'].count(BYEWEEK_TEAM_NAME) > 0:
                    data['played'].remove(BYEWEEK_TEAM_NAME)

        else:
            # create dummy team for byeweek scheduling, other teams know if they played with it or not
            win_dict[BYEWEEK_TEAM_NAME] = {'wins': 0, 'played': []}

    return win_dict


def get_available_teams(win_dict: dict):
    total_teams = list(win_dict.keys())
    if len(total_teams) % 2 != 0:
        total_teams.append(BYEWEEK_TEAM_NAME)

    available_dict = {}
    unavailable_dict = {}
    for team, data in win_dict.items():
        _, played = data['wins'], data['played']
        available = [t for t in total_teams if t not in played and t != team]

        available_dict[team] = available
        unavailable_dict[team] = played 

    return available_dict, unavailable_dict