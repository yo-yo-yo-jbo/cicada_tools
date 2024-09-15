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

def show_all_pages():
    """
        Presents all pages.
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

def get_unsolved_pages():
    """
        Gets all unsolved pages.
    """

    # Try to decrypt all pages
    result = []
    for page in PAGES:

        # Process all text
        processed_text = ProcessedText(page[0])
        for transformer in page[1]:
            transformer.transform(processed_text)

        # Add to result if page is unsolved
        if processed_text.is_unsolved():
            result.append(page[0])

    # Return all unsolved pages
    return result

def get_rune_wordlist():
    """
        Get a Runic wordlist from all solved pages dynamically.
    """

    # Try to decrypt all pages
    result = set()
    for page in PAGES:

        # Process all text
        processed_text = ProcessedText(page[0])
        for transformer in page[1]:
            transformer.transform(processed_text)

        # Skip unsolved pages
        if processed_text.is_unsolved():
            continue

        # Get all words
        for word in processed_text.get_rune_words():
            if len(word) == 0:
                continue
            result.add(word)

    # Return wordlist sorted by word length descending
    return sorted(result, key=len)[::-1]

