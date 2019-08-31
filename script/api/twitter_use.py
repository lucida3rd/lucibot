#!/usr/bin/python
# coding: UTF-8
#####################################################
# public
#   Class   ：ついったーユーズ
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/8/31
#####################################################
# Private Function:
#   __conn(self):
#   __initIniStatus(self):
#   __loadTwitter( self, inPath ):
#   __checkTwitter(self):
#
# Instance Function:
#   __init__( self, inPath ):
#   GetInisStatus(self):
#   CreateTwitter( self, inPath ):
#   Connect( self, inPath=None ):
#   Tweet( self, inTweet ):
#
# Class Function(static):
#   (none)
#
#####################################################
import os
import codecs
import json
import shutil
import subprocess as sp
from requests_oauthlib import OAuth1Session

##from gval import gVal
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
		
		"Mode"			: "home",
		"List"			: None,
		"NoReply"		: "on",
		"Retweet"		: "off"
	}
	
	VAL_TwitNum = 120

	DEF_TWITTER_HOSTNAME = "twitter.com"	#Twitterホスト名
	DEF_MOJI_ENCODE      = 'utf-8'			#ファイル文字エンコード
	DEF_TWITTER_PING_COUNT   = "2"			#Ping回数 (文字型)
##	DEF_TWITTER_PING_TIMEOUT = "1000"		#Pingタイムアウト秒 (文字型)

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
##	def __init__(self):
##	def __init__( self, inPath ):
###	def __init__( self, inPath=None, inNoConn=False ):
	def __init__( self, inPath=None, inGetNum=120, inNoConn=False ):
##		self.__conn()	#接続
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
##		#############################
##		# 書き込みデータを作成
##		wSetLine = []
##		wKeylist = self.STR_TWITTERdata.keys()
##		for iKey in wKeylist :
##			wLine = iKey + "=" + str(self.STR_TWITTERdata[iKey]) + '\n'
##			wSetLine.append(wLine)
##		
##		#############################
##		# ファイル上書き書き込み
###		
###		#############################
###		# 存在チェック
###		if os.path.exists( gVal.STR_File['Twitter_File'] )!=True :
###			wStr = "作成失敗: ファイルがありません: " + gVal.STR_File['Twitter_File']
###			print( wStr )
###			return False	#失敗
###		
###		#############################
###		# 書き込み
##		try:
##			wFile = codecs.open( inDstPath, 'w', self.DEF_MOJI_ENCODE )
##			wFile.writelines( wSetLine )
##			wFile.close()
##		except ValueError as err :
##			return False
###		if self.SaveTwitter( gVal.STR_File['Twitter_File'] )!=True :
		if self.SaveTwitter( inDstPath )!=True :
			return False
		
		print( "Twitterの接続情報の作成 成功!!" + '\n' )
		return True



