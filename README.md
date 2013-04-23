oyakata
==========

**親方!空から女の子が!**  
と言った時、  
Procfile を元に2番のバルブを閉めろと返してくれるアプリケーションです。

inspired [gaffer](https://github.com/benoitc/gaffer)

インストール
----------------

`pip install oyakata`

これで空から降ってきた女の子をキャッチ出来るようになります。

作業の流れ
----------------

1. oyakatad を起動します  
	`oyakatad -c /path/to/oyakata.toml`
2. 管理したいアプリケーションのディレクトリに行って  
	`oyakata load`  
   と実行することでアプリケーションが起動します。  
   `oyakata load` で登録した Procfile は次回 OS 起動時、  
   `oyakatad` が立ち上がったタイミングで同時に起動されます。


親方の使い方
----------------------

####親方に仕事をお願いします。

`oyakata load`

####親方から仕事を取り上げます。

`oyakata unload`

####親方に新しい設定で仕事をやり直してもらいます。

`oyakata reload`

####政府の密命

`oyakata muska`

もっと詳しい使い方はドキュメントを読んで下さい。


Launch Oyakatad
---------------------

###upstart
[oyakata.conf](http://gist)

