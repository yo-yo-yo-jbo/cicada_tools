import transformers

import sys
import os
import json

class LiberPrimus(object):
    """
        The Liber Primus book.
    """

    # Sections cache
    _SECTIONS = None

    @classmethod
    def get_all_sections(cls):
        """
            Gets all sections.
        """

        # Work with a cache
        if cls._SECTIONS is None:

            # Read the book section by section
            cls._SECTIONS = []
            sections_base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'liber_primus')
            for section_name in sorted(os.listdir(sections_base_path)):
                
                # Skip hidden items
                if section_name.startswith('.'):
                    continue

                # Look for "section.json" file
                config_path = os.path.join(sections_base_path, section_name, 'section.json')
                if not os.path.isfile(config_path):
                    continue

                # Load the section data
                with open(config_path, 'r') as fp:
                    section_data = json.load(fp)

                # Initialize all transformers
                section_transformers = []
                for transformer_data in section_data['transformers']:
                    transformer_type = transformer_data['type']
                    assert hasattr(sys.modules['transformers'], transformer_type), Exception(f'Transformer "{transformer_type}" not found')
                    transformer_params = dict([ (k, v) for (k, v) in transformer_data.items() if k != 'type' ])
                    section_transformers.append(getattr(sys.modules['transformers'], transformer_type)(**transformer_params))

                # Create the section object and add all pages
                nice_name = section_name[:]
                if '_' in nice_name:
                    nice_name = ' '.join(nice_name.split('_')[1:])
                section = Section(name=nice_name.title(), title=section_data['title'], transformers=section_transformers)
                for page_data in section_data['pages']:
                    section.add_page(Page(section=section, number=page_data.get('number', None), text=page_data['text']))

                # Append to the setions
                cls._SECTIONS.append(section)

        # Return from cache
        return cls._SECTIONS

class Page(object):
    """
        Represents a book page.
    """

    def __init__(self, section, text, number=None):
        """
            Creates an instance.
        """

        # Validations
        assert number is None or (isinstance(number, int) and number >= 0), Exception(f'Invalid number: {number}')

        # Save members
        self.section = section
        self.text = text
        self.number = number

class Section(object):
    """
        Represents a book section.
    """

    def __init__(self, name, title, transformers):
        """
            Creates an instance.
        """

        # Save members
        self.name = name
        self.title = title
        self.transformers = transformers
        self.pages = []

        # Cache
        self._all_text = None

    def get_all_text(self):
        """
            Get the entire section text.
        """

        # Return text from all pages from cache
        if self._all_text is None:
            self._all_text = '\n'.join([ page.text for page in self.pages ])
        return self._all_text

    def get_page_numbers(self):
        """
            Get the page numbers.
        """

        # Return all non-empty numbers
        return sorted([ page.number for page in self.pages if page.number is not None ])

    def add_page(self, page):
        """
            Adds a page.
        """

        # Invalidate cache
        self._all_text = None

        # Save a page
        self.pages.append(page)