#####################################################
# Twitterタイムライン設定
#####################################################
	def CnfTimeline( self, inPath ):
		#############################
		# Twitter接続情報ファイルのチェック
		if( os.path.exists( inPath )==False ) :
			##失敗
			wStr = "CLS_Twitter_Use: CnfTimeline: Default Twitter file is not found: " + inPath + '\n'
			print( wStr )
			return False
		
		#############################
		# メニューの表示
		wStr = '\n' + "Twitterタイムラインの設定をします。" + '\n'
		wStr = wStr + "Twitterタイムライン設定の変更をおこないますか？"
		print( wStr )
		wSelect = input( "変更する？(y/N)=> " ).strip()
		if wSelect!="y" :
			return True	#キャンセル
		
		#############################
		# 自垢のリスト取得
		wListsRes = self.GetLists()
		if wListsRes['Result']!=True :
			print( "Twitter API Error: " + wRes['Reason'] )
			return False
		wListID   = []
		wListName = ""
		wStrList  = ""
		for wROW in wListsRes['Responce'] :
			wListID.append( str(wROW['id']) )
			wStrList = wStrList + str(wROW['id']) + "   " + str(wROW['slug']) + '\n'
			if wROW['id']==self.STR_TWITTERdata['List'] :
				wListName = wROW['slug']
			##	CLS_OSIF.sPrn( "ID: " + str(wROW['id']) )
			##	CLS_OSIF.sPrn( "Slug: " + str(wROW['slug']) )
			##	CLS_OSIF.sPrn( "Mode: " + str(wROW['mode']) )
			##	CLS_OSIF.sPrn( "Name: " + str(wROW['name']) + "(" + str(wROW['full_name']) + ")" )
			##	CLS_OSIF.sPrn( "Disc: " + str(wROW['description']) )
		
		#############################
		# タイムラインモード
		wStr = '\n' + "タイムラインモードを設定してください。現在の設定。 Mode= " + self.STR_TWITTERdata['Mode']
		if self.STR_TWITTERdata['Mode']=="list" :
			wStr = wStr + " / ListName= " + wListName
		wStr = wStr + '\n'
		wStr = wStr + "  [1] ホーム / [2] ユーザ / [3] リスト / [other] 変更なし"
		print( wStr )
		wInput = input( "=> " ).strip()
		if wInput=="1" :
			self.STR_TWITTERdata['Mode'] = "home"
		elif wInput=="2" :
			self.STR_TWITTERdata['Mode'] = "user"
		elif wInput=="3" :
			self.STR_TWITTERdata['Mode'] = "list"
		
		#############################
		# リストID
		if self.STR_TWITTERdata['Mode']=="list" :
			wStr = '\n' + "取得するリストのリストIDを設定してください。現在の設定。 List= " + str(self.STR_TWITTERdata['List']) + '\n'
			print( wStr )
			### 画面に表示
			print( " List ID               List Name" )
			print( wStrList )
			wInput = input( "List ID=> " ).strip()
			if wInput=="" :
				if self.STR_TWITTERdata['List']==None :
					print( "Twitterタイムライン設定の変更がキャンセルされました" )
					return False	#キャンセル
			if wInput!="" :
				if wInput not in wListID :
					if self.STR_TWITTERdata['List']==None :
						print( "リストにないIDです。キャンセルします。" )
						return False	#キャンセル
					else :
						print( "リストにないIDです。Listは変更されません。" )
				else :
					self.STR_TWITTERdata['List'] = int( wInput )
		
		#############################
		# リプライを除外するか
		wStr = '\n' + "リプライを除外するかを設定してください。現在の設定。 NoReply= " + self.STR_TWITTERdata['NoReply'] + '\n'
		wStr = wStr + "  [1] 除外する / [2] 除外しない / [other] 変更なし"
		print( wStr )
		wInput = input( "=> " ).strip()
		if wInput=="1" :
			self.STR_TWITTERdata['NoReply'] = "on"
		elif wInput=="2" :
			self.STR_TWITTERdata['NoReply'] = "off"
		
		#############################
		# リツイートを含めるか
		wStr = '\n' + "リツイートを含めるかを設定してください。現在の設定。 Retweet= " + self.STR_TWITTERdata['Retweet'] + '\n'
		wStr = wStr + "  [1] 含める / [2] 含めない / [other] 変更なし"
		print( wStr )
		wInput = input( "=> " ).strip()
		if wInput=="1" :
			self.STR_TWITTERdata['Retweet'] = "on"
		elif wInput=="2" :
			self.STR_TWITTERdata['Retweet'] = "off"
		
		print( "Twitterの接続情報の更新中......" + '\n' )
		#############################
		# セーブ
###		if self.SaveTwitter( gVal.STR_File['Twitter_File'] )!=True :
		if self.SaveTwitter( inPath )!=True :
			wStr = "CLS_Twitter_Use: CnfTimeline: Twitter file save is failed: " + inPath + '\n'
			print( wStr )
			return False
		
		print( "Twitterの接続情報の更新 成功!!" + '\n' )
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
		
		self.STR_TWITTERdata['Mode'] = "home"
		self.STR_TWITTERdata['List'] = None
		self.STR_TWITTERdata['NoReply'] = "on"
		self.STR_TWITTERdata['Retweet'] = "off"

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
					continue
				self.STR_TWITTERdata[wLine[0]] = wLine[1]
			
		except ValueError as err :
			self.IniStatus['Reason'] = "CLS_Twitter_Use: __loadTwitter: Load Twitter file Failed: " + err
			return False
		
		#############################
		# 数値変換
		if self.STR_TWITTERdata['List']!=None :
			self.STR_TWITTERdata['List'] = int( self.STR_TWITTERdata['List'] )
		
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
##		if CLS_OSIF.sPing( gVal.DEF_TWITTER_HOSTNAME )!=True :
		if self.__TwitterPing()!=True :
			self.IniStatus['Reason'] = "CLS_Twitter_Use: __conn: Twitter host no responce"
##			return
			return False
		
		#############################
		# Twitterクラスの生成
		try:
			self.Twitter_use = OAuth1Session(
##				gVal.STR_MasterConfig["twCK"],
##				gVal.STR_MasterConfig["twCS"],
##				gVal.STR_MasterConfig["twAT"],
##				gVal.STR_MasterConfig["twAS"]
				self.STR_TWITTERdata["twCK"],
				self.STR_TWITTERdata["twCS"],
				self.STR_TWITTERdata["twAT"],
				self.STR_TWITTERdata["twAS"]
			)
		except ValueError as err :
			self.IniStatus['Reason'] = "CLS_Twitter_Use: __conn: Twitter error: " + str(err)
##			return
			return False
		
		self.IniStatus['Result'] = True		#Twitter初期化完了
##		return
		return True



#####################################################
# twitterサーバのPing確認
#####################################################
##	def __TwitterPing( self, inCount=4 ):
	def __TwitterPing(self):
