from .player import Player, Deck
from ..cards.base import Card
from ..cards.corp_cards import Agenda
from typing import List, Optional

class Corp(Player):
    def __init__(self, name: str, deck: Deck):
        super().__init__(name, deck)
        self.scored_agendas = 0
        self.remote_servers: List[List[Card]] = []
        self.archives: List[Card] = []

    def __str__(self):
        return f"{super().__str__()}, Scored agendas: {self.scored_agendas}, Remote servers: {len(self.remote_servers)}"

    def install_card(self, card: Card, server: Optional[int] = None):
        self.clicks -= 1
        self.hand.remove(card)
        if server is None:
            self.remote_servers.append([card])
            print(f"{self.name} creates a new remote server and installs a card")
        else:
            if server >= len(self.remote_servers):
                self.remote_servers.append([])
            self.remote_servers[server].append(card)
            print(f"{self.name} installs a card in remote server {server}")

    def score_agenda(self, agenda: Agenda):
        self.clicks -= 1
        self.scored_agendas += agenda.agenda_points
        print(f"{self.name} scores {agenda.name} for {agenda.agenda_points} points!")