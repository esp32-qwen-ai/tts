import sys
import os
sys.path.append('../CosyVoice/')
sys.path.append('../CosyVoice/third_party/Matcha-TTS')
from cosyvoice.cli.cosyvoice import CosyVoice2
from cosyvoice.utils.file_utils import load_wav
import numpy as np
import torch

# GPU生成比较慢，如果是streaming，声音断断续续的效果不好
STREAMING = True

class TTS:
    def __init__(self, model_dir='../CosyVoice/pretrained_models/CosyVoice2-0.5B'):
        self.cosyvoice = CosyVoice2(model_dir, load_jit=True, load_trt=True, fp16=True, use_flow_cache=STREAMING)
        self.spk_ids = []
        self.load_wav_to_spk()

    def load_wav_to_spk(self, wav_path="wav_template"):
        spk_ids = []
        for item in os.listdir(wav_path):
            if os.path.isfile(os.path.join(wav_path, item)):
                continue
            prompt_speech_16k = load_wav(os.path.join(wav_path, item, f"{item}.wav"), 16000)
            with open(os.path.join(wav_path, item, f"{item}.txt")) as f:
                prompt_text = f.read()
            self.cosyvoice.add_zero_shot_spk(prompt_text, prompt_speech_16k, item)
            spk_ids.append(item)
        self.spk_ids = spk_ids

    def list_spk(self):
        return self.spk_ids

    @staticmethod
    def tensor_to_pcm_bytearray(tensor: torch.Tensor, num_bits: int = 16) -> bytearray:
        """
        将 PyTorch Tensor 转换为 PCM 格式的 bytearray。
        
        :param tensor: 输入的音频张量，形状应为 (C x L)，其中 C 是声道数，L 是样本长度。
                    如果是单声道，则形状为 (L,)。
        :param num_bits: 每个样本使用的比特数，默认为16位。
        :return: PCM 格式的 bytearray。
        """
        # 确保输入张量位于CPU上，并且是浮点数
        tensor = tensor.cpu().float()

        if num_bits == 8:
            # 缩放到 [0, 255] 范围
            tensor = (tensor + 1.0) * 127.5
            tensor = tensor.to(torch.uint8)
        elif num_bits == 16:
            tensor = torch.clamp(tensor, min=-1.0, max=1.0)
            # 缩放到 [-32768, 32767] 范围
            tensor = (tensor * 32767.0).to(torch.int16)
        else:
            raise ValueError("Only supports 8-bit or 16-bit PCM.")

        # 处理多声道：确保是 (L, C) 形状并展平为交错声道
        if len(tensor.shape) > 1 and tensor.shape[0] > 1:
            # 假设第一个维度是通道数 (C x L) -> (L x C)
            tensor = tensor.transpose(0, 1)
            # 展平为交错声道顺序：L0C0, L0C1, L1C0, L1C1, ...
            array = tensor.numpy().flatten()
        else:
            array = tensor.numpy()

        # 将 numpy 数组转换为 bytearray
        pcm_bytearray = array.tobytes()

        return pcm_bytearray

    def call(self, text, spk_id=""):
        if not text:
            return
        if not spk_id:
            spk_id = self.spk_ids[0]
        resp = self.cosyvoice.inference_zero_shot(text, "", "", spk_id, stream=STREAMING)
        for chunk in resp:
            pcm = TTS.tensor_to_pcm_bytearray(chunk["tts_speech"])
            print(f"{spk_id} generate {len(pcm)}")
            yield pcm

if __name__ == '__main__':
    tts = TTS()
    for chunk in tts.call('收到好友从远方寄来的生日礼物，那份意外的惊喜与深深的祝福让我心中充满了甜蜜的快乐，笑容如花儿般绽放。'):
        print(f"generate:", len(chunk))