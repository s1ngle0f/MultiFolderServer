import os

def func():
    print(__file__[:str(__file__).rfind('\\')+1].replace('\\', '/')[:-1])
    print(os.path.exists(__file__[:str(__file__).rfind('\\')+1].replace('\\', '/')))
