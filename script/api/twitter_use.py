#!/usr/bin/python
# coding: UTF-8
#####################################################
# public
#   Class   ：ついったーユーズ
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/11/22
#####################################################
# Private Function:
#   __initIniStatus(self):
#   __Get_Resp(self):
#   __loadTwitter( self, inPath ):
#   __checkTwitter(self):
#   __NoConn( self, inPath ):
#   __conn(self):
#   __TwitterPing(self):
#
# Instance Function:
#   __init__( self, inPath=None, inGetNum=120, inNoConn=False ):
#   GetInisStatus(self):
#   GetUsername(self):
#   CreateTwitter( self, inDstPath, inSrcPath ):
#   CnfTimeline( self, inPath ):
#   SaveTwitter( self, inPath ):
#
# ◇Twitter接続・切断
#   Connect( self, inPath=None ):
#   
# ◇タイムライン制御系
#   Tweet( self, inTweet ):
#   GetTL(self):
#   GetLists(self):
#
# Class Function(static):
#   (none)
#
#####################################################
# 使い方：
#  1.Twitterでトークンを取得する。
#  2.CreateTwitter( inDstPath, inSrcPath )をコールして接続情報をセットする。
#    inDstPath ..接続情報の元フォーマット(text)
#    inDstPath ..接続情報のパス
#
#  ＜接続情報(text)の書式＞
#----------------------
#TwitterUser=
#twCK=
#twCS=
#twAT=
#twAS=
#----------------------
#  3.Connect( inPath=None )で接続する。
#
#####################################################
# 参考：
#   twitter api rate
#     https://developer.twitter.com/en/docs/basics/rate-limits
#
#####################################################
import os
import codecs
import json
import shutil
import subprocess as sp
from requests_oauthlib import OAuth1Session

#####################################################
class CLS_Twitter_Use():
	Twitter_use = ''						#Twitterモジュール実体
	IniStatus = ""

	STR_TWITTERdata = {
		"TwitterUser"	: "",
		"twCK"			: "",
		"twCS"			: "",
		"twAT"			: "",
		"twAS"			: "",
	}
	
	VAL_TwitNum = 200

	DEF_TWITTER_HOSTNAME = "twitter.com"	#Twitterホスト名
	DEF_MOJI_ENCODE      = 'utf-8'			#ファイル文字エンコード
	DEF_TWITTER_PING_COUNT   = "2"			#Ping回数 (文字型)
##	DEF_TWITTER_PING_TIMEOUT = "1000"		#Pingタイムアウト秒 (文字型)

	#トレンド地域ID
#	DEF_WOEID = "1"				#グローバル
	DEF_WOEID = "23424856"		#日本
		# idにはWOEID Lookupの地域IDを入れる
		#   http://woeid.rosselliot.co.nz/
		#   なんだけどエラー？で取得できない。なんやこれ...



#####################################################
# 初期化状態取得
#####################################################
	def GetIniStatus(self):
		return self.IniStatus	#返すだけ



#####################################################
# ユーザ名取得
#####################################################
	def GetUsername(self):
		if self.STR_TWITTERdata['TwitterUser']=='' :
			return ""
		
		wUser = self.STR_TWITTERdata['TwitterUser'] + "@" + self.DEF_TWITTER_HOSTNAME
		return wUser



#####################################################
# 初期化状態取得
#####################################################
	def __initIniStatus(self):
		self.IniStatus = {
			"Result"   : False,
			"Reason"   : None,
			"Responce" : None
		}
		return



#####################################################
# レスポンス取得
#####################################################

##		#############################
##		# 応答形式の取得
##		#   "Result" : False, "Reason" : None, "Responce" : None
##		wRes = CLS_OSIF.sGet_Resp()

	def __Get_Resp(self):
		wRes = {
			"Result"   : False,
			"Reason"   : None,
			"Responce" : None }
		
		return wRes



