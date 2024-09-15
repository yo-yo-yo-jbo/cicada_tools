#!/usr/bin/env python3
from pages import PAGES
from core import ProcessedText
import os

def press_enter():
    """
        Waits for an ENTER keypress.
    """

    # Get input and clear the screen
    _ = input()
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def main():
    """
        Main routine.
    """

    # Decrypt all pages
    page_index = 1
    for page in PAGES:

        # Build the processed text
        processed_text = ProcessedText(page[0])

        # Get the rune IoC
        rune_ioc = processed_text.get_rune_ioc()

        # Decrypt
        for transformer in page[1]:
           transformer.transform(processed_text)

        # Present and wait for input
        print(f'Page: {page_index}\nRunic IoC: {rune_ioc}\nLatin IoC: {processed_text.get_latin_ioc()}\n\n{processed_text.to_latin()}\n\n{page[0]}\n\n\n')
        press_enter()
        page_index += 1

if __name__ == '__main__':
    main()
