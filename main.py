import logging
import requests
import threading
from prettylog import basic_config
from classes.bazarr import Bazarr
from classes.subtitles import Subtitles

from dotenv import load_dotenv
load_dotenv()


basic_config(level=logging.INFO, buffered=False, log_format='color')

def process_movies():
    logging.info("Processing movies")
    client = Bazarr()
    subs = Subtitles()

    for wanted in client.wanted('movie'):
        subtitles = subs.get_subtitles(wanted.imdb_id, languages=wanted.missing_subtitles, title=wanted.title)
        
        for subtitle in subtitles:
            wanted.resolve(subtitle['content'], subtitle['language'])


def process_episodes():
    logging.info("Processing episodes")
    client = Bazarr()
    subs = Subtitles()

    for wanted in client.wanted('episode'):
        subtitles = subs.get_subtitles(wanted.imdb_id,
                                       episode=wanted.episode, languages=wanted.missing_subtitles, title=wanted.title)
        
        for subtitle in subtitles:
            wanted.resolve(subtitle['content'], subtitle['language'])


def main():
    logging.info("Starting")
    
    process_movies()
    process_episodes()
    

if __name__ == '__main__':
    main()