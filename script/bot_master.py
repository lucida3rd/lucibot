#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：botメイン処理(Master)
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/11/19
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   (none)
#
# Class Function(static):
#   sRun(cls):
#
#####################################################
from twitter_use import CLS_Twitter_Use

from osif import CLS_OSIF
##from toot import CLS_Toot
from config import CLS_Config
from regist import CLS_Regist
from userdata import CLS_UserData

from crontest import CLS_CronTest
from botctrl import CLS_BotCtrl
##from lookhtl import CLS_LookHTL
from lookptl import CLS_LookPTL
from lookltl import CLS_LookLTL
from lookrip import CLS_LookRIP
from trend import CLS_Trend
from lookhard import CLS_LookHard
from twitter_reader import CLS_TwitterReader
from circletoot import CLS_CircleToot
from follow import CLS_Follow
from randtoot import CLS_RandToot
from mylog import CLS_Mylog
from traffic import CLS_Traffic
from usercorr import CLS_UserCorr
from wordcorr import CLS_WordCorr
from gval import gVal
#####################################################
class CLS_BOT_Master() :
#####################################################
	CHR_Account   = ""		#実行アカウント
	CHR_User_path = ""		#ユーザフォルダパス
	ARR_MyAccountInfo = ""
	
	#使用クラス実体化
	OBJ_Mylog    = ""
	OBJ_Mastodon = ""
	OBJ_MyDon    = ""		# CHR_Account用のmastodonオブジェクト
	OBJ_Twitter  = ""
	OBJ_Traffic  = ""
	OBJ_UserCorr = ""
	OBJ_WordCorr = ""
	OBJ_Follow   = ""

#####################################################
# 実行
#####################################################
	@classmethod
	def sRun(cls):
		#############################
		# cronテストとconfigのロード
		#   テスト項目
		#     1.jobチェック
		#       実行ファイルチェック
		#       ユーザ登録チェック(Master、Subの場合)
		#     2.データフォルダチェック
		#     3.Master環境情報ロード(チェック)
		#     4.Userフォルダチェック
		#     5.User環境情報ロード(チェック)
		#     6.実行権限チェック
		#     7.testログ
		wCLS_Test = CLS_CronTest()
		wRes = wCLS_Test.Run()
		if wRes['Result']!=True :
			return	#問題あり
		
	#############################
	# 初期化
	#############################
		#############################
		# 初期化
		gVal.FLG_Console_Mode = False	#コンソールOFF
		cls.CHR_Account   = wRes['Responce']['Account']
		cls.CHR_User_path = wRes['Responce']['User_path']
		
		cls.OBJ_Mylog    = CLS_Mylog( cls.CHR_User_path + gVal.DEF_STR_FILE['UserLog_path'] )
		cls.OBJ_Traffic  = CLS_Traffic( parentObj=cls )
		cls.OBJ_UserCorr = CLS_UserCorr( parentObj=cls )
		cls.OBJ_WordCorr = CLS_WordCorr( parentObj=cls )
		cls.OBJ_Follow   = CLS_Follow( parentObj=cls )
		
		#############################
		# 排他開始 (テストOFFの時)
		if gVal.FLG_Test_Mode==False :
			if CLS_BotCtrl.sLock( cls.CHR_User_path )==True :
				if gVal.FLG_Test_Mode==False :
					cls.OBJ_Mylog.Log( 'a', "排他" )
				else :
					cls.OBJ_Mylog.Log( 'a', "排他(Test)", inView=True )
				
				return	#排他中
		
		#############################
		# 開始ログ
		if gVal.FLG_Test_Mode==False :
			cls.OBJ_Mylog.Log( 'b', "bot開始" )
		else :
			cls.OBJ_Mylog.Log( 'a', "bot開始(Test)", inView=True )
		
		#############################
		# 1時間監視
		if CLS_BotCtrl.sChk1HourTime( cls.CHR_User_path )!=True :
			cls.OBJ_Mylog.Log( 'a', "CLS_BOT_Master: sChk1HourTime failure" )
			
			CLS_BotCtrl.sUnlock( cls.CHR_User_path )
			return
		
		#############################
		# 除外ドメイン読み込み
