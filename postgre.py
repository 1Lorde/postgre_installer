import os
import sys
import time

VERBOSE_MODE = False
LOGFILE_NAME = ".postgre.log"


class TextFormat:
    """ASCII colors and formatting for terminal output"""

    reset = '\033[0m'
    bold = '\033[01m'
    disable = '\033[02m'
    underline = '\033[04m'
    reverse = '\033[07m'
    strikethrough = '\033[09m'
    invisible = '\033[08m'

    class Colors:
        black = '\033[30m'
        red = '\033[31m'
        green = '\033[32m'
        orange = '\033[33m'
        blue = '\033[34m'
        purple = '\033[35m'
        cyan = '\033[36m'
        lightgrey = '\033[37m'
        darkgrey = '\033[90m'
        lightred = '\033[91m'
        lightgreen = '\033[92m'
        yellow = '\033[93m'
        lightblue = '\033[94m'
        pink = '\033[95m'
        lightcyan = '\033[96m'


def cmd(command):
    """Execute command in quiet/verbose mode and log output into file"""

    if VERBOSE_MODE:
        os.system(command + " | tee " + LOGFILE_NAME)
    else:
        os.system(command + " &>> " + LOGFILE_NAME)


def printf(text, color="", style="", end="\n"):
    """Print colored and formatted text into terminal"""

    print(color + style + text + TextFormat.reset, end=end)


def _clear(delay=0, hard=False):
    """A simple function which clear terminal"""

    time.sleep(delay)
    if hard:
        os.system("reset")
    else:
        print(chr(27) + "[2J")
        os.system("clear")


def _show_welcome(timeout=0, only_banner=False):
    """A simple function that show banner and greeting"""

    banner = r"""
#   ____           _                 ____   ___  _     
#  |  _ \ ___  ___| |_ __ _ _ __ ___/ ___| / _ \| |    
#  | |_) / _ \/ __| __/ _` | '__/ _ \___ \| | | | |    
#  |  __/ (_) \__ \ || (_| | | |  __/___) | |_| | |___ 
#  |_|   \___/|___/\__\__, |_|  \___|____/ \__\_\_____|
#                     |___/                            
#   _           _        _ _           
#  (_)_ __  ___| |_ __ _| | | ___ _ __ 
#  | | '_ \/ __| __/ _` | | |/ _ \ '__|
#  | | | | \__ \ || (_| | | |  __/ |   
#  |_|_| |_|___/\__\__,_|_|_|\___|_|   
#                                      
#  
#                           by Vlad Savchuk <group 385>
"""
    printf(banner, TextFormat.Colors.lightgreen, TextFormat.bold)
    time.sleep(timeout)

    if not only_banner:
        printf("   Hey there! This script will help you to configure\nyour PostgreSQL server on CentOS.")
    print()


def _show_status():
    """Print install\\running status into terminal"""

    printf("Status", style=TextFormat.bold)
    print("========================")
    printf("⬧ Installed:", end="")
    if is_installed():
        printf("\t⚫ ", TextFormat.Colors.green, TextFormat.bold, end="")
        printf("Yes", TextFormat.Colors.green, TextFormat.bold)
    else:
        printf("\t⚫ ", TextFormat.Colors.red, TextFormat.bold, end="")
        printf("No", TextFormat.Colors.red, TextFormat.bold)
    print("------------------------")
    printf("⬧ Running:", end="")
    if is_running():
        printf("\t⚫ ", TextFormat.Colors.green, TextFormat.bold, end="")
        printf("Yes", TextFormat.Colors.green, style=TextFormat.bold)
    else:
        printf("\t⚫ ", TextFormat.Colors.red, TextFormat.bold, end="")
        printf("No", TextFormat.Colors.red, style=TextFormat.bold)
    print("========================")
    print()


def main_menu():
    """Function that show main menu and wait for user input"""

    _show_welcome()
    _show_status()
    printf("Menu:", TextFormat.bold)
    printf("  1. Install PostgreSQL server\n  2. Manage & Configure server\n  3. Delete server\n  q. Exit")
    return str(input(TextFormat.underline + TextFormat.bold + "Your choice" + TextFormat.reset + " >>> "))


