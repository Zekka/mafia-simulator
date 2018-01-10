# skill levels
def skill_level_random():
    def guess_faction_chance(guesser, guessee): return 0.0
    def guess_role_chance(guesser, guessee): return 0.0

    return {
        "guess_faction": guess_faction_chance,
        "guess_role": guess_role_chance,
    }

def skill_level_10p():
    def guess_faction_chance(guesser, guessee): return 0.1
    def guess_role_chance(guesser, guessee): return 0.1

    return {
        "guess_faction": guess_faction_chance,
        "guess_role": guess_role_chance,
    }

def skill_level_50p():
    def guess_faction_chance(guesser, guessee): return 0.5
    def guess_role_chance(guesser, guessee): return 0.5

    return {
        "guess_faction": guess_faction_chance,
        "guess_role": guess_role_chance,
    }


def skill_level_perfect_scum():
    def guess_faction_chance(guesser, guessee): 
        if faction_is_scum(guesser["faction"]): return 1.0
        return 0.0
    def guess_role_chance(guesser, guessee): 
        if faction_is_scum(guesser["faction"]): return 1.0
        return 0.0

    return {
        "guess_faction": guess_faction_chance,
        "guess_role": guess_role_chance,
    } 

def skill_level_perfect():
    def guess_faction_chance(guesser, guessee): return 1.0
    def guess_role_chance(guesser, guessee): return 1.0

    return {
        "guess_faction": guess_faction,
        "guess_role": guess_role_chance,
    }
