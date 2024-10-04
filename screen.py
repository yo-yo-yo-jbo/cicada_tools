#!/usr/bin/env python3
from core import RuneUtils

import os
import sys
import string
import base64

# Colors
RED, GREEN, BLUE, WHITE, YELLOW, RESET_COLORS = '', '', '', '', '', ''
try:
    import colorama
    colorama.init()
    RED = colorama.Fore.RED + colorama.Style.BRIGHT
    GREEN = colorama.Fore.GREEN + colorama.Style.BRIGHT
    BLUE = colorama.Fore.LIGHTBLUE_EX + colorama.Style.BRIGHT
    WHITE = colorama.Fore.WHITE + colorama.Style.BRIGHT
    YELLOW = colorama.Fore.YELLOW
    RESET_COLORS = colorama.Style.RESET_ALL
except Exception:
    pass

# Logo
LOGO = base64.b64decode(b'CgogICAgICAsKysrNzc3NzcrKz06LCAgICAgICAgICAgICAgICAgICAgKz0gICAgICAgICAgICAgICAgICAgICAgLCwrKz03Kys9LCwgICAgICAgICAgICAgIOKWhOKWhMK3IOKWqiAgIOKWhOKWhMK3ICDiloTiloTiloTCtyDCt+KWhOKWhOKWhOKWhCAgIOKWhOKWhOKWhMK3ICAgICDiloTigKIg4paE4paM4paE4paE4paE4paE4paE4paqICDiloTiloTilowgIC7iloTiloQgwrcgIAogICAgN34/NyAgICs3STc3IDosSTc3NyAgSSAgICAgICAgICA3NyA3Kzc3IDc6ICAgICAgICAsPzc3Nzc3Nz8/fiw9Kz1+STc/LD03NyBJICAgICAgICAg4paQ4paIIOKWjOKWquKWiOKWiCDilpDilogg4paM4paq4paQ4paIIOKWgOKWiCDilojilojCtyDilojilogg4paQ4paIIOKWgOKWiCAgICAg4paI4paq4paI4paI4paM4oCi4paI4paIICDilojilogg4paI4paI4oCiICDilpDilogg4paALiAgCj03STdJfjcgICw3NzogKys6fis3IDc3PTc3NzcgNyAgICAgKzc3PTcgPTdJNyAgICAgLEk3Nzc9IDc3LDp+NyArPzcsIH43ICAgfiA3Nzc/ICAgICAgICDilojilogg4paE4paE4paQ4paIwrfilojilogg4paE4paE4paE4paI4paA4paA4paIIOKWkOKWiOKWqiDilpDilojiloziloTilojiloDiloDiloggICAgIOKWiOKWjOKWkOKWiOKWjCDilpDilogu4paq4paQ4paIwrfilojilogg4paqIOKWhOKWgOKWgOKWgOKWiOKWhC4KNzcrN0kgNzc3fiwsPTd+ICAsOjo3PTc6IDcgNzcgICA3NzogNyA3ICs3Nyw3IEk3Nzd+Kzc3N0k9ICAgPTosNzcsNzcgIDc3IDcsNzc3LCAgICAgICAgIOKWkOKWiOKWiOKWiOKWjOKWkOKWiOKWjOKWkOKWiOKWiOKWiOKWjOKWkOKWiOKWqiDilpDilozilojiloguIOKWiOKWiCDilpDilojilqog4paQ4paMICAgIOKWkOKWiOKWhOKWiOKWjCDilpDilojilozCt+KWkOKWiOKWjOKWkOKWiOKWjCDiloTilpDilojiloTilqrilpDiloguCiAgPSA3ICA/NyAsIDd+LH4gICsgNzcgPzogOj83NzcgK343NyA3Nz8gSTc3NzdJN0k3IDc3Nys3NyAgID06LCA/NyAgICs3IDc3Nz8gICAgICAgICAgICDCt+KWgOKWgOKWgCDiloDiloDiloDCt+KWgOKWgOKWgCAg4paAICDiloAg4paA4paA4paA4paA4paA4oCiICDiloAgIOKWgCAgICAgIOKWgOKWgOKWgCAg4paA4paA4paAIOKWgOKWgOKWgC7iloDiloDiloAgIOKWgOKWgOKWgOKWgCAgCiAgICAgIDc3IH5JID09IH43Nz0gKzc3NyA3Nzd+OiBJLCs3Nz8gIDcgIDc6Pzc/ID83IDcgNyA3NyB+SSAgIDdJLCw/NyBJNzd+CiAgICAgICBJIDc9Nzd+Kzc3Kz89Okkrfjc3PyAgICAgLCBJIDc/IDc3IDcgICA3Nzd+ICs3IEkrPzcgICs3fj83NzcsNzdJICAgICAgICAgICAgICAgICAgICAgICAgICAgVXRpbGl0aWVzIGZvciBDaWNhZGEgMzMwMSByZXNlYXJjaAogICAgICAgICA9NzcgNzc9ICs3IDc3NzcgICAgICAgICAsNyA3Pzc6LD8/NyAgICAgKzcgICAgNyAgIDc3Pz8rIDc3NzcsICAgICAgICAgICAgICAgICAgICAgICAgICBKb25hdGhhbiBCYXIgT3IgKCJKQk8iKSwgQHlvX3lvX3lvX2pibwogICAgICAgICAgICAgPUksIEkgNys6Nzc/ICAgICAgICAgKzdJNz83Nzc3IDogICAgICAgICAgICAgOjcgNyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFsgaHR0cHM6Ly95by15by15by1qYm8uZ2l0aHViLmlvIF0KICAgICAgICAgICAgICAgIDdJN0k/NzcgfiAgICAgICAgICs3Ojc3LCAgICAgfiAgICAgICAgICs3LDo6NyAgIDcKICAgICAgICAgICAgICAgLDd+Nzc/Nz8gPzogICAgICAgICA3Kzo3Nzc3NywgICAgICAgICAgIDc3IDo3Nzc3PQogICAgICAgICAgICAgICAgPzc3ICtJNyssNyAgICAgICAgIDd+ICA3LCs3ICAsPyAgICAgICA/Nz9+Pzc3NzoKICAgICAgICAgICAgICAgICAgIEk3Nzc9Nzc3NyB+ICAgICA3NyA6ICA3NyA9NyssICAgIEk3NyAgNzc3CiAgICAgICAgICAgICAgICAgICAgICsgICAgICB+PyAgICAgLCArIDcgICAgLCwgfkksICA9ID8gLAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA3NzpJKwogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAsNwogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgOjc3CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA6Cgo=').decode() 

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

