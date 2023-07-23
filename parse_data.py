BYEWEEK_TEAM_NAME = 'byeweek_team'

# terrible code, should be done with import csv for better compatibility
def load_win_dict(filename):
    table = open(filename, "r", encoding="utf8")

    win_dict = {}
    next(table)  # skip first line, bc header

    for line in table:
        splitline = line.split(" \t")
        
        win_dict[f"{splitline[1]}"] = {"wins": 0, "played": []}
        for elem in splitline[1:]:
            elem = elem.replace("\t","")

            if elem == "W":
                win_dict[f"{splitline[1]}"]["wins"] += 1
            elif elem == "B":
                win_dict[f"{splitline[1]}"]["wins"] += 1
                win_dict[f"{splitline[1]}"]["played"].append(BYEWEEK_TEAM_NAME)
            elif elem != "L": #this code here is a warcrime
                if elem != "\n":
                    if elem != f"{splitline[1]}":
                        if elem != "":
                            win_dict[f"{splitline[1]}"]["played"].append(elem)

    # for elem in clandic:
    #     print(elem, clandic[elem])
    
    total_teams = win_dict.keys()
    if len(total_teams) % 2 != 0:
        win_dict[BYEWEEK_TEAM_NAME] = {"wins": 0, "played": []}

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