#####################################################
# 初期化
#####################################################
	def __init__( self, inPath=None, inGetNum=200, inNoConn=False ):
		if inNoConn==True :
			##未接続モードで初期化
			self.__NoConn( inPath )
			return
		
		self.VAL_TwitNum = inGetNum
		self.Connect( inPath )
		return



#####################################################
# twitter接続情報の作成 ※対話型
#####################################################
	def CreateTwitter( self, inDstPath, inSrcPath ):
		#############################
		# Twitter接続情報ファイルのチェック
		if( os.path.exists( inSrcPath )==False ) :
			##失敗
			wStr = "CLS_Twitter_Use: CreateTwitter: Default Twitter file is not found: " + inSrcPath + '\n'
			print( wStr )
			return False
		
		if( os.path.exists( inDstPath )==False ) :
			##ファイルがなければコピーする
			try:
				shutil.copyfile( inSrcPath, inDstPath )
			except ValueError as err :
				return False
		
		#############################
		# 開始
		wStr = "Twitterの接続情報の作成をおこないます。（※先ずTwitterへアプリの登録が済んでいることが前提となります）" + '\n'
		wStr = wStr + "Twitterの接続情報の作成をおこないますか？"
		print( wStr )
		wSelect = input( "作成する？(y/N)=> " ).strip()
		if wSelect!="y" :
			return True	#キャンセル
		
		#############################
		# twiterアカウント名
		wStr = '\n' + "Twitterのアカウント名(@twitter.com省略)を入力してください"
		print( wStr )
		wInput = input( "=> " ).strip()
		if wInput=="" :
			print( "Twitterの接続情報の作成がキャンセルされました" )
			return False	#キャンセル
		self.STR_TWITTERdata['TwitterUser'] = wInput
		
		#############################
		# Consumer key
		wStr = '\n' + "Twitterで取得したConsumer keyを入力してください"
		print( wStr )
		wInput = input( "=> " ).strip()
		if wInput=="" :
			print( "Twitterの接続情報の作成がキャンセルされました" )
			return False	#キャンセル
		self.STR_TWITTERdata['twCK'] = wInput
		
		#############################
		# Consumer Secret
		wStr = '\n' + "Twitterで取得したConsumer Secretを入力してください"
		print( wStr )
		wInput = input( "=> " ).strip()
		if wInput=="" :
			print( "Twitterの接続情報の作成がキャンセルされました" )
			return False	#キャンセル
		self.STR_TWITTERdata['twCS'] = wInput
		
		#############################
		# Access Token
		wStr = '\n' + "Twitterで取得したAccess Tokenを入力してください"
		print( wStr )
		wInput = input( "=> " ).strip()
		if wInput=="" :
			print( "Twitterの接続情報の作成がキャンセルされました" )
			return False	#キャンセル
		self.STR_TWITTERdata['twAT'] = wInput
		
		#############################
		# Access Token Secret
		wStr = '\n' + "Twitterで取得したAccess Token Secretを入力してください"
		print( wStr )
		wInput = input( "=> " ).strip()
		if wInput=="" :
			print( "Twitterの接続情報の作成がキャンセルされました" )
			return False	#キャンセル
		self.STR_TWITTERdata['twAS'] = wInput
		
		print( '\n' + "Twitterの接続テスト中......" + '\n' )
		#############################
		# Twitter接続テスト
		if self.__conn()!=True :
			#失敗
			wStr = "接続失敗: " + str(self.IniStatus['Reason'])
			print( wStr )
			return False	#キャンセル
		
		print( "Twitterに接続成功しました!!" + '\n' )
		
		print( "Twitterの接続情報の作成中......" + '\n' )
		if self.SaveTwitter( inDstPath )!=True :
			return False
		
		print( "Twitterの接続情報の作成 成功!!" + '\n' )
		return True




