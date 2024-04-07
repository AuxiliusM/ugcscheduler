from itertools import combinations

from make_sched import load_data, modify_win_dict, TABLE_TSV
from make_sched import score_team, pretty_print_matching

def calc_matching_costs(matching, win_dict):
    cost = 0
    for t1, t2 in matching.items():
        cost += score_team(t1, t2, win_dict)

    return cost / 2
    

def test_all_matchings(team_list, win_dict):
    all_matchings = []
    for matching in combinations(combinations(team_list, 2), len(team_list) // 2):
        valid = True
        dict = {}
        for match in matching:
            t1, t2 = match
            if t1 in dict or t2 in dict:
                valid = False
            
            dict[t1] = t2
            dict[t2] = t1
        
        if valid:
            all_matchings.append(dict)
    
    all_sorted = sorted(all_matchings, key=lambda x: calc_matching_costs(x, win_dict))
    costs = [calc_matching_costs(m, win_dict) for m in all_sorted]
    
    for m, c in zip(all_sorted, costs):
        if c == costs[0]:
            pretty_print_matching(m)
            print("-----------------------")
        
    print(f"Min cost: {costs[0]}")


if __name__ == '__main__':
    team_list, win_dict = load_data(TABLE_TSV)
    modify_win_dict(win_dict, team_list)

    assert len(team_list) % 2 == 0

    test_all_matchings(team_list, win_dict)
