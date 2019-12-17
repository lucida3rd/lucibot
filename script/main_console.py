#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：メイン処理(コンソール)
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/12/17
#####################################################
# Private Function:
#   __getLucibotVer(cls):
#   __getSystemInfo(cls):
#
# Instance Function:
#   (none)
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
from filectrl import CLS_File
from setup import CLS_Setup
from toot import CLS_Toot
from config import CLS_Config
from regist import CLS_Regist
from userdata import CLS_UserData
from bot_ctrl import CLS_Bot_Ctrl
from dbedit import CLS_DBedit
from logarcive import CLS_LogArcive

from twitter_use import CLS_Twitter_Use
from gval import gVal
#####################################################
class CLS_Main_Console() :
#####################################################

#####################################################
# 実行
#####################################################
	@classmethod
	def sRun(cls):
		#############################
		# システム情報を取得する
		cls().__getSystemInfo()
		cls().__getLucibotVer()
		
		#############################
		# 初期化
		gVal.FLG_Console_Mode = True	#コンソールモード
		
		#############################
		# データフォルダのチェック
		if CLS_File.sExist( gVal.DEF_USERDATA_PATH )!=True :
			###手順ミスorデータ消した
			wStr = '\n' + gVal.STR_SystemInfo['Client_Name'] + " データフォルダがないため起動できません。" + '\n'
			wStr = wStr + "フォルダは " + gVal.STR_SystemInfo['Client_Name'] + " のcloneを置いた上位フォルダ(=cloneと同一階層)に作成します。" + '\n'
			wStr = wStr + "詳しくはreadme_setup.txtをご参照ください。" + '\n'
			CLS_OSIF.sPrn( wStr )
			return
		
		#############################
		# Master環境情報の読み込み
		if CLS_Config.sGetMasterConfig()!=True :
			# MasterConfigがないのでセットアップするか？
			wStr = '\n' + "データフォルダにMaster環境情報がないため起動できません。" + '\n'
			wStr = wStr + "データが初期セットアップされていない可能性があります。"
			CLS_OSIF.sPrn( wStr )
			wRes = CLS_OSIF.sInp( "セットアップしますか？(y/N)=> " )
			if wRes!="y" :
				CLS_OSIF.sPrn( "起動を中止しました。" )
				return
			
			#############################
			# 環境のセットアップ
			wCLS_Setup = CLS_Setup()
			if wCLS_Setup.MasterSetup()!=True :
				CLS_OSIF.sPrn( "セットアップを中止します。" )
				return
			
			wCLS_Setup = ""
			CLS_OSIF.sInp( '\n' + "セットアップが完了しました。リターンキーを押してください。[RT]" )
		
		#####################################################
		# MasterUserが未登録
		if gVal.STR_MasterConfig['MasterUser']=="" :
			CLS_OSIF.sPrn( "MasterUserが登録されていないため、bot動作ができません。MasterUserを登録します。" )
			wCLS_Config = CLS_Config()
			wRes = wCLS_Config.CnfMasterUser()
			if wRes!=True :
				#############################
				# 0件の場合は、ユーザ登録させる
				wList = CLS_UserData.sGetUserList()
				if len(wList)==0 :
					wCLS_work = CLS_Regist()
					wCLS_work.Regist()
				
				CLS_OSIF.sInp( "リターンキーを押して再度コンソールアプリを起動してください。[RT]" )
				return
			
			wCLS_Config = ""
		
		#############################
		# ** 初期化モード **
		wArg = CLS_OSIF.sGetArg()
		if len(wArg)==2 :
			if wArg[1]=="init" :
				wCLS_Setup = CLS_Setup()
				wCLS_Setup.AllInit()
				CLS_OSIF.sInp( "リターンキーを押して再度コンソールアプリを起動してください。[RT]" )
			return
		
		#############################
		# コンソールを表示
		while True :
			wCommand = cls().sViewMainConsole()
			
			if wCommand.find("\\q")>=0 or wCommand=="exit" :
				###終了
				CLS_OSIF.sPrn( "コンソールを停止します。" + '\n' )
				break
			
			wRes = cls().sRunCommand( wCommand )
			if wRes==True :
				CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
		
		return



#####################################################
# メインコンソール画面の表示
#####################################################
	@classmethod
	def sViewMainConsole(cls):
		
		#############################
		# メインコンソール画面
		wRes = cls().sViewDisp( "MainConsole" )
		if wRes==False :
			return "q"	#失敗=強制終了
		
		wCommand = CLS_OSIF.sInp( "コマンド？=> " )
		return wCommand



