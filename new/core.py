import string

# Runes and latin
RUNES = [ 'ᚠ', 'ᚢ', 'ᚦ', 'ᚩ', 'ᚱ', 'ᚳ', 'ᚷ', 'ᚹ', 'ᚻ', 'ᚾ', 'ᛁ', 'ᛄ', 'ᛇ', 'ᛈ', 'ᛉ', 'ᛋ', 'ᛏ', 'ᛒ', 'ᛖ', 'ᛗ', 'ᛚ', 'ᛝ', 'ᛟ', 'ᛞ', 'ᚪ', 'ᚫ', 'ᚣ', 'ᛡ', 'ᛠ' ]
LATIN = [ 'F', 'V', 'TH', 'O', 'R', 'C', 'G', 'W', 'H', 'N', 'I', 'J', 'EO', 'P', 'X', 'S', 'T', 'B', 'E', 'M', 'L', 'NG', 'OE', 'D', 'A', 'AE', 'Y', 'IA', 'EA' ]
PUNCT = { '.': '.\n', '-': ' ', '%': '\n\n', '/': '', '&' : '\n', '\n' : '' }
GP_PRIMES = [ 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109 ]

class ProcessedText(object):

    def __init__(self, rune_text):
        """
        """

        # Save the original text
        self._orig = rune_text[:]

        # Save processes runes
        self._processed_runes = [ c for c in self._orig if c in RUNES ]

        # Currently not marked as unsolved
        self._is_unsolved = False

    @staticmethod
    def get_gp_sum(runes):
        """
            Get the Gematria primes sum.
        """

        # Performs the sum
        result = 0
        for rune in runes:
            if rune in RUNES:
                result += GP_PRIMES[RUNES.index(rune)]
        return result

    def set_unsolved(self):
        """
            Sets as unsolved.
        """

        # Mark
        self._is_unsolved = True

    def is_unsolved(self):
        """
            Indicate if text is still unsolved.
        """

        # Indicate
        return self._is_unsolved

    def get_runes(self):
        """
            Gets the runes.
        """

        # Returns the processed runes
        return self._processed_runes[:]
    
    def set_runes(self, new_runes):
        """
            Save the runes.
        """

        # Save processed runes
        assert len(new_runes) == len(self._processed_runes), Exception(f'Length mismatch between new runes ({len(new_runes)}) and old runes ({len(self._processed_runes)})')
        self._processed_runes = new_runes[:]

    def get_rune_words(self, remove_periods=True):
        """
            Get Runic words.
        """

        # Get the Runic text
        text = self.get_rune_text()
        if remove_periods:
            text = text.replace('.', ' ')
        else:
            text = text.replace('.', ' . ')
        return [ word for word in ''.join([ c for c in text if c in RUNES or c in (' ', '.') ]).split(' ') if len(word) > 0 ]

    def get_first_non_wordlist_word_index(self, wordlist):
        """
            Finds the first Runic word that is not in the given wordlist.
        """

        # Iterate all words
        word_index = -1
        for word in self.get_rune_words():
            word_index += 1
            if word not in wordlist:
                return word_index
        
        # Indicate all words are in the wordlist by just returning the number of words plus one
        return word_index + 1


    def get_rune_text(self, punct_translation=True):
        """
            Gets the rune text.
        """

        # Replace runes from the original with the newly processed runes
        result = ''
        rune_index = 0
        for c in self._orig:
            if c in RUNES:
                result += self._processed_runes[rune_index]
                rune_index += 1
            else:
                if punct_translation and c in PUNCT:
                    result += PUNCT[c]
                else:
                    result += c

        # Return result
        return result

    def to_latin(self):
        """
            Translates to Latin.
        """

        # Translate to Latin unless unsolved
        if self._is_unsolved:
            return '<UNSOLVED>'
        text = self.get_rune_text()
        result = []
        for c in text:
            if c in RUNES:
                result.append(LATIN[RUNES.index(c)])
            else:
                result.append(c)
        return ''.join(result)

    @staticmethod
    def _get_ioc(text, alphabet):
        """
            1-gram IoC calculation.
        """

        # Take only alphabet letters
        instance = [ c for c in text if c in alphabet ]

        # Ignore zero-length
        if len(instance) == 0 or len(alphabet) == 0:
            return 0.0

        # Calculate the IoC
        s = sum([ instance.count(letter) * (instance.count(letter) - 1) for letter in alphabet ])
        d = len(instance) * (len(instance) - 1) / len(alphabet)
        return s / d
 
    def get_rune_ioc(self):
        """
            Returns the IoC for the runes.
        """

        # Calculate IoC
        return self.__class__._get_ioc(self._processed_runes, RUNES)

    
    def get_latin_ioc(self):
        """
            Returns the latin IoC.
        """

        return self.__class__._get_ioc(self.to_latin(), string.ascii_uppercase)


