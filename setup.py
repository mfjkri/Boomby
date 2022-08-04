import os
import logging
import subprocess
import sys


def check_cwd() -> bool:
    return os.path.isfile(
        os.path.join(
            os.getcwd(),
            os.path.basename(__file__)
        )
    )


if __name__ == "__main__":

    is_windows = "win32" in sys.platform
    is_linux = "linux" in sys.platform
    is_darwin = "darwin" in sys.platform

    log = logging.getLogger("CSA_Telegram_Bot setup")
    log.setLevel(10)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    terminal_output = logging.StreamHandler(sys.stdout)
    terminal_output.setFormatter(formatter)
    log.addHandler(terminal_output)

    log_file = logging.FileHandler(f"project_setup.log")
    log_file.setFormatter(formatter)
    log.addHandler(log_file)

    if not check_cwd():
        log.error("Please run this file from the root directory.")
        exit()

    python_keyword: str
    while True:
        python_keyword = input("Please enter your python keyword: ")

        try:
            python_version = subprocess.check_output(
                [python_keyword, "--version"], shell=is_windows).strip()
            log.info(f"PYTHON VERSION BEING USED IS: {python_version}")
            break
        except:
            log.error("You have entered an invalid python keyword. "
                      "Please check your PATH to determine the right keyword.\n\n"
                      "For most operating systems, the keyword for python 3 is either: python or python3")

    # ---------------------------- Creating python env --------------------------- #
    log.info(f"Creating python venv (if already exists, nothing happens)...")
    subprocess.run([python_keyword, "-m", "venv", "venv"])
    # ------------------------------------- - ------------------------------------ #

    # -------------------------- Installing dependencies ------------------------- #
    if is_linux or is_windows or is_darwin:
        log.info(
            f"Installing dependencies from requirements.txt into venv now...")

        if is_linux or is_darwin:
            subprocess.run([
                os.path.join("venv", "bin", python_keyword),
                "-m", "pip", "install", "-r", "requirements.txt"])

        elif is_windows:
            subprocess.run([
                os.path.join("venv", "Scripts", f"{python_keyword}.exe"),
                "-m", "pip", "install", "-r", r".\requirements.txt"], shell=True)

    else:
        log.error(
            "setup.py currently does not support installing of dependencies. Please do this manually.")
    # ------------------------------------- - ------------------------------------ #
