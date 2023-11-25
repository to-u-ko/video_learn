# chapter
チャプター作成アプリ



## 使用技術一覧

<!-- シールド一覧 -->
<!-- 該当するプロジェクトの中から任意のものを選ぶ-->
<p style="display: inline">
  <!-- バックエンドのフレームワーク一覧 -->
  <img src="https://img.shields.io/badge/-Django-092E20.svg?logo=django&style=for-the-badge">
  <!-- バックエンドの言語一覧 -->
  <img src="https://img.shields.io/badge/-Python-F2C63C.svg?logo=python&style=for-the-badge">
  <!-- ミドルウェア一覧 -->
  <img src="https://img.shields.io/badge/-Nginx-269539.svg?logo=nginx&style=for-the-badge">
  <img src="https://img.shields.io/badge/-MySQL-4479A1.svg?logo=mysql&style=for-the-badge&logoColor=white">
  <!-- インフラ一覧 -->
  <img src="https://img.shields.io/badge/-Docker-1488C6.svg?logo=docker&style=for-the-badge">
  <img src="https://img.shields.io/badge/-Amazon%20aws-232F3E.svg?logo=amazon-aws&style=for-the-badge">
</p>

## 目次

1. [プロジェクトについて](#プロジェクトについて)
2. [環境](#環境)
3. [ディレクトリ構成](#ディレクトリ構成)
4. [開発環境構築](#開発環境構築)
5. [トラブルシューティング](#トラブルシューティング)
<br />

<!-- プロジェクト名を記載 -->
## プロジェクト名

チャプたん
<br><br>


<!-- プロジェクトについて -->

## プロジェクトについて

チャプター作成アプリ

（このアプリはCPUでも動作しますが、動画の文字起こしfaster-whisperの処理に時間を要するため、GPUでの動作を推奨します。）

<!-- プロジェクトの概要を記載 -->

  - Djangoのデフォルト管理サイトでユーザー管理。
  - 動画ファイル（.mp4）をアップロードすると、文字起こされ、文字起こしテキストをもとにchatGPTでチャプターを生成。
  - 動画、文字起こしテキストはAWSのS3に保存。

<p align="right">(<a href="#top">トップへ</a>)</p>

## 環境

<!-- 言語、フレームワーク、ミドルウェア、インフラの一覧とバージョンを記載 -->

| 言語・フレームワークなど  | バージョン |
| --------------------- | ---------- |
| Python                | 3.9        |
| Django                | <4         |
| uwsgi                 |            |
| MySQL                 | 8.0        |
| mysqlclient           | 2.1.0      |
| docker compose        | 3.9        |
| openai                | 0.28.1     |
| nginx 1.24.0          | 1.24.0     |
| redis                 | latest     |

| Dockerimageとして使用  | バージョン |
| --------------------- | ---------- |
| MySQL                 | 8.0        |
| nginx 1.24.0          | 1.24.0     |
| redis                 | latest     |

| GPU Dockerimage  | バージョン |
| --------------------- | ---------- |
| nvidia/cuda           | 11.7.1-cudnn8-runtime-ubuntu20.04     |

その他、requirements.txtの内容
> Django<4  
> uwsgi  
> mysqlclient == 2.1.0
>
> faster-whisper
> 
> ffmpeg関係は動画圧縮しなければ不要  
> ffmpeg-python  
> future  
> pydub  
> pyee  
> typing_extensions
> 
> langchain  
> openai == 0.28.1
>
> celery  
> django-celery-results  
> django-redis
>
> boto3  
> django-storages

<p align="right">(<a href="#top">トップへ</a>)</p>


## ディレクトリ構成

<!-- Treeコマンドを使ってディレクトリ構成を記載 -->
<pre>
.
`-- chapter
    |-- Docker
    |   |-- Django
    |   |   |-- Dockerfile
    |   |   `-- requirements.txt
    |   |-- MySQL
    |   |   `-- Dockerfile
    |   `-- Nginx
    |       |-- conf
    |       |   `-- app_nginx.conf
    |       `-- uwsgi_params
    |-- README.md
    |-- docker-compose.yml
    |-- openai_api.env
    |-- sql
    |   `-- init.sql
    `-- src
        |-- chapter_app
        |   |-- __init__.py
        |   |-- admin.py
        |   |-- apps.py
        |   |-- create_chapter.py
        |   |-- forms.py
        |   |-- migrations
        |   |   |-- 0001_initial.py
        |   |   |-- 0002_auto_20231109_1904.py
        |   |   |-- 0003_chapter_video_path.py
        |   |   |-- 0004_rename_video_path_chapter_video_file_path.py
        |   |   |-- 0005_alter_chapter_status.py
        |   |   |-- 0006_alter_chapter_status.py
        |   |   |-- 0007_alter_chapter_status.py
        |   |   |-- 0008_alter_chapter_video_title.py
        |   |   `-- __init__.py
        |   |-- models.py
        |   |-- tests.py
        |   |-- urls.py
        |   `-- views.py
        |-- manage.py
        |-- project
        |   |-- __init__.py
        |   |-- asgi.py
        |   |-- celery.py
        |   |-- settings.py
        |   |-- settings_local.py
        |   |-- urls.py
        |   `-- wsgi.py
        |-- static
        |   |-- chara_icon.png
        |   `-- style.css
        |-- storage
        |   |-- comp_videos
        |   |   `-- init.txt
        |   |-- transcriptions
        |   |   `-- init.text
        |   `-- videos
        |       `-- init.txt
        `-- templates
            |-- base-top.html
            |-- base.html
            |-- edit.html
            |-- login.html
            |-- logout.html
            |-- main.html
            |-- signup.html
            |-- upload.html
            `-- user.html
</pre>

<p align="right">(<a href="#top">トップへ</a>)</p>

## 開発環境構築

<!-- コンテナの作成方法、パッケージのインストール方法など、開発環境構築に必要な情報を記載 -->

### コンテナの作成と起動

#### chapter/openai_api.env ファイルに以下の例のようにopenAIのAPIキーを記載

OPENAI_API_KEY = "sk-v9XXXXXXXXXXXXXXXXXXXXXXXXXXX"

#### chapter/src/project/settings_local.py ファイルに以下の例のようにDjangoのシークレットキー、S3へのアクセスキー・バケット名、メール通知用のアプリパスワード等を記載

> SECRET_KEY = 'django-insecure-XXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

>AWS_ACCESS_KEY_ID = 'AKIAXXXXXXXXXXXXXX'
>AWS_SECRET_ACCESS_KEY = 'ECXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
>AWS_STORAGE_BUCKET_NAME = 'XXXXXXXXXXXXXXXX'

>EMAIL_HOST = 'smtp.gmail.com'
>EMAIL_PORT = 587
>EMAIL_HOST_USER = 'XXXXXXXXXX@gmail.com'
>EMAIL_HOST_PASSWORD = 'XXXXXXXXXXXXXXXX'
>EMAIL_USE_TLS = True
>EMAIL_USE_SSL = False
>DEFAULT_FROM_EMAIL = 'XXXXXXXXXX@gmail.com'

#### GPUを使用するのであれば、docker-compose.ymlファイルのdjangoコンテナと以下のコメントアウトを外す(cpuを使用するのであればそのまま)

services:  
  django:

    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - capabilities: [gpu]

services:  
  celery:

    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - capabilities: [gpu]


#### 以上を修正後、以下のコマンドで環境を構築

docker compose up

### 動作確認

http://127.0.0.1 か、http://localhostにアクセスできるか確認
アクセスできたら成功

### コンテナの停止

以下のコマンドでコンテナを停止することができます

docker compose stop

### 環境変数の一覧

| 変数名                 | 役割                                      |
| ---------------------- | ----------------------------------------- |
| SECRET_KEY    | Djangoのシークレットキー（Djangoのproject新規作成時にsettings.pyに記載される。） |
| ALLOWED_HOSTS          | Djangoにリクエストを許可するホスト名              | 
| DEBUG                  | デバッグモードの切り替え                  |
| TRUSTED_ORIGINS        | CORS で許可するオリジン                   |
| MYSQL_PASSWORD         | MySQL のパスワード（Docker で使用）       | 
| MYSQL_HOST             | MySQL のホスト名（Docker で使用）         | 
| MYSQL_PORT             | MySQL のポート番号（Docker で使用）       |
| AWS_ACCESS_KEY_ID         | AWSにS3バケットを作成し、IAMからアクセスキーを取得しておく   |
| AWS_SECRET_ACCESS_KEY             | AWS_ACCESS_KEY_IDと同時に作成される         |
| AWS_STORAGE_BUCKET_NAME             | AWSのS3のバケット名                 |
| EMAIL_HOST | メールサーバーを指定   |
| EMAIL_PORT          | TLSを使うなら587、SSLを使うなら465              | 
| EMAIL_HOST_USER                  | メールサーバーのメールアカウント                  |
| EMAIL_HOST_PASSWORD        | メールサーバーで取得したアプリパスワード（gmailの場合、ログインパスワードとは別に作成必要）                   |
| DEFAULT_FROM_EMAIL | 送信者のメールアドレス   |


### コマンド一覧

| コマンド                | 実行する処理                                                            |
| ------------------- | ----------------------------------------------------------------------- |
| docker compose up        | ymlファイルのとおりコンテナ起動（Windowsはdocker「-」compose） |
| docker compose stop        | コンテナ停止 |
| docker compose down        | コンテナ停止・削除 |
| sh .docker_clear.sh        | コンテナ停止・削除、imageも全削除 |
| docker compose exec django python3 manage.py makemigrations        | Djangoのmodel.pyを変更したら、migrationファイルを作成 |
| docker compose exec django python3 manage.py migrate        | Djangoのmigrationファイルをデータベースに反映（注意！：既にデータが何かMySQLに入っていると、反映できずにエラーします。） |
| docker compose exec django python3 manage.py collectstatic        | Djangoのcssファイルを適用（本番環境ではこれを実行しないとdjangoコンテナの作成でエラーします。） |
| docker compose exec django python3 manage.py createsuperuser        | Django管理者用アカウントを作成 |
| docker compose run db mysql -u user -p password        | dbコンテナに入る |


<p align="right">(<a href="#top">トップへ</a>)</p>


## トラブルシューティング

### djangoコンテナ又はceleryコンテナが立ちあがらない原因
- settings_local.pyの環境設定が不十分
<br>
<br>

  

### 「celeryエラー」する原因
基本的には、エラーコードをググってください。
以下は実際にあったエラーの原因です。
- ログインユーザーのメールアドレスが空白又は使えないアドレスを設定した。
- chatGPTのAPI利用上限に達した。
- chatGPTの3.5-turboのAPIで、gpt4を使おうとした。（chapter_app/create_chapter.py修正ミス）
- CPUしか使えないのに、GPU処理を使うよう設定した。（yml修正ミス）
- CPUしか使えない環境で文字起こしをすると、PCスペック不足・dockerのリソース不足（主にメモリ不足）の場合、文字起こしのfaster-whisperが落ちます。（メモリ８GB以上を推奨）




<p align="right">(<a href="#top">トップへ</a>)</p>

