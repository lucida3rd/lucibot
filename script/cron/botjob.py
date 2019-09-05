#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ぼっとJob(cron制御)
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/8/18
#####################################################
# Private Function:
#   __getCommand( self, inKind, inAccount ):
#
# Instance Function:
#   __init__(self):
#   Put( self, inKind, inAccount ):
#   Del( self, inKind, inAccount ):
#   isJob( self, inKind, inAccount ):
#   Stop(self):
#   GetList(self):
#   List(self):
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
from userdata import CLS_UserData
from crontab_ctrl import CLS_CronCtrl
from gval import gVal
#####################################################
class CLS_Botjob() :
#####################################################

##	FLG_CronCtrl = False
	OBJ_CronCtrl = ""
	
	Command_Temp = ""

#####################################################
# Initチェック
#####################################################
##	def Check(self):
##		if self.FLG_CronCtrl!=True :
##			return False	#無効
##		
##		return True			#有効



#####################################################
# 初期化
#####################################################
	def __init__(self):
		#############################
		# cron control生成
		self.OBJ_CronCtrl =CLS_CronCtrl( gVal.STR_CronInfo['CronName'] )
		if self.OBJ_CronCtrl.Check()!=True :
			return	#controlが出してくれる
		
		#############################
		# commandテンプレートの組み立て
		self.Command_Temp = "cd " + CLS_OSIF.sGetCwd() + "; python3 "
##		
##		self.FLG_CronCtrl = True	#有効
		return



#####################################################
# job作成
#####################################################
	def Put( self, inKind, inAccount ):
##		#############################
##		# 応答形式の取得
##		#   "Result" : False, "Reason" : None, "Responce" : None
##		wRes = CLS_OSIF.sGet_Resp()
##		
		#############################
		# 入力チェック＆コマンド発行
		wRes = self.__getCommand( inKind, inAccount )
		if wRes['Result']!=True :
			wRes['Reason'] = "CLS_Botjob: Put: Invalid input: " + wRes['Reason']
			return wRes
		
##		#############################
##		# アカウントのcronは既に登録されているか
##		wJobCheck = self.OBJ_CronCtrl.isJob( wSTR_Command['Command'] )
##		if wJobCheck==True :
##			wRes['Reason'] = "CLS_Botjob: Put: Detect booking job: " + wSTR_Command['Reason']
##			return wRes
		
		#############################
		# jobの登録
		wRes = self.OBJ_CronCtrl.JobPut( wRes['Responce'] )
		if wRes['Result']!=True :
			wRes['Reason'] = "CLS_Botjob: Put: Failer put job: " + wRes['Reason']
			return wRes
		
		wRes['Result'] = True
		return wRes



#####################################################
# job削除
#####################################################
	def Del( self, inKind, inAccount ):
##		#############################
##		# 応答形式の取得
##		#   "Result" : False, "Reason" : None, "Responce" : None
##		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# 入力チェック＆コマンド発行
		wRes = self.__getCommand( inKind, inAccount )
		if wRes['Result']!=True :
			wRes['Reason'] = "CLS_Botjob: Del: Invalid input: " + wRes['Reason']
			return wRes
		
##		#############################
##		# アカウントのcronが登録されていないか
##		wJobCheck = self.OBJ_CronCtrl.isJob( wSTR_Command['Command'] )
##		if wJobCheck==False :
##			wRes['Reason'] = "CLS_Botjob: Del: Job is not found: " + wSTR_Command['Reason']
##			return wRes
		
		#############################
		# jobの削除
		wRes = self.OBJ_CronCtrl.JobDel( wRes['Responce'] )
		if wRes['Result']!=True :
			wRes['Reason'] = "CLS_Botjob: Del: Failer delete job: " + wRes['Reason']
			return wRes
		
		wRes['Result'] = True
		return wRes



#####################################################
# jobの確認
#####################################################
	def isJob( self, inKind, inAccount ):
