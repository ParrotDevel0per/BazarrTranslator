import os
import requests
import logging
import pysubs2
from io import BytesIO
from utils.common import random_string

class Wanted(object):
    def __init__(self, data, _type="episode"):
        self.sub_ext = "srt" # Bazarr doesn't support anything else

        self.data = data
        self.type = _type
        self.title = data['seriesTitle'] if 'seriesTitle' in data else data['title']
        self.episode = data.get('episode_number', None)
        self.missing_subtitles = [x['code2'] for x in data['missing_subtitles']]
        self.id = self.data['sonarrSeriesId'] if 'sonarrSeriesId' in data else data['radarrId']

        self.__set_ids()

    def __set_ids(self):
        if self.type == 'episode':
            self.__set_episode_ids()
        else:
            self.__ser_movie_ids()

    def __set_episode_ids(self):
        resp = requests.get(
            f"{os.getenv('SONARR_SERVER')}/api/v3/series/{self.id}",
            headers={
                "X-API-KEY": os.getenv("SONARR_API_KEY"),
                "accept": "application/json",
                "accept-encoding": "identity"
            })
        
        if not resp.ok:
            self.tmdb_id = None
            self.imdb_id = None
            return
        
        self.tmdb_id = resp.json()['tmdbId']
        self.imdb_id = resp.json()['imdbId']

    def __ser_movie_ids(self):
        resp = requests.get(
            f"{os.getenv('RADARR_SERVER')}/api/v3/movie/{self.id}",
            headers={
                "X-API-KEY": os.getenv("RADARR_API_KEY"),
                "accept": "application/json",
                "accept-encoding": "identity"
            })
        
        if not resp.ok:
            self.tmdb_id = None
            self.imdb_id = None
            return
        
        self.tmdb_id = resp.json()['tmdbId']
        self.imdb_id = resp.json()['imdbId']

    def __generate_filename(self):
        return f"{random_string(15)}.{self.sub_ext}"

    def __resolve_movie(self, content: pysubs2.SSAFile, language: str):
        logging.info(f"Resolving subtitles for {self.title} ({language})")

        params = {
            "radarrid": self.data.get("radarrId", None),     
            "language": language,
            "forced": "false",
            "hi": "false" # TODO: Make hearing-impaired detection   
        }

        # Files payload with custom filename
        files = {
            "file": (self.__generate_filename(),
                BytesIO(content.to_string(format_=self.sub_ext).encode("utf-8")), "application/octet-stream")
        }
        # Sending the POST request
        try:
            response = requests.post(f"{os.getenv('BAZARR_SERVER')}/api/movies/subtitles", params=params, files=files, headers={
                "X-API-KEY": os.getenv("BAZARR_API_KEY"),
                "accept": "application/json",
                "accept-encoding": "identity"
            })

            if response.ok:
                logging.info(f"Resolved subtitles for {self.title} ({language})")
            else:
                logging.error(f"Failed to resolve subtitles for {self.title} ({language})")
        except Exception as e:
            logging.error(f"Failed to resolve subtitles for {self.title} ({language})")


    def __resolve_episode(self, content: pysubs2.SSAFile, language: str):
        logging.info(f"Resolving subtitles for [{self.data.get('episode_number', 'X')}] {self.title} ({language})")

        params = {
            "seriesid": self.data.get("sonarrSeriesId", None),     
            "episodeid": self.data.get("sonarrEpisodeId", None),
            "language": language,
            "forced": "false",
            "hi": "false" # TODO: Make hearing-impaired detection   
        }

        # Files payload with custom filename
        files = {
            "file": (self.__generate_filename(),
                BytesIO(content.to_string(format_=self.sub_ext).encode("utf-8")), "application/octet-stream")
        }

        # Sending the POST request
        try:
            response = requests.post(f"{os.getenv('BAZARR_SERVER')}/api/episodes/subtitles", params=params, files=files, headers={
                "X-API-KEY": os.getenv("BAZARR_API_KEY"),
                "accept": "application/json",
                "accept-encoding": "identity"
            })

            if response.ok:
                logging.info(f"Resolved subtitles for {self.title} ({language})")
            else:
                logging.error(f"Failed to resolve subtitles for {self.title} ({language})")
        except Exception as e:    
            logging.error(f"Failed to resolve subtitles for {self.title} ({language})")


    def resolve(self, content: pysubs2.SSAFile, language: str):
        if self.type == 'movie':
            self.__resolve_movie(content, language)
        else:
            self.__resolve_episode(content, language)