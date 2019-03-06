#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：マスター初期化処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/2/27
#####################################################
import os
import sys
gPath = os.path.dirname(os.path.abspath(__file__)) + "/../script"
sys.path.append(gPath)

from datetime import datetime
import time
import subprocess as sp
import global_val
from mylog import CLS_Mylog
from filectrl import CLS_File
from regist import CLS_Regist
from config import CLS_Config
from toot import CLS_Toot


from mainproc import CLS_MainProc

from mastodon_use import CLS_Mastodon_Use
from twitter_use import CLS_Twitter_Use
from randtoot import CLS_RandToot
from lookptl import CLS_LookPTL
from lookrip import CLS_LookRIP
from circletoot import CLS_CircleToot
from userinfo import CLS_UserInfo
from tootcorr import CLS_TootCorrect
from traffic import CLS_Traffic
from lookhard import CLS_LookHard


#####################################################
class CLS_Init:
	FLG_MyLock    = False

#####################################################
# Init
#####################################################
	def __init__(self):
		
		#############################
		# クラスの生成
		global_val.gCLS_Mylog = CLS_Mylog()
		global_val.gCLS_File  = CLS_File()
		global_val.gCLS_Regist = CLS_Regist()
		global_val.gCLS_Config = CLS_Config()
		global_val.gCLS_Toot = CLS_Toot()
		
		#############################
		# システム情報の取得
		self._getLucibotVer()
		self._getPythonVer()
		
		global_val.gSTR_SystemInfo['HostName'] = str(os.uname()[1]).strip()
		return



#####################################################
# ping疎通確認
#####################################################
###	def cPing( self, send_ping, count=4, timeout=5000 ):
	def cPing( self, send_ping, count=4 ):
		index = send_ping.find(global_val.gSTR_SystemInfo['HostName'])
		#############################
		# hostがローカルっぽい？
		if index>=0 :
			wHostLen = len( global_val.gSTR_SystemInfo['HostName'] )
			wPingLen = len( send_ping )
			if (wHostLen+index)==wPingLen :
				return True	#自hostなら疎通チェックせずOKとする
		
###		wRes = sp.getstatusoutput( "ping -c " + str(count) + " -w " + str(timeout) + " " + str(send_ping) )
###		status,result = sp.getstatusoutput( "ping -c " + str(count) + " -w " + str(timeout) + " " + str(send_ping) )
		status,result = sp.getstatusoutput( "ping -c " + str(count) + " " + str(send_ping) )
		if status==0 :
			return True	# Link UP
		
		return False	# Link Down



#####################################################
# 画面クリア
#####################################################
	def cDispClear( self ):
		###os.system('cls') #windowsの場合
		os.system('clear')
		return



#####################################################
# 初期処理
#####################################################
	def cInit(self):
		#############################
		# 環境設定のロード
		global_val.gCLS_Config = CLS_Config()
		global_val.gCLS_Config.cGet()
		
		#############################
		# 排他制御
		#   True =排他中
		#   False=なし/ここで排他する
		if self.cLocked() == True:
			return False
		
		#############################
		# botを起動するか
		if global_val.gConfig["BotStart"] != "on" :
			return False	#起動しない
		
		#############################
		# クラスの生成
		global_val.gCLS_Mylog = CLS_Mylog()
		global_val.gCLS_RandToot = CLS_RandToot()
		global_val.gCLS_LookPTL = CLS_LookPTL()
		global_val.gCLS_LookRIP = CLS_LookRIP()
		global_val.gCLS_CircleToot = CLS_CircleToot()
		global_val.gCLS_UserInfo = CLS_UserInfo()
		global_val.gCLS_TootCorrect = CLS_TootCorrect()
		global_val.gCLS_Traffic = CLS_Traffic()
		global_val.gCLS_LookHard = CLS_LookHard()
		global_val.gCLS_Twitter = CLS_Twitter_Use()
		
		#############################
		# mastodonクラスの生成
		global_val.gCLS_Mastodon = CLS_Mastodon_Use(
				api_base_url = global_val.gConfig["BaseUrl"],
				client_id = global_val.gMastodonParam['RegFilePath'],
				access_token = global_val.gMastodonParam['UserFilePath'],
				flg_orginit=True )
		
		#############################
		# mastodonが生成されたか確認
		if global_val.gCLS_Mastodon.Flg_Init != True :
			return False	#失敗
		
		return True



#####################################################
# 初期処理：ハード監視用
#####################################################
	def cInit_Hard(self):
		#############################
		# 環境設定のロード
		global_val.gCLS_Config = CLS_Config()
		global_val.gCLS_Config.cGet()
		
		#############################
		# botを起動するか
		if global_val.gConfig["LookHard"] != "on" :
			return False	#起動しない
		
		#############################
		# クラスの生成
		global_val.gCLS_LookHard = CLS_LookHard()
		global_val.gCLS_Mylog = CLS_Mylog()
		
		global_val.gCLS_Mastodon = CLS_Mastodon_Use(
				api_base_url = global_val.gConfig["BaseUrl"],
				client_id = global_val.gMastodonParam['RegFilePath'],
				access_token = global_val.gMastodonParam['UserFilePath'],
				flg_orginit=True )
		
		#############################
		# mastodonが生成されたか確認
		if global_val.gCLS_Mastodon.Flg_Init != True :
			return False	#失敗
		
		return True



