DROP DATABASE video_learn;
DROP USER 'user';

CREATE USER 'user' IDENTIFIED BY 'userpass';
CREATE DATABASE video_learn;
USE video_learn;
GRANT ALL PRIVILEGES ON video_learn.* TO 'user';

FLUSH PRIVILEGES;

-- 以下のコマンドで実行する
-- source /home/ubuntu/video_learn/sql/init.sql