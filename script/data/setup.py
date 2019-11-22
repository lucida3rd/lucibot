#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：セットアップ
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/11/22
#####################################################
# Private Function:
#   __initDB(self):
#
# ◇テーブル作成系
#   __create_TBL_USER_DATA( self, inOBJ_DB, inTBLname="TBL_USER_DATA" ):
#   __create_TBL_TRAFFIC_DATA( self, inOBJ_DB, inTBLname="TBL_TRAFFIC_DATA" ):
#   __create_TBL_WORD_CORRECT( self, inOBJ_DB, inTBLname="TBL_WORD_CORRECT" ):
#   __create_TBL_CLAZ_LIST( self, inOBJ_DB, inTBLname="TBL_CLAZ_LIST" ):
#   __create_TBL_TREND( self, inOBJ_DB, inTBLname="TBL_TREND" ):
#   __create_TBL_TWITTER_READER( self, inOBJ_DB, inTBLname="TBL_TWITTER_READER" ):
#
# Instance Function:
#   __init__(self):
#   MasterSetup(self):
#   AllInit(self):
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
from bot_ctrl import CLS_Bot_Ctrl
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
		wCLS_Bot_Ctrl = CLS_Bot_Ctrl()
		
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
##		wCLS_Botjob.Stop()
		wCLS_Bot_Ctrl.CronAllStop()
		
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
##			
##			wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		
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
##				
##				wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		
##		#############################
##		# DBの状態チェック
##		wRes = wOBJ_DB.GetIniStatus()
##		if wRes['Result']!=True :
##			###失敗
##			CLS_File.sRmtree( gVal.DEF_STR_FILE['MasterConfig_path'] )
##			CLS_File.sRmtree( gVal.DEF_USERDATA_PATH + gVal.STR_MasterConfig['MasterUser'] )
##			
##			wStr = "CLS_Setup: DB Connect test is failed: " + wRes['Reason']
##			CLS_OSIF.sPrn( wStr  )
##			return False
##		
##		wStr = "テーブルの作成中......" + '\n'
##		print( wStr )
##		#############################
##		# テーブルの作成
##		self.__create_TBL_USER_DATA( wOBJ_DB )
##		self.__create_TBL_TRAFFIC_DATA( wOBJ_DB )
##		self.__create_TBL_WORD_CORRECT( wOBJ_DB )
##		self.__create_TBL_CLAZ_LIST( wOBJ_DB )
##		
##		#############################
##		# DBのクローズ
##		wOBJ_DB.Close()
##		wStr = "作成完了!!  DataBaseから切断しました。" + '\n'
##		print( wStr )
##		
		#############################
		# DBの初期化
		wRes = self.__initDB()
		if wRes!=True :
			###失敗
			CLS_File.sRmtree( gVal.DEF_STR_FILE['MasterConfig_path'] )
			CLS_File.sRmtree( gVal.DEF_USERDATA_PATH + gVal.STR_MasterConfig['MasterUser'] )
			
			wStr = "CLS_Setup: DB Connect test is failed: " + wRes['Reason']
			CLS_OSIF.sPrn( wStr  )
			return False
		
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
# 全初期化
#   作業ファイルとDBを全て初期化する
#####################################################
	def AllInit(self):
		#############################
		# フォルダの存在チェック
		if CLS_File.sExist( gVal.DEF_STR_FILE['MasterConfig_path'] )!=True :
			CLS_OSIF.sPrn( "CLS_Config: Init: Master Data is not Exist" )
			return False	#失敗
		
		#############################
		# Master環境情報の変更
		wStr = "データベースと全ての作業ファイルをクリアします。" + '\n'
		wStr = wStr + "よろしいですか？(y/N)=> "
		wSelect = CLS_OSIF.sInp( wStr )
		if wSelect!="y" :
			##キャンセル
			CLS_OSIF.sInp( "リターンキーを押して再度コンソールアプリを起動してください。[RT]" )
			return True
		
		CLS_OSIF.sPrn( "cronを停止中。2分ほどお待ちください..." + '\n' )
		#############################
		# ユーザ一覧取得
		wUserList = CLS_UserData.sGetUserList()
		
		#############################
		# cronの停止
##		wCLS_Botjob = CLS_Botjob()
		wCLS_Bot_Ctrl = CLS_Bot_Ctrl()
		wFlg_CronStop = wCLS_Bot_Ctrl.CronAllStop()
		if wFlg_CronStop==True :
			### 停止したbotあり
			CLS_OSIF.sSleep(120)	#とりあえずcronが停止する2分は待つ
		
