## るしぼっと4　セットアップ手順
::Admin= Lucida（lucida3rd@mstdn.mynoghra.jp）  
::github= https://github.com/lucida3rd/lucibot  


## 概要
るしぼっとのセットアップ手順を示します。  
機能概要、バージョンアップ方法、その他については readme.md をご参照ください。  
* [readme.md](https://github.com/lucida3rd/lucibot/readme.md)



## 目次
* [前提](#iPremise)
* [githubアカウントの取り方](#iGetGithub)
* [セットアップ](#iSetup)
* [twitter APIの取得方法](#iGetTwitter)
* [デフォルトエンコードの確認](#iDefEncode)
* [MeCabのインストール](#iMecabInstall)



<a id="iPremise"></a>
## 前提
* mastodon v2.7.2以上（バージョンが異なると一部APIの挙動が異なる場合があるようです）
* CentOS7
* python3（v3.7で確認）
* cron（CentOS7だとデフォルトで動作している認識です）
* セットアップした鯖のmastodonのアカウント（必要数分。マルチアカウント対応。）
* twitterアカウント（なくても動作します）
* githubアカウント
* OSのデフォルトエンコード：utf-8

```
※githubアカウントがなくても運用にこぎつけることはできますが、バージョン管理できないのでここではgithub垢持ってる前提で記載します。
※以上の前提が異なると一部機能が誤動作の可能性があります。
```



<a id="iGetGithub"></a>
## githubアカウントの取り方
おそらくこのドキュメントを見られてる方はgithubアカウントをお持ちと思いますが念のため。  
githubのホームページから取得できます。  
* github：(https://github.com)



<a id="iSetup"></a>
## セットアップ
るしぼっとリポジトリのmasterから最新版をpullする方法で記載します。  
中級者、上級者の方で管理がめんどければforkしちゃっても問題ないです。  
（※readmetxtの下のほうの免責事項はお読みください）  
  
Linuxサーバでの作業となります。まずroot権限で開始します。  
  
1.るしぼっと専用のユーザを作ります。

```
# useradd [ユーザ名]
# passwd [パスワード]
　パスワードは2回入力を求められます

ここで念のためユーザのIDをメモします。※後ででもよいです。
# id [ユーザ名]  
```
  
2. 1で登録したユーザに切り替える。

```
# su - [ユーザ名]
　念のためホームフォルダをメモします
$ pwd
```
  
3.ホームフォルダにるしぼっとのcloneを作成します。

```
$ git clone https://github.com/lucida3rd/lucibot.git bot
　clone先のフォルダ名は任意です。この手順では"bot"というフォルダでcloneされます。
```
  
4.るしぼっとデータ格納用のフォルダを作成します。

```
$ mkdir botdata
  フォルダはcloneを置いた上位フォルダ(=cloneと同一階層)に作成します。
```
  
5.root権限に戻って必要なライブラリをインストールします。

```
$ exit
# pip3 install requests requests_oauthlib
# pip3 install psutil
# pip3 install pytz
# pip3 install python-dateutil
# pip3 install python-crontab
# pip3 install psycopg2
# php3 install pyOpenSSL

　インストールしたライブラリがあるか確認します。
# su - [ユーザ名]
$ pip3 list
$ exit
```
  
6.デフォルトエンコードを確認する。  
　OSのデフォルトエンコードがutf-8かを確認します。  
　以下 [デフォルトエンコードの確認](#iDefEncode) をご参照ください。  
  
7.MeCabをインストールする。  
　以下 [MeCabのインストール](#iMecabInstall) をご参照ください。  

8.Databaseを作成する。  

```
# su - [postgreSQLのマスターユーザ]  
$ psql  
=> create database [ユーザ名];  
=> create role [ユーザ名] with password '[DBパスワード]';  
=> alter role [ユーザ名] with login;  
=> \q  
$ psql -l  
  Databaseができていることを確認します。  
$ exit  
```



<a id="iGetTwitter"></a>
## twitter APIの取得方法
1.以下、twitterのサイトにtwitterアカウントでログインします。  
  (https://apps.twitter.com/app/new)  
  
2～5 までの項目ではDeveropper Accountの設定をおこないます。  
  ※設定済なら6へ進む
  
2.「Create an app」をクリックします。  
  
3.HObby list→Making botをクリックしてNextを押します。  
  
4.各項目を入力し、Nextを押します。  
  What country do you live in? はJapanを選択します。  
  What would you like us to call you? はDeveropper Accountでのユーザ名（英数字）を入力します。  
  Want updates about the Twitter API? は必要に応じてチェックします。  
  
5.各項目にbotを作成する用途を英語で入力し、Nextを押します。  
  In your words以外は「NO」にチェックしてもいいかもしれません。  
  最後に「Looks good!」を押します。  
  
6.「Create an app」をクリックします。  
  
7.以下の必須項目を入力し、登録します。  
* App name（アプリ名）  
  アプリ名は他と重複するのはNGっぽいです  
* Application description（アプリの説明）  
* Website URL（自分のブログのURLなど）  
* Enable Sign in with Twitter をチェック  
* Callback URL（コールバックしないので適当、自分のブログURLなどでいいです）  
* Tell us how this app will be used にアプリの用途を入力します。  
  
8.「Create」を2回クリックします。  
  
9.Key and Tokensタブの以下をメモします。
* Consumer API
* Consumer API Secret key
  
10.Consumer API Secret keyの下のAccess Tokenの「Create」をクリックします。  
  
11.以下をメモします。
* Access token
* Access token secret

```
4つの情報はあとで設定します。
```



<a id="iDefEncode"></a>
## デフォルトエンコードの確認 ★初回のみ設定
OSのデフォルトエンコードを確認したり、utf-8に設定する方法です。  
uft-8に変更することで他のソフトやサービスに影響を及ぼす場合がありますので、
慎重に設定してください。（mastodonには影響ないです）  
  
1.以下のコマンドでエンコードを確認。'utf-8'なら以下の手順は不要です。

```
# python
>>> import sys
>>> sys.getdefaultencoding()
'ascii'
  ※utf-8が表示された場合、2項以降は不要です。
```
  
2.site-packagesの場所を確認します。exit、ctrl+Dで抜けます。

```
>>> import site; site.getsitepackages()
>>> exit
```
  
3. 2項で表示されたsite-packagesディレクトリに _reg/sitecustomize.py を置きます。  
　CentOS 64bit / python2の場合は /uer/lib64/python2.7/site-package/  
  
4.再度1のコマンドを実行して、'utf-8'に変わることを確認します。  
  
5.るしぼっと用のユーザでも確認します。

```
# su - [ユーザ名]
# python
>>> import sys
>>> sys.getdefaultencoding()
'ascii'
```



<a id="iMecabInstall"></a>
## MeCabのインストール ★初回のみ設定
機械学習用にMeCabをインストールします。  
いろいろインストール方法がありますが、ソースコードビルドからのインストールがシンプルです。  
セットアップなのでrootで実行してもよいです。  
  
1.ソースコードを解凍する  
  ソースコードの場所：(http://taku910.github.io/mecab/#download)  

```
# wget "[アーカイブのリンク]"
# tar xvzf "[アーカイブファイル名]"
# cd [解凍されたフォルダ]
  ※アーカイブがgoogle driveにあるらしく""で囲むといいです
```
  
2.MeCabをメイク→インストールする

```
# ./configure --with-charset=utf8
# make
# make install
```
  
3. 1と同じ場所からIPA辞書ソースコードを解凍する。  
  
4.IPA辞書をメイク→インストールする。（コマンドはMeCabと一緒）  
  
5.MeCab pythonをインストールする。  

```
# pip3 install mecab-python3
```
  
6.動作テスト

```
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
```
  
7.ライブラリの位置を確認する。

```
# echo `mecab-config --dicdir`"/mecab-ipadic-neologd"
```

8.共通ライブラリにパスを通しておく。

```
# mecab-config --libs-only-L | sudo tee /etc/ld.so.conf.d/mecab.conf
# ldconfig
```
  
参考にした記事：(https://blogs.yahoo.co.jp/tsukada816/39196715.html)  


