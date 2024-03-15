from csv import DictReader

TABLE_TSV = 'table.tsv'
BYEWEEK_TEAM_NAME = 'Bye'


def load_data(filename: str) -> tuple[list, dict]:
    with open(filename, 'r', encoding="utf8") as f:
        lines = [l.replace(' ', '') for l in f]  # cleanup
        reader = DictReader(lines, delimiter='\t')

        win_dict = {}  # dict for stoting wins
        team_list = [BYEWEEK_TEAM_NAME]  # list of all teams

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
            team_list.append(row['Clan'])

        found_teams = win_dict.keys()
        for _, data in win_dict.items():
            # filter out all dropped teams, bc they are not included as clan name
            data['played'] = [t for t in data['played'] if t in found_teams or t == BYEWEEK_TEAM_NAME]

        if len(win_dict.keys()) % 2 == 0:
            for _, data in win_dict.items():
                # handles edge case if additional team joined late or dropped out
                # if that is the case bye weeks might have happend, but should not be
                # used for scheduling anymore
                while data['played'].count(BYEWEEK_TEAM_NAME) > 0:
                    data['played'].remove(BYEWEEK_TEAM_NAME)

        else:
            # create dummy team for byeweek scheduling, other teams know if they played with it or not
            win_dict[BYEWEEK_TEAM_NAME] = {'wins': 0, 'played': [team for team, data in win_dict.items() if BYEWEEK_TEAM_NAME in data['played']]}

    return team_list, win_dict


def get_available_teams(win_dict: dict) -> list:
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


def get_rankings(team_list: list[str], win_dict: dict) -> dict:
    rankings = {}
    for team in team_list:
        others = [other for other in team_list if other != team]  # remove target
        ranking = sorted(others, key=lambda x: score_team(team, x, win_dict))  # order list by ranking

        rankings[team] = ranking
    
    return rankings


def score_team(target: str, other: str, win_dict: dict):
    base_score = abs(win_dict[target]['wins'] - win_dict[other]['wins'])
    played_count = win_dict[target]['played'].count(other)
    score = base_score + 10 * played_count

    return score


def get_stable_matchings(team_list: list, rankings: dict):
    # rankings to dict for optimization
    team_to_get_rank = {team: {other: rank for rank, other in enumerate(ranking)} for team, ranking in rankings.items()}
    matching = {}

    unmatched = team_list.copy()

    while len(unmatched) > 0:
        target = unmatched.pop()
        
        found = None
        for other in rankings[target]:

            if other not in matching:
                found = other
                break

            get_rank = team_to_get_rank[other]
            if get_rank[target] < get_rank[matching[other]]:
                found = other
                break
        
        if found in matching:
            unmatched.append(matching[found])
        else:
            unmatched.remove(found)

        matching[target] = found
        matching[found] = target
    
    return matching


if __name__ == '__main__':
    team_list, win_dict = load_data(TABLE_TSV)

    rankings = get_rankings(team_list, win_dict)
    matching = get_stable_matchings(team_list, rankings)

    print("Scheduled Matches:\n------------------\n")

    printed = []
    for key in matching.keys():
        if key not in printed:
            print(f"\t{key} : {matching[key]}")
            printed.append(key)
            printed.append(matching[key])
    
    input()

