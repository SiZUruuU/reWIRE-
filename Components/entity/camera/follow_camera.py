from .base_camera import BaseCam

# Camera for following a target
class Follow(BaseCam):
    def __init__(self, camera, target):
        super().__init__(camera, target)

    def scroll(self):
        self.camera.offset.x = self.target.rect.centerx - self.camera.width / 2
        self.camera.offset.y = self.target.rect.centery - self.camera.height / 2