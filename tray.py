#!/usr/bin/python
import asyncio
import sys
import subprocess
import argparse
from pathlib import Path
import threading
from PIL import Image, ImageDraw, ImageFont, ImageColor
import pystray


class TrayApp:
    def __init__(self, command, tooltip=None, autostart=False, bgcolor="blue", fontcolor="yellow", id=None,
                 stopdcolor="red", rundcolor="green", stopfcolor=None, runfcolor=None, stopbcolor=None, runbcolor=None):
        self.command = command
        self.tooltip = tooltip or self.default_tooltip()
        self.id_char = id or self.tooltip.upper()[0]
        self.running_icon = self.create_icon(rundcolor, runbcolor or bgcolor, runfcolor or fontcolor)
        self.stopped_icon = self.create_icon(stopdcolor, stopbcolor or bgcolor, stopfcolor or fontcolor)
        self.icon = None
        self.process = None
        self.timer_task = None

        if autostart:
            self.start_app()

    async def _run_timer(self):
        while True:
            await asyncio.sleep(1)
            if not self.is_running():
                print(f"-[{self.tooltip}] Closed.-")
                self.update_ui()
                break
        self.timer_task = None

    def start_timer(self):
        if self.timer_task is not None:
            return

        def run_loop():
            asyncio.run(self._run_timer())

        t = threading.Thread(target=run_loop, daemon=True)
        t.start()
        self.timer_task = t

    def default_tooltip(self):
        cmd = Path(self.command[0])
        return cmd.stem

    def create_icon(self, dotcolor, bgcolor, fontcolor):
        size = (64, 64)
        image = Image.new("RGB", size, bgcolor)
        fnt = ImageFont.load_default(size=50)
        draw = ImageDraw.Draw(image)
        draw.ellipse((10, 10, 54, 54), fill=dotcolor)
        draw.text((32, 31), self.id_char, font=fnt,
                  fill=fontcolor, anchor="mm", stroke_width=2)
        return image

    def is_running(self):
        return self.process is not None and self.process.poll() is None

    def update_ui(self):
        if not self.icon or self.icon is None:
            return

        if self.is_running():
            self.icon.icon = self.running_icon
            self.icon.title = f"{self.tooltip} (Running)"
        else:
            self.icon.icon = self.stopped_icon
            self.icon.title = f"{self.tooltip} (Closed)"

        self.icon.menu = self.build_menu()

    def start_app(self, *args):
        if not self.is_running():
            try:
                print(f"-[{self.tooltip}] Starting.-")
                self.process = subprocess.Popen(self.command)
                self.start_timer()
            except Exception as e:
                print(f"Failed to start process: {e}")
        self.update_ui()

    def stop_app(self, *args):
        if self.process and self.process is not None and self.is_running():
            print(f"-[{self.tooltip}] Closing.-")
            self.process.terminate()
            self.process.wait()
            self.process = None
        self.update_ui()

    def quit_app(self, *args):
        if not self.icon or self.icon is None:
            return

        self.stop_app()
        self.icon.stop()

    def build_menu(self):
        def start_item():
            return pystray.MenuItem(
                f"Start {self.tooltip}",
                self.start_app,
                enabled=not self.is_running()
            )

        def stop_item():
            return pystray.MenuItem(
                f"Stop {self.tooltip}",
                self.stop_app,
                enabled=self.is_running()
            )

        return pystray.Menu(
            start_item(),
            stop_item(),
            pystray.MenuItem("Quit", self.quit_app)
        )

    def run(self):
        self.icon = pystray.Icon(
            "TrayApp",
            self.running_icon if self.is_running() else self.stopped_icon,
            self.tooltip,
            self.build_menu()
        )
        self.update_ui()
        self.icon.run()


