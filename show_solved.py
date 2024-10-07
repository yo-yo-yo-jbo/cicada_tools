#!/usr/bin/env python3
from experiments import Experiments
import screen

def main():
    """
        Main routine.
    """

    # Shows all pages
    screen.clear()
    Experiments.show_all_sections(True)

if __name__ == '__main__':
    main()
