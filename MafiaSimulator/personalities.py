from utils import *
from tags import *
from roles import faction_is_scum

import random

personalities = []


def __personality(f):
    personalities.append(f)
    return f



# == Standard math == #

# possible_to_vote is {pid: player}
# me is a pid
def __standard_lynch_targets(personality, day, me, possible_to_vote):
    # TODO: Check for a lylo situation and if so, refuse to no lynch.
    if odds_check(personality.no_lynch_propensity(day)):
        return [None]

    wants_to_lynch = []
    for pid, player in possible_to_vote.items():
        if pid == me: continue

        acc = personality.accurate_scumread_propensity(day, player)
        inacc = personality.inaccurate_scumread_propensity(day, player)

        if odds_check(inacc) or (faction_is_scum(player["faction"]) and odds_check(acc)):
            wants_to_lynch.append((pid, player))

    if len(wants_to_lynch) == 0:
        wants_to_lynch = list(possible_to_vote)

    wants_to_lynch_2 = []
    for pid, player in wants_to_lynch:
        if (
            not (faction_is_scum(possible_to_vote[me]["faction"]) and player["faction"] == possible_to_vote[me]["faction"]) or 
            odds_check(personality.bus_propensity(day, player)) # TODO: Don't bus in lylo
        ):
            # remove lynch targets that are known to be of the same faction
            wants_to_lynch_2.append((pid, player))

    if len(wants_to_lynch_2) == 0:
        wants_to_lynch_2.append(None) # no lynch

    return wants_to_lynch_2
        

# == Mafiascum == #
@__personality
# TODO: Implement vote logic for default personality.
#
# Reminder of lynch flow:
# - for each votable player
#   if player is highly inadvisable to kill (ex: on same scumteam) do a bussing check. if bussing check fails, don't add them
#   if they are town *and* check(inaccurate scumread propensity), add them as a scumread
#   if they are scum *and* check(accurate scumread propensity) or check(inaccurate scumread propensity), add them as a scumread
#   if there are no scumreads, use the entire playerlist after filtering out characters who are highly inadvisable to kill.
class TheReckoner(object):
    def __init__(self): pass

    def name(self): return "The Reckoner"

    def tags(self): return [tag_assholish, tag_gallant]

    def __personal_dislike(self, day, other):
        score = daily(day, [0.0])
        score += tag_bonus(other, tag_annoying, 0.2)
        score += tag_bonus(other, tag_verbose, 0.2)
        score += tag_bonus(other, tag_policy, 0.2)
        return score

    def lynch_targets(self, day, me, possible_to_vote): 
        __standard_lynch_targets(self, day, me, possible_to_vote)

    def no_lynch_propensity(self, day):
        score = daily(day, [0.0])
        return score

    def bus_propensity(self, day, other):
        score = daily(day, [0.4, 0.1, 0.0])
        score += self.__personal_dislike(day, other)
        return score

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.2, 0.3, 0.45, 0.6])
        score += self.__personal_dislike(day, other)
        return score

    def inaccurate_scumread_propensity(self, day, other):
        score = daily(day, [0.3, 0.2, 0.1, 0.0]) # after day 4, all inaccurate scumreads will be due to things that annoy reckoner
        score += self.__personal_dislike(day, other)
        return score


@__personality
class Mastin(object):
    def __init__(self): pass

    def name(self): return "Mastin"

    def tags(self): return [tag_humble, tag_verbose]

    def __personal_dislike(self, day, other):
        score = daily(day, [0.0])
        score += tag_bonus(other, tag_verbose, -0.1) # likes verbose players
        return score

    def no_lynch_propensity(self, day):
        score = daily(day, [0.0])
        return score

    def bus_propensity(self, day, other):
        score = daily(day, [0.1, 0.15, 0.0])
        score += self.__personal_dislike(day, other)
        return score

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.2]) 
        score += self.__personal_dislike(day, other)
        return score

    def inaccurate_scumread_propensity(self, day, other):
        score = daily(day, [0.1]) 
        score += self.__personal_dislike(day, other)

        # even though mastin says he doesn't like policy lynches, he LOVES them
        # but only against players who are town
        score += tag_bonus(other, tag_policy, 0.5) 
        return score


