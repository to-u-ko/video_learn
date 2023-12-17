#celery関係
from __future__ import absolute_import, unicode_literals
from celery import shared_task
# チャプター生成用
import os
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
# User,Chapterのデータベース操作用
from .models import User,Chapter
# メール送信用
from django.core.mail import send_mail
# AWS_Sagemaker操作用
import boto3
import sagemaker
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput

from django.core.files.base import ContentFile
from django.conf import settings


# メール送信関数
# 引数に与えたsubject(件名)、message（本文）、user_email(ユーザーのメールアドレス)をもとにメールを送信する
def send_email(subject, message, user_email):
    recipient_list = [
        user_email
    ]
    send_mail(subject, message, None, recipient_list, fail_silently=False)


# データベース保存関数
# chapterデータベースから動画タイトルをもとにデータを取得し、引数で指定された情報を上書きする
def save_chapter(chapter_id, *, chapter_data=None, status=None, video_path=None, transcription_path=None):
    chapter = Chapter.objects.get(id=chapter_id)
    # chapter_dataが指定されていれば上書き
    if chapter_data is not None:
        chapter.chapter_data = chapter_data
    # statusが指定されていれば上書き
    if status is not None:
        chapter.status = status
    # video_pathが指定されていれば上書き
    if video_path is not None:
        chapter.video_path = video_path
    # transcription_path が指定されていれば上書き
    if transcription_path is not None:
        chapter.transcription_path = transcription_path

    chapter.save()


# チャプター生成関数
# 文字起こしテキストのファイルパスと動画タイトルを与えると、チャプターテキストを返す
def create_chap(transcription_text):

    # chunk_sizeなど
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 4000,
        chunk_overlap  = 100,
        length_function = len,
        is_separator_regex = False,
    )

    texts = text_splitter.create_documents([transcription_text])

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

def sagemaker_job(video_title):
    boto_session = boto3.session.Session(region_name="ap-northeast-1")
    sagemaker_client = boto_session.client(service_name='sagemaker', region_name="ap-northeast-1")
    sagemaker_session = sagemaker.session.Session(boto_session=boto_session, sagemaker_client=sagemaker_client)

    script_processor = ScriptProcessor(
                    sagemaker_session = sagemaker_session,
                    image_uri= '612418102865.dkr.ecr.ap-northeast-1.amazonaws.com/sage-whisper:1.0',
                    role= 'arn:aws:iam::612418102865:role/service-role/AmazonSageMaker-ExecutionRole-20231112T121808',
                    command=['python3'],
                    instance_count=1,
                    instance_type='ml.g4dn.xlarge')

    script_processor.run(code='/code/chapter_app/sage_whisper.py',
                        inputs=[ProcessingInput(
                            source= f's3://s3-chapter/storage/videos/{video_title}.mp4',
                            destination='/opt/ml/processing/input')],
                        outputs=[ProcessingOutput(
                            source='/opt/ml/processing/output',
                            destination='s3://s3-chapter/storage/transcriptions/')],
                            arguments=['--video_title', video_title])
    
    transcription_path = f"s3://s3-chapter/storage/transcriptions/{video_title}.txt"

    return transcription_path

# celeryで処理する関数に設定
@shared_task
def celery_process(user_id, chapter_id):
    try:
        user = User.objects.get(pk=user_id)
        user_email = user.email
        chapter = Chapter.objects.get(id=chapter_id)

        # Chapterデータベースから動画タイトルをもとにデータを取得し、chapter_dataとstatusを上書き保存
        save_chapter(chapter_id, status='文字起こし中')
        
        # faster-whisperで文字起こし
        transcriptin_path = sagemaker_job(chapter.video_title)
        print('文字起こし完了')

        """
        # Chapterデータベースから動画タイトルをもとにデータを取得し、chapter_dataとstatusを上書き保存
        transcription_file = ContentFile(transcription_text.encode('utf-8_sig'))
        save_chapter(chapter_id, status = 'チャプター生成中', transcription_path=transcription_file)

        # openAIでチャプター生成
        chapter_text = create_chap(transcription_text)
        print('チャプター生成完了')
        # Chapterデータベースから動画タイトルをもとにデータを取得し、chapter_dataとstatusを上書き保存
        save_chapter(chapter_id, status='完了', chapter_data=chapter_text)
        # メール送信
        subject = 'チャプたん通知（完了）'
        message = f'チャプたんで動画「{chapter.video_title}」のチャプター生成が完了しました。'
        send_email(subject, message, user_email)
        """

    except Exception as e:
        # Chapterでエラーが起きた際の例外処理
        print(e)
        user = User.objects.get(pk=user_id)
        user_email = user.email
        
        save_chapter(chapter_id, status='処理エラー')

        subject = 'チャプたん通知（エラー）'
        message = f'チャプたんで動画「{chapter.video_title}」の処理中にエラーが発生しました。'
        send_email(subject, message, user_email)