#####################################################
# twitter接続情報のロード
#####################################################
	def __loadTwitter( self, inPath ):
		#############################
		# Twitter接続情報 初期化
		self.STR_TWITTERdata['TwitterUser'] = ""
		self.STR_TWITTERdata['twCK'] = ""
		self.STR_TWITTERdata['twCS'] = ""
		self.STR_TWITTERdata['twAT'] = ""
		self.STR_TWITTERdata['twAS'] = ""
		
		#############################
		# 存在チェック
		wRes = os.path.exists( inPath )
		if wRes==False :
			self.IniStatus['Reason'] = "CLS_Twitter_Use: __loadTwitter: Twitter file is not found"
			return False
		
		#############################
		# DB接続情報に読み出す
		try:
			for wLine in open( inPath, 'r'):	#ファイルを開く
				wLine = wLine.strip()
				wLine = wLine.split("=")
				if len(wLine)!=2 :
					continue	#範囲違い
				if wLine[0] not in self.STR_TWITTERdata :
					continue	#ないパラメータ
				self.STR_TWITTERdata[wLine[0]] = wLine[1]
			
		except ValueError as err :
			self.IniStatus['Reason'] = "CLS_Twitter_Use: __loadTwitter: Load Twitter file Failed: " + err
			return False
		
		#############################
		# 正常
		return True



#####################################################
# twitter接続情報のセーブ
#####################################################
	def SaveTwitter( self, inPath ):
		#############################
		# 存在チェック
		wRes = os.path.exists( inPath )
		if wRes==False :
			self.IniStatus['Reason'] = "CLS_Twitter_Use: SaveTwitter: Twitter file is not found"
			return False
		
		#############################
		# 書き込みデータを作成
		wSetLine = []
		wKeylist = self.STR_TWITTERdata.keys()
		for iKey in wKeylist :
			wLine = iKey + "=" + str(self.STR_TWITTERdata[iKey]) + '\n'
			wSetLine.append(wLine)
		
		#############################
		# ファイル上書き書き込み
		try:
			wFile = codecs.open( inPath, 'w', self.DEF_MOJI_ENCODE )
			wFile.writelines( wSetLine )
			wFile.close()
		except ValueError as err :
			self.IniStatus['Reason'] = "CLS_Twitter_Use: SaveTwitter: Exception error: " + str(err)
			return False
		
		#############################
		# 正常
		return True



#####################################################
# twitter接続情報チェック
#####################################################
	def __checkTwitter(self):
		#############################
		# 状態のチェック
		if self.STR_TWITTERdata['TwitterUser']=="" or \
		   self.STR_TWITTERdata['twCK']=="" or \
		   self.STR_TWITTERdata['twCS']=="" or \
		   self.STR_TWITTERdata['twAT']=="" or \
		   self.STR_TWITTERdata['twAS']=="" :
			wMsg = "CLS_Twitter_Use: __checkTwitter: Load Twitter file Invalid: "
			wMsg = wMsg + "Twitter Account=" + self.STR_TWITTERdata['TwitterUser'] + " "
			wMsg = wMsg + "Consumerkey=" + self.STR_TWITTERdata['twCK'] + " "
			wMsg = wMsg + "ConsumerSecret=" + self.STR_TWITTERdata['twCS'] + " "
			wMsg = wMsg + "AccessToken=" + self.STR_TWITTERdata['twAT'] + " "
			wMsg = wMsg + "AccessToken Secret=" + self.STR_TWITTERdata['twAS']
			self.IniStatus['Reason'] = wMsg
			return False
		
		#############################
		# 正常
		return True



#####################################################
# 接続
#####################################################
	def Connect( self, inPath=None ):
		#############################
		# 状態初期化
		self.__initIniStatus()
		
		#############################
		# twitter接続情報のロード
		if inPath==None :
			self.IniStatus['Reason'] = "Twitter information file path is not specified"
			return False
		
		if self.__loadTwitter( inPath )!=True :
			return False
		
		#############################
		# 状態のチェック
		if self.__checkTwitter()!=True :
			return False
		
		#############################
		# twitterに接続
		if self.__conn()!=True :
			return False
		
		return True



