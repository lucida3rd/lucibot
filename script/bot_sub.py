#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：botメイン処理 (Sub用)
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/9
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

from osif import CLS_OSIF
from toot import CLS_Toot
from config import CLS_Config
from regist import CLS_Regist
from userdata import CLS_UserData

from crontest import CLS_CronTest
from mylog import CLS_Mylog
from gval import gVal
#####################################################
class CLS_BOT_Sub() :
#####################################################

	CHR_Account = ""		#実行アカウント
	
	#使用クラス実体化
	OBJ_Mylog = ""


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
		#     4.User環境情報ロード(チェック)
		#     5.実行権限
		wCLS_Test = CLS_CronTest()
		wRes = wCLS_Test.Run( inTest=True )
###		wRes = wCLS_Test.Run()
		if wRes['Result']!=True :
			return	#問題あり
		
		#############################
		# 初期化
		gVal.FLG_Console_Mode = False	#コンソールOFF
		cls.CHR_Account = wRes['Responce']['Account']
		
		wLogPath = gVal.DEF_USERDATA_PATH + cls.CHR_Account + "/" + gVal.STR_File['UserLog_path']
		cls.OBJ_Mylog = CLS_Mylog( wLogPath )


		cls.OBJ_Mylog.Log( 'a', "てすと。"+'\n'+"てすちょーw"+'\n'+"てすと３。", True )

		cls.OBJ_Mylog.Log( 'a', "てすと。"+'\n'+"てすちょーw", True )

		cls.OBJ_Mylog.Log( 'a', "てすと。", True )


		
		return



