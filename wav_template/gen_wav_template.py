import re
import sys
import os

def gen_wav(fpath, output_file):
    print(f"ffmpeg -y -i {fpath} -ar 16000 -ac 1 -sample_fmt s16 {output_file}")
    os.system(f"ffmpeg -y -i {fpath} -ar 16000 -ac 1 -sample_fmt s16 {output_file}")

def concat_wav(fpath, output_file):
    print(f"ffmpeg -y -f concat -safe 0 -i {fpath} -c copy {output_file}")
    os.system(f"ffmpeg -y -f concat -safe 0 -i {fpath} -c copy {output_file}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python gen_wav_template.py <dir>")
        sys.exit(1)

    text = ""
    dir = sys.argv[1]
    basename = os.path.basename(dir)
    wav_file = os.path.join(dir, f"{basename}.wav")
    tmp_file = open(os.path.join(dir, f"{basename}-tmp.txt"), 'w')
    total_pcm_size = 0
    max_size = 30 * 16000 * 2 # 30 s
    for i in range(100):
        print(f"process {i}")
        fpath = os.path.join(dir, f"{i}")
        if not os.path.exists(fpath + ".txt"):
            break

        if os.path.exists(fpath + ".wav"):
            gen_wav(fpath + ".wav", fpath + "-16k.wav")
        elif os.path.exists(fpath + ".mp3"):
            gen_wav(fpath + ".mp3", fpath + "-16k.wav")
        else:
            raise Exception(f"{fpath}.wav or {fpath}.mp3 not exists")

        fsize = os.stat(fpath + "-16k.wav").st_size
        if (total_pcm_size + fsize - 44) > max_size:
            break
        total_pcm_size += fsize - 44
        with open(fpath + ".txt", 'r') as f:
            # 言为心声，字为心画。（改编自扬雄《法言·问神》）
            tmp = f.read()
            tmp = re.sub(r'（[^）]*）\s*$', '', tmp)
            if not tmp.endswith(("。", "！", "？", "，", "；")):
                tmp += "。"
            text += tmp
        tmp_file.write(f"file {os.path.basename(fpath)}-16k.wav\n")

    tmp_file.close()
    concat_wav(tmp_file.name, wav_file)
    text_file = os.path.join(dir, f"{basename}.txt")
    with open(text_file, 'w') as f:
        f.write(text)

if __name__  == '__main__':
    main()