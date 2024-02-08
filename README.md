
# video-learn
チャプター&要約を自動生成してくれる動画共有アプリ

※このアプリは以下の自動チャプター生成アプリをもとに作成しています
https://github.com/hackathon-autumn-c/chaptan

<br/>
<br/>

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
  <img src="https://img.shields.io/badge/-Redis-FC687D.svg?logo=redis&style=for-the-badge&logoColor=white">

  <!-- インフラ一覧 -->
  <img src="https://img.shields.io/badge/-Docker-1488C6.svg?logo=docker&style=for-the-badge">
  <img src="https://img.shields.io/badge/-Amazon%20aws-232F3E.svg?logo=amazon-aws&style=for-the-badge">
</p>
<br/>

## 目次

1. [プロジェクトについて](#プロジェクトについて)
2. [環境](#環境)
3. [ディレクトリ構成](#ディレクトリ構成)
4. [開発環境構築](#開発環境構築)
5. [トラブルシューティング](#トラブルシューティング)
<br/>

<!-- プロジェクトについて -->

## プロジェクトについて

チャプター&要約を自動生成してくれる動画共有アプリ

<!-- プロジェクトの概要を記載 -->

  - 動画の共有サイト
  - 動画をアップロードすると文字起こしを行い、それをもとにチャプターと要約を自動生成します
  - スクールなどの学習環境での利用を想定。講師が講義動画をアップロードし生徒が視聴するイメージです
  - 生徒は動画の視聴、、要約の閲覧、文字起こしのダウンロードが可能
  - 講師は動画のアップロード、視聴、文字起こしのダウンロード、チャプターの編集、要約の編集、動画の削除が可能(編集は自分のアップロードした動画のみ)
  - 内部の仕組みとしては、faster-whisperで動画の文字起こしを実行、文字起こしテキストをもとにchatGPTでチャプターと要約を生成。

<p align="right">(<a href="#top">トップへ</a>)</p>

<br/>

## 環境

<!-- 言語、フレームワーク、ミドルウェア、インフラの一覧とバージョンを記載 -->

| 言語・フレームワークなど  | バージョン |
| --------------------- | ---------- |
| Python                | 3.9        |
| Django                | 3.2.23     |
| uWSGI                 | 2.0.23     |
| mysqlclient           | 2.1.0      |
| typing-extensions　   | 4.9.0      | 
| langchain　           | 0.1.0      | 
| openai　              | 1.7.1      | 
| langchain_openai      | 0.0.2      |
| celery　              | 5.3.6      | 
| django-celery-results | 2.5.1      | 
| django-redis　        | 5.4.0      | 
| boto3　               | 1.34.10    | 
| django-storages　     | 1.14.2     | 
| sagemaker　           | 2.203.0    | 
| django-mdeditor　     | 0.1.20     | 
| Markdown　            | 3.5.1      | 
| opencv-python　       | 4.8.1.78   | 

| Dockerimageとして使用  | バージョン |
| --------------------- | ---------- |
| MySQL                 | 8.0        |
| nginx 1.24.0          | 1.24.0     |
| redis                 | latest     |


<p align="right">(<a href="#top">トップへ</a>)</p>
<br/>

## ディレクトリ構成

<!-- Treeコマンドを使ってディレクトリ構成を記載 -->
<pre>
.
`-- video-learn
    |-- Docker
    |   |-- Django
    |   |   |-- Dockerfile
    |   |   `-- requirements.txt
    |   |-- MySQL
    |   |   `-- Dockerfile
    |   |-- Nginx
    |   |    |-- conf
    |   |    |   `-- app_nginx.conf
    |   |    `-- uwsgi_params
    |   `-- Sage_Docker
    |       `-- Dockerfile
    |-- sql
    |   `-- init.sql
    |-- src
    |   |-- chapter_app
    |   |   |-- migrations
    |   |   |-- templatetags
    |   |   |-- __init__.py
    |   |   |-- admin.py
    |   |   |-- apps.py
    |   |   |-- forms.py
    |   |   |-- models.py
    |   |   |-- processing.py
    |   |   |-- sage_whisper.py
    |   |   |-- tests.py
    |   |   |-- urls.py
    |   |   `-- views.py
    |   |-- media    
    |   |-- project
    |   |   |-- __init__.py
    |   |   |-- asgi.py
    |   |   |-- celery.py
    |   |   |-- settings.py
    |   |   |-- settings_local.py
    |   |-- urls.py
    |   |   `-- wsgi.py
    |   |-- static
    |   |   `-- style.css
    |   |-- templates
    |   |   |-- base-top.html
    |   |   |-- base.html
    |   |   |-- chapter_edit.html
    |   |   |-- login.html
    |   |   |-- logout.html
    |   |   |-- main.html
    |   |   |-- summary_edit.html
    |   |   |-- summary.html
    |   |   |-- upload.html
    |   |   |-- user.html
    |   |   `-- video.html
    |   `-- manage.py
    |-- static
    |-- docker-compose.yml
    |-- openai_api.env
    `-- README.md
</pre>

<p align="right">(<a href="#top">トップへ</a>)</p>
<br/>

## 開発環境構築

developブランチ：ローカル用<br>
mainブランチ：AWSへのデプロイ用

<!-- コンテナの作成方法、パッケージのインストール方法など、開発環境構築に必要な情報を記載 -->

### 1.コンテナの作成と起動
  1. OpenAIのサイトでOPENAI_API_KEYを取得する。
  2. AWSで下記を設定する
   ・IAMユーザーのアクセスキーを取得する
   ・S3でアプリ用のバケットを作成する
   ・Docker/Sage_Docker/Dockerfileをもとにdockerイメージを作成し、ECRのプライベートリポジトリにプッシュする
   ・Sagemaker用のIAMロールを作成し、Sagemaker、S3、ECRのFullAccess権限を与える

　3. video_learn/openai_api.envファイルを作成し以下を記載
```
OPENAI_API_KEY = 'OpenAIサイトで取得したAPIキー'
AWS_DEFAULT_REGION = 'AWSのリージョン'
AWS_ACCESS_KEY_ID = 'IAMユーザーのアクセスキー'
AWS_SECRET_ACCESS_KEY = "AWSシークレットアクセスキー"
```
　4. video_learn/src/project/settings_local.pyファイルを作成し以下を記載

```
SECRET_KEY = 'Djangoのシークレットキー（Djangoのproject新規作成時にsettings.pyに記載される。）'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = 'IAMユーザーのアクセスキー'
AWS_SECRET_ACCESS_KEY = 'IAMユーザーのシークレットアクセスキー'
AWS_STORAGE_BUCKET_NAME = 'AWSのS3のバケット名'
IMAGE_URI = '手順2でプッシュしたDockerイメージのURI'
ROLE = '手順2で作成したSagemaker用のIAMロールのARN'
AWS_S3_REGION_NAME = 'AWSのリージョン'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'メールサーバーを指定'
EMAIL_PORT = 'TLSを使うなら587、SSLを使うなら465'
EMAIL_HOST_USER = 'メールサーバーのメールアカウント'
EMAIL_HOST_PASSWORD = 'メールサーバーで取得したアプリパスワード（gmailの場合、ログインパスワードとは別に作成必要）'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = '送信者のメールアドレス'
```
　3. 以下のコマンドを実行
```
docker compose up
docker compose exec django python manage.py makemigrations	
docker compose exec django python manage.py migrate
docker compose exec django python3 manage.py createsuperuser
```

### 2.動作確認

http://127.0.0.1 か、http://localhost にアクセスできるか確認
アクセスできたら成功

### 3.コンテナの停止

以下のコマンドでコンテナを停止することができます

```
docker compose stop
```

### コマンド一覧

| コマンド                | 実行する処理                                                            |
| ------------------- | ----------------------------------------------------------------------- |
| docker compose up        | ymlファイルのとおりコンテナ起動 |
| docker compose stop        | コンテナ停止 |
| docker compose down        | コンテナ停止・削除 |
| sh .docker_clear.sh        | コンテナ停止・削除、imageも全削除 |
| docker compose exec django python3 manage.py makemigrations        | Djangoのmodels.pyを変更したら、migrationファイルを作成 |
| docker compose exec django python3 manage.py migrate        | Djangoのmigrationファイルをデータベースに反映（注意！：既にデータが何かMySQLに入っていると、反映できずにエラーします。） |
| docker compose exec django python3 manage.py collectstatic        | Djangoのcssファイルを適用（本番環境ではこれを実行しないとdjangoコンテナの作成でエラーします。） |
| docker compose exec django python3 manage.py createsuperuser        | Django管理者用アカウントを作成 |
| docker compose run db mysql -u user -p password        | dbコンテナに入る |


<p align="right">(<a href="#top">トップへ</a>)</p>
<br/>

## トラブルシューティング

### djangoコンテナ又はceleryコンテナが立ちあがらない原因
- settings_local.pyの環境設定が不十分
- S3バケットのポリシー設定が不十分
### ステータスが「処理エラー」になる原因
以下は実際にあったエラーの原因です。
- ログインユーザーのメールアドレスが空白又は使えないアドレスを設定した。
- chatGPTのAPI利用上限に達した。
- chatGPTのモデル違い

<p align="right">(<a href="#top">トップへ</a>)</p>

<br>

## その他
　レスポンシブ未対応です



<p align="right">(<a href="#top">トップへ</a>)</p>