#####################################################
# 未接続
#   ただ接続情報を読みたいだけ用の初期化
#####################################################
	def __NoConn( self, inPath ):
		#############################
		# 状態初期化
		self.__initIniStatus()
		
		#############################
		# twitter接続情報のロード
		if inPath==None :
			self.IniStatus['Reason'] = "Twitter information file path is not specified"
			return False
		
		if self.__loadTwitter( inPath )!=True :
			return False
		
		#############################
		# 状態のチェック
		if self.__checkTwitter()!=True :
			return False
		
		return True



#####################################################
# twitterに接続
#####################################################
	def __conn(self):
##		#############################
##		# 状態初期化
##		self.__initIniStatus()
		
		#############################
		# 通信テスト
		if self.__TwitterPing()!=True :
			self.IniStatus['Reason'] = "CLS_Twitter_Use: __conn: Twitter host no responce"
			return False
		
		#############################
		# Twitterクラスの生成
		try:
			self.Twitter_use = OAuth1Session(
				self.STR_TWITTERdata["twCK"],
				self.STR_TWITTERdata["twCS"],
				self.STR_TWITTERdata["twAT"],
				self.STR_TWITTERdata["twAS"]
			)
		except ValueError as err :
			self.IniStatus['Reason'] = "CLS_Twitter_Use: __conn: Twitter error: " + str(err)
			return False
		
		self.IniStatus['Result'] = True		#Twitter初期化完了
		return True



#####################################################
# twitterサーバのPing確認
#####################################################
	def __TwitterPing(self):
##		wStatus, wResult = sp.getstatusoutput( "ping -c " + str(inCount) + " " + str( self.DEF_TWITTER_HOSTNAME ) )
##		wPingComm = "ping -c " + self.DEF_TWITTER_PING_COUNT + " -w " + self.DEF_TWITTER_PING_TIMEOUT + " " + self.DEF_TWITTER_HOSTNAME
		wPingComm = "ping -c " + self.DEF_TWITTER_PING_COUNT + " " + self.DEF_TWITTER_HOSTNAME
		wStatus, wResult = sp.getstatusoutput( wPingComm )
		if wStatus==0 :
			return True	# Link UP
		
		return False	# Link Down



