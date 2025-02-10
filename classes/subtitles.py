import os
import gzip
import logging
import pysubs2
import requests
from classes.translator import Translator
from utils.common import get_video_subtitles


class Subtitles(object):
    def __init__(self):
        pass

    def _normalize_imdb_id(self, imdb_id):
        return imdb_id.split("tt")[1] if "tt" in imdb_id else imdb_id

    def opensubtitles(self, imdb_id, episode=None):
        url = f"https://rest.opensubtitles.org/search/imdbid-{self._normalize_imdb_id(imdb_id)}"
        if episode:
            episode = str(episode).replace("x", "-").split("-")
            season = episode[0]
            episode = episode[1]
            url = f"https://rest.opensubtitles.org/search/episode-{int(episode)}/imdbid-{self._normalize_imdb_id(imdb_id)}/season-{int(season)}"

        resp = requests.get(url, headers={"X-User-Agent": "trailers.to-UA"})
        if not resp.ok:
            return []

        return resp.json()

    def _get_burned_subs(self, imdb_id, episode, wanted_obj):
        path = wanted_obj.video_path()
        grabbed_subs = get_video_subtitles(path)
        if not grabbed_subs:
            return []

        result = []
        for i, sub in enumerate(grabbed_subs):
            if sub['forced']:
                continue

            if not sub["content"]:
                continue

            result.append({
                "ISO639": sub["language"],
                "language": sub["language"],
                "SubFormat": "ass",
                "content": sub["content"].encode("utf-8"),
                "SubRating": 100-i,
                "sub_info": sub["sub_info"],
            })
        

        return result

    def _translate_subs(self, results, languages=[]):
        logging.info(f"Translating subtitles to {', '.join(languages)}")
        if len(results) == 0:
            return []

        _ = ["de", "en"]
        sorted_ = sorted(
            results,
            key=lambda x: _.index(x["ISO639"]) if x["ISO639"] in _ else len(_),
            reverse=False,
        )
        best = sorted_[0]

        #print(best)
        #exit(0)

        subtitle_content = best.get("content")

        if not subtitle_content:
            subtitle_content = requests.get(best["SubDownloadLink"], headers={"X-User-Agent": "trailers.to-UA"})

            if not subtitle_content.ok:
                return []

            if subtitle_content.url.endswith(".gz"):
                subtitle_content = gzip.decompress(subtitle_content.content)
            else:
                subtitle_content = subtitle_content.content

        translator = Translator()
        response = []

        for language in languages:
            translated = translator.translate_subtitles(
                pysubs2.SSAFile().from_string(subtitle_content.decode("utf-8"), fromat_=best["SubFormat"]),
                best["ISO639"],
                language,
            )
            response.append({
                "language": language,
                "content": translated,
            })

        return response

    def get_subtitles(self, imdb_id, episode=None, languages=[], title="", wanted_obj=None):
        local_name = f"({imdb_id}) [{episode}] {title}" if episode else f"({imdb_id}) {title}"
        logging.info(f"Getting subtitles for {local_name}, Languages: {', '.join(languages)}")

        # Check for subtitles included in the file
        result = self._get_burned_subs(imdb_id, episode=episode, wanted_obj=wanted_obj)

        if not result:
            # Use opensubtitles.org to search for subs
            result = self.opensubtitles(imdb_id, episode=episode)

        _os_results = [
            x
            for x in result
            if x["SubFormat"] in ["ass", "ssa", "srt"]
        ]
        logging.info(f"Found {len(_os_results)} subtitles")

        # Check if any of the subs are already in the correct language
        possible = [item for item in _os_results if item["ISO639"] in languages]
        logging.info(f"Found {len(possible)} subtitles for {', '.join(languages)}")

        _sorted = sorted(possible, key=lambda x: x["SubRating"], reverse=True)

        results, fullfilled = [], []
        for language in languages:
            for item in _sorted:
                if item["ISO639"] == language:
                    results.append(item)
                    fullfilled.append(language)
                    break

        logging.info(f"Available languages: {', '.join(fullfilled) or 'None'}")
        logging.info(f"Missing languages: {', '.join([x for x in languages if x not in fullfilled]) or 'None'}")

        # Translate to languages that were not found
        if os.getenv("LIBRETRANSLATE_ENABLED") == "true":
            results.extend(
                self._translate_subs(_os_results, languages=[x for x in languages if x not in fullfilled])
            )
        else:
            logging.info("Translation has been disabled, set LIBRETRANSLATE_ENABLED=true to enable")

        parsed = []
        for result in results:
            if result.get("content"):
                parsed.append({
                    "language": result["language"],
                    "content": result["content"],
                    "imdb_id": imdb_id,
                    "episode": episode,
                })
                continue

            # Download and parse the subs
            logging.info(f"Downloading '{result['SubFileName']}.gz'")
            resp = requests.get(result["SubDownloadLink"], headers={"User-Agent": "trailers.to-UA"})
            if not resp.ok:
                continue

            logging.info(f"Unzipping '{result['SubFileName']}'")
            ungzipped: bytes = gzip.decompress(resp.content)

            parsed.append({
                "language": result["ISO639"],
                "content": pysubs2.SSAFile().from_string(ungzipped.decode("utf-8"), format_=result['SubFormat']),
                "imdb_id": imdb_id,
                "episode": episode,
            })

        return parsed
