# The current faction list: ["town", "mafia", "sk", "survivor"]
# == factions ==
def faction_can_solowin(faction):
    return faction in ["sk"]

def faction_can_teamwin(faction, other_faction):
    if faction == "survivor":
        return True
    if faction in ["town", "mafia"]:
        return faction == other_faction
    return False

def faction_knows_members(faction, other_faction):
    if faction in ["mafia"]:
        return other_faction in ["mafia"]
    return False 

def faction_is_scum(faction):
    return faction in ["mafia", "sk"]

def faction_has_nighttalk(faction):
    return faction in ["mafia"]
