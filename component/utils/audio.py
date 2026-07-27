from component.utils.enums import AudioType, SFX, OST
import pygame

class AudioComp:

    def __init__(self, game):
        self.game = game
        self.ost = None
        self.sfx = None
        self.walking_channel = pygame.mixer.Channel(0)
        self.ost_channel = pygame.mixer.Channel(1)

        
    def play_sfx(self, audio_type, sfx_name):
        sfx = self.game.assets[audio_type][sfx_name]
        sfx.play()
        print(sfx_name)

    def play_ost(self, audio_type, ost_name):
        self.ost = self.game.assets[audio_type][ost_name]

        if not self.ost_channel.get_busy():
            self.ost_channel.play(self.ost, -1)

    def play_walkingSFX(self, is_walking, audio_type, sfx_name):
        sfx = self.game.assets[audio_type][sfx_name]
        playing = self.walking_channel.get_busy()

        if is_walking:
            if not playing and sfx:
                self.walking_channel.play(sfx, loops=-1)
        else:
            if playing:
                self.walking_channel.stop()

    def stop_ost(self):
        self.ost.stop()