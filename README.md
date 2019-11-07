# Cricket-stats

Two simple Python programs:

1. Parses YAML format match data from Cricheet and produces csv containing
   individual player statsitics from the match, similiar to a match scorecard.
2. Web scrapes cricket player statistics from Cricmetric using the
   player names provided in an external text file and produces csv file of the results.

## Usage - _Currently_

Requires the following zipped files from Cricheet in the working directory:

1. https://cricsheet.org/downloads/2019_male.zip
2. https://cricsheet.org/downloads/odis_male.zip
3. https://cricsheet.org/downloads/ipl_male.zip

- Program essentially only parses data for matches which are of type ODI or IPL and were played in 2019.
