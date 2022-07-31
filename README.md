# PixivTracer
指定したPixivユーザのブックマークをDiscordやSlackに投稿します

# 実行方法
下記の通りに環境変数を設定する  
| 環境変数名 | 説明 |
| --- | ---|
| COOKIE | クローラーがPixivにログインするためのcookie情報 |
| INTERVAL | クローラーがPixivにアクセスする周期(sec) |
| DISCORD_ENDPOINT | Webhookのエンドポイント(Discord) |
| SLACK_ENDPOINT | Webhookのエンドポイント(Slack) |
| USER | 監視対象のユーザ名 |
| ID | 監視対象のユーザID |

適当に必要そうなパッケージをインストールして `run.py` を実行．

## cookieの取得方法・フォーマット
1. シークレットモードでpixivにアクセスする
1. F12で開発者ツールを開く
1. ログイン情報を入力してログインする
1. NetworkのタブからHeadersのタブを開いてcookieのフィールドの値をコピーする

![image](https://user-images.githubusercontent.com/49583698/182020575-f69e3296-678a-41c3-bf67-51ce3df64b23.png)

## Dockerでの実行
下記のdocker-composeファイルに環境変数を設定することで実行できる  
```yml
version: '3'

services:
  pixiv_tracer:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: pixiv_tracer
    restart: always
    environment:
      COOKIE: "xxx"
      INTERVAL: 10
      DISCORD_ENDPOINT: "xxx"
      SLACK_ENDPOINT: "xxx"
      USER: "xxx"
      ID: xxx
```

# 実行例
## discord
![image](https://user-images.githubusercontent.com/49583698/182038412-d4df44f0-b668-4a9e-85cf-ee332f2fbaf8.png)

## slack
![image](https://user-images.githubusercontent.com/49583698/182038510-e065babd-371d-4361-9906-db6c45231aeb.png)

# コメント
コメント，PR募集しています．Twitter: `@_ma1750_`
