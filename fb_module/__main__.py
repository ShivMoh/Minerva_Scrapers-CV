import fb_module.scraper as scraper
import time
WAIT_TIME = 1
if __name__ == "__main__":
    while True:
        scraper.run()
        time.sleep(WAIT_TIME)
