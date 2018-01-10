def townie(name, personality): 
    return { 
        "role": "Townie", 
        "faction": "Town", 
        "name": name,
        "personality": personality, 
    }
def survivor(name, personality): 
    return { 
        "role": "Survivor", 
        "faction": "Survivor", 
        "name": name,
        "personality": personality, 
    }

def __mafioso(pfx):
    def __(name, personality):
        return { 
            "role": "Mafioso %d" % pfx, 
            "faction": "Scum %d" % pfx, 
            "name": name, 
            "personality": personality,
        }
    return __

def __sk(pfx):
    def __(name, personality):
        return { 
            "role": "Serial Killer %d" % pfx, 
            "faction": "SK %d" % pfx, 
            "name": name, 
            "personality": personality,
        }
    return __

mafioso1 = __mafioso(1)
mafioso2 = __mafioso(2)
mafioso3 = __mafioso(3)

sk1 = __sk(1)
sk2 = __sk(2)
sk3 = __sk(3)

# x glom y: x counts towards y's population win condition
def faction_glom(faction, other):
    if faction == other: return True
    if faction == "Survivor":
        if "Sk" in other: return False
        return True
    return False

def faction_has_nightkill(faction):
    if "Sk" in faction: return True
    if "Scum" in faction: return True
    return False

def faction_is_scum(faction):
    if "Sk" in faction: return True
    if "Scum" in faction: return True
    return False
