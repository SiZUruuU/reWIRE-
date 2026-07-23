from component.utils.enums import AudioType, SFX, OST
import pygame

class AudioComp:

    def __init__(self, game):
        self.game = game
        pygame.mixer.init()

    def play_sfx(self, audio_type, sfx_name):
        sfx = self.game.assets[audio_type][sfx_name]
        sfx.play()