from datetime import datetime


def clean_currency(item: str) -> float:    
    return float(str(item).replace('$', '').replace(',', ''))

def extract_year_mdy(timestamp):
    return datetime.strptime(timestamp, '%m/%d/%Y %H:%M:%S').year

def clean_country_usa(item: str) ->str:
    '''
    This function should replace any combination of 'United States of America', USA' etc.
    with 'United States'
    '''
    possibilities = [
        'united states of america', 'usa', 'us', 'united states', 'u.s.'
    ]
    if item.strip().lower() in possibilities:
        return 'United States'
    else:
        return item


if __name__=='__main__':
    assert clean_currency('$1,000') == 1000.0
    assert clean_currency('10,000.01') == 10000.01

    assert extract_year_mdy('12/31/2021 23:59:59') == 2021
    assert extract_year_mdy('2/16/2023 19:14:37') == 2023

    assert clean_country_usa('United States of America') == 'United States'
    assert clean_country_usa('USA') == 'United States'
    assert clean_country_usa('US') == 'United States'
    assert clean_country_usa('United States') == 'United States'    