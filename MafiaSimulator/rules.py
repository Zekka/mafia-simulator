from roles import *
import random

def unique_names(names):
    counts = {}
    for name in names:
        if name in counts: counts[name] += 1
        else: counts[name] = 1

    counts_so_far = dict(counts)
    for name in names:
        if counts[name] > 1:
            yield "%s %s" % (name, counts[name] - counts_so_far[name] + 1)
            counts_so_far[name] -= 1
        else:
            yield name

# simulator: returns which faction won
def play_game(reporter, setup, personalities):
    # == Set up the game. == #
    role_list = setup()
    random.shuffle(role_list)
    personality_list = [builder() for builder in list(personalities())[:len(role_list)]]
    names = unique_names([personality["name"] for personality in personality_list])
    players = [player_builder(name, personality) for player_builder, name, personality in zip(role_list, names, personality_list)]
    original_players = list(players)
    reporter.gamestart(players)

    day = 0
    # == Now run the game. ==
    while True: 
        if game_get_winner(players) != None: break

        day += 1
        reporter.day(day)

        reporter.daystart(players)
        run_day_phase(reporter, players)

        if game_get_winner(players) != None: break

        reporter.nightstart(day)
        run_night_phase(reporter, players)

    outcome = (game_get_winner(players), day)
    reporter.outcome(original_players, outcome[0], outcome[1])
    return outcome

def run_day_phase(reporter, players):
    # Run votes. None is no lynch
    player_votes = {oid: [] for oid, player in enumerate(players)}
    player_votes[None] = []

    voters = list(enumerate(players))
    random.shuffle(voters) # so vote output is in randomized order
    for id, player in voters:
        valid_lynches = None
        if not faction_is_scum(player["faction"]):
            if odds_check(0.2):
                valid_lynches = valid_lynches or [None]

            elif odds_check(0.1):
                # force vote of scum
                valid_lynches = valid_lynches or [oid for oid, other in enumerate(players) if faction_is_scum(other["faction"]) and not faction_glom(player["faction"], other["faction"])]
                reporter.vote_scum(player, not valid_lynches)

            valid_lynches = valid_lynches or [oid for oid, other in enumerate(players) if oid != id]
        else:
            if odds_check(0.2):
                valid_lynches = valid_lynches or [None]

            elif odds_check(0.05):
                reporter.bus(player)

                # force bus
                valid_lynches = valid_lynches or [oid for oid, other in enumerate(players) if other["faction"] == player["faction"] and oid != id]

            # just vote any player not a member of scum's faction 
            valid_lynches = valid_lynches or [oid for oid, other in enumerate(players) if other["faction"] != player["faction"]]
        
        # no target yet: vote for any old player
        valid_lynches = valid_lynches or list(range(len(players)))

        # pick vote and add one
        player_votes[random.choice(valid_lynches)].append(player)

    # Lynch the most voted player, picking at random in the event of a tie
    _, _, most_voted = max((len(votes), random.random(), oid) for oid, votes in player_votes.items())
    reporter.votes(players, player_votes, most_voted)
    if most_voted == None:
        reporter.no_lynch()
    else:
        reporter.lynch(players[most_voted])
        del players[most_voted]

def run_night_phase(reporter, players):
    nightkill_factions = set(player["faction"] for player in players if faction_has_nightkill(player["faction"]))
    for faction in nightkill_factions:
        valid_nightkills = None
        if not faction_is_scum(faction):
            if odds_check(0.1):
                # at least try to kill scum
                valid_nightkills = valid_nightkills or [oid for oid, other in enumerate(players) if faction_is_scum(other["faction"])]
                if valid_nightkills: reporter.nightkill_scum(player)
            elif odds_check(0.3):
                # try to guess the scum by picking anyone who's not us
                valid_nightkills = valid_nightkills or [oid for oid, other in enumerate(players) if other["faction"] != faction]
                if valid_nightkills: reporter.nightkill_randomly(player)
            else:
                # don't even guess
                valid_nightkills = valid_nightkills or [None]

        else:
            # just don't kill a fellow scumbag
            valid_nightkills = valid_nightkills or [oid for oid, other in enumerate(players) if other["faction"] != faction]

        # if we haven't found a kill, don't kill
        valid_nightkills = valid_nightkills or [None]

        kill = random.choice(valid_nightkills)
        reporter.nightkill(players, faction, players[kill])
        if kill != None: del players[kill]


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

    population = sum(factions.values())
    for faction in factions:
        friends = [participator for participator in factions if faction_glom(participator, faction)]
        friends_count = sum(factions[friend] for friend in friends)

        # == Wincon 0: A town faction will teamwin when they and their friends are the whole population ==
        if friends_count == population: return tuple(sorted(friends))

        # == Wincon 1: A scum faction that can teamwin will win if they and factions who can teamwin with them are a majority,. ==
        if faction_is_scum(faction) and friends_count > population / 2: return tuple(sorted(friends))

        # == Wincon 2: A scum faction that can teamwin will win if they and factions who can teamwin with them are 50%, no one outside that 50% has a nightkill, and they do have a nightkill. ==
        if faction_is_scum(faction) and friends_count == population / 2 and population % 2 == 0:
            if not any(faction_has_nightkill(friend) for friend in friends): 
                continue # not a winner: endgaming requires a nightkill

            nonfriends = [participator for participator in factions if not faction_glom(participator, faction)]
            if any(faction_has_nightkill(nonfriends) for nonfriend in nonfriends):
                continue # not a winner: a non-friend has a nightkill

            return tuple(sorted(friends))

    # No one won yet.
    return None
