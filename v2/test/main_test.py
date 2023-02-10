import os


def prepare_zippath(s):
    s = s.replace(chr(92), '/')
    char = '/'
    while char * 2 in s:
        s = s.replace(char * 2, char)
    return os.path.relpath(s, '/').replace(chr(92), '/')

print(prepare_zippath('\\Coursework_1sem_3course\\coursework\\src\\main\\resources\\static\\vendors\\themify-icons\\SVG\\layout-media-overlay-alt-2.svg'))