# Cicada 3301 tools
Cicada 3301 Python utilities for decryption purposes.

## Assumptions
There is a lot of documented material on Cicada 3301 and the currently unsolved version 2 of their rune-based encrypted "book", AKA `Liber Primus` or `LP2` for short.

Based on the encrypted payload, I hafe a few assumptions:
1. The cipher encrypts entire words in some fashion (based on the word lengths and punctuation).
2. The cipher works on at least two letters at the same time (Digraphs) due to IoC tests.
3. The cipher probably treats two consecutive letters differently (e.g. like `Playfair` cipher does). This is a conclusion from the low distribution of doublets in the entire `LP2`.

## Attempts made
1. Using `Hill cipher` with one of the magic squares used as the matrix key, optionally with `Atbash`, `Shifts` and `prime substruction`.
2. Using sophisticated shifts on a decrypted `Vigenere cipher` with the word `INSTAR` as the key.

## Coding and classes
The following section includes coding and useful classes:

### LiberPrimus.py
Contains utilities for `LP` and `LP2` translations:
1. Each translation class inherits from `Translation` base class and should implement one method `decrypt(self, page`). Parameters to translation classes should be assigned at their construction.
2. A class called `UnsolvedTranslation` marks pages that are not translated.
3. The `LiberPrimusPages` class contains a `PAGES` member which is a list of 2-tuples: `(cipher, translation)`.
4. The `LiberPrimusPages` class also exports convinience methods such as `get_unsolved_pages()`.

### CicadataUtils.py
Contains a class called `Cicada` which does a lot of basic encryption, decryption and heuristics.
1. It contains the members `RUNES` and `LATIN` that translate runes to latin as per the Cicada Gematria Primus.
2. Helper methods such as `find_next_prime`, `totient`, `heuristically_english` and `press_enter`.
3. Working translations such as `runes_to_latin`, `hill_decrypt_to_runes`, `autokey_decrypt_to_runes` and `vigenere_decrypt`.
4. Outside of the `Cicada` class there is a method called `tests` which shows all the translated pages, and a method called `solve` which will hopefully one day solve `LP2`. As of now, `solve` is the main way to experiment.

## Example of solution attempt
Assuming we wish to use "INSTAR" as a vigenere cipher, we could code the following:

```python
def solve():
    """
        Wishful thinking.
    """

    # Get all unsolved pages
    pages = LiberPrimus.LiberPrimusPages.get_unsolved_pages()

    # Good luck!
    idx = 0
    for page in pages:
        idx += 1
        print(f'PAGE {idx}\n\n')
        print(Cicada.vigenere_decrypt(page, 'ᛁᚾᛋᛏᚪᚱ'))
        Cicada.press_enter()
```