@__personality
class Goofball(object):
    def __init__(self): pass

    def name(self): return "Goofball"
    def tags(self): return [tag_annoying, tag_assholish]

    def no_lynch_propensity(self, day):
        score = daily(day, [0.0])
        return score
    
    def bus_propensity(self, day, other):
        score = daily(day, [0.1, 0.15, 0.0])
        if day == 1: # dgb FUCKING LOVES bussing scumteam members that she hates
            score += tag_bonus(other, tag_annoying, 0.4)
            score += tag_bonus(other, tag_assholish, 0.4)
            score += tag_bonus(other, tag_policy, 0.4)
        return score

    def accurate_scumread_propensity(self, day, other):
        # earlygame reads better than lategame, not really influenced by superficial features of players
        score = daily(day, [0.4, 0.3, 0.2]) 
        return score

    def inaccurate_scumread_propensity(self, day, other):
        score = daily(day, [0.6, 0.3, 0.2]) # very first read is often wrong
        if day == 1:
            score += tag_bonus(other, tag_verbose, 0.1) # frequently on a verbose player
            score += tag_bonus(other, tag_humble, 0.1) # frequently on a humble player
        return score


@__personality
# TODO: Give Kabuto a propensity to self-vote 
class Kabuto(object):
    def __init__(self): pass

    def name(self): return "Kabuto"
    def tags(self): return [tag_annoying, tag_assholish, tag_policy]

    def no_lynch_propensity(self, day):
        score = daily(day, [0.6, 0.7, 0.8, 0.9, 1.0])
        return score

    def bus_propensity(self, day, other):
        # kabuto thinks this makes him smart
        score = daily(day, [1.0])
        return score

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.0]) # never accurately reads scum
        return score

    def inaccurate_scumread_propensity(self, day, other):
        score = daily(day, [0.0]) # players are only eligible if they annoy kabuto
        score += tag_bonus(other, tag_verbose, 0.2) # frequently on a verbose player
        return score


# == The Genius == #
@__personality
class Kyunghoon(object):
    def __init__(self): pass

    def name(self): return "Kyunghoon"
    def tags(self): return [tag_annoying, tag_gallant, tag_humble, tag_policy, tag_verbose]

    def __personal_dislike(self, day, other):
        score = daily(day, [0.0])
        score += tag_bonus(other, tag_gallant, -0.15) # he has a real weakness for people like sangmin who are gallant
        score += tag_bonus(other, tag_humble, -0.1) # especially those who are humble 
        score += tag_bonus(other, tag_assholish, 0.2) 
        return score

    def no_lynch_propensity(self, day):
        score = daily(day, [0.0])
        return score

    def bus_propensity(self, day, other):
        # kyunghoon likes big twists maybe too much
        score = daily(day, [0.8, 0.5, 0.1])
        score += self.__personal_dislike(day, other)
        return score

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.35, 0.4, 0.55, 0.6, 0.65]) # kyunghoon's intuitions are on point! but...
        score += self.__personal_dislike(day, other)
        return score

    def inaccurate_scumread_propensity(self, day, other):
        score = daily(day, [0.1]) # his suspicions are quite often justified
        score += self.__personal_dislike(day, other)
        return score


@__personality
class Sangmin(object):
    def __init__(self): pass

    def name(self): return "Sangmin"
    def tags(self): return [tag_gallant]

    def no_lynch_propensity(self, day):
        score = daily(day, [0.0])
        return score

    def bus_propensity(self, day, other):
        score = daily(day, [0.1, 0.1, 0.0])
        return score

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.15, 0.25, 0.3, 0.35]) # sangmin is better than average at reading people
        score += tag_bonus(other, tag_verbose, 0.1) # especially those who are verbose 
        score += tag_bonus(other, tag_policy, -0.1) # he is contrarian about people who deserve policy lynches
        return score

    def inaccurate_scumread_propensity(self, day, other):
        # sangmin doesn't usually get inaccurate scumreads
        score = daily(day, [0.0]) # his suspicions are quite often justified
        return score


