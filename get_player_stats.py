from bs4 import BeautifulSoup
import requests
import csv
import timeit


def main():
    players_file = "player_names.txt"

    # create list of all distinct player names
    with open(players_file, 'r') as f:
        players = f.read().split('\n')

    fieldnames = ["Name", "Full Name", "Match Type", "Batting Average", "Batting Strike Rate",
                  "Bowling Average", "Bowling Strike Rate", "Bowling Economy Rate"]

    # creates or overwrites (if file already exists) csv file and writes all headers into the file
    with open("player_stats.csv", mode='w', newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(fieldnames)

    for player in players:
        html = f'http://www.cricmetric.com/playerstats.py?player={player}'
        source = requests.get(html).text
        soup = BeautifulSoup(source, "lxml")

        full_name = soup.find(
            "div", {"class": "panel-heading"}).text
        if full_name == "Player Statistics":  # If player not found
            full_name = player

        # corresponds to relevant table id's to retrieve
        match_types = ["ODI", "TWENTY20"]
        stat_types = ["Batting", "Bowling"]

        for match in match_types:
            career_stats = [player, full_name]

            if match == "TWENTY20":
                career_stats.append("T20")
            else:
                career_stats.append(match)

            for stat in stat_types:
                try:  # if the table exists
                    row = soup.find(
                        "div", {"id": f'{match}-{stat}'}).div.table.tfoot.tr
                    # gets 'total' row data from table
                    data = [td.text for td in row.find_all("td")]

                    career_stats.extend(data[5:7])
                    if stat == "Bowling":
                        career_stats.append(data[4])

                except Exception as e:  # if the table does not exist
                    career_stats.extend(['0', '0'])
                    if stat == "Bowling":
                        career_stats.append('0')

            for i in range(len(career_stats)):
                if career_stats[i] == '-':
                    career_stats[i] = '0'

            # append each players career stats onto csv
            with open("player_stats.csv", mode='a', newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(career_stats)

        print(f'{player} added.')


if __name__ == "__main__":
    start = timeit.default_timer()
    main()
    stop = timeit.default_timer()

    # measure program execution time
    print("Time to complete: ", stop - start)