def config_menu():
    """Function that show config menu and wait for user input"""

    if is_installed():
        menu_str = ""
        menu_str += "  1. Stop server" if is_running() else "  1. Start server"
        menu_str += "\n"
        menu_str += "  2. Restart server\n"
        menu_str += "  3. Disable autostart" if is_autorun() else "  3. Enable autostart"
        menu_str += "\n"
        menu_str += "  4. Edit configuration file"
        menu_str += "\n"
        menu_str += "  0. Back (to Main menu)"

        _clear()
        _show_welcome()
        _show_status()
        printf("Manage & Configure menu:", TextFormat.bold)
        printf(menu_str)
        return str(input(TextFormat.underline + TextFormat.bold + "Your choice" + TextFormat.reset + " >>> "))
    _clear()
    _show_welcome()
    printf("[Not Installed] Install PostgreSQL first.", TextFormat.Colors.yellow,
           TextFormat.bold)
    _clear(3)
    return '0'


def print_progress_bar(iteration, total, prefix='Progress:', suffix='Complete',
                       decimals=1, length=50, fill='█', print_end="\n"):
    """
    Print iterations progress
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        print_end    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), print_end)


def send_notify(message):
    """Function which send graphical notification"""

    os.system("sudo -u $USER DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus notify-send -t 3000 -a "
              "terminal \"PostgreSQL - Installation Script\" \"" + message + "\"")


def version():
    return os.popen("postgres -V").read() if is_installed() else "PostgreSQL not found."


def is_root():
    """Check if script running as root"""

    if os.getuid() != 0:
        printf("[Root Needed] Run this script as root (\"sudo python3 postgre.py\").", TextFormat.Colors.yellow,
               TextFormat.bold)
        return False
    return True


def is_centos():
    """Check if script running on CentOS"""

    result = os.popen("hostnamectl").read()
    if "centos" not in result.lower():
        printf("[Not Supported] Sorry, but this script only works with CentOS.", TextFormat.Colors.yellow,
               TextFormat.bold)
        return False
    return True


def is_installed():
    """Check if PostgreSQL installed"""

    result = os.popen("yum list installed -q | grep postgresql").read()
    if len(result) != 0:
        return True
    return False


def is_running():
    """Check PostgreSQL running status"""

    result = os.popen("systemctl status postgresql 2>&1 | grep -i running").read()
    if len(result) != 0:
        return True
    return False


def is_autorun():
    """Check if PostgreSQL starting at system boot"""

    result = os.popen("ls /etc/systemd/system/multi-user.target.wants/ | grep postgresql.service").read()
    if len(result) == 0:
        return False
    else:
        return True


def install():
    """Install PostgreSQL"""

    if not is_installed():

        send_notify("Installation started..")
        _clear()
        print_progress_bar(0, 4)
        printf(" · Installing postgresql-server package from yum...\n", TextFormat.Colors.lightblue)
        cmd("sudo yum -y install postgresql-server")

        _clear(3)
        print_progress_bar(1, 4)
        printf(" · Installing postgresql-server package from yum...", TextFormat.Colors.lightblue, end=" ")
        printf("Done.", TextFormat.Colors.green, TextFormat.bold)
        time.sleep(1)
        printf(" · Initializing database...\n", TextFormat.Colors.lightblue)
        cmd("sudo postgresql-setup --initdb")

        _clear(3)
        print_progress_bar(2, 4)
        printf(" · Installing postgresql-server package from yum...", TextFormat.Colors.lightblue, end=" ")
        printf("Done.", TextFormat.Colors.green, TextFormat.bold)
        printf(" · Initializing database...", TextFormat.Colors.lightblue, end=" ")
        printf("Done.", TextFormat.Colors.green, TextFormat.bold)
        time.sleep(1)
        printf(" · Starting service...\n", TextFormat.Colors.lightblue)
        cmd("sudo systemctl start postgresql")

        _clear(3)
        print_progress_bar(3, 4)
        printf(" · Installing postgresql-server package from yum...", TextFormat.Colors.lightblue, end=" ")
        printf("Done.", TextFormat.Colors.green, TextFormat.bold)
        printf(" · Initializing database...", TextFormat.Colors.lightblue, end=" ")
        printf("Done.", TextFormat.Colors.green, TextFormat.bold)
        printf(" · Starting service...", TextFormat.Colors.lightblue, end=" ")
        printf("Done.", TextFormat.Colors.green, TextFormat.bold)
        time.sleep(1)
        printf(" · Configuring PostgreSQL to start on every system reboot automatically...\n",
               TextFormat.Colors.lightblue)
        cmd("sudo systemctl enable postgresql")

        _clear(3)
        print_progress_bar(4, 4)
        printf(" · Installing postgresql-server package from yum...", TextFormat.Colors.lightblue,
               end=" ")
        printf("Done.", TextFormat.Colors.green, TextFormat.bold)
        printf(" · Initializing database...", TextFormat.Colors.lightblue, end=" ")
        printf("Done.", TextFormat.Colors.green, TextFormat.bold)
        printf(" · Starting service...", TextFormat.Colors.lightblue, end=" ")
        printf("Done.", TextFormat.Colors.green, TextFormat.bold)
        printf(" · Configuring PostgreSQL to start on every system reboot automatically...",
               TextFormat.Colors.lightblue, end=" ")
        printf("Done.", TextFormat.Colors.green, TextFormat.bold)
        time.sleep(1)
        print()
        printf("Successfully installed!", TextFormat.Colors.green, TextFormat.bold)
        send_notify("Successfully installed!")
        _clear(3)

    else:
        _clear()
        _show_welcome()
        printf("PostgreSQL already installed!", TextFormat.Colors.green, TextFormat.bold)
        _clear(3)


def config(choice):
    """Configure & Manage PostgreSQL"""

    if choice == '1':
        if is_running():
            cmd("sudo systemctl stop postgresql")
            printf("Stopping..", TextFormat.Colors.lightblue)
            time.sleep(1)
        else:
            cmd("sudo systemctl start postgresql")
            printf("Starting..", TextFormat.Colors.lightblue)
            time.sleep(1)

    elif choice == '2':
        cmd("sudo systemctl restart postgresql")
        printf("Restarting..", TextFormat.Colors.lightblue)
        time.sleep(1)

    elif choice == '3':
        if is_autorun():
            cmd("sudo systemctl disable postgresql")
            printf("Disable autorun..", TextFormat.Colors.lightblue)
            time.sleep(1)
        else:
            cmd("sudo systemctl enable postgresql")
            printf("Enable autorun..", TextFormat.Colors.lightblue)
            time.sleep(1)

    elif choice == '4':
        if os.system("sudo ls /var/lib/pgsql/data | grep postresql.conf") != "":
            printf("Opening configuration file..", TextFormat.Colors.lightblue)
            time.sleep(1)
            cmd("sudo nano /var/lib/pgsql/data/postgresql.conf")
        else:
            printf("[Not Exist] Configuration file not exist, try to reinstall.", TextFormat.Colors.yellow)

    _clear()


def remove():
    """Remove PostgreSQL"""

    if is_installed():
        printf("Do you want to keep configurations and databases?", TextFormat.Colors.yellow, TextFormat.bold)
        answer = str(input("[y,n] >>> "))
        if (answer.lower() == 'y') | (answer.lower() == 'n'):
            send_notify("Removing PostgreSQL..")
            _clear()
            printf(" · Removing postgresql-server package...\n", TextFormat.Colors.lightblue)
            cmd("sudo yum -y remove postgresql-server")
            _clear(3)
            printf(" · Removing postgresql-server package...", TextFormat.Colors.lightblue, end=" ")
            printf("Done.", TextFormat.Colors.green, TextFormat.bold)
            time.sleep(1)

            if answer.lower() == 'n':
                printf(" · Removing configurations from /var/lib/pgsql ...\n", TextFormat.Colors.lightblue)
                cmd("sudo rm -rf /var/lib/pgsql/*")
                _clear(3)
                printf(" · Removing postgresql-server package...", TextFormat.Colors.lightblue, end=" ")
                printf("Done.", TextFormat.Colors.green, TextFormat.bold)
                printf(" · Removing configurations from /var/lib/pgsql ...", TextFormat.Colors.lightblue, end=" ")
                printf("Done.", TextFormat.Colors.green, TextFormat.bold)
                time.sleep(1)
                print()

            printf("All done!", TextFormat.Colors.green, TextFormat.bold)
            send_notify("Successfully removed!")
            _clear(3)
        else:
            printf("[Cancelled] Removing aborted.", TextFormat.Colors.lightblue, TextFormat.bold)
            _clear(3)
    else:
        _clear()
        _show_welcome()
        printf("[Not Installed] Can`t remove PostgreSQL, because it is not installed!", TextFormat.Colors.yellow,
               TextFormat.bold)
        _clear(3)


def entry_point():
    global VERBOSE_MODE

    if sys.argv.__contains__("--verbose") | sys.argv.__contains__("-v"):
        VERBOSE_MODE = True
        main()

    elif sys.argv.__contains__("--status") | sys.argv.__contains__("-s"):
        _show_status()

    elif sys.argv.__contains__("--author") | sys.argv.__contains__("-a"):
        _show_welcome(only_banner=True)
        printf("If you have any questions or suggestions,\nfeel free to write me here: t.me/savchuk_vlad.")

    elif sys.argv.__contains__("--version") | sys.argv.__contains__("-V"):
        print(version())

    elif sys.argv.__contains__("--help") | sys.argv.__contains__("-h"):
        man_page = r""".\" manpage for PostgreSQL Installer