@__personality
# TODO: I think yeonseung should frequently reciprocate votes because he's that kind of guy
class Yeonseung(object):
    def __init__(self): pass

    def name(self): return "Yeonseung"
    def tags(self): return [tag_annoying, tag_gallant, tag_humble]

    def no_lynch_propensity(self, day):
        score = daily(day, [0.2])
        return score

    def bus_propensity(self, day, other):
        # never
        score = daily(day, [0.0]) 
        return score

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.4, 0.45, 0.5, 0.6]) # yeonseung's reads are very good
        score += tag_bonus(other, tag_gallant, 0.2) # and he doesn't like gallant people
        score += tag_bonus(other, tag_policy, -0.3) # he really likes people who would be policy lynched
        score += tag_bonus(other, tag_verbose, -0.1) # he tolerates waffliness maybe too much
        return score

    def inaccurate_scumread_propensity(self, day, other):
        # yeonseung's initial reads are good but he's vengeful as FUCK
        score = daily(day, [0.0, 0.1]) # his suspicions are quite often justified
        if day >= 2:
            score += tag_bonus(other, tag_annoying, 0.1)
            score += tag_bonus(other, tag_gallant, 0.1)
            score += tag_bonus(other, tag_assholish, 0.4)
        return score


@__personality
class Jinho(object):
    def __init__(self): pass

    def name(self): return "Jinho"
    def tags(self): return [tag_gallant, tag_humble, tag_verbose]

    def no_lynch_propensity(self, day):
        return 0.0

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.1, 0.1, 0.3]) # jinho's reads are passable and fairly impartial
        return score

    def inaccurate_scumread_propensity(self, day, other):
        score = daily(day, [0.2, 0.0]) # initially noisy
        return score


@__personality
class Dongmin(object):
    def __init__(self): pass

    def name(self): return "Dongmin"
    def tags(self): return [tag_assholish, tag_gallant]

    def no_lynch_propensity(self, day):
        return 0.0

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.3, 0.6, 0.7, 0.8]) # dongmin's reads are really really good
        return score

    def inaccurate_scumread_propensity(self, day, other):
        score = daily(day, [0.35, 0.2, 0.0]) # initially noisy
        score += tag_bonus(other, tag_annoying, 0.2)
        score += tag_bonus(other, tag_gallant, -0.2)
        score += tag_bonus(other, tag_humble, -0.1)
        return score


@__personality
class Gura(object):
    def __init__(self): pass

    def name(self): return "Gura"
    def tags(self): return [tag_assholish]

    def no_lynch_propensity(self, day):
        return 0.0

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.05, 0.05, 0.4, 0.5]) # frankly, pretty bad until the late-game
        score += tag_bonus(other, tag_verbose, 0.2) # but they're better against talkative or verbose players
        return score

    def inaccurate_scumread_propensity(self, day, other):
        score = daily(day, [0.35, 0.2, 0.0]) # initially noisy
        score += tag_bonus(other, tag_verbose, 0.15)
        score += tag_bonus(other, tag_humble, 0.05)
        return score


# == 999 == #
@__personality
class Ace(object):
    def __init__(self): pass

    def name(self): return "Ace"
    def tags(self): return [tag_gallant, tag_policy]

    def no_lynch_propensity(self, day):
        return 0.3

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.05, 0.05, 0.1, 0.1]) # bad in general
        score += tag_bonus(other, tag_verbose, 0.4)  # great in specific
        score += tag_bonus(other, tag_gallant, 0.3) 
        return score

    def inaccurate_scumread_propensity(self, day, other):
        score = daily(day, [0.05, 0.05, 0.0]) # do not inaccurately read players 
        score += tag_bonus(other, tag_assholish, 0.25) # unless they are assholes
        return score


