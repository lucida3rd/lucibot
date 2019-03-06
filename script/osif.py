#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：OS I/F (OS向け共通処理)
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/6
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   Get_PythonVer(self):
#   Get_HostName(self):
#
# Class Function(static):
#   sGetTime(cls):
#   sPing( cls, inSend_Ping, inCount=4 ):
#   sDispClr( cls ):
#   sGetCwd( cls ):
#   sPrn( cls, inMsg ):
#   sInp( cls, inMsg ):
#   sGpp( cls, inMsg ):
#
#####################################################
from datetime import datetime
import time
import os
import sys
import subprocess as sp
from getpass import getpass

#####################################################
class CLS_OSIF() :
#####################################################

	#############################
	# ping除外
	STR_NotPing = [
		"friends.nico",
		"(dummy)"
	]

#####################################################
# 時間を取得する
#####################################################
	@classmethod
	def sGetTime(cls):
		wRes = {
			"Result"	: False,
			"Object"	: "",
			"TimeDate"	: ""
		}
		
		try:
			wRes['Object']   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			wRes['TimeDate'] = str( wRes['Object'] )
		except ValueError as err :
			return wRes
		
		wRes['Result'] = True
		return wRes



#####################################################
# スリープ
#####################################################
	@classmethod
	def sSleep( cls, inSec ):
		if isinstance( inSec, int )!=True :
			inSec = 5
		
		try:
			time.sleep( inSec )
		except ValueError as err :
			return False
		
		return True



#####################################################
# ping疎通確認
#####################################################
	@classmethod
###	def sPing( cls, inSend_Ping, inCount=4, inTimeout=5000 ):
	def sPing( cls, inSend_Ping, inCount=4 ):
		#############################
		# ping除外ホスト
		if inSend_Ping in cls.STR_NotPing :
			return True	#ping除外なら疎通チェックせずOKとする
		
		#############################
		# hostがローカルっぽい？
##		wI = inSend_Ping.find( gVal.STR_SystemInfo['HostName'] )
		wHostname = cls().Get_HostName()
		wI = inSend_Ping.find( wHostname )
		if wI>=0 :
##			wHostLen = len( gVal.STR_SystemInfo['HostName'] )
			wHostLen = len( wHostname )
			wPingLen = len( inSend_Ping )
			if (wHostLen + wI )==wPingLen :
				return True	#自hostなら疎通チェックせずOKとする
		
###		wStatus, wResult = sp.getstatusoutput( "ping -c " + str(inCount) + " -w " + str(inTimeout) + " " + str(inSend_Ping) )
		wStatus, wResult = sp.getstatusoutput( "ping -c " + str(inCount) + " " + str(inSend_Ping) )
		if wStatus==0 :
			return True	# Link UP
		
		return False	# Link Down



#####################################################
# Python version取得
#   参考：
#   sys.version_info(major=2, minor=7, micro=5, releaselevel='final', serial=0)
#####################################################
	def Get_PythonVer(self):
		wCHR_version = str(sys.version_info.major) + "."
		wCHR_version = wCHR_version + str(sys.version_info.minor) + "."
		wCHR_version = wCHR_version + str(sys.version_info.micro) + "."
		wCHR_version = wCHR_version + str(sys.version_info.serial) + " "
		wCHR_version = wCHR_version + sys.version_info.releaselevel
		return wCHR_version



#####################################################
# Host名取得
#####################################################
	def Get_HostName(self):
		wCHR_hostname = str(os.uname()[1]).strip()
		return wCHR_hostname



#####################################################
# 画面クリア
#####################################################
	@classmethod
	def sDispClr( cls ):
		###os.system('cls') #windowsの場合
		os.system('clear')
		return



#####################################################
# カレントパスの取得
#####################################################
	@classmethod
	def sGetCwd( cls ):
		wStr = os.getcwd()
		return wStr



#####################################################
# コンソールへのprint表示
#####################################################
	@classmethod
	def sPrn( cls, inMsg ):
		print( inMsg )
		return



#####################################################
# コンソールへのinput表示
#####################################################
	@classmethod
	def sInp( cls, inMsg ):
		wInput = input( inMsg ).strip()
		return wInput



#####################################################
# コンソールへのinput表示(入力が見えない)
#####################################################
	@classmethod
	def sGpp( cls, inMsg ):
		wInput = getpass( inMsg ).strip()
		return wInput



