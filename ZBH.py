import os
import sys
import cmd
import subprocess
import platform
import webbrowser
import time
import datetime
import curses

command_registry = {}

def register_command(name=None, help_text=""):
    def decorator(func):
        cmd_name = name or func.__name__
        command_registry[cmd_name] = {
            "function": func,
            "help": help_text
        }
        return func
    return decorator

class CustomTerminal(cmd.Cmd):
    intro = "ZBH, The UI based CLI"
    prompt = "@> "

    def __init__(self):
        super().__init__()
        for cmd_name, data in command_registry.items():
            method = data["function"]
            setattr(self, f"do_{cmd_name}", method.__get__(self))
        self.commands = command_registry

    def color_text(self, text, color_code):
        return f"\033[{color_code}m{text}\033[0m"

    def do_help(self, arg):
        print(self.color_text("Available commands:", 36))
        for cmd_name, data in self.commands.items():
            print(self.color_text(f"  {cmd_name:15} {data['help']}", 37))

    def do_exit(self, arg):
        print(self.color_text("Exiting terminal...", 34))
        sys.exit(0)


    @register_command(name="list", help_text="List contents of a directory.")
    def list(self, arg):
        def run_browser(stdscr):
            curses.curs_set(0)
            path = os.getcwd()
            selected = 0

            while True:
                stdscr.clear()
                stdscr.addstr(0, 0, f"Browsing: {path}")
                files = os.listdir(path)
                for i, f in enumerate(files):
                    marker = ">" if i == selected else " "
                    stdscr.addstr(i + 1, 0, f"{marker} {f}")
                stdscr.refresh()

                key = stdscr.getch()
                if key in [ord('q'), 27]:  # q or Esc
                    break
                elif key == curses.KEY_UP:
                    selected = max(0, selected - 1)
                elif key == curses.KEY_DOWN:
                    selected = min(len(files) - 1, selected + 1)
                elif key in [10, 13]:  # Enter
                    target = os.path.join(path, files[selected])
                    if os.path.isdir(target):
                        path = target
                        selected = 0
                    else:
                        curses.endwin()
                        os.system(f"less '{target}'")
                        return

        curses.wrapper(run_browser)


    @register_command(name="sysinfo", help_text="Display basic system information.")
    def sysinfo(self, arg):
        import psutil 
        def run_sysinfo(stdscr):
            curses.curs_set(0)
            while True:
                stdscr.clear()
                mem = psutil.virtual_memory()
                uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
                stdscr.addstr(0, 0, "System Information (press q to quit)")
                stdscr.addstr(2, 0, f"OS: {platform.system()} {platform.release()}")
                stdscr.addstr(3, 0, f"CPU: {platform.processor()}")
                stdscr.addstr(4, 0, f"Memory: {mem.percent}% of {mem.total/1024**3:.1f} GB")
                stdscr.addstr(5, 0, f"Uptime: {uptime}")
                stdscr.refresh()
                if stdscr.getch() in [ord('q'), 27]:
                    break

        curses.wrapper(run_sysinfo)


if __name__ == "__main__":
    terminal = CustomTerminal()
    terminal.cmdloop()
