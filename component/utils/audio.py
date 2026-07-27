import pygame

class AudioComp:
    _mixer_configured = False

    def __init__(self, game):
        self.game = game
        self.ost = None

        # Global mixer configuration (runs once)
        if not AudioComp._mixer_configured:
            pygame.mixer.set_num_channels(32)  
            pygame.mixer.set_reserved(1)  
            AudioComp._mixer_configured = True

        self.ost_channel = pygame.mixer.Channel(0)
        self.loop_channels = {}

    def play_sfx(self, audio_type, sfx_name, volume=0.5):
        sfx = self.game.assets[audio_type][sfx_name]
        sfx.set_volume(volume)
        sfx.play()

    def play_ost(self, audio_type, ost_name, volume=1.0):
        new_ost = self.game.assets[audio_type][ost_name]
        if self.ost_channel.get_sound() != new_ost:
            self.ost = new_ost
            self.ost_channel.stop()
            self.ost_channel.play(self.ost, loops=-1)
        self.ost_channel.set_volume(volume)

    def stop_ost(self):
        if self.ost_channel.get_busy():
            self.ost_channel.stop()
            self.ost = None

    def play_loop(self, loop_name, audio_type, sfx_name, volume=1.0):
        sfx = self.game.assets[audio_type][sfx_name]
        channel = self.loop_channels.get(loop_name)

        if channel is None:
            # find_channel searches channels 1-31 (ignoring reserved OST Channel 0)
            channel = pygame.mixer.find_channel(True)
            if channel is not None:
                self.loop_channels[loop_name] = channel

        if channel is not None:
            if not channel.get_busy() or channel.get_sound() != sfx:
                channel.play(sfx, loops=-1)
            channel.set_volume(volume)

    def stop_loop(self, loop_name):
        # Clears the dictionary key so channel allocation starts fresh next time
        channel = self.loop_channels.pop(loop_name, None)
        if channel is not None and channel.get_busy():
            channel.stop()