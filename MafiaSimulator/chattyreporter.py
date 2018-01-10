def friendly(player):
    return "%s (%s)" % (player["name"], player["role"])


def gamestart(players):
    print "== GAME START =="
    print "The roles are assigned:"
    print 
    print "\n".join(
        "  " + friendly(player) for player in sorted(players, key=friendly)
    )


def day(n):
    print
    print "-- DAY %d --" % n


def daystart(players):
    faction_names = sorted(set(player["faction"] for player in players))
    factions = ", ".join(
        "%s: %d players" % (faction, len([player for player in players if player["faction"] == faction])) 
        for faction in faction_names
    )
    # roles = ", " .join(sorted(player["role"] for player in players))
    # print "(%s) [%s]" % (factions, roles)
    print "(%s)" % factions
    print 
    print "Plurality rules are in effect: whichever player receives the most votes (or No Lynch) will be lynched." 
    print 
    print "'' Day events ''"


def vote_scum(player, however):
    if however:
        print "%s reads scum. (however, %s can win with all remaining scum)" % (friendly(player), friendly(player))
    else:
        print "%s reads scum." % friendly(player)


def bus(player):
    print "%s wants to bus a teammate." % friendly(player)


def votes(players, votes, lynch):
    print "A rope is found and a vote is called."
    print
    name_max = max(max(len(friendly(player)) for player in players), len("No Lynch"))
    for pid, player in enumerate(players):
        print "%s %s: %s  %s" % (
            "*" if pid == lynch else " ",
            friendly(player).ljust(name_max), 
            str(len(votes[pid])).rjust(2), 
            ", ".join("%s (%s)" % (voter["name"], voter["role"]) for voter in votes[pid])
        )
    print "%s %s: %s  %s" % (
        "*" if None == lynch else " ",
        "No Lynch".ljust(name_max), 
        str(len(votes[None])).rjust(2), 
        ", ".join("%s (%s)" % (voter["name"], voter["role"]) for voter in votes[None])
    )
    print


def lynch(player):
    print "%s is lynched." % friendly(player)


def no_lynch():
    print "Nobody is lynched. (Suckers!)"


def nightstart(n):
    print
    print "-- NIGHT %d --" % n


def nightkill(players, faction, kill):
    print "Faction %s (%s) nightkills %s." % (
        faction,
        ", ".join(
            friendly(player) for player in sorted(players, key=friendly) if player["faction"] == faction 
        ),
        friendly(kill)
    )


def outcome(players, winners, day):
    print 
    print "-- OUTCOME --"
    print "On day %s, the winners were: " % day 
    print
    print "\n".join(
        "  " + friendly(player) for player in sorted(players, key=friendly) if player["faction"] in winners
    )
    print
    print "The winning factions were: %s." % ", ".join(winners)