#####################################################
# 実行
#####################################################
	@classmethod
	def sRunCommand( cls, inCommand ):

		wCLS_work = ""
		wFlg = False
		
	#####################################################
		#############################
		# システム情報の表示
##		if inCommand=="-v" :
		if inCommand=="\\v" :
			cls().sView_Sysinfo()
			wFlg = True
		#############################
		# Master環境情報の表示
##		elif inCommand=="-vm" :
		elif inCommand=="\\vm" :
			wCLS_work = CLS_Config()
			wCLS_work.MasterConfig_Disp()
			wFlg = True
		
	#####################################################
		#############################
		# Master環境情報の表示・操作
##		elif inCommand=="-c" :
		elif inCommand=="\\c" :
			wCLS_work = CLS_Config()
			wCLS_work.CnfMasterConfig()
			wFlg = True
		#############################
		# MasterUserの変更
##		elif inCommand=="-cm" :
		elif inCommand=="\\cm" :
			wCLS_work = CLS_Config()
			wCLS_work.CnfMasterUser()
			wFlg = True
		#############################
		# AdminUserの変更
##		elif inCommand=="-ca" :
		elif inCommand=="\\ca" :
			wCLS_work = CLS_Config()
			wCLS_work.CnfAdminUser()
			wFlg = True
		
	#####################################################
		#############################
		# ユーザ登録 一覧表示
##		elif inCommand=="-u" :
		elif inCommand=="\\u" :
			wCLS_work = CLS_UserData()
			wCLS_work.ViewUserList()
			wFlg = True
		
		#############################
		# ユーザ登録 登録
##		elif inCommand=="-ur" :
		elif inCommand=="\\ur" :
			wCLS_work = CLS_Regist()
			wCLS_work.Regist()
			wFlg = True
		
		#############################
		# ユーザ登録 再登録
##		elif inCommand=="-uu" :
		elif inCommand=="\\uu" :
			wCLS_work = CLS_Regist()
			wCLS_work.Update()
			wFlg = True
		
		#############################
		# ユーザ登録 削除
##		elif inCommand=="-ud" :
		elif inCommand=="\\ud" :
			wCLS_work = CLS_Regist()
			wCLS_work.Delete()
			wFlg = True
		#############################
		# User環境情報の表示・操作
##		elif inCommand=="-uc" :
		elif inCommand=="\\uc" :
			wCLS_work = CLS_Config()
			wCLS_work.CnfUserConfig()
			wFlg = True
		
	#####################################################
		#############################
		# 手動トゥートモード
##		elif inCommand=="-t" :
		elif inCommand=="\\t" :
			wCLS_work = CLS_Toot()
			wCLS_work.ManualToot()
			wFlg = True
		
		#############################
		# 同報配信トゥートモード
##		elif inCommand=="-tm" :
		elif inCommand=="\\tm" :
			wCLS_work = CLS_Toot()
			wCLS_work.MulticastToot()
			wFlg = True
		
		#############################
		# Twitterモード
##		elif inCommand=="-tw" :
		elif inCommand=="\\tw" :
			wCLS_work = CLS_Toot()
			wCLS_work.ManualTweet()
			wFlg = True
		
	#####################################################
		#############################
		# 通信テスト
##		elif inCommand=="-test" :
		elif inCommand=="\\test" :
			wCLS_work = CLS_Regist()
			wCLS_work.Test()
			wFlg = True
		
		#############################
		# DBエディタ
##		elif inCommand=="-vdb" :
		elif inCommand=="\\vdb" :
			wCLS_work = CLS_DBedit()
			wCLS_work.View()
			wFlg = True
		
	#####################################################
		#############################
		# master運用操作
##		elif inCommand=="-run" :
		elif inCommand=="\\run" :
			wCLS_work = CLS_Bot_Ctrl()
			wCLS_work.Console()
			wFlg = True
		#############################
		# Twitter連携
##		elif inCommand=="-ct" :
		elif inCommand=="\\ct" :
			wCLS_Twitter = CLS_Twitter_Use()
			wCLS_Twitter.CreateTwitter( gVal.DEF_STR_FILE['Twitter_File'], gVal.DEF_STR_FILE['defTwitter_File'] )
			wCLS_work = CLS_Config()
			wCLS_work.CnfTwitter()	#有効無効設定
			
