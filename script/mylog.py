#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ログ処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/9
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
###import string

from osif import CLS_OSIF
from filectrl import CLS_File
from gval import gVal
#####################################################
class CLS_Mylog():
#####################################################

	CHR_LogPath = ""

#####################################################
# 初期化
#####################################################
	def __init__( self, inPath ):
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
		#############################
		# パスが無設定 or 時計異常？
		if self.CHR_LogPath=="" or wDate[0]=="" :
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
		wLogFile = self.CHR_LogPath + wDate[0] + ".log"
		self.__write( wLogFile, wDate, inMsg )
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
		if len(wMsgLine)>1 :
			del wMsgLine[0]
		
		#############################
		# 1行目
		wLine = wTimeDate + ' ' + wMsg1 + '\n'
		wSetLine.append( wLine )
		
		#############################
		# 2行目以降
		if len(wMsgLine)>0 :
			for wLine in wMsgLine :
				wIncLine = wBlank + ' ' + wLine + '\n'
				wSetLine.append( wIncLine )
		
		#############################
		# ファイル追加書き込み
		if CLS_File.sAddFile( inLogFile, wSetLine )!=True :
			return False	#失敗
		
		return True



