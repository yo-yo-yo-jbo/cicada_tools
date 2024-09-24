#!/usr/bin/env python3
from research import Attempts
import screen

def main():
    """
        Main routine.
    """

    # Shows all pages
    screen.clear()
    Attempts.show_all_pages(True)

if __name__ == '__main__':
    main()
