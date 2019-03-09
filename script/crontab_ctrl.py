#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：crontab制御
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/8
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   __init__(self):
#   Check(self):
#   JobPut( self, inCommand, inSecond=1 ):
#   GetList(self):
#   JobDel( self, inCommand ):
#   Clear(self):
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
from crontab import CronTab
#####################################################
class CLS_CronCtrl():
#####################################################

	FLG_Cron = False
	OBJ_Cron = ""
	CHR_CronUser = ""

	FLG_DispError = True

#####################################################
# Initチェック
#####################################################
	def Check(self):
		if self.FLG_Cron!=True :
			return False	#無効
		
		return True			#有効



#####################################################
# 初期化
#####################################################
	def __init__( self, inUser=None, inDispError=False ):
		if inUser == None :
			return	#ユーザ名がない
		
		#############################
		# cronオブジェクト生成
		try:
			self.OBJ_Cron = CronTab( user=inUser )
		except ValueError as err :
			return
		
		#############################
		# 生成できた情報を処理用に記録
		self.CHR_CronUser  = inUser
		self.FLG_DispError = inDispError
		self.FLG_Cron      = True
		return



#####################################################
# job作成
#####################################################
	def JobPut( self, inCommand, inSecond=1 ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# cronが有効か？
		if self.FLG_Cron!=True :
			wRes['Reason'] = " JobPut: Cron disabled"
			return wRes
		
		#############################
		# ダブってるjobがないか
		wJobList = self.GetList( inCommand )
		if wJobList['Result']!=True :
			###ここは通らないかも
			wRes['Reason'] = wRes['Reason']	#中継
			return wRes
		if wJobList['Responce']['isJob']==True :
			wRes['Reason'] = " JobPut: Detect booking job: " + inCommand
			return wRes
		
		#############################
		# jobをrconに登録 (実行するわけではない)
		job = self.OBJ_Cron.new( command=inCommand )
		job.minute.every( inSecond )
		
		#############################
		# crontabに書き込み
		self.OBJ_Cron.write() 
		
		wRes['Result'] = True
		return wRes



#####################################################
# jobがあるか
#####################################################
##	def isJob( self, inCommand ):
##		#############################
##		# cronが有効か？
##		if self.FLG_Cron!=True :
##			self.__prn( "CLS_CronCtrl: isJob: Cron disabled" )
##			return False
##		
##		#############################
##		# ダブってるjobがないか
##		for wJob in self.OBJ_Cron:  
##			wJobStr = str(wJob)
##			if wJobStr.find( inCommand )>=0 :
##				return True
##		
##		return False



#####################################################
# job一覧
#####################################################
	def GetList( self, inCommand=None ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# cronが有効か？
		if self.FLG_Cron!=True :
			wRes['Reason'] = " GetJoblist: Cron disabled"
			return wRes
		
		#############################
		# jobの文字列リスト化
		wRes['Responce'] = {}
		wRes['Responce'].update({ 'isJob': False, 'List': [] })
		for wJob in self.OBJ_Cron:  
			wJobStr = str(wJob)
			if inCommand!=None :	#ダブってるJobがあればTrue
				if wJobStr.find( inCommand )>=0 :
					wRes['Responce']['isJob'] = True
			
			wRes['Responce']['List'].append( str(wJob) )
		
		wRes['Result'] = True
		return wRes



#####################################################
# job削除
#####################################################
	def JobDel( self, inCommand ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# cronが有効か？
		if self.FLG_Cron!=True :
			wRes['Reason'] = " JobDel: Cron disabled"
			return wRes
		
		#############################
		# jobが存在しない
		wJobList = self.GetList( inCommand )
		if wJobList['Result']!=True :
			###ここは通らないかも
			wRes['Reason'] = wRes['Reason']	#中継
			return wRes
		if wJobList['Responce']['isJob']==False :
			wRes['Reason'] = " JobDel: Job is not found: " + inCommand
			return wRes
		
		#############################
		# commandをキーにjobを削除
		self.OBJ_Cron.remove_all( command=inCommand )
		
		#############################
		# crontabに書き込み
		self.OBJ_Cron.write() 
		
		wRes['Result'] = True
		return wRes

####コメントアウト
##		job.enable(False)
####



#####################################################
# cron 全て停止
#####################################################
	def Clear(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# cronが有効か？
		if self.FLG_Cron!=True :
			wRes['Reason'] = " Clear: Cron disabled"
			return wRes
		
		#############################
		# cronからすべてのjobを削除
		self.OBJ_Cron.remove_all()
		
		#############################
		# crontabに書き込み
		self.OBJ_Cron.write()
		
		wRes['Result'] = True
		return wRes



#####################################################
# cronの内容を表示
#####################################################
##	def List(self):
##		#############################
##		# cronが有効か？
##		if self.FLG_Cron!=True :
##			self.__prn( "CLS_CronCtrl: List: Cron disabled" )
##			return False
##		
##		#############################
##		# ヘッダ
##		wStr = "--------------------" + '\n'
##		wStr = wStr + " " + self.CHR_CronUser + " crontab jobs" + '\n'
##		wStr = wStr + "--------------------" + '\n'
##		
##		#############################
##		# 内容
##		wLen = len( self.OBJ_Cron )
##		if wLen>0 :
##			for wJob in self.OBJ_Cron:  
##				wStr = wStr + str(wJob) + '\n'
##		else:
##			wStr = wStr + "(none job)" + '\n'
##		
##		#############################
##		# 出力
##		CLS_OSIF.sPrn( wStr )
##		return


#####################################################
# コンソールにエラー出力
#####################################################
##	def __prn( self, inMsg ):
##		if self.FLG_DispError==False :
##			return
##		
##		CLS_OSIF.sPrn( inMsg )
##		return



######
# 参考
#   https://pypi.org/project/python-crontab/
#   https://stackabuse.com/scheduling-jobs-with-python-crontab/
#
######
