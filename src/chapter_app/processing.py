#celery関係
from __future__ import absolute_import, unicode_literals
from celery import shared_task
# chatGPTAPI用
import os
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re
# User,Chapterのデータベース操作用
from .models import User, Video, Chapter, Summary
# メール送信用
from django.core.mail import send_mail
# AWS_Sagemaker操作用
import boto3
import sagemaker
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from django.conf import settings
# 動画からサムネイル取得用
import cv2
import sys


# メール送信関数
# 引数に与えたsubject(件名)、message（本文）、user_email(ユーザーのメールアドレス)をもとにメールを送信する
def send_email(subject, message, user_email):
    recipient_list = [
        user_email
    ]
    send_mail(subject, message, None, recipient_list, fail_silently=False)


# サムネイル取得関数
# 動画IDと動画タイトルを与えると動画開始1秒時点のサムネイル画像を生成し、そのファイルパスを返す
def create_thumbnail(video_id, video_url):
    try:
        cap = cv2.VideoCapture(video_url)
        if not cap.isOpened(): return
        fps = cap.get(cv2.CAP_PROP_FPS)

        # 動画開始時点から1秒後のフレームをサムネイル画像として利用するように指定する
        target_second = 1

        # 動画開始時点から1秒後のフレーム枚数目を読み込む様に設定する
        cap.set(cv2.CAP_PROP_POS_FRAMES, fps * target_second)

        # 対象フレームを取得する
        ret, frame = cap.read()

        output_path = f"/code/media/thumbnail_{video_id}.jpg"
        cv2.imwrite(output_path, frame)
        return f"/media/thumbnail_{video_id}.jpg"
    
    except Exception as e:
        print(e)

# sagemakerによる文字起こし処理関数
# boto3を使用してsagemaker processingを呼び出しfaster_whipserによる文字起こしを実行する
def sagemaker_job(video_id):
    video_id = str(video_id)
    script_processor = ScriptProcessor(
                    image_uri= settings.IMAGE_URI,
                    role= settings.ROLE,
                    command=['python3'],
                    instance_count=1,
                    instance_type='ml.g4dn.xlarge')

    script_processor.run(code='/code/chapter_app/sage_whisper.py',
                        inputs=[ProcessingInput(
                            source= f's3://s3-chapter/storage/videos/video_{video_id}.mp4',
                            destination='/opt/ml/processing/input')],
                        outputs=[ProcessingOutput(
                            source='/opt/ml/processing/output',
                            destination='s3://s3-chapter/storage/transcriptions/')],
                            arguments=['--video_id', video_id])
    
    transcription_path = f"storage/transcriptions/transcription_{video_id}.txt"

    return transcription_path


# S3に保存された文字起こしテキストファイルから中身のテキストを取得
def get_transcription(transcriptin_path):
    s3 = boto3.client('s3')

    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    file_name = transcriptin_path

    # S3からファイルの内容を取得
    obj = s3.get_object(Bucket=bucket_name, Key=file_name)
    file_content = obj['Body'].read().decode('utf-8')

    return file_content


# chatGPTの処理関数_gpt4
# 文字起こしテキストを与えると、チャプター＆要約されたテキストを返す
def gpt4_create_chapter_summary(transcription_text):

    # テキスト分割
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 4000,
        chunk_overlap  = 100,
        length_function = len,
        is_separator_regex = False,
    )

    texts = text_splitter.create_documents([transcription_text])

    # 言語モデルとしてOpenAIのモデルを指定
    llm = ChatOpenAI(model_name="gpt-4")

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

    chatgpt_response = ''
    # for文で分割した各テキストに対しチェーンを実行
    for original_sentences in texts:
        response = llm_chain.run(original_sentences)
        chatgpt_response += f"{response}\n"

    return chatgpt_response


# chatGPTの処理関数_gpt4turbo
# 文字起こしテキストを与えると、チャプター＆要約されたテキストを返す
def gpt4turbo_create_chapter_summary(transcription_text):

    # テキスト分割
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 10000,
        chunk_overlap  = 100,
        length_function = len,
        is_separator_regex = False,
    )

    texts = text_splitter.create_documents([transcription_text])

    # 言語モデルとしてOpenAIのモデルを指定
    llm = ChatOpenAI(model_name="gpt-4-1106-preview")

    # プロンプト文
    template = """
    次の文章はITやビジネスに関する講義を文字起こししたものです。
    このテキストをテーマごとに分割し、そのテーマの要点をまとめてください。
    回答は [テーマが開始する時間] テーマのタイトル　テーマの要約 という形式でお願いします。「{original_sentences}」
    """

    # プロンプトのテンプレート内にあるチャプター分け前のテキストを変数として設定
    prompt = PromptTemplate(
        input_variables=["original_sentences"],
        template=template,
    )

    # プロンプトを実行させるチェーンを設定
    llm_chain = LLMChain(llm=llm, prompt=prompt,verbose=False)

    chatgpt_response = ''
    # for文で分割した各テキストに対しチェーンを実行
    for original_sentences in texts:
        response = llm_chain.run(original_sentences)
        chatgpt_response += f"{response}\n"

    return chatgpt_response


# chatGPTの回答からチャプター取り出し
def get_chapter(chatgpt_response):
    pattern = r"^\[\d{2}:\d{2}:\d{2}\]."
    # "[時間]"から始まる行のみ抽出
    chapter_lines = [line for line in chatgpt_response.split('\n') if re.match(pattern, line)]
    # 各行がリスト形式で返ってくるため、それを改行コードで結合させて文字列にする。
    chapter_text = "\n".join(chapter_lines)
    return chapter_text

# chatGPTの回答から要約を取り出し
def get_summary(chatgpt_response):
    pattern = r"\[\d{1,2}:\d{2}:\d{2}\]"
    # "[時間]"を"##"に置換
    summary_text = re.sub(pattern, "##", chatgpt_response)
    return summary_text


# celeryで処理する関数に設定
@shared_task
def celery_process(user_id, video_id):
    try:
        user = User.objects.get(pk=user_id)
        user_email = user.email
        video = Video.objects.get(pk=video_id)
        chapter = Chapter.objects.get(video=video)
        
        # statusを「処理中」に変更
        video.status ='処理中'
        video.save()
        
        # sagemakerを呼び出しfaster-whisperで文字起こし
        transcriptin_path = sagemaker_job(video_id)
        video.transcription_path = transcriptin_path
        video.save()
        print('文字起こし完了')
        
        # S3に保存された文字起こしファイルから中身のテキストを取得
        transcription_text = get_transcription(transcriptin_path)

        # openAIでチャプター生成
        chatgpt_response = gpt4turbo_create_chapter_summary(transcription_text)
        print('chatGPT処理完了')
        chapter_text = get_chapter(chatgpt_response)
        chapter.chapter_text = chapter_text
        chapter.save()
        summary_text = get_summary(chatgpt_response)
        summary = Summary.objects.get(video=video)
        summary.summary_text = summary_text
        summary.save()
        video.status = '完了'
        video.save()
        
        # 処理完了のメール送信
        subject = 'チャプたん通知（完了）'
        message = f'チャプたんで動画「{video.video_title}」のチャプターと要約の生成が完了しました。'
        send_email(subject, message, user_email)
        

    except Exception as e:

        user = User.objects.get(pk=user_id)
        user_email = user.email
        video = Video.objects.get(pk=video_id)
        video.status = "処理エラー"
        video.save()

        subject = 'チャプたん通知（エラー）'
        message = f'チャプたんで動画「{video.video_title}」の処理中にエラーが発生しました。'
        send_email(subject, message, user_email)
