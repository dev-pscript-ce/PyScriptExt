import msvcrt

def read_key():
    key = msvcrt.getch()
    if key in ( b"\x00", b"\xe0"):  # arrow
        key2 = msvcrt.getch()
        return {
            b"H": "UP",
            b"P": "DOWN",
            b"K": "LEFT",
            b"M": "RIGHT"
        }.get(key2, "")
    if key == b"\r":
        return "ENTER"
    if key == b" ":
        return "SPACE" 
    if key == b"\x08":
        return "BACKSPACE"
    try:
        return key.decode("utf-8")
    except:
        return ""