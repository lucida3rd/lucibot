#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ぼっと制御
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/15
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
#   List(self):
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
from userdata import CLS_UserData
from botjob import CLS_Botjob
from gval import gVal
#####################################################
class CLS_Bot_Ctrl() :
#####################################################

	OBJ_Job = ""
	UserList = []

#####################################################
# 初期化
#####################################################
	def __init__(self):
		#############################
		# ジョブクラスの生成
		self.OBJ_Job = CLS_Botjob()
		
		#############################
		# ユーザ一覧取得
		self.UserList = CLS_UserData.sGetUserList()
		
		###バックグラウンドユーザの追加
		self.UserList.append( gVal.DEF_CRON_ACCOUNT_BACKGROUND )
		return



#####################################################
# ぼっと起動
#####################################################
	def __start(self):
		#############################
		# ユーザ名の入力
		wStr = "bot起動するユーザ名をドメインを含める形で入力してください。"
		CLS_OSIF.sPrn( wStr )
		wUser = CLS_OSIF.sInp( "User？=> " )
		
		#############################
		# 種別の設定
		if wUser==gVal.STR_MasterConfig['MasterUser'] :
			wKind = gVal.DEF_CRON_MASTER
		
		elif wUser==gVal.DEF_CRON_ACCOUNT_BACKGROUND :
			wKind = gVal.DEF_CRON_BACK
		
		else :
			wKind = gVal.DEF_CRON_SUB
		
		#############################
		# ジョブの作成
		wRes = self.OBJ_Job.Put( wKind, wUser )
		
		#############################
		# 結果
		if wRes['Result']==True :
			###成功
			wStr = "cronに登録成功しました。"
			CLS_OSIF.sPrn( wStr )
		else :
			###失敗
			wStr = "cronへの登録が失敗しました。 Reason: " + wRes['Reason']
			CLS_OSIF.sPrn( wStr )
		
		CLS_OSIF.sInp( "確認したらリターンキーを押してください。[RT]" )
		return



#####################################################
# ぼっと停止
#####################################################
	def __stop( self):
		#############################
		# ユーザ名の入力
		wStr = "bot停止するユーザ名をドメインを含める形で入力してください。"
		CLS_OSIF.sPrn( wStr )
		wUser = CLS_OSIF.sInp( "User？=> " )
		
		#############################
		# 種別の設定
		if wUser==gVal.STR_MasterConfig['MasterUser'] :
			wKind = gVal.DEF_CRON_MASTER
		
		elif wUser==gVal.DEF_CRON_ACCOUNT_BACKGROUND :
			wKind = gVal.DEF_CRON_BACK
		
		else :
			wKind = gVal.DEF_CRON_SUB
		
		#############################
		# ジョブの削除
		wRes = self.OBJ_Job.Del( wKind, wUser )
		
		#############################
		# 結果
		if wRes['Result']==True :
			###成功
			wStr = "cronを削除しました。2分以内にはbotが止まります。"
			CLS_OSIF.sPrn( wStr )
		else :
			###失敗
			wStr = "cronの削除が失敗しました。 Reason: " + wRes['Reason']
			CLS_OSIF.sPrn( wStr )
		
		CLS_OSIF.sInp( "確認したらリターンキーを押してください。[RT]" )
		return



#####################################################
# 全ぼっと停止
#####################################################
	def __allStop(self):


		return wRes



#####################################################
# 再開
#####################################################
	def __reStart(self):


		return wRes



#####################################################
# コマンド実行
#####################################################
	def __runCommand( self, inCommand ):
		#############################
		# 起動
		if inCommand=="\\r" :
			self.__start()
		
		#############################
		# 停止
		elif inCommand=="\\s" :
			self.__stop()
		
		#############################
		# 全停止
		elif inCommand=="\\as" :
			self.__allStop()
		
		#############################
		# 再開
		elif inCommand=="\\rr" :
			self.__reStart()
		
		return



#####################################################
# ぼっとコンソール
#####################################################
	def Console(self):
		while True :
			wCommand = self.__consoleViewList()
			if wCommand.find("\\q")>=0 :
				###終了
				break
			
			self.__runCommand( wCommand )
		
		return

#####################################################
	def __consoleViewList(self):
		#############################
		# List取得
		wRes = self.OBJ_Job.GetList()
		if wRes['Result']!=True :
			return False
		## wRes['Responce']['List']:  
		
		#############################
		# ヘッダ
		wStr = "--------------------" + '\n'
		wStr = wStr + " bot一覧 (crontab)" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 内容
		#   crontabにユーザが登録されていれば *ON
		#   crontabにユーザが未登録なら        OFF
		for wUser in self.UserList :
			wFlg_Online = False
			for wJob in wRes['Responce']['List']:  
				if wJob.find( wUser )>=0 :
					wFlg_Online = True
			
			if wFlg_Online==True :
				wStat = "*ON "
			else:
				wStat = " OFF"
			
			wStr = wStr + "    " + wStat + "    " + wUser + '\n'
		
		#############################
		# コマンド見本
###		wStr = wStr + "コマンド= [\\q] 終了 / [\\r] 起動 / [\\s] 停止 / [\\as] 全停止" + '\n'
		wStr = wStr + "コマンド= [\\q] 終了 / [\\r] 起動 / [\\s] 停止" + '\n'
		
		#############################
		# 出力
		CLS_OSIF.sDispClr()
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# コマンド
		wCommand = CLS_OSIF.sInp( "コマンド？=> " )
		return wCommand



