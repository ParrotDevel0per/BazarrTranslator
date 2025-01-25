import pysubs2
import requests
import logging
import os
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

class Translator(object):
    def __init__(self):
        self.max_threads = 5  # Hardcoded limit for max concurrent requests

    def __fix_line(self, line: str) -> str:
        if line.endswith("\\N"):
            line = line[:-2]
        
        if line.endswith("\\R"):
            line = line[:-2]

        if str(line).endswith("N"):
                line = line[:-1]

        if str(line).endswith("R"):
                line = line[:-1]

        if line.endswith("\\"):
            line = line[:-1]

        return line

    def translate_line(self, text: str, input_language: str, target_language: str) -> str:
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "q": text.strip(),
            "source": input_language,
            "target": target_language,
            "format": "text",
            "alternatives": 0,
            "api_key": ""
        }
        response = requests.post(f"{os.getenv('LIBRETRANSLATE_SERVER')}/translate", headers=headers, data=json.dumps(data))

        if not response.ok:
            logging.error(f"Failed to translate line: {text}. Status code: {response.status_code}")
            return text
        response = response.json()

        if response.get("translatedText"):
            return response.get("translatedText")
        return text

    def translate_subtitles(self, subs: pysubs2.SSAFile, input_language: str, target_language: str) -> pysubs2.SSAFile:
        lines = [line for line in subs if line.text]  # Filter lines with text to iterate

        def worker(line):
            translated = self.translate_line(line.text, input_language, target_language)
            logging.debug(f"Translated {line.text} -> {translated}")

            line.text = self.__fix_line(translated.strip())


        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            future_to_line = {executor.submit(worker, line): line for line in lines}

            for future in tqdm(as_completed(future_to_line), total=len(lines), desc=f"Translating subtitles ({input_language} -> {target_language})", unit="line"):
                try:
                    future.result()  # Wait for the thread to complete
                except Exception as e:
                    logging.error(f"Error translating line: {e}")

        return subs
