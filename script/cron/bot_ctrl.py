#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ぼっと制御
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/16
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
	UserList = {}
	FLG_AllStop = False

#####################################################
# 初期化
#####################################################
	def __init__(self):
		#############################
		# ジョブクラスの生成
		self.OBJ_Job = CLS_Botjob()
		
		#############################
		# ユーザ一覧取得
		wUserList = CLS_UserData.sGetUserList()
		
		#############################
		# クラス変数に辞書型として納める
		self.UserList = {}
		for wUser in wUserList :
			self.UserList.update({ wUser : False })
		
		###バックグラウンドユーザの追加
		self.UserList.update({ gVal.DEF_CRON_ACCOUNT_BACKGROUND : False })
		return



#####################################################
# ぼっと起動
#####################################################
	def __start(self):
		#############################
		# 全停止の場合は、再開処理にする
		#  =再開コマンド
		if self.FLG_AllStop==True :
			self.__reStart()
			return
		
		#############################
		# ユーザ名の入力
		wStr = "bot起動するユーザ名をドメインを含める形で入力してください。"
		CLS_OSIF.sPrn( wStr )
		wUser = CLS_OSIF.sInp( "User？=> " )
		
		#############################
		# ユーザ名の確認
		wKeylist = self.UserList.keys()
		if wUser not in wKeylist :
			wStr = "登録のないユーザです。[RT]"
			CLS_OSIF.sInp( wStr )
			return
		
		if self.UserList[wUser]==True :
			wStr = "既に起動してます。[RT]"
			CLS_OSIF.sInp( wStr )
			return
		
		#############################
		# 種別の設定
		wKind = self.__getKind( wUser )
		
		#############################
		# ジョブの作成
		wRes = self.OBJ_Job.Put( wKind, wUser )
		
		#############################
		# 結果
		if wRes['Result']==True :
			###成功
			self.UserList[wUser] = True
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
		# ユーザ名の確認
		wKeylist = self.UserList.keys()
		if wUser not in wKeylist :
			wStr = "登録のないユーザです。[RT]"
			CLS_OSIF.sInp( wStr )
			return
		
		if self.UserList[wUser]==False :
			wStr = "既に停止してます。[RT]"
			CLS_OSIF.sInp( wStr )
			return
		
		#############################
		# 種別の設定
		wKind = self.__getKind( wUser )
		
		#############################
		# ジョブの削除
		wRes = self.OBJ_Job.Del( wKind, wUser )
		
		#############################
		# 結果
		if wRes['Result']==True :
			###成功
			self.UserList[wUser] = False
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
		#############################
		# フラグの確認
		if self.FLG_AllStop==True :
			###ありえない
			wStr = "CLS_Bot_Ctrl: __allStop: FLG_AllStop flag contradiction" + '\n'
			wStr = wStr + "フラグをリセットしました。再度やり直してください。[RT]"
			CLS_OSIF.sInp( wStr )
			self.FLG_AllStop = False
			return
		
		#############################
		# 起動中のbotがあるか
		# あれば停止していく
		wFLG_Start = False
		wKeylist = self.UserList.keys()
		for wUser in wKeylist :
			if self.UserList[wUser]==True :
				#############################
				# 種別の設定
				wKind = self.__getKind( wUser )
				
				#############################
				# ジョブの削除
				wRes = self.OBJ_Job.Del( wKind, wUser )
				if wRes['Result']!=True :
					###失敗
					wStr = "cronの削除が失敗しました。 User:" + wUser + " Reason: " + wRes['Reason']
					CLS_OSIF.sPrn( wStr )
					continue
				
				wFLG_Start = True
		
		#############################
		# 処理結果
		if wFLG_Start==False :
			wStr = "停止したbotはありませんでした。[RT]"
			CLS_OSIF.sInp( wStr )
			return
		
		wStr = "起動中のbotを停止しました。[RT]"
		CLS_OSIF.sInp( wStr )
		self.FLG_AllStop = True
		return



#####################################################
# 再開
#####################################################
	def __reStart(self):
		#############################
		# コマンド受かったので一回フラグを落とす
		self.FLG_AllStop = False
		
		#############################
		# 起動中だったbotがあるか
		# あれば起動していく
		wFLG_Start = False
		wKeylist = self.UserList.keys()
		for wUser in wKeylist :
			if self.UserList[wUser]==True :
				#############################
				# 種別の設定
				wKind = self.__getKind( wUser )
				
				#############################
				# ジョブの作成
				wRes = self.OBJ_Job.Put( wKind, wUser )
				if wRes['Result']!=True :
					###失敗
					wStr = "cronの作成が失敗しました。 User:" + wUser + " Reason: " + wRes['Reason']
					CLS_OSIF.sPrn( wStr )
					continue
				
				wFLG_Start = True
		
		#############################
		# 処理結果
		if wFLG_Start==False :
			###ジョブ作成失敗以外はありえない
			wStr = "起動したbotはありませんでした。[RT]"
			CLS_OSIF.sInp( wStr )
			return
		
		wStr = "起動中だったbotを再開しました。[RT]"
		CLS_OSIF.sInp( wStr )
		return



#####################################################
# 種別の取得
#####################################################
	def __getKind( self, inFulluser ):
		#############################
		# 種別の設定
		if inFulluser==gVal.STR_MasterConfig['MasterUser'] :
			wKind = gVal.DEF_CRON_MASTER
		
		elif inFulluser==gVal.DEF_CRON_ACCOUNT_BACKGROUND :
			wKind = gVal.DEF_CRON_BACK
		
		else :
			wKind = gVal.DEF_CRON_SUB
		
		return wKind



#####################################################
# コマンド実行
#####################################################
	def __runCommand( self, inCommand ):
		#############################
		# 起動 or 再開
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
		wKeylist = self.UserList.keys()
		for wUser in wKeylist :
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
		if self.FLG_AllStop==False :
			wStr = wStr + "コマンド= [\\q] 終了 / [\\r] 起動 / [\\s] 停止 / [\\as] 全停止" + '\n'
		else:
			wStr = wStr + "コマンド= [\\q] 終了 / [\\r] 再開" + '\n'
		
		#############################
		# 出力
		CLS_OSIF.sDispClr()
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# コマンド
		wCommand = CLS_OSIF.sInp( "コマンド？=> " )
		return wCommand



