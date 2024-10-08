import pandas as pd
import numpy as np
import streamlit as st
import pandaslib as pl

#TODO Write your extraction code here

# Read google sheet csv file 
survey = pd.read_csv('https://docs.google.com/spreadsheets/d/1IPS5dBSGtwYVbjsfbaMCYIWnOuRmJcbequohNxCyGVw/export?resourcekey=&gid=1625408792&format=csv')
# extract year from date # todo refactor this to a function
survey['year'] = survey['Timestamp'].apply(pl.extract_year_mdy)
# save the survey data to a csv file in the cache
survey.to_csv('cache/survey.csv', index=False)

# get each unique year in the survey data
years = survey['year'].unique()

# for each year
for year in years:
    # get the cost of living data for that year
    col_year = pd.read_html(f"https://www.numbeo.com/cost-of-living/rankings.jsp?title={year}&displayColumn=0")
    # this is the correct table
    col_year = col_year[1]
    # add the year column
    col_year['year'] = year
    # save the data to a csv file in the cache
    col_year.to_csv(f'cache/col_{year}.csv', index=False)


# Read in states data table
url = "https://docs.google.com/spreadsheets/d/14wvnQygIX1eCVo7H5B7a96W1v5VCg6Q9yeRoESF6epw/export?format=csv"
state_table = pd.read_csv(url)
state_table.to_csv('cache/states.csv', index=False)