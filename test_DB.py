
def func():
    print(__file__[:str(__file__).rfind('\\')+1].replace('\\', '/'))
