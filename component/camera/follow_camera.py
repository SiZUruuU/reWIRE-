from .base_camera import BaseCam

# Camera type for following a target:
# logic is simple, you have a target and wherever
# the target goes the camera follows, but in reality
# we just move the world around the player through offset
class Follow(BaseCam):    
    def __init__(self, camera, target):
        super().__init__(camera, target)

    # scroll by finding the target's center then smoothly
    # offset it towards the center, offset is basically
    # the amount of xy the camera should increment to move towards the target
    def scroll(self, delta_time):
        # Calculate the error, how far the target is:
        # there will be a point where target_x/y's value becomes zero
        # that means the camera and the target are in the same position
        target_x = self.target.rect.centerx - self.camera.width / 2    
        target_y = self.target.rect.centery - self.camera.height / 2
        # simple exponential smoothing equation: 
        # use a graphing calc to see how it looks
        self.camera.offset.x += (target_x - self.camera.offset.x) * 2 * delta_time
        self.camera.offset.y += (target_y - self.camera.offset.y) * 2 * delta_time