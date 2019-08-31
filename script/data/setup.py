#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：セットアップ
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/8/31
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
from postgresql_use import CLS_PostgreSQL_Use
from twitter_use import CLS_Twitter_Use

from gval import gVal
#####################################################
class CLS_Setup():
#####################################################

	#使用クラス実体化
	OBJ_DB    = ""

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
		if CLS_File.sExist( gVal.DEF_STR_FILE['MasterConfig_path'] )==True :
			CLS_OSIF.sPrn( "フォルダが既に存在します。セットアップを中止します。" )
			return False	#既にある
		
		wStr = '\n' + "Master環境情報のセットアップを開始します。"
		wStr = wStr + "データのテンプレートをコピーします....."
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# テンプレートデータのコピー(データ作成)
		if CLS_File.sCopytree(
			gVal.DEF_STR_FILE['defMasterdata_path'],
			gVal.DEF_STR_FILE['MasterConfig_path'] )!=True :
			###テンプレートが消えてる (IOエラーはOSが出す)
			CLS_OSIF.sPrn( "CLS_Config: MasterSetup: Master Data Template is not found" )
			return False
		
		#############################
		# フォルダの存在チェック
		if CLS_File.sExist( gVal.DEF_STR_FILE['MasterConfig_path'] )!=True :
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
				##失敗
				CLS_File.sRmtree( gVal.DEF_STR_FILE['MasterConfig_path'] )
				return False
		
		#############################
		# 初期起動直後なので、メンテをOFFにする
		# cronを全て剥がす
##		gVal.STR_MasterConfig['mMainte'] = "off"
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
				##中止なので消す
				CLS_File.sRmtree( gVal.DEF_STR_FILE['MasterConfig_path'] )
				return False
		
		#############################
		# ユーザ登録がされている時
		# もしくは1件だけ登録した時
		# masterユーザを登録する
		wRes = wCLS_Config.CnfMasterUser()
		if wRes!=True :
			##失敗
			CLS_File.sRmtree( gVal.DEF_STR_FILE['MasterConfig_path'] )
			return False
		
		#############################
		# AdminUserの変更
		wCLS_Config.CnfAdminUser()
		
##		#############################
##		# MasterとBackgroundのbotを起動する
##		wRes = wCLS_Botjob.Put( gVal.DEF_CRON_MASTER, gVal.STR_MasterConfig['MasterUser'] )
##		if wRes['Result']!=True :
##			wStr = "Master botの起動に失敗しました。: " + wRes['Reason']
##			CLS_OSIF.sPrn( wStr )
##			return False
##		
##		wRes = wCLS_Botjob.Put( gVal.DEF_CRON_BACK, gVal.DEF_CRON_ACCOUNT_BACKGROUND )
##		if wRes['Result']!=True :
##			wStr = "Background botの起動に失敗しました。: " + wRes['Reason']
##			CLS_OSIF.sPrn( wStr )
##			return False
		
		#############################
		# Databaseの作成
		
		#############################
		# DB接続情報ファイルのチェック
		if CLS_File.sExist( gVal.DEF_STR_FILE['DBinfo_File'] )!=True :
##			###DB接続情報ファイルの作成(空ファイル)
##			if CLS_File.sCopy(
##				gVal.STR_File['defDBinfo_File'], gVal.STR_File['DBinfo_File'] )!=True :
##				##失敗
##				CLS_File.sRmtree( gVal.STR_File['MasterConfig_path'] )
##				CLS_File.sRmtree( gVal.DEF_USERDATA_PATH + gVal.STR_MasterConfig['MasterUser'] )
##				
##				wStr = "CLS_Setup: DataBase file copy failed: src=" + gVal.STR_File['defDBinfo_File']
##				wStr = wStr + " dst=" + gVal.STR_File['DBinfo_File']
##				CLS_OSIF.sPrn( wStr  )
##				return False
##			
			wOBJ_DB = CLS_PostgreSQL_Use()