#####################################################
# ついーと処理
#####################################################
	def Tweet( self, inTweet ):
		#############################
		# 応答形式の取得
		#  {"Result" : False, "Reason" : None, "Responce" : None}
		wRes = self.__Get_Resp()
		
		#############################
		# 入力チェック
		if inTweet=='' :
			wRes['Reason'] = "Twitter内容がない"
			return wRes
		
		#############################
		# 初期化状態のチェック
		wResIni = self.GetIniStatus()
		if wResIni['Result']!=True :
			wRes['Reason'] = "CLS_Twitter_Use: Tweet: Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/statuses/update.json"
		
		#############################
		# パラメータの生成
		wParams = { "status" : inTweet }
		
		#############################
		# ついーと
		try:
			wTweetRes = self.Twitter_use.post( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "CLS_Twitter_Use: Tweet: Twitter error: " + err
			return wRes
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "CLS_Twitter_Use: Tweet: Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		wRes['Result'] = True
		return wRes



#####################################################
# タイムライン読み込み処理
#####################################################
	def GetTL( self, inTLmode="home", inListID=None, inFLG_Rep=True, inFLG_Rts=False ):
		#############################
		# 応答形式の取得
		#  {"Result" : False, "Reason" : None, "Responce" : None}
		wRes = self.__Get_Resp()
		
		#############################
		# 初期化状態のチェック
		wResIni = self.GetIniStatus()
		if wResIni['Result']!=True :
			wRes['Reason'] = "CLS_Twitter_Use: GetTL: Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
		if inTLmode=="home" :
			wAPI = "https://api.twitter.com/1.1/statuses/home_timeline.json"
		elif inTLmode=="user" :
			wAPI = "https://api.twitter.com/1.1/statuses/user_timeline.json"
		elif inTLmode=="list" and isinstance(inListID, int)==True :
			wAPI = "https://api.twitter.com/1.1/lists/statuses.json"
		else :
			wRes['Reason'] = "CLS_Twitter_Use: GetTL: inTLmode is invalid: " + str(inTLmode)
			return wRes
		
		#############################
		# パラメータの生成
		if inTLmode=="list" :
			wParams = {
				"count"           : self.VAL_TwitNum,
				"screen_name"     : self.STR_TWITTERdata['TwitterUser'],
				"exclude_replies" : inFLG_Rep,
				"include_rts"     : inFLG_Rts,
				"list_id"         : inListID
			}
		else :
			wParams = {
				"count"           : self.VAL_TwitNum,
				"screen_name"     : self.STR_TWITTERdata['TwitterUser'],
				"exclude_replies" : inFLG_Rep,
				"include_rts"     : inFLG_Rts
			}
			## exclude_replies  : リプライを除外する True=除外
			## include_rts      : リツイートを含める True=含める
		
		#############################
		# タイムライン読み込み
		try:
			wTweetRes = self.Twitter_use.get( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "CLS_Twitter_Use: GetTL: Twitter error: " + err
			return wRes
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "CLS_Twitter_Use: GetTL: Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		#############################
		# TLを取得
		wRes['Responce'] = json.loads( wTweetRes.text )
		
		#############################
		# 正常
		wRes['Result'] = True
		return wRes



#####################################################
# リスト一覧の取得
#####################################################
	def GetLists(self):
		#############################
		# 応答形式の取得
		#  {"Result" : False, "Reason" : None, "Responce" : None}
		wRes = self.__Get_Resp()
		
		#############################
		# 初期化状態のチェック
		wResIni = self.GetIniStatus()
		if wResIni['Result']!=True :
			wRes['Reason'] = "CLS_Twitter_Use: GetLists: Twitter connect error: " + str(wResIni['Reason'])
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/lists/list.json"
		
		#############################
		# パラメータの生成
		wParams = {
			"count"       : self.VAL_TwitNum,
			"screen_name" : self.STR_TWITTERdata['TwitterUser'],
		}
		
		#############################
		# タイムライン読み込み
		try:
			wTweetRes = self.Twitter_use.get( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "CLS_Twitter_Use: GetTL: Twitter error: " + err
			return wRes
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "CLS_Twitter_Use: GetLists: Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		#############################
		# TLを取得
		wRes['Responce'] = json.loads( wTweetRes.text )
		
		#############################
		# 正常
		wRes['Result'] = True
		return wRes



#####################################################
# トレンド読み込み処理
#####################################################
	def GetTrends(self):
		#############################
		# 応答形式の取得
		#  {"Result" : False, "Reason" : None, "Responce" : None}
		wRes = self.__Get_Resp()
		
		#############################
		# 初期化状態のチェック
		wResIni = self.GetIniStatus()
		if wResIni['Result']!=True :
			wRes['Reason'] = "CLS_Twitter_Use: GetTrends: Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/trends/place.json"
		
		#############################
		# パラメータの生成
		wParams = {
			"id" : self.DEF_WOEID
		}
		
		#############################
		# タイムライン読み込み
		try:
			wTweetRes = self.Twitter_use.get( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "CLS_Twitter_Use: GetTL: Twitter error: " + err
			return wRes
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "CLS_Twitter_Use: GetTrends: Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		#############################
		# TLを取得
		wRes['Responce'] = json.loads( wTweetRes.text )
		
		#############################
		# 正常
		wRes['Result'] = True
		return wRes



