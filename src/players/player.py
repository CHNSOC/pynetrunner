
from typing import List, Optional
from random import shuffle
from ..cards.base import Card
from ..cards.card_types import Agenda, Program
from typing import List, Optional


class Deck:
    def __init__(self, cards: List[Card]):
        self.cards = cards
        shuffle(self.cards)

    def draw(self) -> Optional[Card]:
        return self.cards.pop() if self.cards else None


class Player:
    def __init__(self, name: str, deck: Deck):
        self.name = name
        self.deck = deck
        self.hand: List[Card] = []
        self.credits = 5
        self.clicks = 0

    def __str__(self):
        return f"{self.name} - Credits: {self.credits}, Clicks: {self.clicks}, Hand size: {len(self.hand)}"

    def draw(self, count: int = 1):
        for _ in range(count):
            card = self.deck.draw()
            if card:
                self.hand.append(card)
    
class Corp(Player):
    def __init__(self, name: str, deck: Deck):
        super().__init__(name, deck)
        self.scored_agendas = 0
        self.remote_servers: List[List[Card]] = []
        self.archives: List[Card] = []

    def __str__(self):
        return f"{super().__str__()}, Scored agendas: {self.scored_agendas}, Remote servers: {len(self.remote_servers)}"

    def install_card(self, card, server=None):
        self.clicks -= 1
        self.hand.remove(card)
        if server is None:
            self.remote_servers.append([card])
            print(f"{self.name} creates a new remote server and installs {card}")
        else:
            if server >= len(self.remote_servers):
                self.remote_servers.append([])
            self.remote_servers[server].append(card)
            print(f"{self.name} installs {card} in remote server {server}")

    def score_agenda(self, agenda):
        self.clicks -= 1
        self.scored_agendas += agenda.agenda_points
        print(f"{self.name} scores {agenda} for {agenda.agenda_points} points!")



class Runner(Player):
    def __init__(self, name: str, deck: Deck):
        super().__init__(name, deck)
        self.programs: List[Program] = []
        self.heap: List[Card] = []

    def __str__(self):
        return f"{super().__str__()}, Programs installed: {len(self.programs)}"


    def install_program(self, card):
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