@__personality
class Eric(object):
    def __init__(self): pass

    def name(self): return "Eric"
    def tags(self): return [tag_policy, tag_verbose]

    def no_lynch_propensity(self, day):
        return 0.0

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.0]) # not accurate
        return score

    def inaccurate_scumread_propensity(self, day, other):
        score = daily(day, [0.15]) # slightly noisy
        if day % 2 == 1:
            # on d1, d3, d5
            score += tag_bonus(other, tag_gallant, 0.35) 
            score += tag_bonus(other, tag_humble, 0.35) 
        else:
            score += tag_bonus(other, tag_assholish, 0.35) 
            score += tag_bonus(other, tag_annoying, 0.35) 

        return score


@__personality
class Dio(object):
    def __init__(self): pass

    def name(self): return "Dio"
    def tags(self): return [tag_assholish, tag_gallant]

    def no_lynch_propensity(self, day):
        return 0.0

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.2, 0.2]) # fairly accurate
        return score

    def inaccurate_scumread_propensity(self, day, other):
        score = daily(day, [0.05]) 

        # does not like gallant or annoying players
        score += tag_bonus(other, tag_gallant, 0.15) 
        score += tag_bonus(other, tag_annoying, 0.15) 
        score += tag_bonus(other, tag_verbose, 0.15) 

        return score

@__personality
class June(object):
    def __init__(self): pass

    def name(self): return "June"
    def tags(self): return [tag_gallant, tag_humble, tag_verbose]

    def no_lynch_propensity(self, day):
        return 0.4

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [1.0]) # seeing how she's psychic and has time travel, she can accurately scumread every scum

        # but she likes gallant dudes and won't scumread them
        score += tag_bonus(other, tag_gallant, -0.20) 
        score += tag_bonus(other, tag_humble, -0.10) 

        return score

    def inaccurate_scumread_propensity(self, day, other):
        score = daily(day, [0.01]) 

        # does not like assholish players
        score += tag_bonus(other, tag_assholish, 0.15) 

        return score


# == Danganronpa == #
@__personality
# TODO: Nagito should like self-voting
class Nagito(object):
    def __init__(self): pass 

    def name(self): return "Nagito"
    def tags(self): return [tag_gallant, tag_humble, tag_policy, tag_verbose]

    def no_lynch_propensity(self, day):
        return 0.05

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.6, 0.8, 0.9]) 

        # his love of generically protagonisty characters does not impact his willingness to scumread them
        # he slightly prefers characters who treat him like shit
        score += tag_bonus(other, tag_assholish, -0.2) 
        score += tag_bonus(other, tag_annoying, -0.1) 

        return score

    def inaccurate_scumread_propensity(self, day, other):
        # his scumreads are always accurate
        score = daily(day, [0.0]) 
        return score


@__personality
# TODO: Kokichi should *really* like self-voting
class Kokichi(object):
    def __init__(self): pass

    def name(self): return "Kokichi"
    def tags(self): return [tag_annoying, tag_assholish, tag_policy, tag_verbose]

    def no_lynch_propensity(self, day):
        return 0.00

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.4, 0.5, 0.6])
        return score

    def inaccurate_scumread_propensity(self, day, other):
        # his scumreads are more or less accurate
        score = daily(day, [0.1]) 

        # but he hates protagonists
        score += tag_bonus(other, tag_gallant, 0.2) 
        score += tag_bonus(other, tag_humble, 0.2) 
        score += tag_bonus(other, tag_verbose, 0.1) 

        return score

