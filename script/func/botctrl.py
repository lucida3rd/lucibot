#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：bot制御(共通)
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/14
#####################################################
# Private Function:
#   __openLock( cls, inPath ):
#   __lockWait( cls, inPath ):
#   __backWait( cls, inPath ):
#
# Instance Function:
#   (none)
#
# Class Function(static):
#   sLock( cls, inPath ):
#   sUnlock( cls, inPath ):
#   sChk1HourTime( cls, inPath ):
#
#####################################################

from osif import CLS_OSIF
from filectrl import CLS_File
from gval import gVal
#####################################################
class CLS_BotCtrl():
#####################################################

#####################################################
# 排他制御
#   True =排他中
#   False=なし
#####################################################
	@classmethod
	def sLock( cls, inPath ):
##		#############################
##		# 排他処理をしなければ なし
##		if gVal.STR_MasterConfig['Lock'] != "on" :
##			return False
		
		#############################
		# 排他ファイルオープン
		wLockStat = CLS_BotCtrl.__openLock( inPath )
		
		#############################
		# 排他確認
		
		#############################
		# 排他=0 :なし
		#   排他ONする
		if wLockStat == "0" :
			wLock = []
			wLock.append("1")
			wFilePath = inPath + gVal.STR_File['LockFile']
			if CLS_File.sWriteFile( wFilePath, wLock )!=True :
				return True	#失敗=排他あり にしてる
			
			return False	#排他なし
		
		#############################
		# 排他=1: 排他中
		#   待つ
		elif wLockStat == "1" :
			CLS_BotCtrl.__lockWait( inPath )
		
		#############################
		# 排他=8: バックグラウンド処理待ち
		#   待つ
		elif wLockStat == "8" :
			CLS_BotCtrl.__backWait( inPath )
			return False	#排他なし
		
		#############################
		# 排他=その他 失敗
		#### 排他あり
		
		return True	#排他あり



#####################################################
# 排他解除
#####################################################
	@classmethod
	def sUnlock( cls, inPath ):
		wLock = []
		wLock.append("0")
		wFilePath = inPath + gVal.STR_File['LockFile']
		CLS_File.sWriteFile( wFilePath, wLock )
		return



#####################################################
# 排他読み込み
#####################################################
	@classmethod
	def __openLock( cls, inPath ):
		wLock = []
		wFilePath = inPath + gVal.STR_File['LockFile']
		if CLS_File.sReadFile( wFilePath, wLock )!=True :
			return "3"	#失敗=排他あり にしてる
		
		return wLock[0]



#####################################################
# 排他待ち
#####################################################
	@classmethod
	def __lockWait( cls, inPath ):
		#############################
		# ループ回数に達するまでLockを監視する
		wLoop = 0
		while True:
			#############################
			# sleep
			CLS_OSIF.sSleep( gVal.DEF_LOCK_LOOPTIME )
			
			#############################
			# 排他を確認する
			#   排他が解除されていたらwaitを終わる
			wLockStat = CLS_BotCtrl.__openLock( inPath )
			if wLockStat == "0" :
				return
			
			#############################
			# ループ回数に達したらwaitを終わる
			wLoop += 1
			if wLoop >= gVal.DEF_LOCK_WAITCNT :
				break
		
		#############################
		# 排他を解除する (waitタイムアウト時)
		CLS_BotCtrl.sUnlock( inPath )
		return



#####################################################
# バックグラウンド処理待ち
#####################################################
	@classmethod
	def __backWait( cls, inPath ):
		#############################
		# 排他解除されるまでLockを監視する
		while True:
			#############################
			# sleep
			CLS_OSIF.sSleep( gVal.DEF_LOCK_LOOPTIME )
			
			#############################
			# 排他を確認する
			#   排他が解除されていたらwaitを終わる
			wLockStat = CLS_BotCtrl.__openLock( inPath )
			if wLockStat == "0" :
				return
		
		return



#####################################################
# 1時間監視
#####################################################
	@classmethod
	def sChk1HourTime( cls, inPath ):
		#############################
		# 記録ファイルをロード
		w1HourTime = []
		wFilePath = inPath + gVal.STR_File['Chk1HourFile']
		if CLS_File.sReadFile( wFilePath, w1HourTime )!=True :
			return False	#処理失敗
		
		try:
			w1HourTime = w1HourTime[0].split(',')
			wHour      = w1HourTime[1]
		except:
			return False	#処理失敗
		
		#############################
		# PC時間を取得
		wGetTime = CLS_OSIF.sGetTime()
		if wGetTime['Result']!=True :
			return False	#処理失敗
		
		gVal.STR_TimeInfo['Object']   = wGetTime['Object']
		gVal.STR_TimeInfo['TimeDate'] = wGetTime['TimeDate']
		gVal.STR_TimeInfo['Hour']     = wGetTime['Hour']
		gVal.STR_TimeInfo['Week']     = wGetTime['Week']
		gVal.STR_TimeInfo['Result']   = True	#有効
		
		#############################
		# 時間が同じ＝少なくとも1時間経ってないか？
		if wHour == wGetTime['Hour'] :
			gVal.STR_TimeInfo['OneHour'] = False
			return True
		else :
			gVal.STR_TimeInfo['OneHour'] = True
		
		#############################
		# 時間をセーブ
		wTime = wGetTime['TimeDate'].split(" ")
		wTime = wTime[0] + ',' + wGetTime['Hour'] + ',' + wGetTime['Week']
		
		wSaveTime = []
		wSaveTime.append(wTime)
		if CLS_File.sWriteFile( wFilePath, wSaveTime )!=True :
			return False	#処理失敗
		
		return True



