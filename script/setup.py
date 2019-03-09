#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：セットアップ
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/7
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   __init__(self):
#   MasterSetup(self):
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
from filectrl import CLS_File
from config import CLS_Config
from regist import CLS_Regist
from userdata import CLS_UserData
from botjob import CLS_Botjob
from gval import gVal
#####################################################
class CLS_Setup():
#####################################################

#####################################################
# 初期化
#####################################################
	def __init__(self):
		return



#####################################################
# Master環境情報セットアップ
#####################################################
	def MasterSetup(self):
		#############################
		# フォルダの存在チェック
		if CLS_File.sExist( gVal.STR_File['MasterConfig_path'] )==True :
			CLS_OSIF.sPrn( "フォルダが既に存在します。セットアップを中止します。" )
			return False	#既にある
		
		wStr = '\n' + "Master環境情報のセットアップを開始します。"
		wStr = wStr + "データのテンプレートをコピーします....."
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# テンプレートデータのコピー(データ作成)
		if CLS_File.sCopytree(
			gVal.STR_File['defMasterdata_path'],
			gVal.STR_File['MasterConfig_path'] )!=True :
			###テンプレートが消えてる (IOエラーはOSが出す)
			CLS_OSIF.sPrn( "CLS_Config: MasterSetup: Master Data Template is not found" )
			return False
		
		#############################
		# フォルダの存在チェック
		if CLS_File.sExist( gVal.STR_File['MasterConfig_path'] )!=True :
			CLS_OSIF.sPrn( "CLS_Config: MasterSetup: Data Copy check failed" )
			return False	#失敗
		
		#############################
		# コピー完了
		CLS_OSIF.sPrn( "Master環境情報のコピーが完了しました。" + '\n' )
		
		#############################
		# 使うクラスの作成
		wCLS_Config = CLS_Config()
		wCLS_Regist = CLS_Regist()
		wCLS_Botjob = CLS_Botjob()
		
		#############################
		# Master環境情報の変更
		wStr = "Master環境情報の変更をおこないますか？" + '\n'
		wStr = wStr + "（あとで変更することもできます）"
		CLS_OSIF.sPrn( wStr )
		wSelect = CLS_OSIF.sInp( "変更する？(y/N)=> " )
		if wSelect=="y" :
			wRes = wCLS_Config.CnfMasterConfig()
			if wRes!=True :
				return False	#失敗
		
		#############################
		# 初期起動直後なので、メンテをOFFにする
		# cronを全て剥がす
		gVal.STR_MasterConfig['mMainte'] = "off"
		wCLS_Botjob.Stop()
		
		#############################
		# ユーザ登録=0の時、ユーザ登録させる
		wList = CLS_UserData.sGetUserList()
		if len(wList)==0 :
			wFLG_regist = False
			while True:
				wStr = '\n' + "Master User(mastodonでbotとして使うユーザ)の登録をおこないます。" + '\n'
				wStr = wStr + "ユーザ名をドメインを含めて入力してください。: 例= " + gVal.DEF_EXAMPLE_ACCOUNT
				CLS_OSIF.sPrn( wStr )
				wMasterUser = CLS_OSIF.sInp( "MasterUser？=> " )
				wRes = wCLS_Regist.Regist( wMasterUser )
				if wRes==True :
					###登録できたので次へ
					wFLG_regist = True
					break
				else :
					###登録できないと、登録できるまで継続したい
					CLS_OSIF.sPrn( "ユーザの登録がないとbotが動作できません。" )
					wRes = CLS_OSIF.sInp( "登録を中止しますか？(y)=> " )
					if wRes=='y' :
						return False	#セットアップいちお完了だけどユーザ未登録
			
			if wFLG_regist!=True :
				return False
		
		#############################
		# ユーザ登録がされている時
		# もしくは1件だけ登録した時
		# masterユーザを登録する
		wRes = wCLS_Config.CnfMasterUser()
		if wRes!=True :
			return False
		
		#############################
		# AdminUserの変更
		wCLS_Config.CnfAdminUser()
		






		return True



