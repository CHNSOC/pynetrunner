import random

from typing import List, Optional
from ..cards.base import Card
from ..cards.runner_cards import Program
from ..cards.corp_cards import Agenda
from .player import Deck, Player


class Runner(Player):
    def __init__(self, name: str, deck: Deck):
        super().__init__(name, deck)
        self.programs: List[Program] = []
        self.heap: List[Card] = []

    def __str__(self):
        return f"{super().__str__()}, Programs installed: {len(self.programs)}"


    def install_program(self, card: Program):
        if self.credits >= card.cost:
            self.clicks -= 1
            self.credits -= card.cost
            self.hand.remove(card)
            self.programs.append(card)
            print(f"{self.name} installed {card.name}")
        else:
            print("Not enough credits to install this program")

    def initiate_run(self, server: str) -> bool:
        if self.clicks > 0:
            self.clicks -= 1
            print(f"{self.name} is initiating a run on {server}")
            return True
        else:
            print(f"{self.name} doesn't have enough clicks to initiate a run")
            return False

    def access_cards(self, cards: List[Card]):
        for card in cards:
            print(f"{self.name} accessed {card.name}")
            # Implement card access logic here

    def score_agenda(self, agenda):
        print(f"{self.name} scores {agenda.name} for {agenda.agenda_points} points!")
        return agenda.agenda_points