##		wFLG_Wait = False
##		wWaitRestart = {}
##		wIndex       = 0
##		for wUser in wUserList :
##			#############################
##			# 種別を判定
##			if gVal.STR_MasterConfig['MasterUser']==wUser :
##				wKind = gVal.DEF_CRON_MASTER
##			else :
##				wKind = gVal.DEF_CRON_SUB
##			
##			#############################
##			# ジョブの削除
##			wRes = wCLS_Botjob.Del( wKind, wUser )
##			if wRes['Result']!=True :
##				###おそらく動いてないcronのためスキップ
##				continue
##			
##			#############################
##			# 停止cronをメモ
##			wWaitRestart.update({ wIndex : wIndex })
##			wWaitRestart[wIndex] = {}
##			wWaitRestart[wIndex].update({ "Kind" : wKind })
##			wWaitRestart[wIndex].update({ "User" : wUser })
##			wFLG_Wait  = True
##			wIndex    += 1
##		
##		#############################
##		# 1つでも停止cronがあれば2分待つ
##		if wFLG_Wait==True :
##			CLS_OSIF.sSleep(120)
		
		CLS_OSIF.sPrn( "各ユーザの作業ファイルを初期化しています..." + '\n' )
		#############################
		# ファイルの初期化(各ユーザ)
		for wUser in wUserList :
			CLS_OSIF.sPrn( "ユーザ " + wUser + " 初期化中..." )
			
			#############################
			# ユーザフォルダチェック
			wRes = CLS_UserData.sGetUserPath( wUser )
			if wRes['Result']!=True :
				CLS_OSIF.sPrn( "CLS_Setup: Init: User folder is not Exist: user=" + wUser + '\n' )
				continue
			wUserPath = wRes['Responce']
			
			#############################
			# 1時間ファイル
			wDefFile_path = gVal.DEF_STR_FILE['defUserdata_path'] + gVal.DEF_STR_FILE['Chk1HourFile']
			wDstFile_path = wUserPath + gVal.DEF_STR_FILE['Chk1HourFile']
			self.__initFile( wDefFile_path, wDstFile_path )
			
			#############################
			# HTL過去ファイル
			wDefFile_path = gVal.DEF_STR_FILE['defUserdata_path'] + gVal.DEF_STR_FILE['Rate_HTLFile']
			wDstFile_path = wUserPath + gVal.DEF_STR_FILE['Rate_HTLFile']
			self.__initFile( wDefFile_path, wDstFile_path )
			
			#############################
			# LTL過去ファイル
			wDefFile_path = gVal.DEF_STR_FILE['defUserdata_path'] + gVal.DEF_STR_FILE['Rate_LTLFile']
			wDstFile_path = wUserPath + gVal.DEF_STR_FILE['Rate_LTLFile']
			self.__initFile( wDefFile_path, wDstFile_path )
			
			#############################
			# PTL過去ファイル
			wDefFile_path = gVal.DEF_STR_FILE['defUserdata_path'] + gVal.DEF_STR_FILE['Rate_PTLFile']
			wDstFile_path = wUserPath + gVal.DEF_STR_FILE['Rate_PTLFile']
			self.__initFile( wDefFile_path, wDstFile_path )
			
			#############################
			# リプライ過去ファイル
			wDefFile_path = gVal.DEF_STR_FILE['defUserdata_path'] + gVal.DEF_STR_FILE['Rate_RipFile']
			wDstFile_path = wUserPath + gVal.DEF_STR_FILE['Rate_RipFile']
			self.__initFile( wDefFile_path, wDstFile_path )
			
			#############################
			# 過去通知ファイル
			wDefFile_path = gVal.DEF_STR_FILE['defUserdata_path'] + gVal.DEF_STR_FILE['Rate_IndFile']
			wDstFile_path = wUserPath + gVal.DEF_STR_FILE['Rate_IndFile']
			self.__initFile( wDefFile_path, wDstFile_path )
			
			#############################
			# フォローファイル
			wDefFile_path = gVal.DEF_STR_FILE['defUserdata_path'] + gVal.DEF_STR_FILE['FollowListFile']
			wDstFile_path = wUserPath + gVal.DEF_STR_FILE['FollowListFile']
			self.__initFile( wDefFile_path, wDstFile_path )
			
			#############################
			# フォロワーファイル
			wDefFile_path = gVal.DEF_STR_FILE['defUserdata_path'] + gVal.DEF_STR_FILE['FollowerListFile']
			wDstFile_path = wUserPath + gVal.DEF_STR_FILE['FollowerListFile']
			self.__initFile( wDefFile_path, wDstFile_path )
		
	#############################
		#############################
		# ファイルの初期化(masterConfig)
		
		CLS_OSIF.sPrn( "masterConfig 初期化中..." + '\n' )
		#############################
		# ドメイン情報
		wDefFile_path = gVal.DEF_STR_FILE['defMasterdata_path'] + gVal.DEF_STR_FILE['MstdnDomains_File']
		wDstFile_path = gVal.DEF_STR_FILE['MasterConfig_path'] + gVal.DEF_STR_FILE['MstdnDomains_File']
		self.__initFile( wDefFile_path, wDstFile_path )
		
		#############################
		# 過去ツイート
		wDefFile_path = gVal.DEF_STR_FILE['defMasterdata_path'] + gVal.DEF_STR_FILE['TweetFile']
		wDstFile_path = gVal.DEF_STR_FILE['MasterConfig_path'] + gVal.DEF_STR_FILE['TweetFile']
		self.__initFile( wDefFile_path, wDstFile_path )
		
		#############################
		# 周期トゥート
		wDefFile_path = gVal.DEF_STR_FILE['defMasterdata_path'] + gVal.DEF_STR_FILE['CLDataFile']
		wDstFile_path = gVal.DEF_STR_FILE['MasterConfig_path'] + gVal.DEF_STR_FILE['CLDataFile']
		self.__initFile( wDefFile_path, wDstFile_path )
		
	#############################
		CLS_OSIF.sPrn( "データベースを初期化しています..." + '\n' )
		#############################
		# DBの初期化
		wFLG_Init = True
		### 初期化
		if self.__initDB()!=True :
			wFLG_Init = False
		### 修復
		if self.__recovery_TBL_TRAFFIC_DATA()!=True :
			wFLG_Init = False
		
		if wFLG_Init==True :
			CLS_OSIF.sPrn( "データベースの初期化をおこないました" + '\n' )
		else :
			##ありえない
			CLS_OSIF.sPrn( "*** データベースの初期化に失敗しました" + '\n' )
		
		#############################
		# cronの再起動
