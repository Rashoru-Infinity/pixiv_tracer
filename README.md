# HGWR

# 実行方法
コンフィグファイルを以下の形式で用意する．  
適当に必要そうなパッケージをインストールして `run.py` を実行．

# 実行例
## discord
![image](https://user-images.githubusercontent.com/43315739/181920772-b43af186-c7f4-4224-ba07-b1121b293496.png)


## slack
![image](https://user-images.githubusercontent.com/43315739/181920796-9d5436a7-6084-4a36-b0cf-2f79b4686f99.png)


# configファイル
```json
{
    "cookie": {},
    "interval": 60,
    "webhook_endpoints": [],
    "users": [
        {
            "name": "regedit",
            "id": 30815700
        },
        {
            "name": "aabbdd129",
            "id": 7181059
        },
        {
            "name": "ma_1750",
            "id": 11451301
        }
    ]
}
```

- cookie: Pixivにログインしたときのcookieをブラウザのデベロッパーツールから持ってくる．  
          ログインを実装できないので．👈 こいつダサすぎて草．プログラミング初心者かな？  
          ※コピーしてそのままだと `=` と `;` で構成されているので手動でjson形式にする．
- inteval: クローリングする間隔．int，単位は秒．デフォルト60秒．常識的な範囲で．
- webhook_endpoints: 通知先のwebhookのアドレスのリスト．現在，slack or discordのみ対応．
- users: 監視したいユーザ．ユーザ名とID．少なくとも1人は書いておこう．オススメは30815700．
    - name: 表示名
    - id: ユーザID


# コメント
コメント，PR募集しています．Twitter: `@_ma1750_`
