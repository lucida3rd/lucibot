#!/usr/bin/python
# coding: UTF-8
#####################################################
# public
#   Class   ：OS I/F (OS向け共通処理)
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/11/24
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
#   sRe_Replace( cls, inPatt, inCont, inReplace ):
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

	__DEF_LAG_TIMEZONE  = 9			#デフォルト時間差 タイムゾーン: 9=東京
	__DEF_LAG_THRESHOLD = 300		#デフォルト時間差 時間差(秒)
									# 300(s) = 60 * 5(min)
	
##	DEF_PING_COUNT   = "2"			#Ping回数 (文字型)
	__DEF_PING_COUNT = "2"			#Ping回数 (文字型)
##	DEF_PING_TIMEOUT = "1000"		#Pingタイムアウト秒 (文字型)

	#############################
	# ping除外
##	STR_NotPing = [
	__DEF_ARR_NOTPING = [
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
##	def sGetTimeformat( cls, inTimedate, inTimezone=__DEF_TIMEZONE ):
	def sGetTimeformat( cls, inTimedate, inTimezone=__DEF_LAG_TIMEZONE ):
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
# 計算しやすいように時間フォーマットを変更する
# (twitter時間)
#####################################################
	@classmethod
	def sGetTimeformat_Twitter( cls, inTimedate, inTimezone=__DEF_LAG_TIMEZONE ):
		wRes = {
			"Result"	: False,
			"Format"	: "",
			"TimeDate"	: ""
		}
		
		wTD = inTimedate
		#############################
		# タイムゾーンで時間補正
		try:
			###整形
			wIfind = wTD.find('Z')
			if wIfind>=0 :
				### Trend形式
				wTD = str( wTD )
				wTD = wTD[0:wIfind]
				wTD = wTD.split('T')
				wTD = wTD[0] + " " + wTD[1]
				
				wTD = datetime.strptime( wTD, "%Y-%m-%d %H:%M:%S") + timedelta( hours=inTimezone )
				wTD = str( wTD )
				
				wRes['Format'] = "TrendType"
			else :
				### Twitter形式
				wTD = datetime.strptime( wTD, "%a %b %d %H:%M:%S %z %Y" ) + timedelta( hours=inTimezone )
				wTD = str( wTD )
				wIfind = wTD.find('+')
				if wIfind>=0 :
					wTD = wTD[0:wIfind]
				
				wRes['Format'] = "TwitterType"
			
			wRes['TimeDate'] = wTD
		except:
			return wRes	#失敗
		
		wRes['Result'] = True
		return wRes



#####################################################
# 時間差
#   inTimedate   比べる日時
#   inThreshold  比べる時間差(秒)
#   inTimezone   タイムゾーン補正値: デフォルト 9=東京
#                                    補正なし   -1
# 使い方１：
#   比べる日時と時間差を出す
#     inTimedate を設定("%Y-%m-%d %H:%M:%S")、
#     inThreshold を設定
#
# 使い方２：
#   現在日時から指定時間差の過去日時を出す
#     inTimedate は未設定 (None or null)
#     inThreshold を設定
#
#####################################################
	@classmethod
##	def sTimeLag( cls, inTimedate, inThreshold=300, inTimezone=__DEF_TIMEZONE ):
	def sTimeLag( cls, inTimedate=None, inThreshold=__DEF_LAG_THRESHOLD, inTimezone=__DEF_LAG_TIMEZONE ):
		#############################
		# 応答形式
		wRes = {
			"Result"	: False,	# 結果
			
			"Beyond"	: False,	# True= 比べる時間差を超えている
			"Future"	: False,	# True= 比べる時間が未来時間
			"InputTime"	: "",		# 比べる日時 str(入力時)
			"NowTime"	: "",		# 現在日時 str
			"RateTime"	: "",		# 現在日時から指定時間差の過去日時 str
			"RateDay"	: 0,		# 時間差(日数)
			"RateSec"	: 0			# 時間差(秒)
		}
		
		#############################
		# 現時間の取得
		wNowTime = cls().sGetTime()
		if wNowTime['Result']!=True :
			return wRes	#失敗
		
		#############################
		# 入力時間の整形
		if inTimedate!=None and inTimedate!="" :
		### 使い方１の場合= 比べる日時と時間差を出す
			wTD = str( inTimedate )
				##形式合わせ +、.を省く（鯖によって違う？
			wIfind = wTD.find('+')
			wTD = wTD[0:wIfind]
			wIfind = wTD.find('.')
			if wIfind>=0 :
				wTD = wTD[0:wIfind]
			
			### 加工しやすいようにフォーマットする
			try:
				wTD = datetime.strptime( wTD, "%Y-%m-%d %H:%M:%S")
			except:
				return wRes	#失敗
		
		### 現在日時から指定時間差の過去日時を出す
		else :
			wTD = wNowTime['Object'] - timedelta( seconds=inThreshold )
			wTD = str( wTD )
				##形式合わせ +、.を省く（鯖によって違う？
			wIfind = wTD.find('+')
			wTD = wTD[0:wIfind]
			wIfind = wTD.find('.')
			if wIfind>=0 :
				wTD = wTD[0:wIfind]
			
			### 加工しやすいようにフォーマットする
			try:
				wTD = datetime.strptime( wTD, "%Y-%m-%d %H:%M:%S")
			except:
				return wRes	#失敗


##		#############################
##		# 現時間の取得
##		wNowTime = cls().sGetTime()
##		if wNowTime['Result']!=True :
##			return wRes	#失敗
##		
##		#############################
##		# 加工しやすいようにフォーマットする
##		try:
##			wTD = datetime.strptime( wTD, "%Y-%m-%d %H:%M:%S") + timedelta( hours=inTimezone )
##			wTD = datetime.strptime( wTD, "%Y-%m-%d %H:%M:%S")
##		except:
##			return wRes	#失敗
##		
		
		#############################
		# タイムゾーンの指定があれば補正する
		if inTimezone!=-1 :
			wTD = wTD + timedelta( hours=inTimezone )
		
		#############################
		# 使い方１の場合
		#  =差を求める(秒差)
		if inTimedate!=None and inTimedate!="" :
			if wNowTime['Object']>=wTD :
				wRateTime = wNowTime['Object'] - wTD
			else :
				wRateTime = wTD - wNowTime['Object']
				wRes['Future'] = True	#未来時間
			
			wRes['RateDay'] = wRateTime.days
			wRes['RateSec'] = wRateTime.total_seconds()
			
			if wRes['RateSec'] > inThreshold :
				wRes['Beyond'] = True	#差あり
			
			wRes['InputTime'] = wTD
			wRes['NowTime']   = wNowTime['TimeDate']
		
		#############################
		# 使い方２の場合
		#  =結果を載せる
		else :
			wRes['NowTime']   = wNowTime['TimeDate']
			wRes['RateTime']  = wTD
##			print(str( wRes['RateTime'] ))
		
		#############################
		# 正常
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
###	def sPing( cls, inSend_Ping ):
	def sPing( cls, inSend_Ping="127.0.0.1" ):
		#############################
		# ping除外ホスト
##		if inSend_Ping in cls.STR_NotPing :
		if inSend_Ping in cls.__DEF_ARR_NOTPING :
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
		
		#############################
		# Ping実行
##		wPingComm = "ping -c " + cls.DEF_PING_COUNT + " -w " + cls.DEF_PING_TIMEOUT + " " + str(inSend_Ping)
		wPingComm = "ping -c " + cls.__DEF_PING_COUNT + " " + str(inSend_Ping)
		
		#############################
		# 結果判定
##		wStatus, wResult = sp.getstatusoutput( "ping -c " + str(inCount) + " -w " + str(inTimeout) + " " + str(inSend_Ping) )
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
# row['content']からURLを除去
#####################################################
	@classmethod
	def sDel_URL( cls, inCont ):
		wPatt = re.compile(r"https?:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+")
		wD_Cont = wPatt.sub( "", inCont )
		return wD_Cont



#####################################################
# 文字列からパターン検索
#   wRes.group()  正規表現にマッチした文字列を返す。
#   wRes.start()  マッチの開始位置を返す。
#   wRes.end()    マッチの終了位置を返す。
#   wRes.span()   マッチの位置 (start, end) を含むタプルを返す。
#####################################################
	@classmethod
	def sRe_Search( cls, inPatt, inCont ):
		try:
			wRes = re.search( inPatt, inCont )
		except:
			return False
		
		return wRes



#####################################################
# 文字列からパターン置換
#####################################################
	@classmethod
	def sRe_Replace( cls, inPatt, inCont, inReplace ):
		wRes = {
			"Result"	: False,
			"Match"		: False,
			"After"		: None
		}
		
		if inCont=="" :
			return wRes
		
		wRes['Match'] = cls.sRe_Search( inPatt, inCont )
		
		try:
			wRes['After'] = inCont.replace( inPatt, inReplace )
		except:
			return wRes
		
		wRes['Result'] = True
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



