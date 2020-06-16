# Used for local testing and manual report generation
# This is not used in the AWS Lambda deployment

from report_main import generate_report
import pandas as pd
import time


if __name__ == "__main__":
    # Used this code to back-fill reports we had not generated yet, ran locally
    begin = pd.to_datetime('2020-5-28')
    end = pd.to_datetime('2020-6-12')

    while begin <= end:
        start_time = time.time()

        # generate report for this day
        # (change new_report to False to update existing reports instead)
        generate_report(event='', context='', date=begin, new_report=True)

        # print execution time
        elapsed = time.time() - start_time
        minutes = int(elapsed / 60)
        seconds = round(elapsed % 60, 2)
        print(f"\nFinished in {minutes} minutes and {seconds} seconds\n\n")

        # move to next day
        begin += pd.Timedelta(days=1)
