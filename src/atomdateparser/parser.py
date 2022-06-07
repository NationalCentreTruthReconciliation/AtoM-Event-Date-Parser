''' AtoM-specific date parsing.

AtoM CSV templates (specifically archival descriptions and accession) have three
columns for dates: eventDates, eventStartDates, and eventEndDates. The
EventDateParser class handles parsing the dates in each of those three columns
and returns clean, uniformly-formatted dates to be used to update each of those
columns.
'''
from typing import Union
import datetime
import re

from atomdateparser.handlers import *
from atomdateparser.stringutils import split_by, cardinality


SANITIZE_DATE = re.compile(
    r'(?i)^\s*[{\[\s]*(?:ca\.?|c\.|circa|between)?\s*'
    r'(?P<sanitized>.*?)'
    r'\s*\??\s*[}\]\s]*\s*$')


class EventDateParser:
    def __init__(self, unknown_date: str = 'Unknown date',
                 unknown_start_date: Union[str, datetime.date] = '1800-01-01',
                 unknown_end_date: Union[str, datetime.date] = '2010-01-01',
                 timid: bool = False, **dateparser_kwargs):

        self.dateparser_kwargs = dateparser_kwargs

        if isinstance(unknown_start_date, str):
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', unknown_start_date):
                raise ValueError((
                    'unknown_start_date "{}" does not match yyyy-mm-dd format'
                ).format(unknown_start_date))
            self.unknown_start_date = datetime.date(
                *[int(x) for x in unknown_start_date.split('-')]
            )
        else:
            self.unknown_start_date = unknown_start_date

        if isinstance(unknown_end_date, str):
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', unknown_end_date):
                raise ValueError((
                    'unknown_end_date "{}" does not match yyyy-mm-dd format'
                ).format(unknown_end_date))
            self.unknown_end_date = datetime.date(
                *[int(x) for x in unknown_end_date.split('-')]
            )
        else:
            self.unknown_end_date = unknown_end_date

        self.unknown_date = unknown_date
        self.str_unknown_start_date = str(unknown_start_date)
        self.str_unknown_end_date = str(unknown_end_date)
        if self.unknown_end_date < self.unknown_start_date:
            # Swap
            self.unknown_start_date, self.unknown_end_date =\
            self.unknown_end_date, self.unknown_start_date
            # Swap
            self.str_unknown_start_date, self.str_unknown_end_date =\
            self.str_unknown_end_date, self.str_unknown_start_date

        init_vars = (self.unknown_date, self.unknown_start_date, self.unknown_end_date)
        self.parser = UnknownDateHandler(*init_vars)
        final_parser = self.parser.set_next(YearRangeHandler(*init_vars))\
            .set_next(YearMonthDayHandler(*init_vars))\
            .set_next(YearMonthRangeHandler(*init_vars))\
            .set_next(YearMonthDayRangeHandler(*init_vars))\
            .set_next(ZeroMonthHandler(*init_vars))\
            .set_next(ZeroDayHandler(*init_vars))\
            .set_next(DecadeHandler(*init_vars))\
            .set_next(DecadeRangeHandler(*init_vars))\
            .set_next(YearHandler(*init_vars))\
            .set_next(SeasonHandler(*init_vars))\
            .set_next(MonthWordYearHandler(*init_vars))\
            .set_next(MonthWordDayYearHandler(*init_vars))\
            .set_next(DayMonthWordYearHandler(*init_vars))\
            .set_next(MonthWordDayYearRangeHandler(*init_vars))\
            .set_next(DateParserHandler(*init_vars, **dateparser_kwargs)) # Special case

        if not timid:
            final_parser.set_next(YearAnywhereInDateHandler(*init_vars))

    def parse_date(self, date: str) -> EventDate:
        ''' Get parsed date range, and a clean string representation of the date. May raise an
        UnkonwnDateFormat exception if the date could not be parsed.

        Args:
            date (str): The date string to parse

        Returns:
            (EventDate): An EventDate tuple. The date property contains the
            eventDate (a string), and the start and end properties contain the
            date range (as datetime.dates)
        '''
        try:
            return self.parser.handle(self._sanitize_date(date))
        except ValueError as exc:
            raise UnknownDateFormat(f'{exc} for {date}') from exc

    def _sanitize_date(self, date: str):
        if date is None:
            return ''
        return SANITIZE_DATE.match(date).group('sanitized')

    def parse_event_dates(self, event_date: str, start_date: str = None,
                          end_date: str = None) -> dict:
        ''' Parse dates and get well-formatted string dates for each date column.

        Args:
            event_date (str): A single eventDate, should not include a pipe character
            start_date (str): An optional single eventStartDate, should not include a pipe character
            end_date (str): An optional single eventEndDate, should not include a pipe character

        Returns:
            (dict): A fixed-up version of the eventDates, eventStartDates, and eventEndDates
                columns. Each fixed up column is in a similarly-named key of the dictionary, e.g.,
                the fixed eventDates are in the eventDates key.
        '''
        event_date = event_date.strip() if event_date else ''
        start_date = start_date.strip() if start_date else ''
        end_date = end_date.strip() if end_date else ''
        all_dates = (event_date, start_date, end_date)
        if any([cardinality(d) > 1 for d in all_dates]):
            raise ValueError('parse_event_dates does not accept pipe-delimited date cells')
        trivial_result = self._handle_trivial_cases(all_dates)
        if trivial_result:
            return trivial_result
        return self._parse_date_group(event_date, start_date, end_date)

    def _handle_trivial_cases(self, dates):
        if not any(dates) or dates[0] == self.unknown_date:
            return {
                'eventDates': self.unknown_date,
                'eventStartDates': self.str_unknown_start_date,
                'eventEndDates': self.str_unknown_end_date,
            }
        if all([x.lower() in ('', 'null') for x in dates]):
            return {
                'eventDates': 'NULL',
                'eventStartDates': 'NULL',
                'eventEndDates': 'NULL',
            }
        return None

    def _parse_date_group(self, event_date: str, event_start_date: str, event_end_date: str):
        fixed_event_dates = set() # Set of strings
        all_start_end_dates = set() # Set of datetime.date objects

        for date in split_by(event_date, ' and '):
            parsed = self.parse_date(date)
            fixed_event_dates.add(parsed.date)
            all_start_end_dates.add(parsed.start)
            all_start_end_dates.add(parsed.end)

        curr_min_date = self.get_min_date_avoid_reserved_dates(all_start_end_dates)
        curr_max_date = self.get_max_date_avoid_reserved_dates(all_start_end_dates)
        curr_date_unknown = self.date_is_unknown(curr_min_date, curr_max_date)

        start_end_range = self._get_start_end_date_range(event_start_date, event_end_date)
        start_end_min = start_end_range[0] if start_end_range else curr_min_date
        start_end_max = start_end_range[1] if start_end_range else curr_max_date
        start_end_unknown = self.date_is_unknown(start_end_min, start_end_max)

        if curr_date_unknown and not start_end_unknown:
            curr_min_date = start_end_min
            curr_max_date = start_end_max

        # eventStartDates or eventEndDates fell outside of parsed eventDates
        if start_end_min < curr_min_date or start_end_max > curr_max_date:
            new_start_date = min(curr_min_date, start_end_min)
            new_end_date = max(curr_max_date, start_end_max)
            date_range = '{} - {}'.format(str(new_start_date), str(new_end_date))
            try:
                handler = YearMonthDayRangeHandler(None, None, None)
                parsed = handler.handle(date_range)
                new_event_dates = parsed.date
            except UnknownDateFormat:
                new_event_dates = date_range

        # eventDates encompassed eventStartDates and eventEndDates
        else:
            new_event_dates = self._get_well_formatted_event_dates(
                fixed_event_dates, curr_min_date, curr_max_date
            )
            new_start_date = curr_min_date
            new_end_date = curr_max_date

        return {
            'eventDates': new_event_dates,
            'eventStartDates': new_start_date.strftime(r'%Y-%m-%d'),
            'eventEndDates': new_end_date.strftime(r'%Y-%m-%d'),
        }

    def date_is_unknown(self, start_date, end_date):
        return start_date == self.unknown_start_date and end_date == self.unknown_end_date

    def get_min_date_avoid_reserved_dates(self, dates):
        ''' Get the earliest date in a set, avoiding returning unknown dates whenever possible '''
        return self._get_min_max_date_avoid_reserved(min, self.unknown_start_date, dates)

    def get_max_date_avoid_reserved_dates(self, dates):
        ''' Get the latest date in a set, avoiding returning unknown dates whenever possible '''
        return self._get_min_max_date_avoid_reserved(max, self.unknown_end_date, dates)

    def _get_min_max_date_avoid_reserved(self, max_min_function, default, dates):
        if not dates:
            return default
        if len(dates) == 1:
            return next(iter(dates))
        if len(dates) > 1:
            reserved = (self.unknown_start_date, self.unknown_end_date)
            no_reserved_dates = list(filter(lambda d: d not in reserved, dates))
            return max_min_function(no_reserved_dates) if no_reserved_dates else default
        return default

    def _get_start_end_date_range(self, event_start_date: str, event_end_date: str):
        ''' Get the earliest and latest dates represented by the start and end dates. Does not add
        dates in if they are unknown.

        Args:
            event_start_date (str): A single eventStartDate
            event_end_date (str): A single eventEndDate

        Returns:
            (tuple): A tuple containing the earliest date and the latest date, in that order. May be
                None if no dates were found or could be parsed.
        '''
        start_end_dates = set()
        all_dates = set([event_start_date, event_end_date])

        if self.str_unknown_start_date in all_dates and self.str_unknown_end_date in all_dates:
            return None

        for date in all_dates:
            try:
                parsed = self.parse_date(date)
                if self.date_is_unknown(parsed.start, parsed.end):
                    continue
                start_end_dates.add(parsed.start)
                start_end_dates.add(parsed.end)
            except UnknownDateFormat:
                pass

        if not start_end_dates:
            return None

        min_date = min(start_end_dates)
        max_date = max(start_end_dates)

        if self.date_is_unknown(min_date, max_date):
            return None

        return (min_date, max_date)

    def _get_well_formatted_event_dates(self, event_dates: set, min_date: datetime.date,
                                        max_date: datetime.date):
        ''' Creates a clean string representation of the event_dates set.

        Returns a string without "NULL" or unknown_date if there are other valid dates in
        event_dates. If there are no known dates in event_dates, the returned string will be the
        range of the min_date and max_date. If the min_date and max_date are the reserved start and
        end dates, the returned string will be the unknown date.

        Args:
            event_dates (set): Set of eventDate strings
            min_date (datetime.date): The earliest date represented by all the eventDates
            max_date (datetime.date): The latest date represented by all eventDates

        Returns:
            str: A fixed up version of the event_dates, joined by ' and ' if there are multiple
                dates.
        '''
        new_event_dates = ''
        non_null_event_dates = {x for x in event_dates if x not in ('NULL', self.unknown_date)}

        if non_null_event_dates:
            new_event_dates = ' and '.join(sorted(list(non_null_event_dates)))
        elif self.date_is_unknown(min_date, max_date):
            new_event_dates = self.unknown_date
        elif min_date.year == max_date.year:
            new_event_dates = str(min_date.year)
        else:
            new_event_dates = f'{min_date.year}-{max_date.year}'
        return new_event_dates
