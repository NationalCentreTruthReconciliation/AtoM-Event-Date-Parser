import pytest

from atomdateparser.parser import EventDateParser

class TestParseDatesNoStartOrEndDates_IgnoreEventActors:
    @pytest.mark.parametrize('event_dates', [
        ('n.d.'),
        ('[n.d.]'),
        ('0000-00-00'),
        ('0000-99-00'),
        ('0000-00-12'),
        ('19-?'),
        ('Unknown'),
        ('NO DATE'),
        ('Undated'),
        (''),
    ])
    def test_no_date(self, event_dates):
        parser = EventDateParser(unknown_date='Unknown date', unknown_start_date='1800-01-01',
                                 unknown_end_date='2010-01-01')
        parsed = parser.parse_event_dates(event_dates)
        assert parsed['eventDates'] == 'Unknown date'
        assert parsed['eventStartDates'] == '1800-01-01'
        assert parsed['eventEndDates'] == '2010-01-01'

    def test_null_date(self):
        parser = EventDateParser()
        parsed = parser.parse_event_dates('NULL')
        assert parsed['eventDates'] == 'NULL'
        assert parsed['eventStartDates'] == 'NULL'
        assert parsed['eventEndDates'] == 'NULL'

    @pytest.mark.parametrize('event_dates,expected_event_dates,expected_early,expected_late', [
        ('2000-01-01', '2000-01-01', '2000-01-01', '2000-01-01'),
        ('2000/02/02', '2000-02-02', '2000-02-02', '2000-02-02'),
        ('2000.03.03', '2000-03-03', '2000-03-03', '2000-03-03'),
    ])
    def test_yyyy_mm_dd(self, event_dates, expected_event_dates, expected_early, expected_late):
        parser = EventDateParser()
        parsed = parser.parse_event_dates(event_dates)
        assert parsed['eventDates'] == expected_event_dates
        assert parsed['eventStartDates'] == expected_early
        assert parsed['eventEndDates'] == expected_late

    @pytest.mark.parametrize('event_dates,expected_event_dates,expected_early,expected_late', [
        ('01-01-2000', '2000-01-01', '2000-01-01', '2000-01-01'),
        ('02/02/2000', '2000-02-02', '2000-02-02', '2000-02-02'),
        ('03.03.2000', '2000-03-03', '2000-03-03', '2000-03-03'),
        ('12-13-2000', '2000-12-13', '2000-12-13', '2000-12-13'),
        ('05-01-2000', '2000-05-01', '2000-05-01', '2000-05-01'),
        ('15-01-2000', '2000-01-15', '2000-01-15', '2000-01-15'),
    ])
    def test_month_day_before_year(self, event_dates, expected_event_dates, expected_early, expected_late):
        parser = EventDateParser()
        parsed = parser.parse_event_dates(event_dates)
        assert parsed['eventDates'] == expected_event_dates
        assert parsed['eventStartDates'] == expected_early
        assert parsed['eventEndDates'] == expected_late

    @pytest.mark.parametrize('event_dates,expected_event_dates,expected_early,expected_late', [
        ('2000', '2000', '2000-01-01', '2000-12-31'),
        ('[CA 2000]', '2000', '2000-01-01', '2000-12-31'),
        ('[c. 2000]', '2000', '2000-01-01', '2000-12-31'),
        ('Circa 2000?', '2000', '2000-01-01', '2000-12-31'),
        ('[ 2000? ]', '2000', '2000-01-01', '2000-12-31'),
        ('2000-00-00', '2000', '2000-01-01', '2000-12-31'),
    ])
    def test_handle_year(self, event_dates, expected_event_dates, expected_early, expected_late):
        parser = EventDateParser()
        parsed = parser.parse_event_dates(event_dates)
        assert parsed['eventDates'] == expected_event_dates
        assert parsed['eventStartDates'] == expected_early
        assert parsed['eventEndDates'] == expected_late

    @pytest.mark.parametrize('event_dates,expected_event_dates,expected_early,expected_late', [
        ('2000-2001', '2000 - 2001', '2000-01-01', '2001-12-31'),
        ('[Between 1996 and 1998]', '1996 and 1998', '1996-01-01', '1998-12-31'),
        ('1995 - 1992', '1992 - 1995', '1992-01-01', '1995-12-31'),
        ('[1993-00-00 - 1994]', '1993 - 1994', '1993-01-01', '1994-12-31'),
        ('1901-20', '1901 - 1920', '1901-01-01', '1920-12-31'),
        ('[1919 - 21]', '1919 - 1921', '1919-01-01', '1921-12-31'),
    ])
    def test_handle_year_range(self, event_dates, expected_event_dates, expected_early, expected_late):
        parser = EventDateParser()
        parsed = parser.parse_event_dates(event_dates)
        assert parsed['eventDates'] == expected_event_dates
        assert parsed['eventStartDates'] == expected_early
        assert parsed['eventEndDates'] == expected_late

    @pytest.mark.parametrize('event_dates,expected_event_dates,expected_early,expected_late', [
        ('2000/01/00 - 2001.03-00', 'January 2000 - March 2001', '2000-01-01', '2001-03-31'),
        ('2000.02.00-2000.04.00', 'February 2000 - April 2000', '2000-02-01', '2000-04-30'),
        ('[Circa 2000/02/00 - 2000/07/00 ? ]', 'February 2000 - July 2000', '2000-02-01', '2000-07-31'),
    ])
    def test_handle_year_month_range(self, event_dates, expected_event_dates, expected_early, expected_late):
        parser = EventDateParser()
        parsed = parser.parse_event_dates(event_dates)
        assert parsed['eventDates'] == expected_event_dates
        assert parsed['eventStartDates'] == expected_early
        assert parsed['eventEndDates'] == expected_late

    @pytest.mark.parametrize('event_dates,expected_event_dates,expected_early,expected_late', [
        ('January 1979', 'January 1979', '1979-01-01', '1979-01-31'),
        ('Jan. 1979', 'January 1979', '1979-01-01', '1979-01-31'),
        ('Jan 1979', 'January 1979', '1979-01-01', '1979-01-31'),
        ('February 1980', 'February 1980', '1980-02-01', '1980-02-29'), # Leap Year
        ('Feb. 1980', 'February 1980', '1980-02-01', '1980-02-29'), # Leap Year
        ('Feb 1980', 'February 1980', '1980-02-01', '1980-02-29'), # Leap Year
        ('March 1981', 'March 1981', '1981-03-01', '1981-03-31'),
        ('Mar. 1981', 'March 1981', '1981-03-01', '1981-03-31'),
        ('Mar 1981', 'March 1981', '1981-03-01', '1981-03-31'),
        ('April 1982', 'April 1982', '1982-04-01', '1982-04-30'),
        ('Apr. 1982', 'April 1982', '1982-04-01', '1982-04-30'),
        ('Apr 1982', 'April 1982', '1982-04-01', '1982-04-30'),
        ('May 1983', 'May 1983', '1983-05-01', '1983-05-31'),
        ('May. 1983', 'May 1983', '1983-05-01', '1983-05-31'),
    ])
    def test_handle_month_word_year(self, event_dates, expected_event_dates, expected_early, expected_late):
        parser = EventDateParser()
        parsed = parser.parse_event_dates(event_dates)
        assert parsed['eventDates'] == expected_event_dates
        assert parsed['eventStartDates'] == expected_early
        assert parsed['eventEndDates'] == expected_late