#####################################################
# 排他制御
#   True =排他中
#   False=なし
#####################################################
	def cLocked(self):
		#############################
		# 排他処理をしなければ なし
		if global_val.gConfig["Lock"] == "off" :
			return False
		
		#############################
		# 排他ファイルオープン
		for line in open( global_val.gLock_file, 'r'):	#ファイルを開く
			lockstat = line.strip()
		
		#############################
		# 排他=なし
		#   排他ONする
		if lockstat == '0':
			file = open( global_val.gLock_file, 'w')
			file.close()
			file = open( global_val.gLock_file, 'w')
			
			line = "1"
			setline = []
			setline.append(line)
			file.writelines( setline )
			file.close()
			
			self.FLG_MyLock = True
			return False	#排他なし
		
		#############################
		# 排他=排他中
		#   待つ
		if line == "1":
			self.cLockwait()
		
		return True	#排他あり



#####################################################
# 排他解除
#####################################################
	def cUnlock(self):
		file = open( global_val.gLock_file, 'w')
		file.close()
		file = open( global_val.gLock_file, 'w')
		
		line = "0"
		setline = []
		setline.append(line)
		file.writelines( setline )
		file.close()
		return



#####################################################
# 排他待ち
#####################################################
	def cLockwait(self):
		
		#############################
		# ループ回数に達するまでLockを監視する
		wLoop = 0
		while True:
			#############################
			# 5秒wait
			time.sleep(5)
			
			#############################
			# 排他を確認する
			#   排他が解除されていたらwaitを終わる
			for line in open( global_val.gLock_file, 'r'):	#ファイルを開く
				lockstat = line.strip()
			
			if lockstat == '0':
				return
			
			#############################
			# ループ回数に達したらwaitを終わる
			wLoop += 1
			if wLoop >= global_val.gLockWait_Num :
				break
		
		#############################
		# 排他を解除する
		self.cUnlock()
		
		return



#####################################################
# 時間を取得する
#####################################################
	def cGetTime(self):
		wRes = {
			"Result"	: False,
			"Object"	: "",
			"TimeDate"	: ""
		}
		
		try:
			wRes['Object'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			wRes['TimeDate'] = str( wRes['Object'] )
		except ValueError as err :
			return wRes
		
		wRes['Result'] = True
		return wRes



#####################################################
# コンソールへのprint表示
#   pythonバージョン混在回避のため関数からコールさせる
#####################################################
	def cPrint( self, message ):
		print( message )
		return



#####################################################
# システム情報の表示
#####################################################
	def cViewSysinfo(self):
		
		###画面クリアして一覧表示する
		global_val.gCLS_Init.cDispClear()
		wStr = "--------------------" + '\n'
		wStr = wStr + " システム情報" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 時間の取得
		wRes = self.cGetTime()
		if wRes['Result']==True :
			wStr = wStr + wRes['TimeDate'] + '\n'
		
		#############################
		# 情報組み立て
		wStr = wStr + "Name= " + global_val.gSTR_SystemInfo['BotName'] + '\n'
		wStr = wStr + "Date= " + global_val.gSTR_SystemInfo['BotDate'] + '\n'
		wStr = wStr + "Ver = " + global_val.gSTR_SystemInfo['Version'] + '\n'
		wStr = wStr + "Admin= " + global_val.gSTR_SystemInfo['Admin'] + '\n'
		wStr = wStr + "github= " + global_val.gSTR_SystemInfo['github'] + '\n'
		
		wStr = wStr + "Python= " + str( global_val.gSTR_SystemInfo['PythonVer'] )  + '\n'
		wStr = wStr + "HostName= " + global_val.gSTR_SystemInfo['HostName'] + '\n'
		
		#############################
		# コンソールに表示
		self.cPrint( wStr )
		return



#####################################################
# HELP表示
#####################################################
	def cViewHelp(self):
		if global_val.gCLS_File.cExist( global_val.gSTR_File['Readme_Command'] )!=True :
			###イレギュラーなんだよなぁ...
			global_val.gCLS_Init.cPrint( "cCLS_Init: cViewHelp: Readme Command file is not found: " + global_val.gSTR_File['Readme_Command'] )
			return False
		
		wStr = ""
		for line in open( global_val.gSTR_File['Readme_Command'], 'r'):	#ファイルを開く
			wStr = wStr + line
			
		global_val.gCLS_Init.cPrint( wStr )
		return True



#####################################################
# るしぼっとVersion
#####################################################
	def _getLucibotVer(self):
		if global_val.gCLS_File.cExist( global_val.gSTR_File['Readme'] )!=True :
			###イレギュラーなんだよなぁ...
			global_val.gCLS_Init.cPrint( "cCLS_Init: cViewHelp: Readme file is not found: " + global_val.gSTR_File['Readme'] )
			return False
		
		for line in open( global_val.gSTR_File['Readme'], 'r'):	#ファイルを開く
			#############################
			# 分解+要素数の確認
			line = line.strip()
			get_line = line.split("= ")
			if len(get_line) != 2 :
				continue
			
			get_line[0] = get_line[0].replace("::", "")
			#############################
			# キーがあるか確認
			if get_line[0] not in global_val.gSTR_SystemInfo :
				continue
			
			#############################
			# キーを設定
			global_val.gSTR_SystemInfo[get_line[0]] = get_line[1]
		
		return True



#####################################################
# Python version取得
#   参考：
#   sys.version_info(major=2, minor=7, micro=5, releaselevel='final', serial=0)
#####################################################
	def _getPythonVer(self):
##		global_val.gSTR_SystemInfo['PythonVer'] = sys.version_info.major
		
		wCHR_version = str(sys.version_info.major) + "."
		wCHR_version = wCHR_version + str(sys.version_info.minor) + "."
		wCHR_version = wCHR_version + str(sys.version_info.micro) + "."
		wCHR_version = wCHR_version + str(sys.version_info.serial) + " "
		wCHR_version = wCHR_version + sys.version_info.releaselevel
		global_val.gSTR_SystemInfo['PythonVer'] = wCHR_version
		return



