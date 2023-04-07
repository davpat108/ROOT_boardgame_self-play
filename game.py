from actors import Marquise, Eyrie, Alliance, Vagabond
from item import Item
from dtos import MoveDTO, CraftDTO, Battle_DTO, OverworkDTO
from map import build_regular_forest
from deck import Deck, Card



class Game():
    def __init__(self) -> None:
        self.map = build_regular_forest()
        self.marquise = Marquise()
        self.eyrie = Eyrie('Despot')
        self.alliance = Alliance()
        self.vagabond = Vagabond()
        self.deck = Deck()


