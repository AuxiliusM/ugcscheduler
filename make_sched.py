from parse_data import load_win_dict, get_available_teams

TABLE_TSV = 'table.tsv'


def score_matches(available: dict, win_dict: dict):
    match_dict = {} #  key: tuple(team1, team2) <- teamnames sorted alphabetically

    for team, opponents in available.items():
        for op in opponents:
            match_tuple = tuple(sorted((team, op)))
            match_dict[match_tuple] = score_match(team, op, available, win_dict, depth=5)

    return match_dict


def score_match(team: str, op: str, available: dict, win_dict: dict, depth=0):
    wins_team = win_dict[team]['wins']
    wins_op = win_dict[op]['wins']

    score = abs(wins_team - wins_op)

    if depth == 0:
        return score
    
    score_sum = 0
    for other_op in available[op]:
        score_sum += score - score_match(op, other_op, available, win_dict, depth-1)

    return score + score_sum


def schedule_matches(match_dict: dict, available: dict):
    teams = list(available.keys())
    matches = list(match_dict.keys())
    matches = sorted(matches, key=match_dict.get)

    sched_matches = []
    succ = schedule_matches_rec(teams, matches, sched_matches)

    if not succ:
        print("Could not find a schedule, too few teams compared to weeks played.")

    return sched_matches


def schedule_matches_rec(teams: list, matches: list, sched_matches: list):  # function works in place!
    if len(teams) > 0 and len(matches) == 0:
        return False
    elif len(teams) == 0 and len(matches) == 0:
        return True

    for m in matches:
        team, op = m
        new_teams = [t for t in teams if t != team and t != op]
        new_matches = [mat for mat in matches if not (mat[0] in m or mat[1] in m)]

        succ = schedule_matches_rec(new_teams, new_matches, sched_matches)

        if succ:
            sched_matches.append(m)
            return True
        
    return False



win_dict = load_win_dict(TABLE_TSV)

# 1. check wich teams are available
available = get_available_teams(win_dict)

# 2. teams should be as close as possible together
match_dict = score_matches(available, win_dict)

res = schedule_matches(match_dict, available)

print(res)

