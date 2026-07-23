from component.utils.enums import AudioType, SFX, OST
import pygame

class AudioComp:

    def __init__(self, game):
        self.game = game

    def play_sfx(self, audio_type, sfx_name):
        sfx = self.game.assets[audio_type][sfx_name]
        sfx.stop()
        sfx.play()

    def play_ost(self, audio_type, ost_name):
        ost = self.game.assets[audio_type][ost_name]
        ost.play()