##		#############################
##		# 応答形式の取得
##		#   "Result" : False, "Reason" : None, "Responce" : None
##		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# 入力チェック
		wRes = self.__getCommand( inKind, inAccount )
		if wRes['Result']!=True :
			wRes['Reason'] = "CLS_Botjob: isJob: Invalid input: " + wRes['Reason']
			return wRes
		
		#############################
		# job一覧とjobが存在するかを取得
		wRes = self.OBJ_CronCtrl.GetList( wRes['Responce'] )
		if wRes['Result']!=True :
			wRes['Reason'] = "CLS_Botjob: isJob: GetList fauled: " + wRes['Reason']
			return wRes
		
		#############################
		# wRes['Responce']['isJob']  jobが存在するか？ True=jobあり、False=jobなし
		# wRes['Responce']['List']   job list(string形式)
		
		wRes['Result'] = True
		return wRes



	#####################################################
	def __getCommand( self, inKind, inAccount ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# cronが有効か？
		if self.OBJ_CronCtrl.Check()!=True :
			wRes['Reason'] = "Cron disable"
			return wRes
		
		#############################
		# inKindが有効か？
		if inKind not in gVal.STR_CronInfo :
			wRes['Reason'] = "inKind is disable: " + inKind
			return wRes
		
		#############################
		# 登録のあるアカウントか？
		if inKind==gVal.DEF_CRON_MASTER or inKind==gVal.DEF_CRON_SUB :
			wUserList = CLS_UserData.sGetUserList()
			if inAccount not in wUserList :
				wRes['Reason'] = "Unregistered account: " + inAccount
				return wRes
		
		#############################
		# コマンドの組み立て
		if inKind==gVal.DEF_CRON_MASTER or inKind==gVal.DEF_CRON_SUB :
			wRes['Responce'] = self.Command_Temp + inKind + " " + inAccount
##		elif inKind==gVal.DEF_CRON_BACK :
##			wRes['Responce'] = self.Command_Temp + inKind + " " + gVal.DEF_CRON_ACCOUNT_BACKGROUND
		else :
			wRes['Responce'] = "Type that can not issue command: " + inKind
			return wRes
		
		wRes['Result'] = True
		return wRes



#####################################################
# 全停止
#####################################################
	def Stop(self):
##		#############################
##		# 応答形式の取得
##		#   "Result" : False, "Reason" : None, "Responce" : None
##		wRes = CLS_OSIF.sGet_Resp()
##		
##		#############################
##		# cronが有効か？
##		if self.FLG_CronCtrl!=True :
##			wRes['Reason'] = "CLS_Botjob: Stop: Cron disable"
##			return wRes
		
		#############################
		# 全cron job削除(停止)
		wRes = self.OBJ_CronCtrl.Clear()
		if wRes['Result']!=True :
			wRes['Reason'] = "CLS_Botjob: Stop: Failded: " + wRes['Reason']
			return wRes
		
		wRes['Result'] = True
		return wRes



#####################################################
# 一覧取得
#####################################################
	def GetList(self):
		#############################
		# cronが有効か？
		if self.OBJ_CronCtrl.Check()!=True :
			wRes['Reason'] = "Cron disable"
			CLS_OSIF.sPrn( "CLS_Botjob: List: Cron disable" )
			return wRes
		
		#############################
		# List取得
		wRes = self.OBJ_CronCtrl.GetList()
		if wRes['Result']!=True :
			CLS_OSIF.sPrn( "CLS_Botjob: List: Failed: " + wRes['Reason']  )
			return wRes
		
		return wRes



#####################################################
# 一覧
#####################################################
	def List(self):
		#############################
		# cronが有効か？
		if self.OBJ_CronCtrl.Check()!=True :
			wRes['Reason'] = "Cron disable"
			CLS_OSIF.sPrn( "CLS_Botjob: List: Cron disable" )
			return False
		
		#############################
		# List取得
		wRes = self.OBJ_CronCtrl.GetList()
		if wRes['Result']!=True :
			CLS_OSIF.sPrn( "CLS_Botjob: List: Failed: " + wRes['Reason']  )
			return False
		
		#############################
		# 一覧を出力

		#############################
		# ヘッダ
		wStr = "--------------------" + '\n'
		wStr = wStr + " crontab jobs" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 内容
		wLen = len( wRes['Responce']['List'] )
		if wLen>0 :
			for wJob in wRes['Responce']['List']:  
				wStr = wStr + str(wJob) + '\n'
		else:
			wStr = wStr + "(none job)" + '\n'
		
		#############################
		# 出力
		CLS_OSIF.sPrn( wStr )
		
		return True



