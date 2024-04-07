from csv import DictReader

TABLE_TSV = 'table.tsv'
BYEWEEK_TEAM_NAME = 'Bye'


def load_data(filename: str) -> tuple[list, dict]:
    with open(filename, 'r', encoding="utf8") as f:
        lines = [l.replace(' ', '') for l in f]  # cleanup
        reader = DictReader(lines, delimiter='\t')

        win_dict = {}  # dict for stoting wins
        team_list = []  # list of all teams

        for row in reader:
            played = []
            win_count = 0
            bye_count = 0

            count = 1
            while str(count) in row:
                key = str(count)
                match_res = row[key]

                if match_res == 'W':  # regular win
                    win_count += 1
                    played.append(row['Opp'+key])

                elif match_res == 'B':  # byeweek win
                    bye_count += 1
                    played.append(BYEWEEK_TEAM_NAME)  # force own byeweek team name
                
                elif match_res == 'L':  # loss
                    played.append(row['Opp'+key])
                
                else:  # no more valid results found
                    break
                
                count += 1

            win_dict[row['Clan']] = {'wins': win_count+bye_count, 'played': played}
            team_list.append(row['Clan'])

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
     
    score = (played_count << 16) + base_score

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


# hacky solution for considering the ordering of the team list
# currently the tsv doesnt contain any info on the points of a team
# the only information is the ordering in the team list, which shows te best team first
def modify_win_dict(win_dict: dict, team_list: list):
    for team in team_list:
        win_dict[team]['wins'] = (win_dict[team]['wins'] << 8) + (len(team_list) - team_list.index(team))


def handle_byeweek(team_list: list, win_dict: dict):
    new_list = team_list.copy()

    new_list = sorted(new_list, key=lambda x: (win_dict[x]['played'].count(BYEWEEK_TEAM_NAME) << 32) + (win_dict[x]['wins'] << 16) + (len(team_list) - team_list.index(x)))
    bye_team = new_list[0]

    new_list.remove(bye_team)

    return bye_team, new_list


def pretty_print_matching(matching):
    printed = []
    for key in matching.keys():
        if key not in printed:
            print(f"\t{key} : {matching[key]}")
            printed.append(key)
            printed.append(matching[key])


if __name__ == '__main__':
    team_list, win_dict = load_data(TABLE_TSV)
    
    modify_win_dict(win_dict, team_list)  # hacky solution

    has_byweek = len(team_list) % 2 != 0

    if has_byweek:  # odd number of teams, find team to get byeweek
        bye_team, rest_list = handle_byeweek(team_list, win_dict)
        team_list = rest_list

    assert len(team_list) % 2 == 0  # always match even number of teams

    rankings = get_rankings(team_list, win_dict)
    matching = get_stable_matchings(team_list, rankings)

    if has_byweek:  # add byeweek and byeweek team after the rest was matched
        matching[bye_team] = BYEWEEK_TEAM_NAME
        matching[BYEWEEK_TEAM_NAME] = bye_team

    print("Scheduled Matches:\n------------------\n")

    pretty_print_matching(matching)
    
    input()

