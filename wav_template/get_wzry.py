import os
import requests
import json
import sys

'''
[
    {
        "text": "替月行道",
        "mp3": "https://game.gtimg.cn/images/yxzj/zlkdatasys/audios/audio/20231201/17014019361826.mp3"
    },
    {
        "text": "今天是对面的坏日子。",
        "mp3": "https://game.gtimg.cn/images/yxzj/zlkdatasys/audios/audio/20220409/16494894561361.wav"
    },
]
'''
def main():
    if len(sys.argv) != 3:
        print("Usage: python get_wzry.py <fpath> <output_path>")
        sys.exit(1)

    fpath = sys.argv[1]
    output_path = sys.argv[2]
    with open(fpath, 'r') as f:
        buf = f.read().strip()
    jm = json.loads(buf)
    os.makedirs(output_path, exist_ok=True)
    for i, item in enumerate(jm):
        text = item['text']
        audio_url = item['mp3']
        suffix = audio_url.split('.')[-1]
        print(f'{i}: {text}')
        with open(os.path.join(output_path, f'{i}.txt'), 'w') as f:
            f.write(text)
        with open(os.path.join(output_path, f'{i}.{suffix}'), 'wb') as f:
            resp = requests.get(audio_url)
            f.write(resp.content)

if __name__ == '__main__':
    main()