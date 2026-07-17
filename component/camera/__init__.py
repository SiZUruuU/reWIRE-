# Cool thing about python packages, applying __init__.py
# in a package like this one, camera/, we can actually treat
# it like a library, basically a utility if the we import the package
from .camera import Camera
from .follow_camera import Follow

# what gets imported if we do  from .camera import *
__all__ = ["Camera", "Follow"]