##		if cls.OBJ_UserCorr.GetDomainREM()!=True :
##			cls.OBJ_Mylog.Log( 'a', "CLS_BOT_Master: GetDomainREM failure" )
		cls.OBJ_UserCorr.GetDomainREM()
		
		#############################
		# 禁止ワード読み込み
##		if cls.OBJ_WordCorr.GetWordREM()!=True :
##			wStr = "CLS_BOT_Sub: GetWordREM failure"
##			cls.OBJ_Mylog.Log( 'a', wStr )
		cls.OBJ_WordCorr.GetWordREM()
		
		#############################
		# mastodonクラス生成
		cls.OBJ_Mastodon = CLS_Regist()
		wRes = cls.OBJ_Mastodon.CreateMastodon( cls.CHR_Account )
		if wRes['Result']!=True :
			wStr = "CLS_BOT_Master: Mastodon connect failure: " + wRes['Reason']
			cls.OBJ_Mylog.Log( 'a', wStr )
			
			CLS_BotCtrl.sUnlock( cls.CHR_User_path )
			return
		
		wRes = cls.OBJ_Mastodon.GetMastodon( cls.CHR_Account )
		if wRes['Result']!=True :
			wStr = "CLS_BOT_Master: Mastodon get failer: " + wRes['Reason']
			cls.OBJ_Mylog.Log( 'a', wStr )
			
			CLS_BotCtrl.sUnlock( cls.CHR_User_path )
			return
		
		cls.OBJ_MyDon = wRes['Responce']	#1個だけ取り出す
		
		#############################
		# 自アカウント情報の取得
		wRes = cls.OBJ_MyDon.GetMyAccountInfo()
		if wRes['Result']!=True :
			wStr = "CLS_BOT_Master: Get Mastodon my account info is failure: " + wRes['Reason']
			cls.OBJ_Mylog.Log( 'a', wStr )
			
			CLS_BotCtrl.sUnlock( cls.CHR_User_path )
			return
		cls.ARR_MyAccountInfo = wRes['Responce']
			# ['id']
			# ['username']
			# ['display_name']
			# ['url']
		
		#############################
		# Twitterと接続 (クラス生成)
		if gVal.STR_MasterConfig['Twitter']=="on" :
			cls.OBJ_Twitter = CLS_Twitter_Use( gVal.DEF_STR_FILE['Twitter_File'], gVal.DEF_STR_TLNUM['getTwitTLnum'] )
		else :
			cls.OBJ_Twitter = CLS_Twitter_Use()
		
	#############################
	# mastodon処理
	#############################
		#############################
		# フォロー・フォロワー情報の取得
		cls.OBJ_Follow.Get_FollowLists()
		
		#############################
		# 自動フォロー処理
		if gVal.STR_MasterConfig['AutoFollow']=="on" :
			cls.OBJ_Follow.RunAutoFollow()
		
		#############################
		# LTL監視処理
		wOBJ_LookLTL = CLS_LookLTL( parentObj=cls )
		
		#############################
		# PTL監視処理
		wOBJ_LookPTL = CLS_LookPTL( parentObj=cls )
		
		#############################
		# RIP監視処理
		wOBJ_LookRIP = CLS_LookRIP( parentObj=cls )
		
		#############################
		# トレンド処理
		if gVal.STR_MasterConfig['Trend']=="on" :
			wOBJ_Trend = CLS_Trend( parentObj=cls )
		
		#############################
		# ランダムトゥート処理
		if gVal.STR_MasterConfig['RandToot']=="on" :
			wOBJ_RandToot = CLS_RandToot( parentObj=cls )
		
		#############################
		# 周期トゥート処理
		if gVal.STR_MasterConfig['CircleToot']=="on" :
			wOBJ_CircleToot = CLS_CircleToot( parentObj=cls )
		
		#############################
		# フォロー・フォロワー情報の更新
		cls.OBJ_Follow.Set_FollowLists()
		
		#############################
		# ハード監視処理
		if gVal.STR_MasterConfig['LookHard']=="on" :
			wOBJ_LookHard = CLS_LookHard( parentObj=cls )
		
		#############################
		# Twitterリーダ処理
		if gVal.STR_MasterConfig['Twitter']=="on" :
			wOBJ_TwitterReader = CLS_TwitterReader( parentObj=cls )
		
	#############################
	# 後処理
	#############################
		#############################
		# 排他解除
		CLS_BotCtrl.sUnlock( cls.CHR_User_path )
		return