##		if wFLG_Wait==True :
##			CLS_OSIF.sPrn( "停止していたcronを再開します..." + '\n' )
##			
##			wKeylist = wWaitRestart.keys()
##			for wKey in wKeylist :
##				#############################
##				# ジョブの登録
##				wRes = wCLS_Botjob.Put( wWaitRestart[wKey]["Kind"], wWaitRestart[wKey]["User"] )
##				if wRes['Result']!=True :
##					###失敗
##					CLS_OSIF.sPrn( "cronの起動に失敗しました: user=" + wWaitRestart[wKey]["User"] + '\n' )
##		
		if wFlg_CronStop==True :
			### 停止したbotあり
			CLS_OSIF.sPrn( "停止していたcronを再開します..." + '\n' )
			wCLS_Bot_Ctrl.CronReStart()
		
		#############################
		# 終わり
		CLS_OSIF.sPrn( "初期化が正常終了しました。" )
##		CLS_OSIF.sInp( "リターンキーを押して再度コンソールアプリを起動してください。[RT]" )
		return True
	
	#####################################################
	def __initFile( self, inSrcFile, inDstFile ):
		if CLS_File.sCopy( inSrcFile, inDstFile )!=True :
			##失敗
			CLS_OSIF.sPrn( "CLS_Setup: Init: Copy error: " + inDstFile + '\n' )
		return



#####################################################
# データベースの初期化
#####################################################
	def __initDB(self):
		#############################
		# DBの接続
		wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			###失敗
