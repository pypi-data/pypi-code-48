# TODO Windows truncates the path updates to 1024 chars?
import curses
import curses.ascii
import os
from os import system, environ
from os.path import join, expanduser, exists
import sys
from signal import signal, SIGINT, SIGTERM
import pathlib
from configparser import ConfigParser


class Jswitch:

    def __init__(self, screen):
        self.java_envs = []

        # Capture CTRL-C/CTRL-Z breaks
        signal(SIGINT, self.shutdown)
        signal(SIGTERM, self.shutdown)

        # Use  ``~/.config/jswitch/jswitch.ini`` as the default config file
        config_dir = join(expanduser("~"), ".config", "jswitch")
        self.jswitch_config_filepath = join(config_dir, "jswitch.ini")

        # Create the config directory if it does not exist
        if not exists(config_dir):
            print('[*] No config directory detected. Creating ~/.config/jswitch/')
            pathlib.Path(config_dir).mkdir(parents=True, exist_ok=True)

        # Generate an example ini file if one does not exist
        if not exists(self.jswitch_config_filepath):
            print(f'[*] No jswitch.ini file detected. Creating {self.jswitch_config_filepath}')
            config = ConfigParser()
            config['Example JDK 8'] = {
                'JAVA_HOME': 'C:\\Program Files\\Java\\jdk1.8.0_221',
            }
            with open(self.jswitch_config_filepath, 'w') as output_file:
                config.write(output_file)

        self.load_java_envs()

        self.active_choice = 0

        self.screen = screen
        self.screen.keypad(1)
        curses.curs_set(0)
        curses.noecho()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

    def run(self):
        self.input_loop()

    def print_options(self):
        # TODO print current java env
        self.screen.clear()
        num_header_rows = 4
        self.screen.addstr(0, 0, f"Current JAVA_HOME: {os.environ.get('JAVA_HOME')}")
        self.screen.addstr(2, 0, "Select an option (Press H for help):")

        for i, java_env in enumerate(self.java_envs):
            if i == self.active_choice:
                self.screen.addstr(i + num_header_rows, 0, " > %s" % (java_env), curses.color_pair(1) | curses.A_BOLD)
            else:
                self.screen.addstr(i + num_header_rows, 0, "   %s" % (java_env))
        self.screen.refresh()

    def input_loop(self):
        while True:
            self.print_options()

            try:
                char_ord = self.screen.getch()
                char = chr(char_ord).upper()

                if char == 'Q' or char_ord == curses.ascii.ESC:  # Esc or Q
                    self.shutdown()
                elif char == 'J' or char_ord == curses.KEY_DOWN:  # Down or J
                    if self.active_choice < len(self.java_envs) - 1:
                        self.active_choice += 1
                elif char == 'K' or char_ord == curses.KEY_UP:  # Up or K
                    if self.active_choice > 0:
                        self.active_choice -= 1
                elif char == 'E':
                    self.launch_editor()
                elif char == 'R':  # Refresh screen
                    self.load_java_envs()
                elif char == 'H':  # Print help screen
                    self.print_help_screen()
                elif char_ord == curses.ascii.LF or char == 'L' or char_ord == curses.KEY_RIGHT:  # Enter, L or Right
                    # Choice has been selected already, exit the menu system
                    break
            except Exception as e:
                print('[-] Invalid keypress detected.')
                print(e)

        # After breaking out of loop, update the system environment vars
        self.cleanup_curses()
        self.update_environment_vars()

    def load_java_envs(self):
        # Read the config file. One should now exist even if it is the default.
        config = ConfigParser()
        config.read(self.jswitch_config_filepath)
        self.java_envs = []
        for java_env in config:
            if java_env == 'DEFAULT':
                continue  # This exists even if not in the file
            # Store in list as ``My JDK 8 | C:\path\to\jdk8\``
            self.java_envs.append(f'{java_env} | {config[java_env].get("JAVA_HOME")}')

    def update_environment_vars(self):
        java_home_dir = self.java_envs[self.active_choice].split(' | ')[1]  # Split the text option

        if os.name == 'nt':  # Windows
            system(f'setx JAVA_HOME "{java_home_dir}"')
            # In windows, it lets you keep the variable itself in the path
            # if f'{java_home_dir}\\bin' not in os.environ.get('PATH', ''):
            #     system(f'setx PATH "%PATH%";"%JAVA_HOME%\\bin"')
        else:  # Mac/Linux
            system(f'export JAVA_HOME="{java_home_dir}"')
            # if '$JAVA_HOME/bin' not in os.environ.get('PATH', ''):
                # Linux will use the JAVA_HOME value once and not store the variable reference
                # system(f'export PATH="$PATH:$JAVA_HOME/bin"')

    def cleanup_curses(self):
        self.screen.keypad(0)
        curses.curs_set(1)
        curses.echo()
        curses.endwin()

    def shutdown(self):
        self.cleanup_curses()
        sys.exit(0)

    def launch_editor(self):
        editor = environ.get('EDITOR')
        if editor is None:  # Default editors
            if sys.platform == 'win32':
                editor = 'notepad.exe'
            elif sys.platform == 'darwin':
                editor = 'nano'
            elif 'linux' in sys.platform:
                editor = 'vi'
        system("%s %s" % (editor, self.jswitch_config_filepath))
        self.load_java_envs()  # Reload after changes

    def print_help_screen(self):
        self.screen.clear()

        self.screen.addstr(0, 0, "## Help ##")
        self.screen.addstr(1, 0, f" Config file: {self.jswitch_config_filepath}")
        self.screen.addstr(2, 0, "  H - This help screen")
        self.screen.addstr(3, 0, "  Q or ESC - Quit the program")
        self.screen.addstr(4, 0, "  E - Edit config file")
        self.screen.addstr(5, 0, "  R - Reload config file")
        self.screen.addstr(6, 0, "  Down or J - Move selection down")
        self.screen.addstr(7, 0, "  Up or K - Move selection up")
        self.screen.addstr(8, 0, "  Right or L or Enter - Choose current selection")
        self.screen.addstr(10, 0, "Note, you may need to restart your command prompt or application")
        self.screen.addstr(11, 0, "for changes to environment variables to update")
        self.screen.addstr(13, 0, "Press any key to continue")
        # TODO add a Generate new default config file option

        self.screen.getch()  # Wait for any key press


def main_wrapper(main_screen):
    jswitch = Jswitch(main_screen)
    jswitch.run()


def main():
    curses.wrapper(main_wrapper)


if __name__ == '__main__':
    main()
