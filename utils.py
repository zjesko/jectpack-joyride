import sys
import select
import tty
import termios
import subprocess as sp


class NBInput:

    def __init__(self):
        self.old_settings = termios.tcgetattr(sys.stdin)

    def reset_term(self):
        termios.tcgetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    @classmethod
    def kb_hit(cls):
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

    @classmethod
    def get_ch(cls):
        return sys.stdin.read(1)

    @classmethod
    def flush(cls):
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def clear():
    sp.call('clear', Shell = True)



