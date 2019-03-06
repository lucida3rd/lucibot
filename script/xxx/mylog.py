#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ログ処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/3
#####################################################
# Private Function:
#   __write( cls, inLogFile, inDate, inMsg ):
#
# Instance Function:
#   (none)
#
# Class Function(static):
#   sLog( cls, inLevel, inLogFile, inMsg, inView=False ):
#
#####################################################
###import string

from osif import CLS_OSIF
from filectrl import CLS_File
from gval import gVal
#####################################################
class CLS_Mylog():
#####################################################
# ログデータのセット
#####################################################
	@classmethod
	def sLog( cls, inLevel, inLogPath, inMsg, inView=False ):
		#############################
		# 設定されたログレベルが適当でなければ
		# 'a'を設定しなおす
		if inLevel != 'a' and inLevel != 'b' and inLevel != 'c' :
			wLevel = inLevel
		else :
			wLevel = 'a'
		
		#############################
		# ログレベルで出力が有効か
		if gVal.STR_MasterConfig['LogLevel'] == 'c' and ( wLevel == 'b' or wLevel == 'c' ) :
			return
		
		if gVal.STR_MasterConfig['LogLevel'] == 'b' and wLevel == 'c' :
			return
		
		###※以下ログ出力
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			CLS_OSIF.sPrn( inMsg )
			return
		
		wDate = wTD['TimeDate'].split(" ")
		#############################
		# パスが無設定 or 時計異常？
		if inLogPath=="" or wDate[0]=="" :
			###時間取得失敗  時計壊れた？
			CLS_OSIF.sPrn( inMsg )
			return
		
		#############################
		# コンソールに表示する
		# = システムログに出る
		if inView==True :
			CLS_OSIF.sPrn( wTD['TimeDate'] + ' ' + inMsg )
		
		#############################
		# ファイルへ書き出す
		wLogFile = inLogPath + wDate[0] + ".log"
		cls().__write( wLogFile, inDate, inMsg )
		return



#####################################################
# ファイルへの書き出し
#####################################################
	def __write( cls, inLogFile, inDate, inMsg ):
		#############################
		# データを作成
		wSetLine = []
			# 2行目以降のブランク文字列
		wBlank   = " " * len(inDate)
			# 2行目以降の文字列リスト作成
		wMsgLine = inMsg.split('\n')
		wMsgLine.remove(0)
		
		#############################
		# 1行目
		wLine = inDate + ' ' + inMsg + '\n'
		wSetLine.append( wLine )
		
		#############################
		# 2行目以降
		for wLine in wMsgLine :
			wIncLine = wBlank + ' ' + wLine + '\n'
			wSetLine.append( wIncLine )
		
		#############################
		# ファイル追加書き込み
		if CLS_File.sAddFile( inLogFile, wSetLine )!=True :
			return False	#失敗
		
		return True



