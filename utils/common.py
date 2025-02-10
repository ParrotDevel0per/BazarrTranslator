import random
import string
import json
import ffprobe3
import subprocess
import pycountry
import logging

def random_string(length, digits=True, incUppercase=True):
    letters = string.ascii_letters if incUppercase else string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def get_video_subtitles(video_path):
    logging.info(f"Extracting subtitles from {video_path}")
    metadata = ffprobe3.probe(str(video_path))
    
    subtitles = []
    index = 0
    for sub in metadata.streams:
        if not sub.is_subtitle():
            continue

        descriptor = sub.__dict__['parsed_json']['tags']['title'].lower()

        c = False
        for x in ["song", "sing", "sign"]:
            if x in sub.__dict__['parsed_json']['tags']['title'].lower():
                c = True
                break

        if c: continue


        #print(sub.__dict__['parsed_json'].keys())
        #exit(0)

        # Extract subtitle content
        extract_cmd = [
            "ffmpeg", "-y", "-i", str(video_path), "-map", f"0:s:{index}", "-f", "ass", "-"
        ]

        try:   
            extract_result = subprocess.run(extract_cmd, capture_output=True, text=True, check=True)
            content = extract_result.stdout
        except:
            content = ""

        language = sub.__dict__['parsed_json']['tags']['language']
        if len(language) == 3:
            language = pycountry.languages.get(alpha_3=language).alpha_2


        subtitles.append({
            "language": language,
            "format": "ass",
            "content": content,
            "forced": sub.__dict__['parsed_json']['disposition']['forced'] == 1,
            "sub_info": sub.__dict__})

        logging.info(f"[{index}] Extracted subtitles for {language}")
        index += 1
        
    return subtitles
