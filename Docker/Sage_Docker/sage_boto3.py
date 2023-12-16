import boto3
import sagemaker
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput

#role = get_execution_role()
# リージョンを指定する
session = boto3.Session(region_name='ap-northeast-1')  # 例: 'us-west-2'
sagemaker_session = sagemaker.Session(boto_session=session)


script_processor = ScriptProcessor(
                image_uri='ECRプライベートリポジトリのイメージURI',
                role= 'Sagemaker用のIAMロールのARN',
                command=['python3'],
                instance_count=1,
                instance_type='ml.g4dn.xlarge')

script_processor.run(code='sage_whisper.py',
                     inputs=[ProcessingInput(
                        source='s3://s3-chapter/storage/videos/20231115_775.mp4',
                        destination='/opt/ml/processing/input')],
                     outputs=[ProcessingOutput(
                        source='/opt/ml/processing/output',
                        destination='s3://s3-chapter/storage/transcriptions/')],
                        arguments=['--video_title', '20231115_775'])