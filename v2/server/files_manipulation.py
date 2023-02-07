import enum
import os.path


class ManipulationType(enum.Enum):
    GET = 0
    UPLOAD = 1
    DELETE = 2

def file_manipulate(file_path, manipulation_type, file_bytes = None):
    if manipulation_type is ManipulationType.GET:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()
            return data
    if manipulation_type is ManipulationType.UPLOAD:
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        with open(file_path, 'wb') as f:
            f.write(file_bytes)
    if manipulation_type is ManipulationType.DELETE:
        if os.path.exists(file_path):
            os.remove(file_path)
