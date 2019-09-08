#!/usr/bin/python
# coding: UTF-8
#####################################################
# public
#   Class   ：OS I/F (OS向け共通処理)
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/9/7
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   Get_PythonVer(self):
#   Get_HostName(self):
#
# Class Function(static):
#   sGet_Resp(cls):
#   sGetArg(cls):
#   sGetTime(cls):
#   sGetTimeformat( cls, inTimedate, inTimezone=__DEF_TIMEZONE ):
#   sTimeLag( cls, inTimedate, inThreshold=300, inTimezone=cls.DEF_TIMEZONE ):
#   sSleep( cls, inSec ):
#   sPing( cls, inSend_Ping, inCount=4 ):
#   sDispClr( cls ):
#   sGetCwd( cls ):
#   sPrn( cls, inMsg ):
#   sInp( cls, inMsg ):
#   sGpp( cls, inMsg ):
#   sDel_HTML( cls, inCont ):
#   sChkREMString( cls, inStr, inSpace=True ):
#   sRe_Search( cls, inPatt, inCont ):
#   sGetRand( cls, inValue ):
#
#####################################################
from datetime import datetime
from datetime import timedelta
import time
import os
import sys
import re
import subprocess as sp
from getpass import getpass
import random

#####################################################
class CLS_OSIF() :
#####################################################

	__DEF_TIMEZONE = 9				#タイムゾーン: 9=東京
	DEF_PING_COUNT   = "2"			#Ping回数 (文字型)
##	DEF_PING_TIMEOUT = "1000"		#Pingタイムアウト秒 (文字型)

	#############################
	# ping除外
	STR_NotPing = [
		"friends.nico",
		"flower.afn.social",
		"(dummy)"
	]

#####################################################
# 共通レスポンス取得
#####################################################

##		#############################
##		# 応答形式の取得
##		#   "Result" : False, "Reason" : None, "Responce" : None
##		wRes = CLS_OSIF.sGet_Resp()

	@classmethod
	def sGet_Resp(cls):
		wRes = {
			"Result"   : False,
			"Reason"   : None,
			"Responce" : None }
		
		return wRes



#####################################################
# 引数取得
#####################################################
	@classmethod
	def sGetArg(cls):
		wArg = sys.argv
		return wArg



#####################################################
# 時間を取得する
#####################################################
	@classmethod
	def sGetTime(cls):
		wRes = {
			"Result"	: False,
			"Object"	: "",
			"TimeDate"	: "",
			"Hour"		: 0,
			"Week"		: 0,
			"(dummy)"	: 0
		}
		
		try:
			wNow_TD = datetime.now()
			wRes['Object']   = wNow_TD
			wRes['TimeDate'] = wNow_TD.strftime("%Y-%m-%d %H:%M:%S")
			wRes['Hour']     = wNow_TD.strftime("%H")		#時間だけ
			wRes['Week']     = str( wNow_TD.weekday() )		#曜日 0=月,1=火,2=水,3=木,4=金,5=土,6=日
		except ValueError as err :
			return wRes
		
		wRes['Result'] = True
		return wRes



#####################################################
# 計算しやすいように時間フォーマットを変更する
# (mastodon時間)
#####################################################
	@classmethod
	def sGetTimeformat( cls, inTimedate, inTimezone=__DEF_TIMEZONE ):
		wRes = {
			"Result"	: False,
			"TimeDate"	: ""
		}
		
		#############################
		# 入力時間の整形
		wTD = str( inTimedate )
			##形式合わせ +、.を省く（鯖によって違う？
		wIfind = wTD.find('+')
		wTD = wTD[0:wIfind]
		wIfind = wTD.find('.')
		if wIfind>=0 :
			wTD = wTD[0:wIfind]
		
		#############################
		# タイムゾーンで時間補正
		try:
			wRes['TimeDate'] = datetime.strptime( wTD, "%Y-%m-%d %H:%M:%S") + timedelta( hours=inTimezone )
		except:
			return wRes	#失敗
		
		wRes['Result'] = True
		return wRes



