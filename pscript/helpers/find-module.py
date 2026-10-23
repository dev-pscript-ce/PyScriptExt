import sys
sys.dont_write_bytecode = True

import importlib
import subprocess
import platform
import os
from pathlib import Path

def add_root(level: int = 2):
    ROOT_DIR = Path(__file__).resolve().parents[level]

    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))

    return ROOT_DIR
add_root()

# Lệnh tạo môi trường riêng [.py311] cho version python 3.11 + cài pygame
'''
"py -3.11 -m venv .py311" -> thiết lập venv 
".py311\Script\activate" -> vào venv [terminal]
"pip install pygame" -> cài pygame

'''

# ========= UI =========

def ensure(pkg, module=None):
    if not module:
        module = pkg
    try:
        importlib.import_module(module)
    except ImportError:
        print(f"Đang cài {pkg} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
ensure ("colorama")

from colorama import init
init(autoreset=True)

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


# ========= CORE =========

class Dependency:
    def __init__(self, pip_names, import_name=None):
        self.pip_names = pip_names if isinstance(pip_names, list) else [pip_names]
        self.import_name = import_name

    def is_installed(self):
        if not self.import_name:
            return True
        try:
            importlib.import_module(self.import_name)
            return True
        except ImportError:
            return False

    def install(self):
        try:
            printl.C(f"🔧 Đang cài: {' '.join(self.pip_names)} ...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", *self.pip_names]
            )
            printl.G(f"✅ OK: {' '.join(self.pip_names)}\n")
        except Exception as e:
            printl.R(f"❌ Lỗi khi cài {self.pip_names}: {e}")
    
    def un_install_pkg(self,mode="install", ask=True):
        """
        mode:
            - "install"   → chưa có thì hỏi cài
            - "uninstall" → đã có thì hỏi gỡ
            - "repair"    → gỡ + cài lại
        """

        self.import_name = self.import_name or self.pip_names

        # ===== CHECK =====
        try:
            for name in (self.import_name if isinstance(self.import_name, list) else [self.import_name]):
                importlib.import_module(name)
            installed = True
        except ImportError:
            installed = False

        # ===== INSTALL =====
        if mode == "install":
            if installed:
                print(f"✔ '{' '.join(self.pip_names)}' đã được cài.")
                return True

            if ask:
                c = input(f"❓ '{' '.join(self.pip_names)}' chưa có. Cài không? (y/n): ").lower()
                if c != "y":
                    print("⏩ Bỏ qua.")
                    return False
                
            return self.get_pkg()

        # ===== UNINSTALL =====
        elif mode == "uninstall":
            if not installed:
                print(f"⚠ '{' '.join(self.pip_names)}' chưa được cài.")
                return False

            if ask:
                c = input(f"❓ Gỡ '{' '.join(self.pip_names)}'? (y/n): ").lower()
                if c != "y":
                    print("⏩ Huỷ.")
                    return False

            return self.unget_pkg()

        # ===== REPAIR =====
        elif mode == "repair":
            if ask:
                c = input(f"🔧 Repair '{' '.join(self.pip_names)}' (gỡ + cài lại)? (y/n): ").lower()
                if c != "y":
                    print("⏩ Huỷ repair.")
                    return False

            success = True

            # nếu đã cài → gỡ trước
            if installed:
                success &= self.unget_pkg(' '.join(self.pip_names))
            else:
                print(f"⚠ '{' '.join(self.pip_names)}' chưa có → sẽ cài mới")

            # luôn cài lại
            success &= self.get_pkg()

            if success:
                print(f"🎉 Repair thành công: {' '.join(self.pip_names)}")
            else:
                print(f"❌ Repair thất bại: {' '.join(self.pip_names)}")

            return success
        else:
            raise ValueError("mode phải là 'install' | 'uninstall' | 'repair'")


    # ========= INTERNAL =========

    def get_pkg(self):
        try:
            printl.G(f"🔧 Đang cài: {' '.join(self.pip_names)} ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install","--no-cache-dir","--force", *self.pip_names])
            printl.C(f"✅ Đã cài: {' '.join(self.pip_names)}\n")
            return True
        except subprocess.CalledProcessError as e:
            printl.R(f"❌ Lỗi khi cài {self.pip_names}: {e}")
            return False


    def unget_pkg(self):
        try:
            print(f"🗑 Đang gỡ: {' '.join(self.pip_names)} ...")
            subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", *self.pip_names])
            print(f"✅ Đã gỡ: {' '.join(self.pip_names)}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Lỗi khi gỡ {self.pip_names}: {e}")
            return False
