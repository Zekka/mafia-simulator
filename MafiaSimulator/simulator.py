from roles import *
from personalities import *
from rules import play_game
import random
import chattyreporter

if __name__ == "__main__":
    outcome = play_game(chattyreporter, 
        lambda: [townie, townie, townie, townie, townie, townie, townie, townie, townie, townie, survivor, mafioso1, mafioso1, mafioso2, mafioso2, sk1],
        lambda: p_any(50) # enough random roles for any setup
    )
    print
    print outcome
    print