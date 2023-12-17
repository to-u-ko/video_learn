# 文字起こし用
from faster_whisper import WhisperModel
import argparse

#秒数を時間、分、秒に変換する関数
def seconds_to_hms(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

# 文字起こし関数
# 動画タイトルを与えると、その動画の文字起こしをしてテキストファイルを生成する
def faster_whisper(video_title):
    video_path = f'/opt/ml/processing/input/{video_title}.mp4'
    model_size = "medium"
    model = WhisperModel(model_size, device="cuda", compute_type="float32")

    ####タイムスタンプ付き、テキストのみ書き出し####
    segments, info = model.transcribe(video_path, beam_size=5, temperature=1.0, language="ja")

    transcription_path = f'/opt/ml/processing/output/{video_title}.txt'

    with open(transcription_path, 'w',encoding="utf-8") as f:
        for segment in segments:
            time_formatted = seconds_to_hms(segment.start)
            print(time_formatted)
            f.write(f"[{time_formatted}] {segment.text}\n")

if __name__ == '__main__':
    # argparseを使用してコマンドライン引数を解析
    parser = argparse.ArgumentParser(description="動画の文字起こし処理")
    parser.add_argument("--video_title", type=str, required=True, help="動画のタイトル")

    # 引数を解析
    args = parser.parse_args()

    # 解析した引数を関数に渡す
    faster_whisper(args.video_title)
