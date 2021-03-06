#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ログ処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/9/17
#####################################################
# Private Function:
#   __write( self, inLogFile, inDate, inMsg ):
#
# Instance Function:
#   __init__( self, inPath ):
#   Log( cls, inLevel, inMsg, inView=False ):
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
from filectrl import CLS_File
from gval import gVal
#####################################################
class CLS_Mylog():
#####################################################

	CHR_LogPath  = ""

#####################################################
# 初期化
#####################################################
##	def __init__( self, inPath ):
	def __init__( self, inPath=None ):
		#############################
		# ログフォルダの存在チェック
		if CLS_File.sExist( inPath )!=True :
			self.CHR_LogPath = ""
			return 		#ない
		
		self.CHR_LogPath = inPath
		return



#####################################################
# ログデータのセット
#####################################################
	def Log( self, inLevel, inMsg, inView=False ):
		#############################
		# チェック
		if self.CHR_LogPath==None :
			### パスが無設定
			CLS_OSIF.sPrn( inMsg )
			return
		
		#############################
		# ログレベル：LogLevel
		#  a：全てのログを記録　　　　　　　（LevelA,B,C）
		#  b：重要なログと気になるログを記録（LevelA,Bのみ、LevelCは記録しない）
		#  c：重要なログだけ記録　　　　　　（LevelAログのみ、LevelB,Cは記録しない）
		
		#############################
		# 設定されたログレベルが適当でなければ
		# 'a'を設定しなおす
		if inLevel != 'a' and inLevel != 'b' and inLevel != 'c' :
			wLevel = 'a'
		else :
			wLevel = inLevel
		
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
		
##		#############################
##		# パスが無設定 or 時計異常？
##		if self.CHR_LogPath=="" or wDate[0]=="" :
##			###時間取得失敗  時計壊れた？
##			CLS_OSIF.sPrn( inMsg )
##			return
		
		#############################
		# ファイルへ書き出す
		wLogFile = self.CHR_LogPath + wDate[0] + ".log"
		wOutLog = self.__write( wLogFile, wDate, inMsg )
		
		#############################
		# コンソールに表示する
		# = システムログに出る
		if inView==True :
			CLS_OSIF.sPrn( wOutLog )
		
		return



#####################################################
# Masterログデータのセット
#####################################################
	def MasterLog( self, inAccount, inMsg, inView=False, inHard=False ):
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			CLS_OSIF.sPrn( inMsg )
			return
		wDate = wTD['TimeDate'].split(" ")
		
		#############################
		# ファイルパスを作成する
		wDate = self.CHR_TimeDate.split(" ")
		wDate = wDate.split("-")
		
		if inHard==False :
			### Masterログ
			wLogFile = gVal.DEF_STR_FILE['MasterLog_path'] + wDate[0] + wDate[1] + "_" + inAccount + ".log"
		else :
			### ハードログ
			wLogFile = gVal.DEF_STR_FILE['MasterLog_path'] + wDate[0] + wDate[1] + "_hard" + ".log"
		
		#############################
		# ファイルへ書き出す
		wOutLog = self.__write( wLogFile, wDate, inMsg )
		
		#############################
		# コンソールに表示する
		# = システムログに出る
		if inView==True :
			CLS_OSIF.sPrn( wOutLog )
		
		return



#####################################################
# ファイルへの書き出し
#####################################################
	def __write( self, inLogFile, inDate, inMsg ):
		#############################
		# データを作成
		wTimeDate = inDate[0] + " " + inDate[1]
		
		wSetLine = []
			# 2行目以降のブランク文字列
		wBlank   = " " * len(wTimeDate)
			# 2行目以降の文字列リスト作成
		wMsgLine = inMsg.split('\n')
		wMsg1 = wMsgLine[0]
		del wMsgLine[0]
		
		wOutLine = ""
		#############################
		# 1行目
		wLine = wTimeDate + ' ' + wMsg1 + '\n'
		wSetLine.append( wLine )
		wOutLine = wLine
		
		#############################
		# 2行目以降
		if len(wMsgLine)>0 :
			for wLine in wMsgLine :
				wIncLine = wBlank + ' ' + wLine + '\n'
				wSetLine.append( wIncLine )
				wOutLine = wOutLine + wIncLine
		
		#############################
		# ファイル追加書き込み
		CLS_File.sAddFile( inLogFile, wSetLine, inExist=False )
		
		wOutLine = wOutLine.strip()
		return wOutLine