##			if wOBJ_DB.CreateDBdata( gVal.STR_File['DBinfo_File'] )!=True :
			if wOBJ_DB.CreateDBdata( gVal.DEF_STR_FILE['DBinfo_File'], gVal.DEF_STR_FILE['defDBinfo_File'] )!=True :
				##失敗
				CLS_File.sRmtree( gVal.DEF_STR_FILE['MasterConfig_path'] )
				CLS_File.sRmtree( gVal.DEF_USERDATA_PATH + gVal.STR_MasterConfig['MasterUser'] )
				
				wStr = "CLS_Setup: DataBase file create failed: src=" + gVal.DEF_STR_FILE['defDBinfo_File']
				wStr = wStr + " dst=" + gVal.DEF_STR_FILE['DBinfo_File']
				CLS_OSIF.sPrn( wStr  )
				return False
			
			wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		
		else :
			###DB接続情報変更
			wStr = "DataBaseの接続情報の更新をおこないます。DataBaseの接続情報の更新をおこないますか？"
			print( wStr )
			wSelect = input( "更新する？(y/N)=> " ).strip()
			if wSelect=="y" :
				wOBJ_DB = CLS_PostgreSQL_Use()
##				if wOBJ_DB.CreateDBdata( gVal.DEF_STR_FILE['DBinfo_File'] )!=True :
				if wOBJ_DB.CreateDBdata( gVal.DEF_STR_FILE['DBinfo_File'], gVal.DEF_STR_FILE['defDBinfo_File'] )!=True :
					##失敗
					CLS_File.sRmtree( gVal.DEF_STR_FILE['MasterConfig_path'] )
					CLS_File.sRmtree( gVal.DEF_USERDATA_PATH + gVal.STR_MasterConfig['MasterUser'] )
					
					wStr = "CLS_Setup: DataBase file create failed: src=" + gVal.DEF_STR_FILE['defDBinfo_File']
					wStr = wStr + " dst=" + gVal.DEF_STR_FILE['DBinfo_File']
					CLS_OSIF.sPrn( wStr  )
					return False
				
				wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		
		#############################
		# DBの状態チェック
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			###失敗
			CLS_File.sRmtree( gVal.DEF_STR_FILE['MasterConfig_path'] )
			CLS_File.sRmtree( gVal.DEF_USERDATA_PATH + gVal.STR_MasterConfig['MasterUser'] )
			
			wStr = "CLS_Setup: DB Connect test is failed: " + wRes['Reason']
			CLS_OSIF.sPrn( wStr  )
			return False
		
		wStr = "テーブルの作成中......" + '\n'
		print( wStr )
		#############################
		# テーブルの作成
		self.__create_TBL_USER_DATA( wOBJ_DB )
		self.__create_TBL_TRAFFIC_DATA( wOBJ_DB )
		self.__create_TBL_WORD_CORRECT( wOBJ_DB )
		self.__create_TBL_CLAZ_LIST( wOBJ_DB )
		
		#############################
		# DBのクローズ
		wOBJ_DB.Close()
		wStr = "作成完了!!  DataBaseから切断しました。" + '\n'
		print( wStr )
		
		#############################
		# Twitter接続情報の作成
		wOBJ_Twitter = CLS_Twitter_Use()
		wOBJ_Twitter.CreateTwitter( gVal.DEF_STR_FILE['Twitter_File'], gVal.DEF_STR_FILE['defTwitter_File']  )
		wCLS_Config.CnfTwitter()	#有効無効設定
		
		#############################
		# MasterとBackgroundのbotを起動する
		wRes = wCLS_Botjob.Put( gVal.DEF_CRON_MASTER, gVal.STR_MasterConfig['MasterUser'] )
		if wRes['Result']!=True :
			##失敗
			CLS_File.sRmtree( gVal.DEF_STR_FILE['MasterConfig_path'] )
			CLS_File.sRmtree( gVal.DEF_USERDATA_PATH + gVal.STR_MasterConfig['MasterUser'] )
			
			wStr = "Master botの起動に失敗しました。: " + wRes['Reason']
			CLS_OSIF.sPrn( wStr )
			return False
		
		return True



