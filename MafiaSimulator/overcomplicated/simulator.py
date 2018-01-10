from factions import *

# simulator: returns which faction won
def play_game(setup, skill_level):
    # == Set up the game. == #
    role_list = setup()
    players = [player_builder(name) for player_builder in role_list]
    factions = set(player["faction"] for player in players)

    # == No player knows any player's role or faction at first. ==
    known_role = {}
    known_faction = {}
    for knower in range(len(players)):
        for knowee in range(len(players)):
            known_role[knower, knowee] = None
            known_faction[knower, knowee] = None

    # == Each player knows his own role and faction. ==
    for knower in range(len(players)):
        known_role[knower, knower] = knower["role"]
        known_faction[knower, knower] = knower["faction"]

    # == Some factions know the roles of players who are in another faction. (ex. mafia players know mafia players) ==
    for knower in range(len(players)):
        for other in range(len(players)):
            if ( faction_knows_members(knower["faction"], other["faction"]) or # if knower faction knows other faction
                len(factions) <= 2 # or if there are two or fewer factions
            ) : 
                known_faction[(knower, other)] = other["faction"]

    # == Now run the game. ==
    while game_get_winner(players) == None:
        # == Day phase ==
        pass

    return game_get_winner(players)

def game_get_winner(players):
    # First of all, get a list of participating factions and their membership counts
    factions = {}
    for i in players:
        faction = i["faction"]

        if faction not in factions: factions[faction] = 0
        factions[faction] += 1

    if len(factions) == 0:
        # == Wincon 0: If every player is dead, then the winner is no faction. == #
        return ()

    for faction in factions:
        # == Wincon 1: A faction that can teamwin will win if they and factions who can teamwin with them are the only ones left. ==
        if not faction_can_teamwin(faction): continue

        # if every remaining faction that isn't `faction` can teamwin with faction
        if all(faction_can_teamwin(other, faction) for other in factions.keys() if other != faction): 
            # it's a big teamwin!
            return tuple(sorted(factions.keys()))

    for faction in factions:
        # == Wincon 2: A faction that can solowin will win if only one player is left and that player is a member of that faction. ==
        if not faction_can_solowin(faction): continue

        if set(factions.keys()) == set(faction) and factions[faction] == 1: return (faction,)

    # No one won yet.
    return None