# Cicada utils
Cicada 3301 Python utilities for decryption and research purposes.

## Assumptions
There is a lot of documented material on Cicada 3301 and the currently unsolved version 2 of their rune-based encrypted "book", AKA `Liber Primus` or `LP2` for short.

Based on the encrypted payload, I have a few assumptions:
1. The cipher encrypts entire words in some fashion (based on the word lengths and punctuation).
2. The cipher works on at least two letters at the same time (Digraphs) due to IoC tests.
3. The cipher probably treats two consecutive letters differently (e.g. like `Playfair` cipher does). This is a conclusion from the low distribution of doublets in the entire `LP2`.

## Attempts made
All attempts are under the `Attempts` class, in `research.py`. Once executed, that file presents a menu dynamically based on all methods tried so far.  
That's a great programmatic way of documenting all attempts.

## Coding and classes
The following section includes coding and useful classes:

### pages.py
Contains pages in Runes as an array called `PAGES`, with each page also containing its decryption `Transformer`, if available.

### core.py
Contains utilities for translations, including the most important class, `ProcessedText`.  
That class keeps a mutation of all runes while maintaining all punctuation and non-rune instances.
 
### transformers.py
Contains `Transformer` classes, which transform `ProcessedText` instances runes by calling `transform` on them.

### research.py
Considered to be the "main" research-based module. Just run it.

### squares.py
Contains matrices found in `LP` in `sympy.Matrix` form.  
Might be useful for things later such as `Hill cipher` attempts.

### screen.py
Pretty-printing utilities. 

