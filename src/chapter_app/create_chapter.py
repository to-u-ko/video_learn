#celery関係
from __future__ import absolute_import, unicode_literals
from celery import shared_task

# 共通　ファイルパス設定用
from django.conf import settings
from pathlib import Path
# 動画圧縮用
import subprocess
# 文字起こし用
from faster_whisper import WhisperModel
# チャプター生成用
import os
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
# User,Chapterのデータベースを操作
from .models import User,Chapter
# メール送信モジュール
from django.core.mail import send_mail
#S3操作
import boto3


#秒数を時間、分、秒に変換する関数を作成 
def seconds_to_hms(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
  
# 文字起こし関数
# 圧縮動画のファイルパスと動画タイトルを与えると、文字起こしをしてテキストのファイルパスを返す
def faster_whisper(comp_video_path, video_title):
    transcription_path = f"/code/storage//transcriptions/trans_{video_title}.txt"

    model_size = "medium"
    model = WhisperModel(model_size, device="auto", compute_type="float32")

    ####タイムスタンプ付き、テキストのみ書き出し####
    segments, info = model.transcribe(comp_video_path, beam_size=5, temperature=1.0, language="ja")

    with open(transcription_path, 'w',encoding="utf-8") as f:
        for segment in segments:
            time_formatted = seconds_to_hms(segment.start)
            print(time_formatted)
            f.write(f"[{time_formatted}] {segment.text}\n")

    return transcription_path


# チャプター生成関数
# 文字起こしテキストのファイルパスと動画タイトルを与えると、チャプターテキストを返す
def create_chap(transcription_path, video_title):
    # 音声テキストファイルからテキストデータを読み込み
    with open(transcription_path, encoding="utf-8_sig") as f:
        state_of_the_union = f.read()

    # chunk_sizeなど
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 4000,
        chunk_overlap  = 100,
        length_function = len,
        is_separator_regex = False,
    )

    texts = text_splitter.create_documents([state_of_the_union])

    # 言語モデルとしてOpenAIのモデルを指定
    llm = OpenAI(model_name="gpt-4")

    # プロンプト文
    template = """
    次の文章は時間とセリフが書いてあるシナリオです。
    この内容に最も適した見出しを作り、一番最初の時間と見出しを回答して下さい。
    回答は [時間] 見出し という形式でお願いします。「{original_sentences}」
    """

    # プロンプトのテンプレート内にあるチャプター分け前のテキストを変数として設定
    prompt = PromptTemplate(
        input_variables=["original_sentences"],
        template=template,
    )

    # プロンプトを実行させるチェーンを設定
    llm_chain = LLMChain(llm=llm, prompt=prompt,verbose=True)

    chapter_text = ''
    # for文で分割した各テキストに対しチェーンを実行
    # 実行結果をoutput.txtに出力
    for original_sentences in texts:
        response = llm_chain.run(original_sentences)
        chapter_text += f"{response}\n"

    return chapter_text

# メール送信関数
# 引数に与えたsubject(件名)、message（本文）、user_email(ユーザーのメールアドレス)をもとにメールを送信する
def send_email(subject, message, user_email):
    recipient_list = [
        user_email
    ]
    send_mail(subject, message, None, recipient_list, fail_silently=False)

# データベース保存関数
# chapterデータベースから動画タイトルをもとにデータを取得し、引数で指定された情報を上書きする
def save_chapter(video_title, *, chapter_data=None, status=None, video_file_path=None):
    chapter = Chapter.objects.get(video_title=video_title)
    # chapter_dataが指定されていれば上書き
    if chapter_data is not None:
        chapter.chapter_data = chapter_data
    # statusが指定されていれば上書き
    if status is not None:
        chapter.status = status
    # video_file_pathが指定されていれば上書き
    if video_file_path is not None:
        chapter.video_file_path = video_file_path
    chapter.save()

# celeryで処理する関数に設定
@shared_task
def celery_process(user_id, video_path, video_title):
    try:
        user = User.objects.get(pk=user_id)
        user_email = user.email

        # Chapterデータベースから動画タイトルをもとにデータを取得し、chapter_dataとstatusを上書き保存
        save_chapter(video_title, status='文字起こし中')
        
        # faster-whisperで文字起こし
        transcription_path = faster_whisper(video_path, video_title)
        print('文字起こし完了')
        # Chapterデータベースから動画タイトルをもとにデータを取得し、chapter_dataとstatusを上書き保存
        save_chapter(video_title, status='チャプター生成中')
        # ローカルのtranscriptionファイルをS3に保存
        # upload_to_s3(transcription_path, f"storage/transcriptions/trans_{video_title}.txt")
        # transcription_url = f"{media_url}/transcriptions/trans_{video_title}.txt"
        
        # 音声テキストファイルからテキストデータを読み込み
        with open(transcription_path, encoding="utf-8_sig") as f:
            state_of_the_union = f.read()

        # Chapterデータベースから動画タイトルをもとにデータを取得し、chapter_dataとstatusを上書き保存
        save_chapter(video_title, status = 'チャプター生成中', chapter_data=state_of_the_union)
        # メール送信
        subject = 'チャプたん通知（文字起こし）'
        message = 'チャプたんで動画「' + video_title + '」の文字起こしが完了しました。'
        send_email(subject, message, user_email)
       

        # openAIでチャプター生成
        chapter_text = create_chap(transcription_path, video_title)
        print('チャプター生成完了')
        # Chapterデータベースから動画タイトルをもとにデータを取得し、chapter_dataとstatusを上書き保存
        save_chapter(video_title, status='完了', chapter_data=chapter_text)
        # メール送信
        subject = 'チャプたん通知（完了）'
        message = 'チャプたんで動画「' + video_title + '」のチャプター生成が完了しました。'
        send_email(subject, message, user_email)


    except Exception as e:
        # Chapterでエラーが起きた際の例外処理
        print(e)
        user = User.objects.get(pk=user_id)
        user_email = user.email
        
        save_chapter(video_title, status='処理エラー')

        subject = 'チャプたん通知（エラー）'
        message = 'チャプたんで動画「' + video_title + '」の処理中にエラーが発生しました。'
        send_email(subject, message, user_email)