#####################################################
# 時間差
#    Threshold = 300	# 60(s) * 5(m)
#####################################################
	@classmethod
	def sTimeLag( cls, inTimedate, inThreshold=300, inTimezone=__DEF_TIMEZONE ):
		wRes = {
			"Result"	: False,
			"Beyond"	: False,
			"Future"	: False,
			"InputTime"	: "",
			"NowTime"	: "",
			"RateTime"	: "",
			"RateSec"	: 0
		}
		
		#############################
		# 入力時間の整形
		wTD = str( inTimedate )
			##形式合わせ +、.を省く（鯖によって違う？
		wIfind = wTD.find('+')
		wTD = wTD[0:wIfind]
		wIfind = wTD.find('.')
		if wIfind>=0 :
			wTD = wTD[0:wIfind]
		
		#############################
		# 現時間の取得
		wNowTime = cls().sGetTime()
		if wNowTime['Result']!=True :
			return wRes	#失敗
		
		#############################
		# タイムゾーンで時間補正
		try:
##			wTD = datetime.strptime( wTD, "%Y-%m-%d %H:%M:%S") + timedelta( hours=inTimezone )
			wTD = datetime.strptime( wTD, "%Y-%m-%d %H:%M:%S")
		except:
			return wRes	#失敗
		if inTimezone!=-1 :
			wTD = wTD + timedelta( hours=inTimezone )
		
		#############################
		# 差を求める(秒差)
##		wRateTime = wNowTime['Object'] - wTD
		if wNowTime['Object']>=wTD :
			wRateTime = wNowTime['Object'] - wTD
		else :
			wRateTime = wTD - wNowTime['Object']
			wRes['Future'] = True	#未来時間
		
		wRateSec = wRateTime.total_seconds()
		
		if wRateSec > inThreshold :
			wRes['Beyond'] = True	#差あり
		
		wRes['InputTime'] = wTD
		wRes['NowTime']   = wNowTime['TimeDate']
		wRes['RateTime']  = wRateTime
		wRes['RateSec']   = wRateSec
		wRes['Result']    = True
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
###	def sPing( cls, inSend_Ping, inCount=4 ):
	def sPing( cls, inSend_Ping ):
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
###		wStatus, wResult = sp.getstatusoutput( "ping -c " + str(inCount) + " " + str(inSend_Ping) )
##		wPingComm = "ping -c " + cls.DEF_PING_COUNT + " -w " + cls.DEF_PING_TIMEOUT + " " + str(inSend_Ping)
		wPingComm = "ping -c " + cls.DEF_PING_COUNT + " " + str(inSend_Ping)
		wStatus, wResult = sp.getstatusoutput( wPingComm )
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



#####################################################
# row['content']からHTMLタグを除去
#####################################################
	@classmethod
	def sDel_HTML( cls, inCont ):
		wPatt = re.compile(r"<[^>]*?>")
		wD_Cont = wPatt.sub( "", inCont )
		return wD_Cont



#####################################################
# row['content']からHTMLタグを除去
#####################################################
	@classmethod
	def sChkREMString( cls, inStr, inSpace=True ):
		wPatt = r'[\\|/|:|?|.|"|<|>|\|]'
		wRes = cls().sRe_Search( wPatt, inStr )
		if wRes==False :
			return False
		
		if inSpace==True :
			if inStr.find(" ")<0 :
				return False
		
		return True



#####################################################
# 文字列からパターン検索
#####################################################
	@classmethod
	def sRe_Search( cls, inPatt, inCont ):
		try:
			wRes = re.search( inPatt, inCont )
		except:
			return False
		
		return wRes



#####################################################
# ランダム値を取得
#####################################################
	@classmethod
	def sGetRand( cls, inValue ):
		if not isinstance( inValue, int ):
			return -1
		
		try:
			wVal = random.randrange( inValue )
		except:
			return -1
		
		return wVal