# d = Dependency("colorama")
from pscript.helpers.color import *
# d.un_install_pkg("uninstall")

# ========= DANH SÁCH DEP =========

DEPENDENCIES = [
    Dependency("pyautogui", "pyautogui"),
    Dependency("pillow", "PIL"), # pip_names != import
    Dependency("imageio", "imageio"),
    Dependency("imageio-ffmpeg", None), # chỉ cần pip_names
    Dependency("numpy", "numpy"),
    Dependency("pytesseract", "pytesseract"),
    Dependency("pyttsx3", "pyttsx3"),
    Dependency("msvcrt",None), # chỉ cần pip_names
    Dependency("matplotlib", "matplotlib"),
    Dependency("speechrecognition", "speech_recognition"),
    Dependency("mss","mss"),
    Dependency("opencv-python","cv2"),
    Dependency("pygame","pygame"),
]


# ========= PY AUDIO HANDLER =========

def handle_audio():
    python_ver = tuple(map(int, platform.python_version().split(".")))

    printl.Y("⚠ Kiểm tra audio (PyAudio)...")

    if python_ver >= (3, 12):
        return ask_replace_audio()

    dep = Dependency("pyaudio", "pyaudio")

    if not dep.is_installed():
        ask_install(dep)
    else:
        printl.G("✔ PyAudio đã có.")

    return True


def ask_replace_audio():
    # 🔍 Check trước
    deps = [
        Dependency("sounddevice", "sounddevice"),
        Dependency("numpy", "numpy"),
    ]

    all_installed = all(d.is_installed() for d in deps)

    # ===== Nếu đã có đủ → không cần hỏi =====
    if all_installed:
        printl.M("⚠ PyAudio không hỗ trợ Python >= 3.12")
        printl.G("🎉 sounddevice + numpy đã có sẵn!")
        printl.C("👉 Sử dụng sounddevice + numpy thay thế PyAudio OK!\n")
        return True

    # ===== Nếu thiếu → mới hỏi =====
    while True:
        printl.M("\n❌ PyAudio không hỗ trợ Python >= 3.12")
        printl.Y("Cài sounddevice + numpy thay thế PyAudio?")

        printl.C("[1] Có")
        printl.B("[2] Bỏ qua")
        printl.R("[0] Thoát")

        c = inputl.Y("👉 Chọn: ").strip()

        if c == "1":
            for d in deps:
                if not d.is_installed():
                    d.install()
                else:
                    printl.G(f"✔ {d.pip_names[0]} đã có")
            return True

        elif c == "2":
            return False

        elif c == "0":
            sys.exit(0)

# ========= UI =========

def ask_install(dep: Dependency):
    while True:
        printl.Y(f"\nModule '{dep.pip_names[0]}' chưa được cài!")

        printl.C("[1] 👉 Cài")
        printl.M("[2] 👉 Bỏ qua")
        printl.R("[0] 👉 Thoát")

        c = inputl.Y("👉 Chọn: ").strip()

        if c == "1":
            dep.install()
            return
        elif c == "2":
            printl.M(f"⏩ Bỏ qua {dep.pip_names[0]}")
            return
        elif c == "0":
            sys.exit(0)


# ========= MAIN =========

def main():
    cls()
    printl.M("=== 🔍 KIỂM TRA DEPENDENCY ===\n")

    # xử lý audio riêng
    handle_audio()

    # check bình thường
    for dep in DEPENDENCIES:
        if dep.is_installed():
            printl.G(f"✔ {dep.pip_names[0]} OK")
        else:
            ask_install(dep)

    printl.G("\n🎉 Hoàn tất kiểm tra!\n")


if __name__ == "__main__":
    main()