class TestParseWithStartEndDatesPresent_IgnoreEventActors:
    @pytest.mark.parametrize('event_dates,event_start_dates,event_end_dates,expected', [
        ('', '1800-01-01', '2000-01-01', '1800 - 2000'),
        ('NULL', '1901-12-01', '2010-01-01', '1901 - 2010'),
        ('', '2000-02-02', '2010-01-01', '2000 - 2010'),
        ('No date', '2020-06-13', '1999-01-01', '1999 - 2020'),
        ('', '1906-12-21', 'NULL', '1906'),
        ('', '1906-12-21', '', '1906'),
        ('UNKNOWN', 'NULL', '1907-04-19', '1907'),
        ('UNKNOWN', '', '1907-04-19', '1907'),
    ])
    def test_handle_no_event_dates(self, event_dates, event_start_dates, event_end_dates, expected):
        parser = EventDateParser()
        parsed = parser.parse_event_dates(event_dates, event_start_dates, event_end_dates)
        assert parsed['eventDates'] == expected

    @pytest.mark.parametrize('event_dates,start_dates,end_dates,ed_expect,start_expect,end_expect', [
        # End date outside
        ('March 2001', '2000-03-01', '2002-02-02', 'March 1, 2000 - February 2, 2002', '2000-03-01', '2002-02-02'),
        # Start date outside
        ('March 2001', '2001-02-15', '2001-03-31', 'February 15, 2001 - March 31, 2001', '2001-02-15', '2001-03-31'),
        # Both outside
        ('March 2001', '1999-02-15', '2001-04-04', 'February 15, 1999 - April 4, 2001', '1999-02-15', '2001-04-04'),
    ])
    def test_start_end_dates_outside_of_event_dates(self, event_dates, start_dates, end_dates,
                                                    ed_expect, start_expect, end_expect):
        parser = EventDateParser()
        parsed = parser.parse_event_dates(event_dates, start_dates, end_dates)
        assert parsed['eventDates'] == ed_expect
        assert parsed['eventStartDates'] == start_expect
        assert parsed['eventEndDates'] == end_expect

    def test_start_end_dates_between_event_dates(self):
        parser = EventDateParser()
        parsed = parser.parse_event_dates('2001-03-00', '2001-03-15', '2001-03-18')
        assert parsed['eventDates'] == 'March 2001'
        assert parsed['eventStartDates'] == '2001-03-01'
        assert parsed['eventEndDates'] == '2001-03-31'

    @pytest.mark.parametrize('event_dates,ed_expect,start_expect,end_expect', [
        ('March 2001', 'March 2001', '2001-03-01', '2001-03-31'),
        ('1984-02-03', '1984-02-03', '1984-02-03', '1984-02-03'),
        ('May 17, 2009', '2009-05-17', '2009-05-17', '2009-05-17'),
    ])
    def test_event_dates_preferred_unknown_start_end(self, event_dates, ed_expect,
                                                     start_expect, end_expect):
        parser = EventDateParser()
        parsed = parser.parse_event_dates(event_dates, '1800-01-01', '2010-01-01')
        assert parsed['eventDates'] == ed_expect
        assert parsed['eventStartDates'] == start_expect
        assert parsed['eventEndDates'] == end_expect