@__personality
class Gundham(object):
    def __init__(self): pass

    def name(self): return "Gundham"
    def tags(self): return [tag_annoying, tag_verbose]

    def no_lynch_propensity(self, day):
        return 0.0

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.2, 0.2, 0.3]) # not remarkable
        return score

    def inaccurate_scumread_propensity(self, day, other):
        score = daily(day, [0.2]) # not remarkable
        score += tag_bonus(other, tag_verbose, 0.2) # but he doesn't like verbose players
        score += tag_bonus(other, tag_policy, 0.1) 
        return score


@__personality
# TODO: Korekiyo should love nightkilling
class Korekiyo(object):
    def __init__(self): pass

    def name(self): return "Korekiyo"
    def tags(self): return [tag_annoying, tag_gallant, tag_verbose]

    def no_lynch_propensity(self, day):
        return 0.0

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.5, 0.4, 0.6]) 
        score += tag_bonus(other, tag_humble, -0.2)  # he likes players who are humble
        score += tag_bonus(other, tag_verbose, -0.2)  # he likes players who talk too much
        return score

    def inaccurate_scumread_propensity(self, day, other):
        score = daily(day, [0.2]) # not remarkable
        score += tag_bonus(other, tag_gallant, 0.2) # slight tendency to scumread gallant players
        return score


@__personality
class Togami(object):
    def __init__(self): pass

    def name(self): return "Togami"
    def tags(self): [tag_gallant, tag_verbose]

    def no_lynch_propensity(self, day):
        return 0.0

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.4, 0.2, 0.3]) 
        score += tag_bonus(other, tag_humble, -0.2)  # he likes players who are humble
        score += tag_bonus(other, tag_policy, 0.3)  # he frequently policy-lynches correctly
        return score

    def inaccurate_scumread_propensity(self, day, other):
        score = daily(day, [0.2]) # not remarkable
        score += tag_bonus(other, tag_assholish, 0.2) # he often scumreads assholish players
        score += tag_bonus(other, tag_annoying, 0.1) # he often scumreads annoying players
        return score

# == people who have something wrong with them in real life ==
@__personality
# TODO: Retaliate
class Gore(object):
    def __init__(self): pass

    def name(self): return "Gore"
    def tags(self): return [tag_assholish, tag_annoying, tag_verbose]

    def no_lynch_propensity(self, day):
        return 0.0

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.1, 0.14, 0.18, 0.22]) # his reads are just bad
        return score

    def inaccurate_scumread_propensity(self, day, other):
        score = daily(day, [0.2]) # not remarkable
        score += tag_bonus(other, tag_assholish, 0.3) # he often scumreads assholish players
        score += tag_bonus(other, tag_policy, 0.4) # he often scumreads policy players
        return score


@__personality
# TODO: He should literally be worse than random at guessing scum
# Write code so that instead of following the normal system, he just votes for a random player who isn't scum.
class p_dark_syde_phil(object):
    def __init__(self): pass

    def name(self): return "Phil"
    def tags(self): return [tag_assholish, tag_annoying]

@__personality
# TODO: He should be like, supernaturally policy lynchable
class p_alias888(object):
    def __init__(self): pass

    def name(self): return "Alias" # aka Mr. Pink
    def tags(self): return [tag_assholish, tag_annoying, tag_humble, tag_policy]

    def no_lynch_propensity(self, day, other):
        return 0.0

    def accurate_scumread_propensity(self, day, other):
        score = daily(day, [0.8, 0.85, 0.9, 0.95]) # his reads are uh, really really good
        return score

    def inaccurate_scumread_propensity(self, day, other):
        score = daily(day, [0.05]) # wrong scumreads are quite infrequent for him
        score += tag_bonus(other, tag_assholish, 0.05) # they are more common for assholish players
        return score

def p_any(n):
    personalities_1 = []
    for i in range(n):
        if len(personalities_1) == 0:
            personalities_1 = personalities[:]
            random.shuffle(personalities_1)
        yield personalities_1[0]
        del personalities_1[0]

# utils
def tag_bonus(player, tag, n):
    return n if tag in player["personality"]["tags"] else 0.0

def daily(day, l):
    return l[min(max(day, 0), len(l - 1))]
