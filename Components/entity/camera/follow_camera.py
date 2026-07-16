from .base_camera import BaseCam

# Camera for following a target
class Follow(BaseCam):
    def __init__(self, camera, target):
        super().__init__(camera, target)

    def scroll(self, delta_time):
        target_x = self.target.rect.centerx - self.camera.width / 2
        target_y = self.target.rect.centery - self.camera.height / 2
        self.camera.offset.x += (target_x - self.camera.offset.x) * 5 * delta_time
        self.camera.offset.y += (target_y - self.camera.offset.y) * 5 * delta_time