##		wStatus, wResult = sp.getstatusoutput( "ping -c " + str(inCount) + " " + str( self.DEF_TWITTER_HOSTNAME ) )
##		wPingComm = "ping -c " + self.DEF_TWITTER_PING_COUNT + " -w " + self.DEF_TWITTER_PING_TIMEOUT + " " + self.DEF_TWITTER_HOSTNAME
		wPingComm = "ping -c " + self.DEF_TWITTER_PING_COUNT + " " + self.DEF_TWITTER_HOSTNAME
		wStatus, wResult = sp.getstatusoutput( wPingComm )
		if wStatus==0 :
			return True	# Link UP
		
		return False	# Link Down



#####################################################
# 再接続
#####################################################
##	def ReConnect(self):
##		self.__conn()	#接続
##		return



#####################################################
# ついーと処理
#####################################################
	def Tweet( self, inTweet ):
		#############################
		# 応答形式の取得
		#  {"Result" : False, "Reason" : None, "Responce" : None}
##		wRes = CLS_OSIF.sGet_Resp()
		wRes = self.__Get_Resp()
		
##		#############################
##		# Twitterが利用可能か
##		if gVal.STR_MasterConfig['Twitter'] != 'on' :
##			wRes['Reason'] = "Twitter機能=off"
##			return wRes
##		
		#############################
		# 入力チェック
		if inTweet=='' :
			wRes['Reason'] = "Twitter内容がない"
			return wRes
		
##		#############################
##		# Twitterに接続
##		self.ReConnect()
##		wResIni = GetIniStatus()
##		if wResIni['Result']!=True :
##			wRes['Reason'] = "CLS_Twitter_Use: Tweet: Twitter connect error: " + wResIni['Reason']
##			return wRes
		
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
##			wTweetRes = self.Twitter_use.post( gVal.DEF_TWITTER_URL, params=wParams )
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
##	def GetTL( self, inTLmode="user", inList=None, inReply=True, inRetweet=False ):
	def GetTL(self):
		#############################
		# 応答形式の取得
		#  {"Result" : False, "Reason" : None, "Responce" : None}
##		wRes = CLS_OSIF.sGet_Resp()
		wRes = self.__Get_Resp()
		
##		#############################
##		# Twitterが利用可能か
##		if gVal.STR_MasterConfig['Twitter'] != 'on' :
##			wRes['Reason'] = "Twitter機能=off"
##			return wRes
##		
		#############################
		# 初期化状態のチェック
		wResIni = self.GetIniStatus()
		if wResIni['Result']!=True :
			wRes['Reason'] = "CLS_Twitter_Use: GetTL: Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
##		if inTLmode=="user" :
		if self.STR_TWITTERdata['Mode']=="user" :
			##ユーザタイムライン
			wAPI = "https://api.twitter.com/1.1/statuses/user_timeline.json"
		
##		elif inTLmode=="home" :
		elif self.STR_TWITTERdata['Mode']=="home" :
			##ホームタイムライン (連合みたいなもの)
			wAPI = "https://api.twitter.com/1.1/statuses/home_timeline.json"
		
##		elif inTLmode=="list" :
		elif self.STR_TWITTERdata['Mode']=="list" :
			##リストタイムライン
##			if inList==None :
			if self.STR_TWITTERdata['List']==None :
				wRes['Reason'] = "CLS_Twitter_Use: GetTL: List Name is null"
				return wRes
			wAPI = "https://api.twitter.com/1.1/lists/statuses.json"
		
		else :
			wRes['Reason'] = "CLS_Twitter_Use: GetTL: Unknown timeline mode: " + inTLmode
			return wRes
		
		#############################
		# パラメータの生成
		
		###Bool化
			# on  = True
			# off = False
		wFLG_Reply   = True if self.STR_TWITTERdata['NoReply']==False else False
		wFLG_Retweet = True if self.STR_TWITTERdata['Retweet']==False else False
		
##		if inTLmode=="list" :
		if self.STR_TWITTERdata['Mode']=="list" :
			wParams = {
##				"count"       : gVal.STR_TLnum['getTwitTLnum'],
				"count"       : self.VAL_TwitNum,
				"list_id"     : self.STR_TWITTERdata['List']
			}
		else :
			wParams = {
##				"count"       : gVal.STR_TLnum['getTwitTLnum'],
				"count"       : self.VAL_TwitNum,
				"screen_name" : self.STR_TWITTERdata['TwitterUser'],
##				"exclude_replies" : inReply,
##				"include_rts"     : inRetweet
				"exclude_replies" : wFLG_Reply,
				"include_rts"     : wFLG_Retweet
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
##		wRes = CLS_OSIF.sGet_Resp()
		wRes = self.__Get_Resp()
		
##		#############################
##		# Twitterが利用可能か
##		if gVal.STR_MasterConfig['Twitter'] != 'on' :
##			wRes['Reason'] = "Twitter機能=off"
##			return wRes
		
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
##			"count"       : gVal.STR_TLnum['getTwitTLnum'],
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



