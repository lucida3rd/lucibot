#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：cronテスト
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/9/28
#####################################################
# Private Function:
#   __testLog( self, inKind, inAccount  ):
#
# Instance Function:
#   __init__(self):
#   Run(self):
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
from filectrl import CLS_File
from config import CLS_Config
from userdata import CLS_UserData
from botjob import CLS_Botjob
from gval import gVal
#####################################################
class CLS_CronTest():
#####################################################

#####################################################
# Init
#####################################################
	def __init__(self):
		return



#####################################################
# cron動作確認
#   テスト項目
#     1.jobチェック
#       実行ファイルチェック
#       ユーザ登録チェック(Master、Subの場合)
#     2.データフォルダチェック
#     3.Master環境情報ロード(チェック)
#     4.Userフォルダチェック
#     5.実行権限チェック
#     6.テストログ
#####################################################
	def Run(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# 引数取得
		wArg = CLS_OSIF.sGetArg()
		if len(wArg)==3 :	#テストモードか
			if wArg[2]==gVal.DEF_TEST_MODE :
				gVal.FLG_Test_Mode = True
		
		elif len(wArg)!=2 :	#引数が足りない
			wStr = "CLS_CronTest: Argument deficiency: argument=" + str( wArg )
			CLS_OSIF.sPrn( wStr  )	#メールに頼る
			return wRes
		
		wKind    = wArg[0]
		wAccount = wArg[1]
		
##		#############################
##		# Backgroundのチェックは別でやる
##		if wKind==gVal.DEF_CRON_BACK and wAccount==gVal.DEF_CRON_ACCOUNT_BACKGROUND :
##			wRes = self.__backgroundTest( outRes=wRes )
##			return wRes
		
		#############################
		# 1.jobチェック
		#     実行ファイルチェック
		#     ユーザ登録チェック(Master、Subの場合)
		wCLS_Botjob = CLS_Botjob()
		wRes = wCLS_Botjob.isJob( wKind, wAccount )
		if wRes['Result']!=True :
			wStr = "CLS_CronTest: Job check NG: " + wRes['Reason']
			CLS_OSIF.sPrn( wStr  )	#メールに頼る
			return wRes
		
		if wRes['Responce']['isJob']==False and gVal.FLG_Test_Mode==False :
##			wStr = "CLS_CronTest: Job is not found: kind=" + wKind + ": account=" + wAccount
			wStr = "CLS_CronTest: Job is not found: kind=" + wKind + ": account=" + wAccount + " current: " + CLS_OSIF.sGetCwd()
			CLS_OSIF.sPrn( wStr  )	#メールに頼る
			
			wRes['Result'] = False	#テストはNG
			return wRes
		
		wFlg_ok = True
		#############################
		# 2.データフォルダのチェック
		if CLS_File.sExist( gVal.DEF_USERDATA_PATH )!=True :
			wFlg_ok = False
		
		#############################
		# 3.Master環境情報の読み込み
		if CLS_Config.sGetMasterConfig()!=True :
			wFlg_ok = False
		
		#############################
		# Master環境情報に異常はないか
		if wFlg_ok==False :
##			wRes = wCLS_Botjob.Stop()	#全cronを削除する
##			if wRes['Result']!=True :
##				wStr = "CLS_CronTest: Cron stop failed: " + wRes['Reason']
##				CLS_OSIF.sPrn( wStr  )	#メールに頼る
##			
##			wStr = "Master環境情報に異常があったため、" + gVal.STR_SystemInfo['Client_Name']
##			wStr = wStr + "で登録した全cronを停止しました。"
			wStr = "Master環境情報に異常があったため、処理を中止します。"
			CLS_OSIF.sPrn( wStr  )		#メールに頼る
			
			wRes['Result'] = False	#テストはNG
			return wRes
		
		#############################
		# 4.Userフォルダチェック
		wRes = CLS_UserData.sGetUserPath( wAccount )
		if wRes['Result']!=True :
			wRes = wCLS_Botjob.Del( wKind, wAccount )	#cronを削除する
			if wRes['Result']!=True :
				wStr = "CLS_CronTest: Cron delete failed: " + wRes['Reason']
				CLS_OSIF.sPrn( wStr  )	#メールに頼る
			
			wStr = "Userフォルダが存在しないため、" + wAccount
			wStr = wStr + "のcronを停止しました。"
			CLS_OSIF.sPrn( wStr  )		#メールに頼る
			
			wRes['Result'] = False	#テストはNG
			return wRes
		
		wUserPath = wRes['Responce']
		
##		#############################
##		# 5.User環境情報の読み込み
##		wRes = CLS_Config.sGetUserConfig( wAccount )
##		if wRes['Result']!=True :
##			wRes = wCLS_Botjob.Del( wKind, wAccount )	#cronを削除する
##			if wRes['Result']!=True :
##				wStr = "CLS_CronTest: Cron delete failed: " + wRes['Reason']
##				CLS_OSIF.sPrn( wStr  )	#メールに頼る
##			
##			wStr = "User環境情報に異常があったため、" + wAccount
##			wStr = wStr + "のcronを停止しました。"
##			CLS_OSIF.sPrn( wStr  )		#メールに頼る
##			
##			wRes['Result'] = False	#テストはNG
##			return wRes
		
		#############################
		# 5.実行権限チェック
		wFlg_Authority = True
		#############################
		# コマンドの組み立て
		if wKind==gVal.DEF_CRON_MASTER :	# Masuer User以外か
			if wAccount!=gVal.STR_MasterConfig['MasterUser'] :
				wFlg_Authority = False
		
##		elif wKind==gVal.DEF_CRON_BACK :	# Background以外か
##			if wAccount!=gVal.DEF_CRON_ACCOUNT_BACKGROUND :
##				wFlg_Authority = False
		
		elif wKind==gVal.DEF_CRON_SUB :	# Sub以外か
##			if wAccount==gVal.STR_MasterConfig['MasterUser'] or \
##			   wAccount==gVal.DEF_CRON_ACCOUNT_BACKGROUND :
			if wAccount==gVal.STR_MasterConfig['MasterUser'] :
				wFlg_Authority = False
		
		else :
			###ここではありえない
			wFlg_Authority = False
		
		if wFlg_Authority==False :
			wRes = wCLS_Botjob.Del( wKind, wAccount )	#cronを削除する
			if wRes['Result']!=True :
				wStr = "CLS_CronTest: Cron delete failed: " + wRes['Reason']
				CLS_OSIF.sPrn( wStr  )	#メールに頼る
			
			wStr = "実行権限に問題があったため、" + wAccount
			wStr = wStr + "のcronを停止しました。"
			CLS_OSIF.sPrn( wStr  )		#メールに頼る
			
			wRes['Result'] = False	#テストはNG
			return wRes
		
		# ここまででtestは合格してる
		#############################
		
		#############################
		# 6.testログ
		self.__testLog( wKind, wAccount )
		
		wRes['Responce'] = {}
		wRes['Responce'].update({ "Kind" : wKind, "Account" : wAccount, "User_path" : wUserPath })
		wRes['Result'] = True
		return wRes


#####################################################
# Background用テスト
#####################################################
##	def __backgroundTest( self, outRes ):
##		#############################
##		# ※コール時に厳選してるので
##		#   Account、Kindの権限チェックは合格しているものとする
##		
##		wFlg_ok = True
##		#############################
##		# 1.データフォルダのチェック
##		if CLS_File.sExist( gVal.DEF_USERDATA_PATH )!=True :
##			wFlg_ok = False
##		
##		#############################
##		# 2.Master環境情報の読み込み
##		if CLS_Config.sGetMasterConfig()!=True :
##			wFlg_ok = False
##		
##		#############################
##		# Master環境情報に異常はないか
##		if wFlg_ok==False :
##			wRes = wCLS_Botjob.Stop()	#全cronを削除する
##			if wRes['Result']!=True :
##				wStr = "CLS_CronTest: __backgroundTest: Cron stop failed: " + wRes['Reason']
##				CLS_OSIF.sPrn( wStr  )	#メールに頼る
##			
##			wStr = "Master環境情報に異常があったため、" + gVal.STR_SystemInfo['Client_Name']
##			wStr = wStr + "で登録した全cronを停止しました。"
##			CLS_OSIF.sPrn( wStr  )		#メールに頼る
##			
##			return outRes	#NG
##		
##		#############################
##		# 3.testログ
##		self.__testLog( gVal.DEF_CRON_BACK, gVal.DEF_CRON_ACCOUNT_BACKGROUND )
##		
##		outRes['Responce'] = {}
##		outRes['Responce'].update({
##			"Kind"		: gVal.DEF_CRON_BACK,
##			"Account"	: gVal.DEF_CRON_ACCOUNT_BACKGROUND,
##			"User_path"	: gVal.STR_File['MasterConfig_path'] })
##		
##		outRes['Result'] = True
##		return


#####################################################
# test log
#####################################################
	def __testLog( self, inKind, inAccount  ):
		#############################
		# TestLog有効か
		if gVal.STR_CronInfo[inKind]!=True :
##			return		#ログ無効
			return None	#ログ無効
		
		wExeName = inKind.split(".")
		
		#############################
		# 時間取得
##		wTime = CLS_OSIF.sGetTime()
##		wDate = wTime['TimeDate'].split(" ")
##		if wDate['Result']!=True :
		wTime = CLS_OSIF.sGetTime()
		if wTime['Result']!=True :
			return None	#時間取得失敗
		
		#############################
		# パスの生成
##		wDate = wTime['TimeDate'].split(" ")
##		wDate = wDate.split("-")
		wDate = wTime['TimeDate'].split(" ")
		wDate = wDate[0].split("-")
		wLogFile = gVal.DEF_STR_FILE['MasterLog_path'] + wDate[0] + wDate[1] + "_" + inAccount + ".log"
		
		#############################
		# 書き込みデータを作成
		wSetLine = []
		wLine = wTime['TimeDate'] + " cron run: " + inKind + '\n'
		wSetLine.append(wLine)
		
		#############################
		# テストログ書き込み
##		wLogFile = gVal.STR_CronInfo['Log_path'] + wDate[0] + "_cron" + wExeName[0] + "_" + inAccount + ".log"
		CLS_File.sAddFile( wLogFile, wSetLine, inExist=False )
		return wLogFile