##			##タイムラインの設定
##			CLS_OSIF.sPrn( '\n' + "Twitterと接続しています......" )
##			wCLS_Twitter = CLS_Twitter_Use( gVal.DEF_STR_FILE['Twitter_File'], gVal.DEF_STR_TLNUM['getTwitTLnum'] )
##			if gVal.STR_MasterConfig['Twitter']=="on" :
##				wCLS_Twitter.CnfTimeline( gVal.DEF_STR_FILE['Twitter_File'] )
##			
			wFlg = True
		#############################
		# ログアーカイブ
		elif inCommand=="\\arc" :
			wCLS_work = CLS_LogArcive()
			wCLS_work.Run()
			wFlg = True
		
		return wFlg



#####################################################
# ディスプレイ表示
#####################################################
	@classmethod
	def sViewDisp( cls, inDisp ):
		#############################
		# ディスプレイファイルの確認
		wKeylist = gVal.DEF_STR_DISPFILE.keys()
		if inDisp not in wKeylist :
			###キーがない(指定ミス)
			CLS_OSIF.sPrn( "CLS_Main_Console: __viewDisp: Display key is not found: inDisp= " + inDisp )
			return False
		
		if CLS_File.sExist( gVal.DEF_STR_DISPFILE[inDisp] )!=True :
			###ファイルがない...(消した？)
			CLS_OSIF.sPrn( "CLS_Main_Console: __viewDisp: Display file is not found: " + gVal.DEF_STR_DISPFILE[inDisp] )
			return False
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# 中身表示
		wStr = ""
		for wLine in open( gVal.DEF_STR_DISPFILE[inDisp], 'r'):	#ファイルを開く
			wStr = wStr + wLine
		
		CLS_OSIF.sPrn( wStr )
		return True



#####################################################
# システム情報の表示
#####################################################
	@classmethod
	def sView_Sysinfo(cls):
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " システム情報" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 時間の取得
		wRes = CLS_OSIF.sGetTime()
		if wRes['Result']==True :
			wStr = wStr + wRes['TimeDate'] + '\n'
		
		#############################
		# 情報組み立て
		wStr = wStr + "Name= " + gVal.STR_SystemInfo['BotName'] + '\n'
		wStr = wStr + "Date= " + gVal.STR_SystemInfo['BotDate'] + '\n'
		wStr = wStr + "Ver = " + gVal.STR_SystemInfo['Version'] + '\n'
		wStr = wStr + "Admin= " + gVal.STR_SystemInfo['Admin'] + '\n'
		wStr = wStr + "github= " + gVal.STR_SystemInfo['github'] + '\n'
		
		wStr = wStr + "Python= " + str( gVal.STR_SystemInfo['PythonVer'] )  + '\n'
		wStr = wStr + "HostName= " + gVal.STR_SystemInfo['HostName'] + '\n'
		
		#############################
		# コンソールに表示
		CLS_OSIF.sPrn( wStr )
		return



#####################################################
# るしぼっとVersion
#####################################################
	def __getLucibotVer(cls):
		if CLS_File.sExist( gVal.DEF_STR_FILE['Readme'] )!=True :
			###readmeファイル消すなwww
			CLS_OSIF.sPrn( "CLS_Main_Console: __getLucibotVer: Readme file is not found: " + gVal.DEF_STR_FILE['Readme'] )
			return False
		
		for wLine in open( gVal.DEF_STR_FILE['Readme'], 'r'):	#ファイルを開く
			#############################
			# 分解+要素数の確認
			wLine = wLine.strip()
			wGetLine = wLine.split("= ")
			if len(wGetLine) != 2 :
				continue
			
			wGetLine[0] = wGetLine[0].replace("::", "")
			#############################
			# キーがあるか確認
			if wGetLine[0] not in gVal.STR_SystemInfo :
				continue
			
			#############################
			# キーを設定
			gVal.STR_SystemInfo[wGetLine[0]] = wGetLine[1]
		
		return



#####################################################
# システム情報の取得
#####################################################
	def __getSystemInfo(cls):
		wCLS_work = CLS_OSIF()
		gVal.STR_SystemInfo['PythonVer'] = wCLS_work.Get_PythonVer()
		gVal.STR_SystemInfo['HostName']  = wCLS_work.Get_HostName()
		return



