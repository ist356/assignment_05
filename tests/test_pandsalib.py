import pytest 
import code.pandaslib as pl


def test_should_pass():
    print("\nAlways True!")
    assert True


def test_clean_currency():
    tests = [ 
        {'expected': 1000.0, 'input': '$1,000'},
        {'expected': 10000.01, 'input': '10,000.01'},
        {'expected': 10_000_000.99, 'input': '10,000,000.99'},
    ]
    for t in tests:
        print(f"\nTESTING: clean_curency({t['input']}) == {t['expected']}")
        assert pl.clean_currency(t['input']) == t['expected']


def test_extract_year_mdy():
    tests = [
        {'expected': 2021, 'input': '12/31/2021 23:59:59'},
        {'expected': 2023, 'input': '2/16/2023 19:14:37'},
        {'expected': 2019, 'input': '1/1/2019 12:00:00'},
    ]
    for t in tests:
        print(f"\nTESTING: extract_year_mdy({t['input']}) == {t['expected']}")
        assert pl.extract_year_mdy(t['input']) == t['expected']


def test_clean_country_usa():
    test = [
        {'expected': 'United States', 'input': 'United States of America'},
        {'expected': 'United States', 'input': 'USA'},
        {'expected': 'United States', 'input': 'US'},
        {'expected': 'United States', 'input': 'U.S.'},
        {'expected': 'United States', 'input': 'United States'},
    ]
    for t in test:
        print(f"\nTESTING: clean_country_usa({t['input']}) == {t['expected']}")
        assert pl.clean_country_usa(t['input']) == t['expected']
    
