# Cicada utils
Cicada 3301 Python utilities for decryption and research purposes.
![Screenshot](screenshot.png)

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

### liber_primus.py
Contains sections in Runes, parsed dynamically from the folder `liber_primus`. The structure of the `liber_primus` folder is quite intuitive:
1. Each directory under `liber_primus` is taken into account (besides directories starting with a `.`) and is considered a `section`. They will be sorted alphabetically.
2. By convension, we use `index_section_name` where `index` is a 3-digit Decimal number (increasing), including preceding zeros.
3. Each such directory (section) has a `section.json` file, which contains the section `title` (if available), its `transformers` and `pages`.
4. Each `transformer` will be translated into an actual `transformer` instance (see `transformers.py`), and applied in the mentioned order on the runes.
5. Each `page` is expected to optionally have a corresponding `number`, as well as `text` (mandatory).

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

### secrets.py
Contains other secrets that are not squares, such as the [2013 missing primes](https://uncovering-cicada.fandom.com/wiki/What_Happened_Part_1_(2013)#THE_DIFFERENCE).

### screen.py
Pretty-printing utilities. 

## Non-technical remarks about solved sections
* `A WARNING`: Message from Cicada: "do not modify the book". This might be a hint that even spacing or graphics are meaningful. Also, an example of a simple linear modification of each rune by its value (`Atbash`).
* `WELCOME`: Vigenere cipher and use of previously seen words ("DIVINITY"), alongside `interrupters`. As of now, only the letter "F" is used for interrupters, which is meaningful when looking for cribs, as we can assume non-F ciphertext could not have been non-F plaintext.
* `SOME WISDOM`: Message from Cicada: "the idea of GP-sums is important". A `GP-sum` is the process of taking the primes associated with each rune and summing them up to get a value for a runic word. The reference to "MOBIUS" is interesting in terms of the Mobius function. Significance to the Euler Totient function and primes, that are obviously strongly connected.
* `A KOAN`: Encryption methods from previously solved pages could be combined (`Atbash` alongside `Caesar cipher` in this case). Additionally, basic repeating phrases and language style could be inferred ("A COAN", "AN INSTRUCTION", the fact that Cicada prefers to write down number English names ("FOUR") rather than as a number).
* `THE LOSS OF DIVINITY`: More potential keys to be used: "DIVINITY", "CIRCUMFERENCE", as well as the importance of the following three words combined in some manner: "CONSUMPTION", "PRESERVATION", "ADHERENCE". Also note the numbering appears after the English number name ("TWO").
* `A KOAN` (2): The notion that a key could be an English word with some occurences modified ("FIRFUMFERENFE").
* `AN INSTRUCTION`: Currently *unknown* but that square matrix was used back in 2013. Minor details: "KNOW THIS" is a potential crib.
* `AN END` (page 64): Cribbing (guessting plaintext is "AN END") is useful, walking backwards. The decryption could be a reference to the Totient function and primes as mentioned earlier, but a Totient function on a prime is simply that prime minus 1, so maybe the Totient function still needs to be used. The hash `36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4` is important.
* `Parable` (page 65): Repeating certain potential keys like "CIRCUMFERENCE" or "INSTAR".

