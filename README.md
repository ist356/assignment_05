# IST356 Assignment 04 (assignment_04)

## Meta

### Learning Objectives

This assignment you will use pandas to build a data pipeline. 

### Assignment Layout

The each assignment will have a common layout.

- `code` folder contains our code / application. This is where you will create files and write code.
- `code/solution` folder contains the solution to the assignment, for reference.
- `data` data files folder
- `tests` folder contains code to test our application
- `requirements.txt` contains the packages we need to `pip install` to execute the application code
- `readme.md` contains these instructions
- `.vscode` folder contains VS Code setup configurations for running / debugging the application and tests.
- `reflection.md` is where you submit your reflection, comments on what you learned, things that confuse you, etc.

### Prerequisites 

Before starting this assignment you must:

Install the assignemnt python requirements:

1. From VS Code, open a terminal: Menu => Terminal => New Terminal
2. In the terminal, type and enter: `pip install -r requirements.txt`


### Running Tests

There is some code and tests already working in this assignment. These are sanity checks to ensure VS Code is configured properly.

1. Open **Testing** in the activity bar: Menu => View => Testing
2. You'll need to install the testing tools. Choose **pytest**
3. Open the **>** by clicking on it next to **assignment_04**. Keep clicking on **>** until you see **test_should_pass** in the **test_assignment.py**
4. Click the Play button `|>` next to **test_should_pass** to execute the test. 
5. A green check means the test code ran and the test has passed.
6. A red X means the test code ran but the test has failed. When a test fails you will be given an error message and stack trace with line numbers.

## Assignment: https://www.askamanager.org/

