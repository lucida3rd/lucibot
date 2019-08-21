#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：botメイン処理(Master)
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/8/19
#####################################################
# Private Function:
#   __getLucibotVer(cls):
#   __getSystemInfo(cls):
#
# Instance Function:
#   ViewHelp(self):
#
# Class Function(static):
#   sRun(cls):
#   sViewMainConsole(cls):
#   sRunCommand( cls, inCommand ):
#   sViewDisp( cls, inDisp ):
#   sView_Sysinfo(cls):
#
#####################################################

from osif import CLS_OSIF


##from toot import CLS_Toot
from config import CLS_Config
from regist import CLS_Regist
from userdata import CLS_UserData
from gval import gVal
#####################################################
class CLS_BOT_Master() :
#####################################################

#####################################################
# 実行
#####################################################
	@classmethod
	def sRun( cls, inARRarg ):
		#############################
		# 初期化
		gVal.FLG_Console_Mode = False	#コンソールOFF
		
		#############################
		# データフォルダのチェック
		if CLS_File.sExist( gVal.DEF_USERDATA_PATH )!=True :


			return
		
		#############################
		# Master環境情報の読み込み
		if CLS_Config.sGetMasterConfig()!=True :
			# MasterConfigがないのでセットアップするか？



			return
			

		#####################################################
		# MasterUserが未登録
		if gVal.STR_MasterConfig['MasterUser']=="" :




		
		#############################
		# コンソールを表示










		
		return



