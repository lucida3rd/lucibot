---------------------------------
  るしぼっと4　セットアップ手順
    ::Admin= Lucida（lucida3rd@mstdn.mynoghra.jp）
    ::github= https://github.com/lucida3rd/lucibot
---------------------------------
＜概要＞
るしぼっとのセットアップ手順を示します。
機能概要、バージョンアップ方法、その他については readme.txt をご参照ください。
　readme.txt：https://github.com/lucida3rd/lucibot/blob/master/readme.txt


＜目次＞
◆前提
◆セットアップ
◆twitter APIの取得方法
◆デフォルトエンコードの確認
◆MeCabのインストール

---------------------------------
＜前提＞
・mastodon v2.7.2以上（バージョンが異なると一部APIの挙動が異なる場合があるようです）
・CentOS7
・python3（v3.7で確認）
・cron（CentOS7だとデフォルトで動作している認識です）
・セットアップした鯖のmastodonのアカウント（必要数分。マルチアカウント対応。）
・twitterアカウント（なくても動作します）
・githubアカウント
・OSのデフォルトエンコード：utf-8

※githubアカウントがなくても運用にこぎつけることはできますが、
　バージョン管理できないのでここではgithub垢持ってる前提で記載します。

※以上の前提が異なると一部機能が誤動作の可能性があります


---------------------------------
＜githubアカウントの取り方＞
おそらくこのドキュメントを見られてる方はgithubアカウントをお持ちと思いますが、
念のため。githubのホームページから取得できます。
　github：https://github.com


---------------------------------
＜セットアップ＞
るしぼっとリポジトリのmasterから最新版をpullする方法で記載します。
中級者、上級者の方で管理がめんどければforkしちゃっても問題ないです。
（※readmetxtの下のほうの免責事項はお読みください）

Linuxサーバでの作業となります。まずroot権限で開始します。

1.るしぼっと専用のユーザを作ります。
# useradd [ユーザ名]
# passwd [パスワード]
　パスワードは2回入力を求められます

　ここで念のためユーザのIDをメモします。※後ででもよいです
# id [ユーザ名]

2. 1で登録したユーザに切り替える。
# su - [ユーザ名]
　念のためホームフォルダをメモします
$ pwd

3.ホームフォルダにるしぼっとのcloneを作成します。
$ git clone https://github.com/lucida3rd/lucibot.git bot
　clone先のフォルダ名は任意です。この手順では"bot"というフォルダでcloneされます。

4.るしぼっとデータ格納用のフォルダを作成します。
$ mkdir botdata
  フォルダはcloneを置いた上位フォルダ(=cloneと同一階層)に作成します。

5.root権限に戻って必要なライブラリをインストールします。
$ exit
# pip3 install requests requests_oauthlib
# pip3 install psutil
# pip3 install pytz
# pip3 install python-dateutil
# pip3 install mecab-python3
# pip3 install python-crontab

　インストールしたライブラリがあるか確認します。
# su - [ユーザ名]
$ pip3 list
$ exit

6.デフォルトエンコードを確認する。
　OSのデフォルトエンコードがutf-8かを確認します。
　以下＜デフォルトエンコードの確認＞をご参照ください。

7.MeCabをインストールする。
　以下＜MeCabのインストール＞をご参照ください。


---------------------------------
＜twitter APIの取得方法＞

1.以下、twitterのサイトにtwitterアカウントでログインします。
　https://apps.twitter.com/app/new

2.以下を入力し、登録します。
　・Name（アプリ名）
　・Description（アプリの説明）
　・Website（自分のブログのURLなど）
　・Callback URLは空欄でOKです。

3.Detailsタブの以下をメモします。
　★Consumer key
　★Consumer secret

4.Settingタブをクリックし、Application TypeをRead and Wtireにして
　「Update this Twitter application’s settings」ボタンをクリックします。

5.Detailsタブに戻り、画面の最下部に「Create my access token」ボタンがあるのでクリックします。

6.以下をメモします。
　★Access token
　★Access token secret

★4つの情報はあとで設定します。


---------------------------------
＜デフォルトエンコードの確認：初回のみ＞
OSのデフォルトエンコードを確認したり、utf-8に設定する方法です。
uft-8に変更することで他のソフトやサービスに影響を及ぼす場合がありますので、
慎重に設定してください。（mastodonには影響ないです）

1.以下のコマンドでエンコードを確認。'utf-8'なら以下の手順は不要です。
# python
>>> import sys
>>> sys.getdefaultencoding()
'ascii'

2.site-packagesの場所を確認します。exit、ctrl+Dで抜けます。
>>> import site; site.getsitepackages()
>>> exit

3. 2項で表示されたsite-packagesディレクトリに _reg/sitecustomize.py を置きます。
　CentOS 64bit / python2の場合は /uer/lib64/python2.7/site-package/

4.再度1のコマンドを実行して、'utf-8'に変わることを確認します。

5.るしぼっと用のユーザでも確認します。
# su - [ユーザ名]
# python
>>> import sys
>>> sys.getdefaultencoding()
'ascii'


---------------------------------
＜MeCabのインストール：初回のみ＞
機械学習用にMeCabをインストールします。
いろいろインストール方法がありますが、ソースコードビルドからのインストールがシンプルです。
セットアップなのでrootで実行してもよいです。

1.ソースコードを解凍する
ソースコードの場所：
http://taku910.github.io/mecab/#download

# wget "[アーカイブのリンク]"
# tar xvzf "[アーカイブファイル名]"
# cd [解凍されたフォルダ]
※アーカイブがgoogle driveにあるらしく""で囲むといいです

2.MeCabをメイク→インストールする
# ./configure --with-charset=utf8
# make
# make install

3. 1と同じ場所からIPA辞書ソースコードを解凍する

4.IPA辞書をメイク→インストールする（コマンドはMeCabと一緒）

5.MeCab pythonをインストールする
# pip install mecab-python

6.動作テスト
# mecab
本マグロってホンマにグロいのかな

本      接頭詞,名詞接続,*,*,*,*,本,ホン,ホン
マグロ  名詞,一般,*,*,*,*,マグロ,マグロ,マグロ
って    助詞,格助詞,連語,*,*,*,って,ッテ,ッテ
ホンマに        副詞,一般,*,*,*,*,ホンマに,ホンマニ,ホンマニ
グロ    名詞,一般,*,*,*,*,グロ,グロ,グロ
い      動詞,非自立,*,*,一段,連用形,いる,イ,イ
の      名詞,非自立,一般,*,*,*,の,ノ,ノ
か      助詞,副助詞／並立助詞／終助詞,*,*,*,*,か,カ,カ
な      助詞,終助詞,*,*,*,*,な,ナ,ナ
EOS

7.ライブラリの位置を確認する。
# echo `mecab-config --dicdir`"/mecab-ipadic-neologd"

8.共通ライブラリにパスを通しておく
# mecab-config --libs-only-L | sudo tee /etc/ld.so.conf.d/mecab.conf
# ldconfig


参考にした記事：
https://blogs.yahoo.co.jp/tsukada816/39196715.html


