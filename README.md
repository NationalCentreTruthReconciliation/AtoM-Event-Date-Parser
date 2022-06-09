# AtoM Event Date Parser

Date parser for eventDates, eventStartDates, eventEndDates in [AtoM](https://accesstomemory.org) CSV templates.

## Installation

Install with pip form [PyPi](https://pypi.org/project/atomdateparser/):

```
pip install atomdateparser
```

## Usage

Use the `EventDateParser` class to parse dates. When possible, the Event date parser will try to construct a start and an end date for the given date, as opposed to parsing a single date for the specified date, as most date parsers do.

```python
from atomdateparser.parser import EventDateParser

parser = EventDateParser(
    unknown_date='Date Unknown',
    unknown_start_date='2000-01-01',
    unknown_end_date='2010-01-01',
    timid=True,
    dateparser_kwargs={
        'languages': ['en', 'fr'],
        'settings': {
            'PREFER_DAY_OF_MONTH': 'first',
            'PREFER_DATES_FROM': 'past',
        }
    },
)

parsed = parser.parse_event_dates('Circa 2001')

''' Returns:
{
    'eventDates': '2001',
    'eventStartDates': '2001-01-01',
    'eventEndDates': '2001-12-31',
}
'''
```

### EventDateParser Options

- **unknown_date**: The text to return for eventDates when the date is not known
- **unknown_start_date**: The date to return for eventStartDates when the date is not known
- **unknown_end_date**: The date to return for eventEndDates when the date is not known
- **timid**: `True` if an exception should be thrown if the *entire* date cannot be parsed, or `False` if no date could be found, and no year could be found from the date being parsed. Note that if timid is `False`, some date information may be lost.
- **dateparser_kwargs**: The [dateparser](https://pypi.org/project/dateparser/) library is used as a fallback method to parse the input date in the event that none of the other date parsing handlers are able to parse the date. Controlling dateparser is done using this keyword argument. Keyword arguments are passed to `dateparser.parse()`. For more information, visit [dateparser on GitHub](https://github.com/scrapinghub/dateparser) or visit the [dateparser settings docs](https://dateparser.readthedocs.io/en/latest/settings.html).
