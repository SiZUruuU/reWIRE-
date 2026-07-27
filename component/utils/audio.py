import pygame

class AudioComp:
    def __init__(self, game):
        self.game = game
        self.ost = None
        self.ost_channel = pygame.mixer.Channel(1) # save one for the ost
        self.loop_channels = {} # channels for every looping sfx
        self._next_channel_id = 2

    # USE THIS FOR NON LOOPING LOGIC, ONE SHOT ONLY
    def play_sfx(self, audio_type, sfx_name):
        sfx = self.game.assets[audio_type][sfx_name]
        sfx.play()

    def play_ost(self, audio_type, ost_name):
        self.ost = self.game.assets[audio_type][ost_name]
        if not self.ost_channel.get_busy():
            self.ost_channel.play(self.ost, -1)

    def stop_ost(self):
        if self.ost is not None:
            self.ost_channel.stop()

    # USE THIS FOR LOGIC WITH LOOOOOOOOOOOOPS
    def play_loop(self, loop_name, audio_type, sfx_name):
        # check if the name is not registered
        if loop_name not in self.loop_channels:
            # registers it
            self.loop_channels[loop_name] = pygame.mixer.Channel(self._next_channel_id)
            self._next_channel_id += 1

        # sfx play logic
        # finds the sfx registered in the channel
        channel = self.loop_channels[loop_name]
        # if that audio is NOT playing, play it
        if not channel.get_busy():
            sfx = self.game.assets[audio_type][sfx_name]
            channel.play(sfx, loops=-1)

    # call this after a sfx trigger is NO LONGER TRUE
    # loop_name can be anything just make sure you are consistent
    # like play_sfx("walk") must also be stop_sfx("walk")
    def stop_loop(self, loop_name):
        channel = self.loop_channels.get(loop_name)
        
        if channel is not None and channel.get_busy():
            channel.stop()