def main():
    parser = argparse.ArgumentParser(description="Tray Icon Toggle App")
    parser.add_argument('-tt', '--tooltip',
                        help='Tooltip text for the tray icon. Can have spaces. (default: executable name, stripped)')

    parser.add_argument('-id', '--id-char',
                        help='Single character for the tray icon. (default: executable name, first char)')

    parser.add_argument('-bg', '--bg-color', default="blue",
                        help='Color for the tray icon background. (default: blue)')

    parser.add_argument('-fc', '--font-color', default="yellow",
                        help='Color for the tray icon font. (default: yellow)')

    parser.add_argument('-sdc', '--stopped-dot-color', default="red",
                        help='Color for dot in "Stopped" state. (default: red)')

    parser.add_argument('-rdc', '--running-dot-color', default="green",
                        help='Color for dot in "Running" state. (default: green)')

    parser.add_argument('-sfc', '--stopped-font-color',
                        help='Color for font in "Stopped" state, IF SET. (default: not set)')

    parser.add_argument('-rfc', '--running-font-color',
                        help='Color for font in "Running" state, IF SET. (default: not set)')

    parser.add_argument('-sbc', '--stopped-bg-color',
                        help='Color for background in "Stopped" state, IF SET. (default: not set)')

    parser.add_argument('-rbc', '--running-bg-color',
                        help='Color for background in "Running" state, IF SET. (default: not set)')

    parser.add_argument('-sn', '--start-now', action='store_true',
                        help='Start the app immediately. (default: not enabled)')

    parser.add_argument('command', nargs=argparse.REMAINDER,
                        help='Command to run')

    args = parser.parse_args()

    if not args.command:
        print("You must at minimum provide a command to run.\n")
        parser.print_help()
        sys.exit(1)

    if args.command[0] == "--":
        args.command = args.command[1:]

    _exit = False

    color_fields = {
        "bg_color": args.bg_color,
        "font_color": args.font_color,
        "stopped_dot_color": args.stopped_dot_color,
        "running_dot_color": args.running_dot_color,
        "stopped_font_color": args.stopped_font_color,
        "running_font_color": args.running_font_color,
        "stopped_bg_color": args.stopped_bg_color,
        "running_bg_color": args.running_bg_color,
    }

    for name, value in color_fields.items():
        if value is None:
            continue

        try:
            ImageColor.getrgb(value)
        except ValueError:
            print(f"Error: Invalid color value for '{name.replace('_', '-')}' -- specified value was {value!r}")
            _exit = True

    cmd_path = Path(args.command[0])

    if not cmd_path.parent == '.':
        pwd_path = Path.cwd() / cmd_path.name

        if pwd_path.exists():
            args.command[0] = str(pwd_path)
            print(f"Notice: '{cmd_path}' not found. Will use '{pwd_path}' instead.")
        else:
            print(f"Error: Command file '{cmd_path}' not found (also not in current directory).")
            _exit = True

    if _exit:
        sys.exit(1)

    tray_app = TrayApp(args.command,
                       tooltip=args.tooltip, id=args.id_char, autostart=args.start_now,
                       bgcolor=args.bg_color, fontcolor=args.font_color,
                       rundcolor=args.running_dot_color, stopdcolor=args.stopped_dot_color,
                       runfcolor=args.running_font_color, stopfcolor=args.stopped_font_color,
                       runbcolor=args.running_bg_color, stopbcolor=args.stopped_bg_color)
    tray_app.run()


if __name__ == '__main__':
    main()

# Test args:
# --tooltip "Test me" --bg-color='rgb(0%, 5%, 100%)' -fc black -sdc="#CC0000" --running-dot-color "rgba(0, 128, 0, 128)" -rfc 'hsl(15,0%,0%)' -sfc "#aaf" --running-bg-color="aquamarine" -sbc 'hsv(15, 50%, 10%)' -- vban_emitter_monitor.sh --tooltip "Safe: Not parsed by tray.py"
# --tooltip "Test me" --bg-color='rgb(0%, 5%, 100%)' -fc black -sdc="#CC0000" --running-dot-color "rgba(0, 128, 0, 128)" -rfc 'hsl(15,0%,0%)' -sfc "#aaf" --running-bg-color="aquamarine" -sbc 'hsv(15, 50%, 10%)' vban_emitter_monitor.sh --tooltip "Still Safe: Not parsed by tray.py"