[https://www.askamanager.org/](https://www.askamanager.org/) has a salary survey its members complete. We will use this data to build out a data pipeline.

Survey is here: [https://www.askamanager.org/2021/04/how-much-money-do-you-make-4.html](https://www.askamanager.org/2021/04/how-much-money-do-you-make-4.html) They make the data publically available.

You can view the data here: [https://docs.google.com/spreadsheets/d/1IPS5dBSGtwYVbjsfbaMCYIWnOuRmJcbequohNxCyGVw/edit?resourcekey=&gid=1625408792](https://docs.google.com/spreadsheets/d/1IPS5dBSGtwYVbjsfbaMCYIWnOuRmJcbequohNxCyGVw/edit?resourcekey=&gid=1625408792)

You can download the data with `pd.read_csv` using this version of the URL:
[https://docs.google.com/spreadsheets/d/1IPS5dBSGtwYVbjsfbaMCYIWnOuRmJcbequohNxCyGVw/export?resourcekey=&gid=1625408792&format=csv](https://docs.google.com/spreadsheets/d/1IPS5dBSGtwYVbjsfbaMCYIWnOuRmJcbequohNxCyGVw/export?resourcekey=&gid=1625408792&format=csv)

You will need a US state name to abbreviation lookup table, which you can build here:
[https://docs.google.com/spreadsheets/d/14wvnQygIX1eCVo7H5B7a96W1v5VCg6Q9yeRoESF6epw/export?format=csv](https://docs.google.com/spreadsheets/d/14wvnQygIX1eCVo7H5B7a96W1v5VCg6Q9yeRoESF6epw/export?format=csv)


### The Job!

You have been hired by askamanager.org to produce two specific reports from their data:

1. a cross tabulation of US city / state of employment (row), to the highest degree obtained (col). At ther intersection for example: Boise, ID and High School should be the average annual salary as adjusted for cost of living in that city. 

2. Similar to the first report but by age demographic in the column.

They need the reports on an Amazon S3 bucket in `csv` format so they can display the data in their dashboarding Application.

### The Process

This job is best suited for the classic Extract-Transform-Load, or ETL pipeline. You can build data pipelines without using the ETL approach, but using this method breaks them up logically and makes them more resilient to change.

`extract.py`

In the extract phase you pull your data from the internet and store it locally for further processing. This way you are not constantly accessing the internet and scraping data more than you need to. This also decouples the transformation logic from the logic that fetches the data. This way if the source data changes we don't need to re-implement the transformations. 

- For each file you extract save it in `.csv` format with a header to the `cache` folder. The basic process is to read the file, add lineage, then write as a `.csv` to the `cache` folder. 
- Extract the states with codes google sheet. Save as `cache/states.csv`
- Extract the survey google sheet, and engineer a `year` column from the `Timestamp` using the `extract_year_mdy` function. Then save as `cache/survey.csv`
- For each unique year in the surveys: extract the cost of living for that year from the website, engineer a `year` column for that year, then save as `cache/col_{year}.csv` for example for `2024` it would be `cache/col_2024.csv`

`transform.py`

The bulk of the work is done in the transform process. Here we read our data from the cache back into pandas. From there we will clean the data, engineer new columns, join datasets together, etc all on route to producing a dataset from which we can create the reports. In the final transformation step, we write the reports back to the cache. 


First load the data from the cache:

- Load the states and survey data from the cache into dataframes.
- For each year in the surey data, load the cost of living data from the cache into a dataframe, then combine all the dataframes into a single cost of living (COL) dataframe

Next, we want to join the survey data to its cost of living data, by matching the city from the COL dataframe example: "Seattle, WA, United States" to the survey data. Before we can do that we need to clean up the survey data, and engineer a column similar to the example:

- First, clean the entry under "Which country do you work in?" so that all US countries say "United States" use the `clean_country_usa` function here and generate a new column `_country`
- Next under the "If you're in the U.S., what state do you work in?" column we need to convert the states into state codes Example: "New York => NY" to do this, join the states dataframe to the survey dataframe. User and inner join to drop non-matches. Call the new dataframe `survey_states_combined`
- Engineer a new column consisting of the city, a comma, the 2-character state abbreviation, another comma and `_country` For example: "Syracuse, NY, United States". name this column `_full_city`
- create the dataframe `combined` by matching the `survey_states_combined` to cost of living data matching on the `year` and `_full_city` columns

Finally we want to normalize each annual salary based on cost of living. How do you do this? A COL 90 means the cost of living is 90% of the average, so $100,000 in a COL city of 90 is the equivalent buying power of(100/90) * $100,000 ==  $111,111.11 

- Clean the salary column so that its a float. use `clean_currency`. generate a new column `__annual_salary_cleaned`
- generate a column `_annual_salary_adjusted` based on this formula. 

At this point you have engineerd the dataset required to produce the necessary reports.

- Save the engineered dataset to the cache `survey_dataset.csv`
- create the first report to show a pivot table of the the average `_annual_salary_adjusted` with `_full_city` in the row and Age band (How old are you?) in the column. Save this back to the cache as `annual_salary_adjusted_by_location_and_age.csv`
- create a similar report but show highest level of education in the column. Save this back to the cache as `annual_salary_adjusted_by_location_and_education.csv`


`load.py`

Much of the load process has been written for you. Its not the point of the exercise, the plan is to expose you to something new,m course. 

- save the transofrmations to minio AWS S3 compatible object storage you can check on
https://play.min.io

  URL       : https://play.min.io
  AccessKey : Q3AM3UQ867SPQQA43P2F
  SecretKey : zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG


It consists of 3 inputs:

- upload a file in Excel (XLSX), Comma-Separared, with Header (CSV), or Row-Oriented Json (JSON) into a dataframe
- select which columns to display from the dataframe
- build a fiter on the dataframe based on a text column and one of the values in the column.

And 2 outputs:

- the dataframe with column / row filters applied.
- the describe of the dataframe (to see statistics for the numerical columns)

**NOTE** There are sample files to load in the `data` folder.

## Advice

`pandaslib.py`

start by writing the functions in this file. They are ordered from easiest to most difficult.

- Function definitions with type hints and doc strings have been written for you. just complete the function body.
- Use the pytest tests to ensure your functions are correct
- The tests will not debug, so write code under the `if __name__=='__main__'` section to debug it that way.

`unibrow.py`

- use streamlit widgets to accept file browser input
- for the column multi-select, start with all columns selected
- a toggle to ask to include a filter, if enabled...
- You need two drop down widgets for the filter: object column names and  unique values in that column
- display the dataframe filtered by rows / columns
- descrived the dataframe (again the one filtered by row/columns)

## Commit Requirements

This assignment requires a minimum of 2 git commits. One suggestion is to commit after you complete a coding session (whether your code works or not.) At minimum you should commit after you complete `pandaslib.py` then again after `unibrow.py` 

## Turning it in

- Make sure tests pass and code works as expected
- Write your reflection in `reflection.md`
- Commit your changes: VS Code -> menu -> View -> Source Control -> Enter Commit message -> Click "Commit"
- Push your changes: VS Code -> menu -> View -> Source Control -> Click "Sync Changes"

## Grading 

🤖 Beep, Boop. This assignment is bot-graded! When you push your code to GitHub, my graderbot is notified there is something to grade. The bot then takes the following actions:

1. Your assignment repository is cloned from Github
2. The bot checks your code and commits according to guidelines outlined in `assignment-criteria.json` (it runs tests, checking code correctness, etc.)
3. The bot reads your `reflection.md` and provides areas for improvement (based on the instructions in the file).
4. A grade is assigned by the bot. Feedback is generated including justification for the grade given.
5. The grade and feedback are posted to Blackboard.

You are welcome to review the bot's feedback and improve your submission as often as you like.

**NOTE: ** Consider this an experiment in the future of education. The graderbot is an AI teaching assistant. Like a human grader, it will make mistakes. Please feel free to question the bots' feedback! Do not feel as if you should gamify the bot. Talk to me! Like a person, we must teach it how to do its job effectively. 

