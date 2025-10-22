A dead-simple daemon tracker for Linux X11 desktops.

Use case:
- You need to run a non-interactive daemon, script, or other executable (vban_emitter, for example) and wish to monitor if it closes, but don't care about its terminal output.
- You wish to be able to know its state at a glance or start/stop it easily.
- You use a system tray in your desktop environment.

The app will generate a simple persistent system tray icon; a solid colored background, a colored dot, and a single colored character, with a tooltip indicating its name (or --tooltip) and run state. Defaults are indicated.

The tray icon has a context menu; "Start [name]", "Stop [name]", and "Quit". "Quit" also implies "Stop" if the process is running.

The app does not care about external processes. It ONLY tracks the run state of its immediate child process.

ALL text following tray.py options will be passed directly as a command and arguments for it. The first presence of a non-argument string is considered the command. The use of `--` is also respected to indicate no further arguments.

Command may be specified with absolute path. If path is omitted, current directory will be checked first, then PATH. A notice will be printed to stdout if search is used.

```
[git/tray-py]$ ./tray.py
You must at minimum provide a command to run.

usage: tray.py [-h] [-tt TOOLTIP] [-id ID_CHAR] [-bg BG_COLOR] [-fc FONT_COLOR] [-sdc STOPPED_DOT_COLOR] [-rdc RUNNING_DOT_COLOR] [-sfc STOPPED_FONT_COLOR] [-rfc RUNNING_FONT_COLOR] [-sbc STOPPED_BG_COLOR] [-rbc RUNNING_BG_COLOR] [-sn] ...

Tray Icon Toggle App

positional arguments:
  command               Command to run

options:
  -h, --help            show this help message and exit
  -tt, --tooltip TOOLTIP
                        Tooltip text for the tray icon. Can have spaces. (default: executable name, stripped)
  -id, --id-char ID_CHAR
                        Single character for the tray icon. (default: executable name, first char)
  -bg, --bg-color BG_COLOR
                        Color for the tray icon background. (default: blue)
  -fc, --font-color FONT_COLOR
                        Color for the tray icon font. (default: yellow)
  -sdc, --stopped-dot-color STOPPED_DOT_COLOR
                        Color for dot in "Stopped" state. (default: red)
  -rdc, --running-dot-color RUNNING_DOT_COLOR
                        Color for dot in "Running" state. (default: green)
  -sfc, --stopped-font-color STOPPED_FONT_COLOR
                        Color for font in "Stopped" state, IF SET. (default: not set)
  -rfc, --running-font-color RUNNING_FONT_COLOR
                        Color for font in "Running" state, IF SET. (default: not set)
  -sbc, --stopped-bg-color STOPPED_BG_COLOR
                        Color for background in "Stopped" state, IF SET. (default: not set)
  -rbc, --running-bg-color RUNNING_BG_COLOR
                        Color for background in "Running" state, IF SET. (default: not set)
  -sn, --start-now      Start the app immediately. (default: not enabled)
```

Example commands to demonstrate flexibility:
```
./tray.py vban_emitter --ipaddress=192.168.1.1 -p 6890 --streamname Monitor
./tray.py --id 'X' --tooltip VBAN_XMIT -- vban_emitter --ipaddress=192.168.1.1 -p 6890 --streamname Monitor
./tray.py --id-char=2 --tooltip "VBAN Monitor for Notifications" -bg black --running-dot-color blue -- vban_emitter --ipaddress=192.168.1.1 -p 6890 --streamname Monitor
./tray.py -id 4 --tooltip "Test me" --bg-color='rgb(0%, 5%, 100%)' -fc black -sdc="#CC0000" --running-dot-color "rgba(0, 128, 0, 128)" -rfc 'hsl(15,0%,0%)' -sfc "#aaf" --running-bg-color="aquamarine" -sbc 'hsv(15, 50%, 10%)' test_script.sh --tooltip "Still Safe: Not parsed by tray.py"
./tray.py --id '2' --tooltip "VBAN Monitor for Notifications" -bg black --running-dot-color blue -- /usr/bin/vban_emitter --ipaddress=192.168.1.1 -p 6890 --streamname Monitor
./tray.py --id-char='q' -- vban_emitter --ipaddress=192.168.1.1 -p 6890 --streamname Monitor
./tray.py ~/git/tray-py/test-script.sh
```


I know everyone loves pics and I'm no different but there isn't much to show. None the less;

Using "T" as an ID, menu open:

<img width="182" height="114" alt="image" src="https://github.com/user-attachments/assets/3b954ecd-1208-4b69-897c-2e0e6ccb21cd" />

Using "4" as an ID, menu closed, manual colors:

<img width="37" height="31" alt="image" src="https://github.com/user-attachments/assets/f553ee60-e12d-445b-8f9d-0bbfe1b65409" />