.\" Contact t.me/savchuk_vlad to correct errors or typos
.TH posgtgre.py 1 "31 May 2020" "version 1.0" "PostgreSQL Installer manpage"

.SH NAME
.B PostgreSQL Installer
- install, configure, manage and remove PostgreSQL server on CentOS.

.SH SYNOPSIS
.B postgre.py
.RI "[" FLAG "]..."

.SH DESCRIPTION
.B postgre.py
- use this script for installation, configuration, managing and removing PostgreSQL server in CentOS.
.PP

.SH OPTIONS
.TP
.B -v | --verbose
Run script in verbose mode.
.TP
.B -s | --status
Print current server status in system.
.TP
.B -a | --author
Information about author.
.TP
.B -V | --version
Show installed PostgreSQL version.
.TP
.B -h | --help
Show this man-page.

.SH EXAMPLES
The following will show a typical usage.
.PP
.RS
.BR $ " sudo python3 postgre.py -v"
.br
.BR $ " sudo python3 postgre.py --status"

.SH EXIT STATUS
If operating system isn`t CentOS, output will be the next:
.RS
.BR "[Not Supported] Sorry, but this script only works with CentOS."
.br
.PP
.RE
If run script without root, output will be the next:
.RS
.BR "[Root Needed] Run this script as root (sudo python3 postgre.py)."

.SH BUGS
No known bugs, yet :)

.SH AUTHOR
Vlad Savchuk (t.me/savchuk_vlad)

.SH COPYRIGHT
MIT License
.PP
Copyright (c) 2020 Vlad Savchuk
"""
        if not os.path.exists("./postgre_manpage"):
            os.system("touch postgre_manpage")
            with open("postgre_manpage", "w") as file:
                file.write(man_page)
        os.system("man ./postgre_manpage")

    else:
        main()


def main():
    try:
        if is_centos():
            if is_root():
                _clear()
                while True:
                    choice = main_menu()
                    if choice == '1':
                        install()
                    elif choice == '2':
                        while True:
                            choice = config_menu()
                            config(choice)
                            if choice == '0':
                                break
                    elif choice == '3':
                        remove()
                    elif choice == 'q':
                        exit()
                    else:
                        _clear()

                    if choice.lower() == 'q':
                        break

    except KeyboardInterrupt:
        printf("\n[EXIT] Script exited by user.", TextFormat.Colors.red, TextFormat.bold)
        exit()


if __name__ == '__main__':
    entry_point()
