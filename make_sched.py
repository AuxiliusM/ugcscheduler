from parse_data import load_win_dict, get_available_teams

TABLE_TSV = 'table.tsv'


def score_matches(available: dict, win_dict: dict):
    match_dict = {} #  key: tuple(team1, team2) <- teamnames sorted alphabetically

    for team, opponents in available.items():
        for op in opponents:
            match_tuple = tuple(sorted((team, op)))
            match_dict[match_tuple] = score_match(team, op, available, win_dict, depth=5)

    return match_dict


def score_repeated_matches(unavailable: dict, win_dict: dict):
    match_dict = score_matches(unavailable, win_dict)

    for match in match_dict.keys():
        team, op = match
        multiplier = win_dict[team]['played'].count(op)  # the amount of time both teams have played each other (always >= 1)
        match_dict[match] *= multiplier  # should hinder even more matches against each other

    return match_dict


def score_match(team: str, op: str, available: dict, win_dict: dict, depth=0):
    wins_team = win_dict[team]['wins']
    wins_op = win_dict[op]['wins']

    score = abs(wins_team - wins_op)

    if depth == 0:
        return score
    
    score_diff_sum = 0
    for other_op in available[op]:
        score_diff_sum += score - score_match(op, other_op, available, win_dict, depth-1)
    avg_score_diff = score_diff_sum / len(other_op)

    return score + avg_score_diff


def schedule_matches(teams: list, available_matches: dict, unavailable_matches: dict):
    teams = teams.copy()
    sched_matches = []
    
    matches = list(available_matches.keys())
    matches = sorted(matches, key=available_matches.get)

    filler_matches = list(unavailable_matches.keys())
    filler_matches = sorted(filler_matches, key=unavailable_matches.get)

    # hit and miss, trying to find best repeat matches in a loop (bad performance, easiest solution)
    succ = False
    while not succ:
        succ = schedule_matches_rec(teams, matches, sched_matches)

        if succ:
            return sched_matches
        
        filler = filler_matches.pop(0)
        sched_matches.append(filler)
        matches = [mat for mat in matches if not (mat[0] in filler or mat[1] in filler)]
        print(f"Adding repeat match {filler}.")
    
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


if __name__ == '__main__':
    win_dict = load_win_dict(TABLE_TSV)

    # 1. check wich teams are available
    available, unavailable = get_available_teams(win_dict)

    # 2. teams should be as close as possible together
    available_match_dict = score_matches(available, win_dict)
    unavailable_match_dict = score_repeated_matches(unavailable, win_dict)

    res = schedule_matches(list(available.keys()), available_match_dict, unavailable_match_dict)

    print(res)
    input()

