import sys
sys.dont_write_bytecode = True
import time
from pathlib import Path

def add_root(level: int = 2):
    ROOT_DIR = Path(__file__).resolve().parents[level]

    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))

    return ROOT_DIR
add_root()

from pscript.helpers.color import(
    multi_char,
    printl,
    c,
    ProgressBar,
    inputl,
    done,
    MultiProgress,
    ansi
)


# printl(
#     c("Text1",(255,0,0)),
#     c("Text2", "u"),
#     c("Text3", ansi.R.b)
# )

def test_printl():
    multi_char("-",88,"#5ef")
    printl.G(f'printl.G("text") | printl(("text",ansi.G)) | printl(("Text",ansi.ansi_basic(32)))')
    multi_char("-",88,"#5ef")
    printl.green(f'printl.green("text") | printl(("text",ansi.green)) | printl(("text",ansi.rgb(0,255,0)))')
    multi_char("-",88,"#5ef")
    printl.hR(f'printl.hR("text") | printl(("text",ansi.hR)) | printl(("text",ansi.hex("#f00")))')
    multi_char("-",88,"C")
    text0 = c('printl(\n  ("text0","G"),','M')
    text1 = c('  ("text1","#0ef"),','G')
    text2 = c('  ("text2",(120,0,255))\n)','#0ef')
    printl(f"{text0}\n{text1}\n{text2}")

def test1():
        rows = [
        {"file": "index.js", "size": 1234, "status": "OK"},
        {"file": "main.py",  "size": 98765, "status": "ERROR"},
        {"file": "data.json","size": 4567, "status": "WARN"}
    ]
        printl.table(rows,color = "B")              # auto pretty
        printl.table(rows,color = "G")
        printl.G({"a":1})
        printl.R([{"x":1},{"x":2}])

        bar=ProgressBar(50)

        for i in range(50):
            time.sleep(0.02)
            bar.tick()

        sp=ProgressBar(30)
        sp.render()
        time.sleep(2)
        sp.tick()



def test2 ():
    rows = [
        {"file": "index.js", "size": 1234, "status": "OK"},
        {"file": "main.py",  "size": 98765, "status": "ERROR"},
        {"file": "data.json","size": 4567, "status": "WARN"}
    ]

    printl.info("File list:")
    printl.table(rows, color="G")
    
    choice = inputl.select([
        "NodeJS",
        "Python",
        "Docker",
        "Nginx"
    ],multi=True)

    printl.G("Bạn chọn:", choice)
    ok = inputl.confirm("Xoá file?")
    ok = inputl.G.confirm("Tiếp tục?")
    ok = inputl.b.R.confirm("Force delete?", default=False)

def test3():
    pb = ProgressBar(100, name="Download")

    for i in range(100):
        time.sleep(0.05)

        if i == 30:
            pb.pause()
            time.sleep(1)
            pb.resume()

        pb.tick()
        print("\r" + pb.render(), end="")
    done(pb)
   

def test4():
    choice = inputl.select([f"Item {i}" for i in range(100)])
    printl.G("Bạn chọn:", choice)

def test5():
    mp = MultiProgress(fps=12)

    b1 = ProgressBar(100, name="Download",theme="dark")
    b2 = ProgressBar(200, name="Build",theme="dark")
    b3 = ProgressBar(150, name="Upload",theme="dark")

    mp.add(b1)
    mp.add(b2)
    mp.add(b3)

    mp.start()

    for i in range(200):
        time.sleep(0.03)

        if i < 100:
            b1.tick()

        if i < 150:
            b3.tick()
        b2.tick()

    done(b1)
    done(b2)
    done(b3)
    mp.stop()

def test6():
    printl.glass("Hello")
    printl.danger("Hello")
    printl.warning("Warning")
    printl.title("Title")
    
# if __name__ == "__main__":
#     # test_printl()
#     # test1()
#     # test2()
#     # test3()
#     # test4()
#     # test5()
#     test6()

printl(("text",ansi.green),("Text1",ansi.rY))

    


