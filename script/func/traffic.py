#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：トラヒック処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/13
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   __init__( self, inPath ):
#   Countup(self):
#   CountReset(self):
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
from filectrl import CLS_File
from gval import gVal
#####################################################
class CLS_Traffic():
#####################################################
	Obj_Parent = ""		#親クラス実体

###	CHR_DataPath = ""


#####################################################
# Init
#####################################################
##	def __init__( self, inPath ):
##		self.CHR_DataPath = inPath
	def __init__( self, parentObj=None ):
		if parentObj==None :
			###親クラス実体の未設定
			CLS_OSIF.sPrn( "CLS_Traffic: __init__: You have not set the parent class entity for parentObj" )
			return
		
		self.Obj_Parent = parentObj
		return



#####################################################
# カウントアップ(Master/Sub用)
#####################################################
	def Countup(self):
		#############################
		# 読み出し先初期化
		wCount = []
		
		#############################
		# ファイル読み込み
###		wFile_path = self.CHR_DataPath + gVal.STR_File['TrafficFile']
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.STR_File['TrafficFile']
		if CLS_File.sReadFile( wFile_path, outLine=wCount )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Countup: Traffic count file read failed: " + wFile_path )
			return False	#失敗
		
		#############################
		# データチェック
		#   空の時、リセット
		if len(wCount)==0 :
			wCount.append( "0,0" )
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Countup: Traffic counter value null(Crash?). Counter Reset." )
		
		#############################
		# データ整形
		try:
			wCount = wCount[0].split(",")
			wCount[0] = int( wCount[0] )	# 現カウント
			wCount[1] = int( wCount[1] )	# 1時間前のカウント
		except ValueError as err :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Countup: Traffic count exception: " + str(err) )
			return False	#失敗
		
		#############################
		# 1時間経ってる周回か
		if gVal.STR_TimeInfo['OneHour']==True :
			wCount[1] = wCount[0]
			wCount[0] = 1
		#############################
		# カウントアップ
		else:
			wCount[0] += 1
		
		#############################
		# 書き込み用データ整形
		wLine = str( wCount[0] ) + "," + str( wCount[1] )
		
		#############################
		# ファイル書き込み
		wSetLine = []
		wSetLine.append( wLine )
		if CLS_File.sWriteFile( wFile_path, wSetLine )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Countup: Traffic count file write failed: " + wFile_path )
			return False	#失敗
		
		return True			#成功



#####################################################
# カウントリセット(Master/Sub用)
#####################################################
	def CountReset(self):
		#############################
		# パス設定
##		wFile_path = self.CHR_DataPath + gVal.STR_File['TrafficFile']
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.STR_File['TrafficFile']
		
		#############################
		# 書き込み用データ整形
		wLine = "0,0"
		
		#############################
		# ファイル書き込み
		wSetLine = []
		wSetLine.append( wLine )
		if CLS_File.sWriteFile( wFile_path, wSetLine )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: CountReset: Traffic count file write failed: " + wFile_path )
			return False	#失敗
		
		self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: CountReset: トラヒックカウント リセット済" )
		return True			#成功



