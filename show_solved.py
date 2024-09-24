#!/usr/bin/env python3
from main import Attempts
import screen

def main():
    """
        Main routine.
    """

    # Shows all pages
    screen.clear()
    Attempts.show_all_sections(True)

if __name__ == '__main__':
    main()