##			CLS_OSIF.sPrn( "CLS_Setup: __initDB: DB connect error: " + wRes['Reason'] + '\n' )
			return False
		
		#############################
		# テーブルの作成
		self.__create_TBL_USER_DATA( wOBJ_DB )
		self.__create_TBL_TRAFFIC_DATA( wOBJ_DB )
		self.__create_TBL_WORD_CORRECT( wOBJ_DB )
		self.__create_TBL_CLAZ_LIST( wOBJ_DB )
		self.__create_TBL_TREND( wOBJ_DB )
		self.__create_TBL_TWITTER_READER( wOBJ_DB )
		
		#############################
		# DBのクローズ
		wOBJ_DB.Close()
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
					"locked      BOOL  DEFAULT false," + \
					"lupdate     TIMESTAMP," + \
					" PRIMARY KEY ( id ) ) ;"
		
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
					"rat_days    INTEGER  DEFAULT -1," + \
					"now_days    INTEGER  DEFAULT 0," + \
					" PRIMARY KEY ( domain ) ) ;"
		
		inOBJ_DB.RunQuery( wQuery )
		return

	#############################
	# トラヒックを元にテーブルを修復する
	def __recovery_TBL_TRAFFIC_DATA(self):
		#############################
		# 読み出し先初期化
		wTrafficUser = []
		
		#############################
		# ファイル読み込み
		wFile_path = gVal.DEF_STR_FILE['TrafficFile']
		if CLS_File.sReadFile( wFile_path, outLine=wTrafficUser )!=True :
			wStr = "CLS_Regist : __recovery_TBL_TRAFFIC_DATA: TrafficFile read is failed: " + gVal.DEF_STR_FILE['TrafficFile']
			CLS_OSIF.sPrn( wStr )
			return False
		
		#############################
		# DBの接続
		wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			###失敗
			wStr = "CLS_Regist : __recovery_TBL_TRAFFIC_DATA: DB connect error: " + wRes['Reason']
			CLS_OSIF.sPrn( wStr )
			return False
		
		#############################
		# 修復
		for wLine in wTrafficUser :
			wDomain = wLine.split("@")
			if len(wDomain)!=2 :
				wStr = "CLS_Regist : __recovery_TBL_TRAFFIC_DATA: Traffic user is invalid: user=" + wLine
				CLS_OSIF.sPrn( wStr )
				continue
			wDomain = wDomain[1]
			
			##クエリ作成＆実行
			wQuery = "insert into TBL_TRAFFIC_DATA values (" + \
						"'" + wDomain + "'," + \
						"0," + \
						"-1," + \
						"-1," + \
						"-1," + \
						"0" + \
						") ;"
			wDBRes = wOBJ_DB.RunQuery( wQuery )
			wDBRes = wOBJ_DB.GetQueryStat()
			if wDBRes['Result']!=True :
				##失敗
				wStr = "CLS_Regist : __recovery_TBL_TRAFFIC_DATA: DB insert is failed: " + wDBRes['Reason']
				CLS_OSIF.sPrn( wStr )
				wOBJ_DB.Close()
				return False
		
		#############################
		# DBのクローズ
		wOBJ_DB.Close()
		return True



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



#####################################################
# テーブル作成: TBL_TREND
#####################################################
	def __create_TBL_TREND( self, inOBJ_DB, inTBLname="TBL_TREND" ):
		#############################
		# テーブルのドロップ
		wQuery = "drop table if exists " + inTBLname + ";"
		inOBJ_DB.RunQuery( wQuery )
		
		#############################
		# テーブル枠の作成
		wQuery = "create table " + inTBLname + "(" + \
					"rank        INTEGER  DEFAULT 0," + \
					"name        TEXT  NOT NULL," + \
					"domain      TEXT  NOT NULL," + \
					"uses        INTEGER  DEFAULT 0," + \
					"accs        INTEGER  DEFAULT 0," + \
					"lupdate     TIMESTAMP" + \
					" ) ;"
		
		inOBJ_DB.RunQuery( wQuery )
		return



#####################################################
# テーブル作成: TBL_TWITTER_READER
#####################################################
	def __create_TBL_TWITTER_READER( self, inOBJ_DB, inTBLname="TBL_TWITTER_READER" ):
		#############################
		# テーブルのドロップ
		wQuery = "drop table if exists " + inTBLname + ";"
		inOBJ_DB.RunQuery( wQuery )
		
		#############################
		# テーブル枠の作成
		wQuery = "create table " + inTBLname + "(" + \
					"id          TEXT  NOT NULL," + \
					"text        TEXT  NOT NULL," + \
					"screen_name TEXT  NOT NULL," + \
					"send_user   TEXT  NOT NULL," + \
					"tags        TEXT  NOT NULL," + \
					"lupdate     TIMESTAMP," + \
					"sended      BOOL  DEFAULT false," + \
					" PRIMARY KEY ( id ) ) ;"
		
		inOBJ_DB.RunQuery( wQuery )
		return



