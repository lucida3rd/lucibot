# coding: UTF-8
#####################################################
# 十八試るしぼっと
#   Class   ：ついったーユーズ
#   Site URL：https://mynoghra.jp/
#   Update  ：2018/11/24
#####################################################
from requests_oauthlib import OAuth1Session
import global_val
#####################################################
class CLS_Twitter_Use:
	Twitter_use = ''						# Twitterモジュール実体

#####################################################
# Init
#####################################################
	def __init__(self):
		return



#####################################################
# ついったぁーに接続
#####################################################
	def pConnect(self):
		#############################
		# Twitterクラスの生成
		try:
			self.Twitter_use = OAuth1Session(
				global_val.gConfig["twCK"],
				global_val.gConfig["twCS"],
				global_val.gConfig["twAT"],
				global_val.gConfig["twAS"]
			)
		except ValueError as err :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Twitter_Use：Twitter生成失敗：'+err, True )
			return False
		
		return True



#####################################################
# ついーと処理
#####################################################
	def cTweet( self, tweet ):
		if global_val.gConfig['Twitter'] != 'on' :
			global_val.gCLS_Mylog.cLog('c', 'CLS_Twitter_Use：cTweet：機能off' )
			return False
		
		if tweet=='' :
			return False
		
		#############################
		# Twitterに接続
		if self.pConnect()!=True :
			return False
		
		#############################
		# 本文の生成
		params = { "status" : tweet }
		
		#############################
		# ついーと
		try:
			res = self.Twitter_use.post( global_val.gTwitter_url, params = params )
			
		except ValueError as err :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Twitter_Use：cTweet：Post送信失敗：'+err )
			return False
		
		#############################
		# 結果
		if res.status_code != 200 :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Twitter_Use：cTweet：投稿エラー：'+str(res.status_code) )
			return False
		
		return True



