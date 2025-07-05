import scraper.article_scraper as article_scraper
import scraper.response_formatter as response_formatter
import time

"""
    in the future, to know if its a duplicate, we should just query the main db
    however, for now, we're gonna just store a history of json
    and if the title already exists there, we're gonna skip
"""
WAIT_TIME = 5
if __name__ == "__main__":

    while True:
        print("Running...")
        article_scraper.run()

        if not response_formatter.is_data_available():
            print("No data is available")
            time.sleep(WAIT_TIME)
            continue

        response_formatter.format_responses()
        # response_formatter.send_responses()

        # data is refreshed every day
        time.sleep(WAIT_TIME)

    
