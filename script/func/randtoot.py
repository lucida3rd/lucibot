#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ランダムトゥート
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/9/14
#####################################################
# Private Function:
#   __selectMeCabDic(self):
#   __analizeMeCab( self, inWords ):
#
# Instance Function:
#   __init__( self, inPath ):
#   GetWordCorrectStat(self):
#   GetWordREM(self) :
#   WordStudy( self, inCont ):
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
##from filectrl import CLS_File
##from userdata import CLS_UserData
from gval import gVal
#####################################################
class CLS_RandToot():
#####################################################
	CHR_LogName = "ランダムトゥート"
	Obj_Parent  = ""		#親クラス実体

##	STR_Cope = {			#処理カウンタ
##		"Now_Cope"  : 0,		#処理した新トゥート数
##		
##		"Now_Favo"  : 0,		#今ニコった数
##		"Now_Boot"  : 0,		#今ブーストした数
##		"Now_ARip"  : 0,		#今エアリプした数
##		"Now_Word"  : 0,		#今ワード監視した数
##		"UserCorr"	: 0,		#ユーザ収集
##		"dummy"     : 0	#(未使用)
##	}

#	DEF_TOOTRANGE = "public"
#	DEF_TOOTRANGE = "unlisted"

#####################################################
# Init
#####################################################
	def __init__( self, parentObj=None ):
		if parentObj==None :
			###親クラス実体の未設定
			CLS_OSIF.sPrn( "CLS_RandToot: __init__: You have not set the parent class entity for parentObj" )
			return
		
		self.Obj_Parent = parentObj
		self.__run()	#処理開始
		return



#####################################################
# 処理実行
#####################################################
	def __run(self):
		#############################
		# 開始ログ
		self.Obj_Parent.OBJ_Mylog.Log( 'b', self.CHR_LogName + " 開始" )
		
		wTootStat = "off"
		#############################
		# トゥート頻度(乱数発生)
		wVAL_Rand = CLS_OSIF.sGetRand( gVal.DEF_STR_TLNUM['getRandRange'] )
		wVAL_Pub  = CLS_OSIF.sGetRand( gVal.DEF_STR_TLNUM['getRandPublic'] )
		
##		if wVAL_Rand < gVal.DEF_STR_TLNUM['getRandVal'] :
		if wVAL_Rand < gVal.DEF_STR_TLNUM['getRandVal'] or gVal.FLG_Test_Mode==True :
		#############################
		# ランダムトゥートを実行する
			### public頻度
			if wVAL_Pub==1 :
				wCHR_Range = "public"
			else :
				wCHR_Range = "unlisted"
			
			wCHR_Toot = self.Obj_Parent.OBJ_WordCorr.GetRandToot()
			if wCHR_Toot=="" :
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_RandToot: __run: GetRandToot is failed" )
				return
			
##			wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, visibility="public" )
##			wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, visibility=self.DEF_TOOTRANGE )
			wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, visibility=wCHR_Range )
			if wRes['Result']!=True :
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_RandToot: __run: Mastodon error: " + wRes['Reason'] )
				return
			
			wTootStat = "on"
		
		#############################
		# 処理結果ログ
		wStr = self.CHR_LogName + " 結果: Toot=" + wTootStat + " "
		wStr = wStr + "Rand=" + str( wVAL_Rand ) + " "

		if gVal.FLG_Test_Mode==False :
			self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr )
		else:
			self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr, inView=True )
		
		return



