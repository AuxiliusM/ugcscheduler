from csv import DictReader


TABLE_TSV = 'table.tsv'
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


def score_matches(available: dict, win_dict: dict):
    match_scores = {} #  key: tuple(team1, team2) <- teamnames sorted alphabetically

    for team, opponents in available.items():
        for op in opponents:
            match_tuple = tuple(sorted((team, op)))
            match_scores[match_tuple] = score_match(team, op, available, win_dict, depth=5)

    return match_scores


def score_repeated_matches(unavailable: dict, win_dict: dict, available_match_scores: dict):
    available_matches = available_match_scores.keys()
    match_dict = score_matches(unavailable, win_dict)

    for team, opponents in unavailable.items():
        for op in opponents:
            match = tuple(sorted((team, op)))
            # counts how many matches would be unavailable if match is scheduled
            matches_canceled = 0
            matches_remaining = 0
            # sums up the scores of the cancelled matches
            remaining_score_sum = 0
            for available in available_matches:
                if team in available or op in available:
                    matches_canceled += 1
                else:
                    matches_remaining += 1
                    remaining_score_sum += available_match_scores[available]
            
            if matches_remaining > 0:
                avg_remaining_score = remaining_score_sum / matches_remaining
            else:
                avg_remaining_score = 2 << 32

            multiplier = win_dict[team]['played'].count(op)  # the amount of time both teams have played each other (always >= 1)
            match_dict[match] = avg_remaining_score + matches_canceled + match_dict[match] * multiplier  # should hinder even more matches against each other

    return match_dict


def score_match(team: str, op: str, available: dict, win_dict: dict, depth=0):
    if team == BYEWEEK_TEAM_NAME or op == BYEWEEK_TEAM_NAME:
        return 0

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

        team, op = filler
        teams = remove_teams(teams, team, op)
        matches = remove_matches(matches, filler)
        filler_matches = remove_matches(filler_matches, filler)

        print(f"Adding repeat match {filler}.")
    
    return sched_matches


def schedule_matches_rec(teams: list, matches: list, sched_matches: list):  # function works in place!
    if len(teams) > 0 and len(matches) == 0:
        return False
    elif len(teams) == 0 and len(matches) == 0:
        return True

    for m in matches:
        team, op = m
        new_teams = remove_teams(teams, team, op)
        new_matches = remove_matches(matches, m)

        succ = schedule_matches_rec(new_teams, new_matches, sched_matches)

        if succ:
            sched_matches.append(m)
            return True
        
    return False


def remove_teams(teams: list, team1: str, team2: str):
    return [t for t in teams if t != team1 and t != team2]


def remove_matches(matches: list, match: tuple):
    return [mat for mat in matches if not (mat[0] in match or mat[1] in match)]


if __name__ == '__main__':
    win_dict = load_win_dict(TABLE_TSV)

    # 1. check wich teams are available
    available, unavailable = get_available_teams(win_dict)

    # 2. teams should be as close as possible together
    available_match_scores = score_matches(available, win_dict)

    # 3. score already played matches for repeated plays
    unavailable_match_scores = score_repeated_matches(unavailable, win_dict, available_match_scores)

    res = schedule_matches(list(available.keys()), available_match_scores, unavailable_match_scores)

    print(res)
    input()

