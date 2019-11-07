import yaml
import csv
import timeit
from os import listdir
from os.path import isfile, join


def main():
    fieldnames = ["Venue", "City", "Date", "Match Type", "Teams",
                  "Name", "Runs", "Balls Faced", "Balls Bowled",
                  "Wickets Taken", "Runs Conceded", "Overs Bowled",
                  "Batting Strike Rate", "Bowling Strike Rate", "Bowling Economy Rate"]

    # creates or overwrites (if file already exists) csv file and writes all headers into the file
    with open("match_stats.csv", mode='w', newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(fieldnames)

    dir_1 = "2019_male"
    dir_2 = "odis_male"
    dir_3 = "ipl_male"

    # creates list of files from dir_1 that are also in either dir_2 or dir_3
    files = [f for f in listdir(dir_1) if (
        isfile(join(dir_1, f)) and ".yaml" in f and (isfile(join(dir_2, f)) or isfile(join(dir_3, f))))]

    # parses every ".yaml" file in the directory
    for file in files:
        with open(join(dir_1, file), 'r') as yaml_in:
            match = yaml.safe_load(yaml_in)  # main performance hit

        """
        Player structure:
        "Name": {
            runs: int,
            balls_faced: int,
            balls_bowled: int,
            wickets_taken: int, 
            runs_conceded: int,
            overs_bowled: float,
            batting_sr: float,
            bowling_sr: float,
            bowling_econ: float
        }
        """

        stats = {}

        for inning in match["innings"]:
            for i in inning:
                for bowls in inning[i]["deliveries"]:
                    for b in bowls:
                        batsman = bowls[b]["batsman"]
                        if batsman in stats:  # updates existing batsman's stats
                            # runs scored by the batsman
                            stats[batsman]["runs"] += bowls[b]["runs"]["batsman"]

                            # balls faced, not including wide balls
                            if "extras" not in bowls[b] or "wides" not in bowls[b]["extras"]:
                                stats[batsman]["balls_faced"] += 1

                        else:  # creates batsman's stats in stats
                            # initial run scored by the batsman
                            stats[batsman] = {
                                "runs": bowls[b]["runs"]["batsman"]}

                            # initial ball faced, not including wide balls
                            if "extras" in bowls[b] and "wides" in bowls[b]["extras"]:
                                stats[batsman]["balls_faced"] = 0
                            else:
                                stats[batsman]["balls_faced"] = 1

                            # set up all other player stats
                            stats[batsman]["balls_bowled"] = 0
                            stats[batsman]["wickets_taken"] = 0
                            stats[batsman]["runs_conceded"] = 0

                        bowler = bowls[b]["bowler"]
                        if bowler in stats:  # updates existing bowler's stats
                            # balls bowled, not including byes and leg byes
                            if "extras" in bowls[b] and ("byes" in bowls[b]["extras"] or "legbyes" in bowls[b]["extras"]):
                                stats[bowler]["balls_bowled"] += 1
                            elif "extras" not in bowls[b]:
                                stats[bowler]["balls_bowled"] += 1

                            # wickets taken, only if batsman has been bowled, caught, caught and bowled, lbw (leg before wicket) or stumped out
                            if "wicket" in bowls[b] and bowls[b]["wicket"]["kind"] in ["bowled", "caught", "caught and bowled", "lbw", "stumped"]:
                                stats[bowler]["wickets_taken"] += 1

                            # runs conceded by bowler if run scored by batsman or run awarded from extras not including leg byes, byes and penalties
                            stats[bowler]["runs_conceded"] += bowls[b]["runs"]["batsman"]
                            if "extras" in bowls[b]:
                                for e in bowls[b]["extras"]:
                                    if e not in ["legbyes", "byes", "penalty"]:
                                        stats[bowler]["runs_conceded"] += bowls[b]["extras"][e]

                        else:  # creates bowler's stats in stats
                            # set up all other inital player stats
                            stats[bowler] = {"runs": 0}
                            stats[bowler]["balls_faced"] = 0

                            # initial balls bowled, not including byes and leg byes
                            if "extras" in bowls[b] and ("byes" in bowls[b]["extras"] or "legbyes" in bowls[b]["extras"]):
                                stats[bowler]["balls_bowled"] = 1
                            elif "extras" not in bowls[b]:
                                stats[bowler]["balls_bowled"] = 1
                            else:
                                stats[bowler]["balls_bowled"] = 0

                            # initial wickets taken, only if batsman has been bowled, caught, caught and bowled, lbw (leg before wicket) or stumped out
                            if "wicket" in bowls[b] and bowls[b]["wicket"]["kind"] in ["bowled", "caught", "caught and bowled", "lbw", "stumped"]:
                                stats[bowler]["wickets_taken"] = 1
                            else:
                                stats[bowler]["wickets_taken"] = 0

                            # initial runs conceded by bowler if run scored by batsman or run awarded from extras not including leg byes, byes and penalties
                            stats[bowler]["runs_conceded"] = bowls[b]["runs"]["batsman"]
                            if "extras" in bowls[b]:
                                for e in bowls[b]["extras"]:
                                    if e not in ["legbyes", "byes", "penalty"]:
                                        stats[bowler]["runs_conceded"] += bowls[b]["extras"][e]

        for player in stats:
            # overs bowled
            stats[player]["overs_bowled"] = stats[player]["balls_bowled"] // 6 + \
                (stats[player]["balls_bowled"] % 6 * 0.1)

            # batting strike rate
            if stats[player]["balls_faced"] != 0:
                stats[player]["batting_sr"] = (
                    100 * stats[player]["runs"]) / stats[player]["balls_faced"]
            else:
                stats[player]["batting_sr"] = 0

            # bowling strike rate
            if stats[player]["wickets_taken"] != 0:
                stats[player]["bowling_sr"] = stats[player]["balls_bowled"] / \
                    stats[player]["wickets_taken"]
            else:
                stats[player]["bowling_sr"] = 0

            # bowling economy rate
            if stats[player]["overs_bowled"] != 0:
                stats[player]["bowling_econ"] = stats[player]["runs_conceded"] / \
                    (int(stats[player]["overs_bowled"]) + (((stats[player]
                                                             ["overs_bowled"] - int(stats[player]["overs_bowled"])) * 10) / 6))
            else:
                stats[player]["bowling_econ"] = 0

        # append each match's summarised player stats onto csv
        with open("match_stats.csv", mode='a', newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            for player in stats:
                writer.writerow({
                    "Venue": match["info"]["venue"],
                    "City": match["info"]["city"],
                    "Date": match["info"]["dates"][0],
                    "Match Type": match["info"]["match_type"],
                    "Teams": f'{match["info"]["teams"][0]} v {match["info"]["teams"][1]}',
                    "Name": player,
                    "Runs": stats[player]["runs"],
                    "Balls Faced": stats[player]["balls_faced"],
                    "Balls Bowled": stats[player]["balls_bowled"],
                    "Wickets Taken": stats[player]["wickets_taken"],
                    "Runs Conceded": stats[player]["runs_conceded"],
                    "Overs Bowled": stats[player]["overs_bowled"],
                    "Batting Strike Rate": stats[player]["batting_sr"],
                    "Bowling Strike Rate": stats[player]["bowling_sr"],
                    "Bowling Economy Rate": stats[player]["bowling_econ"]
                })

        print(f'File: {file} written.')
    return


if __name__ == "__main__":
    start = timeit.default_timer()
    main()
    stop = timeit.default_timer()

    # measure program execution time
    print("Time to complete: ", stop - start)
