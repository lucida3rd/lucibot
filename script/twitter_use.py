#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ついったーユーズ
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/4
#####################################################
# Private Function:
#   __conn(self):
#   __initIniStatus(self):
#
# Instance Function:
#   __init__(self):
#   GetInisStatus(self):
#   ReConnect(self):
#   Tweet( self, inTweet ):
#
# Class Function(static):
#   (none)
#
#####################################################
from requests_oauthlib import OAuth1Session

from osif import CLS_OSIF
from toot import CLS_Toot
from mastodon_use import CLS_Mastodon_Use
from gval import gVal
#####################################################
class CLS_Twitter_Use():
	Twitter_use = ''						#Twitterモジュール実体
	IniStatus = ""

#####################################################
# 初期化状態取得
#####################################################
	def GetIniStatus(self):
		return self.IniStatus	#返すだけ



#####################################################
# 初期化状態取得
#####################################################
	def __initIniStatus(self):
		self.IniStatus = {
			"Result"   : False,
			"Reason"   : None
##			"Responce" : None
		}
		return



#####################################################
# 初期化
#####################################################
	def __init__(self):
		self.__conn()	#接続
		return



#####################################################
# ついったぁー!?!?(椅子から転げ落ちる)に接続
#####################################################
	def __conn(self):
		#############################
		# 状態初期化
		self.__initIniStatus()
		
		#############################
		# 通信テスト
		if CLS_OSIF.sPing( gVal.DEF_TWITTER_HOSTNAME )!=True :
			self.IniStatus['Reason'] = "CLS_Twitter_Use: __conn: Twitter host no responce"
			return
		
		#############################
		# Twitterクラスの生成
		try:
			self.Twitter_use = OAuth1Session(
				gVal.STR_MasterConfig["twCK"],
				gVal.STR_MasterConfig["twCS"],
				gVal.STR_MasterConfig["twAT"],
				gVal.STR_MasterConfig["twAS"]
			)
		except ValueError as err :
			self.IniStatus['Reason'] = "CLS_Twitter_Use: __conn: Twitter error: " + err
			return
		
		self.IniStatus['Result'] = True		#Twitter初期化完了
		return



#####################################################
# 再接続
#####################################################
	def ReConnect(self):
		self.__conn()	#接続
		return



#####################################################
# ついーと!?!?処理
#####################################################
	def Tweet( self, inTweet ):
		
		#############################
		# 応答形式の取得
		#  {"Result" : False, "Reason" : None, "Responce" : None}
		wRes = CLS_Toot.sGet_API_Resp()
		
		#############################
		# Twitterが利用可能か
		if gVal.STR_MasterConfig['Twitter'] != 'on' :
			wRes['Reason'] = "Twitter機能=off"
			return wRes
		
		if inTweet=='' :
			wRes['Reason'] = "Twitter内容がない"
			return wRes
		
		#############################
		# Twitterに接続
		self.ReConnect()
		wResIni = GetIniStatus()
		if wResIni['Result']!=True :
			wRes['Reason'] = "CLS_Twitter_Use: Tweet: Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# 本文の生成
		wParams = { "status" : inTweet }
		
		#############################
		# ついーと
		try:
			wTweetRes = self.Twitter_use.post( gVal.DEF_TWITTER_URL, params=wParams )
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



