#!/usr/bin/env python3
import os
import sys
import string
import base64
from core import RUNES

# Colors
RED, GREEN, BLUE, WHITE, YELLOW, RESET_COLORS = '', '', '', '', '', ''
try:
    import colorama
    colorama.init()
    RED = colorama.Fore.RED + colorama.Style.BRIGHT
    GREEN = colorama.Fore.GREEN + colorama.Style.BRIGHT
    BLUE = colorama.Fore.BLUE + colorama.Style.BRIGHT
    WHITE = colorama.Fore.WHITE + colorama.Style.BRIGHT
    YELLOW = colorama.Fore.YELLOW
    RESET_COLORS = colorama.Style.RESET_ALL
except Exception:
    pass

# Logo
LOGO = base64.b64decode(b'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAsCiDiloTiloTCtyDilqogICDiloTiloTCtyAg4paE4paE4paEwrcgwrfiloTiloTiloTiloQgICDiloTiloTiloTCtyAgICAg4paE4oCiIOKWhOKWjOKWhOKWhOKWhOKWhOKWhOKWqiAg4paE4paE4paMICAu4paE4paEIMK3ICAgICAgICAgICAgICAgICAgIGAtLiAgIFwgICAgLi0nCuKWkOKWiCDilozilqrilojilogg4paQ4paIIOKWjOKWquKWkOKWiCDiloDilogg4paI4paIwrcg4paI4paIIOKWkOKWiCDiloDiloggICAgIOKWiOKWquKWiOKWiOKWjOKAouKWiOKWiCAg4paI4paIIOKWiOKWiOKAoiAg4paQ4paIIOKWgC4gICAgICAgICAgICwtImBgYGBgIiItXF9fIHwgIC8K4paI4paIIOKWhOKWhOKWkOKWiMK34paI4paIIOKWhOKWhOKWhOKWiOKWgOKWgOKWiCDilpDilojilqog4paQ4paI4paM4paE4paI4paA4paA4paIICAgICDilojilozilpDilojilowg4paQ4paILuKWquKWkOKWiMK34paI4paIIOKWqiDiloTiloDiloDiloDilojiloQuICAgICAgICAgICctLi5fICAgIF8uLSdgICctbywK4paQ4paI4paI4paI4paM4paQ4paI4paM4paQ4paI4paI4paI4paM4paQ4paI4paqIOKWkOKWjOKWiOKWiC4g4paI4paIIOKWkOKWiOKWqiDilpDilowgICAg4paQ4paI4paE4paI4paMIOKWkOKWiOKWjMK34paQ4paI4paM4paQ4paI4paMIOKWhOKWkOKWiOKWhOKWquKWkOKWiC4gICAgICAgICAgICAgIF8+LS06e3s8ICAgKSB8KQrCt+KWgOKWgOKWgCDiloDiloDiloDCt+KWgOKWgOKWgCAg4paAICDiloAg4paA4paA4paA4paA4paA4oCiICDiloAgIOKWgCAgICAgIOKWgOKWgOKWgCAg4paA4paA4paAIOKWgOKWgOKWgC7iloDiloDiloAgIOKWgOKWgOKWgOKWgCAgICAgICAgICAgIC4tJycgICAgICAnLS5fXy4tb2AKICAgICAgVXRpbGl0aWVzIGZvciBDaWNhZGEgMzMwMSByZXNlYXJjaC4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICctLl9fX19fLi4tL2AgIHwgIFwKICAgICAgSm9uYXRoYW4gQmFyIE9yICgiSkJPIiksIEB5b195b195b19qYm8uICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgLC0nICAgLyAgICBgLS4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgYAoK').decode() 

def print_logo():
    """
        Prints out the logo.
    """

    # White if possible
    print(f'{WHITE}{LOGO}{RESET_COLORS}')

def print_blue(msg, end='\n'):
    """
        Prints a blue message.
    """

    # Blue if possible
    print(f'{BLUE}{msg}{RESET_COLORS}', end=end)

def print_green(msg, end='\n'):
    """
        Prints a green message.
    """

    # Green if possible
    print(f'{GREEN}{msg}{RESET_COLORS}', end=end)

def print_red(msg, end='\n'):
    """
        Prints a red message.
    """

    # Red if possible
    print(f'{RED}{msg}{RESET_COLORS}', end=end)

def print_yellow(msg, end='\n'):
    """
        Prints a yellow message.
    """

    # Yellow if possible
    print(f'{YELLOW}{msg}{RESET_COLORS}', end=end)

def clear():
    """
        Clears the screen.
    """
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    
    # Print the logo as a header
    print_logo()

def press_enter():
    """
        Waits for an ENTER keypress.
    """

    # Get input and clear the screen
    print('Press ', end='')
    print_yellow('ENTER', end='')
    _ = input(' to continue.')
    clear()

def print_solved_text(text):
    """
        Prettifies and prints solved text.
    """

    # Color digits and lowercase
    s = text
    for c in string.digits + string.ascii_lowercase:
        s = s.replace(c, f'[!!!BLUE!!!]{c}[!!!RESET_COLORS!!!]')
    s = s.replace('[!!!RESET_COLORS!!!]', RESET_COLORS).replace('[!!!BLUE!!!]', BLUE)

    # Color runes
    for rune in RUNES:
        s = s.replace(rune, f'{RED}{rune}{RESET_COLORS}')
    
    # Color uppercase
    for letter in string.ascii_uppercase:
        s = s.replace(letter, f'{GREEN}{letter}{RESET_COLORS}')

    # Print
    print(s)

