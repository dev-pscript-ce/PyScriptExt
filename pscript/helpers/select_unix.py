import tty, termios,sys

def read_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)

        if ch1 == "\x1b":
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return {
                "A": "UP",
                "B": "DOWN"
            }.get(ch3, "")

        if ch1 == "\r":
            return "ENTER"
        if ch1 == " ":
            return "SPACE"
        if ch1 == "\x7f":
            return "BACKSPACE"

        return ch1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)