#####################################################
# テーブル作成: TBL_USER_DATA
#####################################################
	def __create_TBL_USER_DATA( self, inOBJ_DB, inTBLname="TBL_USER_DATA" ):
		#############################
		# テーブルのドロップ
		wQuery = "drop table if exists " + inTBLname + ";"
		inOBJ_DB.RunQuery( wQuery )
		
		#############################
		# テーブル枠の作成
		wQuery = "create table " + inTBLname + "(" + \
					"id          TEXT  NOT NULL," + \
					"username    TEXT  NOT NULL," + \
					"domain      TEXT  NOT NULL," + \
					"status      CHAR(1) DEFAULT '-'," + \
					"followed    BOOL  DEFAULT false," + \
					"follow      BOOL  DEFAULT false," + \
					"follower    BOOL  DEFAULT false," + \
					"locked      BOOL  DEFAULT false," + \
					"lupdate     TIMESTAMP," + \
					"lchacked    TIMESTAMP," + \
					" PRIMARY KEY ( id ) ) ;"
		
		# "status      CHAR(1) DEFAULT '-'," + \
			## @ フォローチェック予約(まだ未フォロー)
			## - フォローチェック済
			## D ドメインブロックユーザ
			## R リムーブ予約
			## X チェックもしくはフォロー失敗
			## * リストから消す
			## M 自分
		
		inOBJ_DB.RunQuery( wQuery )
		return



#####################################################
# テーブル作成: TBL_TRAFFIC_DATA
#####################################################
	def __create_TBL_TRAFFIC_DATA( self, inOBJ_DB, inTBLname="TBL_TRAFFIC_DATA" ):
		#############################
		# テーブルのドロップ
		wQuery = "drop table if exists " + inTBLname + ";"
		inOBJ_DB.RunQuery( wQuery )
		
		#############################
		# テーブル枠の作成
		wQuery = "create table " + inTBLname + "(" + \
					"domain      TEXT  NOT NULL," + \
					"count       INTEGER  DEFAULT 0," + \
					"rat_count   INTEGER  DEFAULT -1," + \
					"now_count   INTEGER  DEFAULT -1," + \
					" PRIMARY KEY ( domain ) ) ;"
		
		inOBJ_DB.RunQuery( wQuery )
		return



#####################################################
# テーブル作成: TBL_WORD_CORRECT
#####################################################
	def __create_TBL_WORD_CORRECT( self, inOBJ_DB, inTBLname="TBL_WORD_CORRECT" ):
		#############################
		# テーブルのドロップ
		wQuery = "drop table if exists " + inTBLname + ";"
		inOBJ_DB.RunQuery( wQuery )
		
		#############################
		# テーブル枠の作成
		wQuery = "create table " + inTBLname + "(" + \
					"word        TEXT  NOT NULL," + \
					"claz        TEXT  NOT NULL," + \
					"yomi        TEXT," + \
					"cla1        TEXT," + \
					"cla2        TEXT," + \
					"cla3        TEXT," + \
					"ktyp        TEXT," + \
					"kkat        TEXT," + \
					"lupdate     TIMESTAMP," + \
					"keeped      BOOL  DEFAULT false," + \
					" PRIMARY KEY ( word ) ) ;"
		
		inOBJ_DB.RunQuery( wQuery )
		return



#####################################################
# テーブル作成: TBL_CLAZ_LIST
#####################################################
	def __create_TBL_CLAZ_LIST( self, inOBJ_DB, inTBLname="TBL_CLAZ_LIST" ):
		#############################
		# テーブルのドロップ
		wQuery = "drop table if exists " + inTBLname + ";"
		inOBJ_DB.RunQuery( wQuery )
		
		#############################
		# テーブル枠の作成
		wQuery = "create table " + inTBLname + "(" + \
					"claz        TEXT  NOT NULL," + \
					"lupdate     TIMESTAMP," + \
					"keeped      BOOL  DEFAULT false," + \
					" PRIMARY KEY ( claz ) ) ;"
		
		inOBJ_DB.RunQuery( wQuery )
		return



