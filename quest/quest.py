from __future__ import with_statement, absolute_import

from nagare import presentation, component, state, var
from nagare.namespaces import xhtml

from elixir import *

from quest import models
import random

# gather models
from quest.roomdisplay import RoomDisplay
from quest.monster import Monster, Monsters
from quest.questlogin import QuestLogin

class GameSession(object):
    def __init__(self):
        self.loginManager = component.Component(QuestLogin())
        self.loginManager.on_answer(self.startGame)
        self.model = state.stateless(var.Var("login"))

    def startGame(self, player):
        plo = models.Player.get(player)

        self.foo = plo
        self.player = player

        self.playerBox = component.Component(Player(player, self))
        self.roomDisplay = component.Component(RoomDisplay(plo.position.name, self))

        self.model("game")

    def enterRoom(self, roomname):
        player = self.foo #models.Player.get(self.player)
        player.position = models.Room.get(roomname)

class Wordbag(object):
    """This class holds the words that the player posesses."""
    def __init__(self, gs):
        self.diceWords()

    def diceWords(self):
        self.words = {}

        words = list(models.WordCard.query.order_by(models.WordCard.word))
        sum = 0
        while sum < 100:
            num = random.randint(1, 10)
            self.words[random.choice(words)] = num
            sum += num

    def useWord(self, wo):
        wc = [wrd for wrd in self.words if wrd.word == wo][0]
        self.words[wc] -= 1
        if self.words[wc] == 0:
            del self.words[wc]

class Player(object):
    """This Component represents the player of the game."""
    def __init__(self, name, gs):
        self.name = name
        self.hp = 100
        self.wordbag = state.stateless(Wordbag(gs))

    def changeHp(self, offset):
        self.hp += offset

@presentation.render_for(Player)
def player_render(self, h, binding, *args):
    with h.div(class_ = "playerbox"):
        h << h.h1(self.name)
        with h.span():
           h << "You currently have "
           h << h.span(self.hp, id="hp")
           h << " health points."
           h << h.a("--").action(lambda: self.changeHp(-1))
           h << h.a("++").action(lambda: self.changeHp(+1))

    return h.root

@presentation.render_for(Player, model="wordbag")
def wordbag_render(self, h, binding, *args):
    if len(self.wordbag.words) > 0:
        with h.div(class_="wordbag"):
            h << {"style": "column-count:5; -moz-column-count:5; -webkit-column-count:5; position:absolute; bottom: 5px; left: 5px; right: 5px; height: auto" }
            h << h.a("re-fill bag.").action(self.wordbag.diceWords)
            with h.ul():
                for wo, ct in self.wordbag.words.iteritems():
                    with h.li():
                        h << h.span(ct, class_="count")
                        h << h.a(" " + wo.word).action(lambda wo=wo: self.wordbag.useWord(wo.word))
    else:
        with h.div(class_="wordbag"):
            h << "Woops. No words :("
    
    return h.root


@presentation.render_for(GameSession)
def render(self, h, *args):
    h.head << h.head.title("LojbanQuest draft")
    if self.model() == "login":
        h << self.loginManager
    elif self.model() == "game":
        h << h.h1("Welcome to LojbanQuest!")
        h << self.playerBox
        h << self.playerBox.render(xhtml.AsyncRenderer(h), model="wordbag")
        h << self.roomDisplay
        h << h.div(self.roomDisplay.render(h, model="map"), style="position:absolute; right: 0; top: 0;")
    return h.root


# ---------------------------------------------------------------

app = GameSession
