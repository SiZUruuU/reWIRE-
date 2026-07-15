# ABSTRACT CLASS FOR SCREEN STATE
class State:
    def __init__(self, game):
        self.game = game
        self.prev_state = None

    def update(self, delta_time, actions):
        pass

    def render(self, surface):
        pass

    def enter_state(self):
        if len(self.game.state_stack) > 1:
            # peek the current state and store that to prev_state
            self.prev_state = self.game.state_stack[-1]
        # add the new state to the stack
        self.game.state_stack.append(self)
    
    def exit_state(self):
        # remove the current state
        self.game.state_stack.pop()