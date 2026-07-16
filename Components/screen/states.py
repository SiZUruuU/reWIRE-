# ABSTRACT CLASS FOR SCREEN STATE
# uses a Stack data struct
class State:
    def __init__(self, game):
        self.game = game
        self.prev_state = None

    def update(self, delta_time, actions):
        pass

    def render(self, surface):
        pass

    # called to enter next assigned state
    # usage: GameScreen.enter_state()
    def enter_state(self):
        if len(self.game.state_stack) > 1:
            # peek the current state and store that to prev_state
            self.prev_state = self.game.state_stack[-1]
        # add the new state to the stack
        self.game.state_stack.append(self)
    
    # called when exiting a state
    def exit_state(self):
        # remove the current state
        self.game.state_stack.pop()