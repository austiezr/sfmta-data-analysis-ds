# Used for local testing and manual report generation
# This is not used in the AWS Lambda deployment

from report_main import generate_report
import time


if __name__ == "__main__":
    before = time.time()

    generate_report(event='', context='', date='2020-6-13', new_report=True)

    elapsed = time.time() - before
    minutes = int(elapsed / 60)
    seconds = round(elapsed % 60, 2)
    print(f"\nFinished in {minutes} minutes and {seconds} seconds")
