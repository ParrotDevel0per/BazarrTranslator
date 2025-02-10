import logging
import requests
import threading
from prettylog import basic_config
from classes.bazarr import Bazarr
from classes.subtitles import Subtitles

# NOTE: Remove in production
from dotenv import load_dotenv
load_dotenv()


basic_config(level=logging.INFO, buffered=False, log_format='color')

def process_movies():
    logging.info("Processing movies")
    client = Bazarr()
    subs = Subtitles()

    for wanted in client.wanted('movie'):
        subtitles = subs.get_subtitles(wanted.imdb_id,
                                        languages=wanted.missing_subtitles,
                                        title=wanted.title,
                                        wanted_obj=wanted)
        
        for subtitle in subtitles:
            wanted.resolve(subtitle['content'], subtitle['language'])


def process_episodes():
    logging.info("Processing episodes")
    client = Bazarr()
    subs = Subtitles()

    for wanted in client.wanted('episode'):
        subtitles = subs.get_subtitles(wanted.imdb_id,
                                       episode=wanted.episode,
                                       languages=wanted.missing_subtitles,
                                       title=wanted.title,
                                       wanted_obj=wanted)
        
        for subtitle in subtitles:
            wanted.resolve(subtitle['content'], subtitle['language'])


def main():
    logging.info("Starting")
    tasks = [
        threading.Thread(target=process_movies, name="Movie Processor"),
        threading.Thread(target=process_episodes, name="Episode Processor"),
    ]

    for t in tasks:
        t.start()

    for t in tasks:
        t.join()


    

if __name__ == '__main__':
    main()