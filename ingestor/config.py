# Constants for ingestor app

BENFORD_DISTRIBUTION = 30
BENFORD_TOLERANCE = 2.5

# To add support for a new separator, add a tuple of this format: ('display_name', 'separator_character')
SEP_CHOICES = (('comma', ','),
               ('tab', '\t'),
               ('pipe', '|'))

SUPPORTED_SEPARATORS = [x[0] for x in SEP_CHOICES]