def press_enter(clear_screen=True):
    """
        Waits for an ENTER keypress.
    """

    # Get input and clear the screen
    print('Press ', end='')
    print_yellow('ENTER', end='')
    _ = input(' to continue.')
    if clear_screen:
        clear()

def print_solved_text(text):
    """
        Prettifies and prints solved text.
    """

    # Color lowercase
    s = text
    for c in string.ascii_lowercase:
        s = s.replace(c, f'[!!!BLUE!!!]{c}[!!!RESET_COLORS!!!]')
    s = s.replace('[!!!RESET_COLORS!!!]', RESET_COLORS).replace('[!!!BLUE!!!]', BLUE)

    # Color titles
    s = s.replace('<', RED).replace('>', RESET_COLORS)

    # Print
    print(s)

def run_menu(title, menu_items_list):
    """
        Runs a menu. The given menu items argument must be a list that maps keys to values.
    """

    # Run forever
    last_error = None
    while True:

        # Print title
        clear()
        if last_error is not None:
            print_red(f'{last_error}\n')
            last_error = None
        print_yellow(title)

        # Print menu item
        dots_max_len = len(str(len(menu_items_list))) + 15 + max([ len(item[0]) for item in menu_items_list ])
        index = 0
        for k, v in menu_items_list:
            index += 1
            print_blue(f'{index}.', end=' ')
            dots = '.' * (dots_max_len - (len(k) + len(str(index))))
            print(f'{k} {dots} {v}')

        # Get user choice
        print('\nChoose ', end='')
        print_yellow('Q', end='')
        print(' to quit, or ', end='')
        print_yellow('CTRL+C', end='')
        print(' to get back to main menu.\n')

        # Get choice and return it
        choice = input('Enter your choice: ').strip()
        if choice in ('q', 'Q'):
            return None
        if choice == '':
            continue
        if not choice.isdigit():
            last_error = 'Invalid choice'
            continue
        menu_index = int(choice)
        if menu_index <= 0 or menu_index > len(menu_items_list):
            last_error = 'Invalid choice'
            continue
        return menu_index - 1

