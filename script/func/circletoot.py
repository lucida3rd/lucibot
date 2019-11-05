#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：周期トゥート処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/10/18
#####################################################
# Private Function:
#   __run(self):
#   __sendToot( self, inKind, inFileName ):
#
# Instance Function:
#   __init__( self, parentObj=None ):	※親クラス実体を設定すること
#   CheckData(self):
#   Get_CLData(self):
#   Set_CLData(self):
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
from userdata import CLS_UserData
from filectrl import CLS_File
from gval import gVal
#####################################################
class CLS_CircleToot():
#####################################################
	CHR_LogName  = "周期Toot処理"
	Obj_Parent   = ""		#親クラス実体

	ARR_CLData   = {}		#周期データ

	STR_Cope = {			#処理カウンタ
		"Now_Cope"  : 0,		#処理したスケジュール数
		
		"Sended"	: 0,		#送信済み数
		"Invalid"	: 0,		#無効数
		
		"dummy"     : 0	#(未使用)
	}

	DEF_TITLE_PRTOOT = "[PR Toot]"

#####################################################
# Init
#####################################################
	def __init__( self, parentObj=None ):
		if parentObj==None :
			###親クラス実体の未設定
			CLS_OSIF.sPrn( "CLS_CircleToot: __init__: You have not set the parent class entity for parentObj" )
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
##		if gVal.FLG_Test_Mode==False :
##			self.Obj_Parent.OBJ_Mylog.Log( 'b', self.CHR_LogName + " 開始" )
##		else:
##			self.Obj_Parent.OBJ_Mylog.Log( 'b', self.CHR_LogName + " 開始", True )
		self.Obj_Parent.OBJ_Mylog.Log( 'b', self.CHR_LogName + " 開始" )
		
		#############################
		# 周期Data取得
		wRes = self.Get_CLData()
		if wRes!=True :
			return
		
		#############################
		# データチェック＆トゥート
		wRes = self.CheckData()
		if wRes!=True :
			return
		
		#############################
		# 周期Data保存
		wRes = self.Set_CLData()
		if wRes!=True :
			return
		
		#############################
		# 処理結果ログ
		wSTR_Word = self.Obj_Parent.OBJ_WordCorr.GetWordCorrectStat()	#収集状況の取得
		
		wStr = self.CHR_LogName + " 結果: 処理数=" + str(self.STR_Cope['Now_Cope'])
		wStr = wStr + " Sended=" + str(self.STR_Cope['Sended'])
		wStr = wStr + " Invalid=" + str(self.STR_Cope['Invalid'])
		
##		if gVal.FLG_Test_Mode==False :
##			self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr )
##		else:
##			self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr, True )
		self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr )
		
		return



#####################################################
# データチェック
#####################################################
	def CheckData(self):
##		#############################
##		# 現在時刻を取得する
##		wTime = CLS_OSIF.sGetTime()
##		if wTime['Result']!=True :
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_CircleToot: CheckData: sGetTime failed" )
##			return False
		
		#############################
		# 現時分
##		wHour   = str( wTime['Object'].strftime("%H") )
##		wMinute = str( wTime['Object'].strftime("%M") )
		wHour   = str( gVal.STR_TimeInfo['Object'].strftime("%H") )
		wMinute = str( gVal.STR_TimeInfo['Object'].strftime("%M") )
		
		#############################
		# データチェック
		wKeylist = list(self.ARR_CLData.keys())
		for wKey in wKeylist :
			self.STR_Cope['Now_Cope'] += 1
			
			#############################
			# 有効か
			if self.ARR_CLData[wKey]["Valid"]!=True :
				self.STR_Cope['Invalid'] += 1
				continue
			
			#############################
			# 種別チェック
			if self.ARR_CLData[wKey]["Kind"]!="t" and self.ARR_CLData[wKey]["Kind"]!="w" :
				self.STR_Cope['Invalid'] += 1
				continue
			
			#############################
			# 曜日チェック
			if self.ARR_CLData[wKey]["Week"]!="" :
				wWeeks = self.ARR_CLData[wKey]["Week"].split(",")
				if gVal.STR_TimeInfo['Week'] not in wWeeks :
					self.STR_Cope['Invalid'] += 1
					continue
			
			#############################
			# 時間チェック：0～23時
			if self.ARR_CLData[wKey]["Sended"]!="*" :
				if self.ARR_CLData[wKey]["Hour"]!=wHour :
					# 実行済み＝戻す
					self.ARR_CLData[wKey]["Sended"] = "-"
					continue
			
			#############################
			# 分チェック or 定時チェック
			if self.ARR_CLData[wKey]["Minute"]!=wMinute :
				# 実行済み＝戻す
				self.ARR_CLData[wKey]["Sended"] = "-"
				continue
			else :
				#############################
				# 同一分で実行済みは実行しない
				if self.ARR_CLData[wKey]["Sended"]=="*" :
					continue
			
			#############################
			# 送信
			wRes = self.__sendToot( self.ARR_CLData[wKey]["Kind"], self.ARR_CLData[wKey]["TootFile"] )
			if wRes['Result']!=True :
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __copeFavo: Mastodon error: " + wRes['Reason'] )
				self.STR_Cope['Invalid'] += 1
				continue
			
			self.ARR_CLData[wKey]["Sended"] = "*"
			self.STR_Cope['Sended'] += 1
		
		return True

	#####################################################
	def __sendToot( self, inKind, inFileName ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# ファイル読み出し
		wToot = []
		
		wFile_path = gVal.DEF_STR_FILE['Toot_path'] + inFileName
		if CLS_File.sReadFile( wFile_path, outLine=wToot )!=True :
			wRes['Reason'] = "CLS_CircleToot: __sendToot: Toot file read failed: " + wFile_path
			return wRes		#失敗
		
		if len(wToot)<=1 :
			wRes['Reason'] = "CLS_CircleToot: __sendToot: Toot is sortest: " + wFile_path
			return wRes		#失敗
		
		#############################
		# 範囲の設定
		wRange = CLS_UserData.sGetRange( wToot[0] )
		del wToot[0]
		
		#############################
		# 種別=CWトゥート
		if inKind=="w" :
			wTitle = self.DEF_TITLE_PRTOOT + " " + wToot[0]
			del wToot[0]
			wSetToot = ""
		else :
			wSetToot = self.DEF_TITLE_PRTOOT + " "
		
		#############################
		# トゥートの組み立て
		for wLine in wToot :
			wSetToot = wSetToot + wLine + '\n'
		
##		wSetToot = wSetToot + " " + gVal.STR_MasterConfig['prTag']
##		
##		# 管理者がいれば通知する
##		if gVal.STR_MasterConfig['AdminUser']!="" and gVal.STR_MasterConfig['AdminUser']!=self.Obj_Parent.CHR_Account:
##			wSetToot = wSetToot + '\n' + '\n' + "[Admin] @" + gVal.STR_MasterConfig['AdminUser']
##		
		wSetToot = wSetToot + '\n' + "#" + gVal.STR_MasterConfig['prTag']
		
		if len(wSetToot)>500 :
			wRes['Reason'] = "CLS_CircleToot: __sendToot: Create toot is over length"
			return wRes		#失敗
		
		#############################
		# トゥートの送信
		if inKind=="w" :
			wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wSetToot, visibility=wRange, spoiler_text=wTitle )
		else :
			wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wSetToot, visibility=wRange )
		
		if wRes['Result']!=True :
			wRes['Reason'] = "CLS_LookRIP: __copeFavo: Mastodon error: " + wRes['Reason']
			return wRes
		
		wRes['Result'] = True
		return wRes



#####################################################
# 周期Data取得・保存
#####################################################
	def Get_CLData(self):
		#############################
		# 読み出し先初期化
		self.ARR_CLData = {}
		wCLTootList = []	#トゥートパターン
		wCLDataList = []	#データ
		wWeekly = [ "1", "2", "3", "4", "5", "6", "0" ]
		
		#############################
		# ファイル読み込み
		wFile_path = gVal.DEF_STR_FILE['CLTootFile']
		if CLS_File.sReadFile( wFile_path, outLine=wCLTootList )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_CircleToot: Get_CLData: CLTootFile read failed: " + wFile_path )
			return False	#失敗
		
##		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['CLDataFile']
		wFile_path = gVal.DEF_STR_FILE['MasterConfig_path'] + gVal.DEF_STR_FILE['CLDataFile']
		if CLS_File.sReadFile( wFile_path, outLine=wCLDataList )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_CircleToot: Get_CLData: CLDataFile read failed: " + wFile_path )
			return False	#失敗
		
		#############################
		# データ枠の作成
		for wLine in wCLTootList :
			wLine = wLine.split( gVal.DEF_DATA_BOUNDARY )
##			if len(wLine)!=3 :
			if len(wLine)!=4 :
				continue	#フォーマットになってない
			if wLine[0].find("#")==0 :
				continue	#コメントアウト
			
##			wIndex = wLine[1] + ":" + wLine[2]
			wIndex = wLine[1] + ":" + wLine[3]
			wKeylist = list( self.ARR_CLData.keys() )
			if wIndex in wKeylist :
				continue	#キー被り
			
			wLine[1] = wLine[1].split(":")
			if len(wLine[1])!=2 :
				continue	#フォーマットになってない
			
			self.ARR_CLData.update({ wIndex : "" })
			self.ARR_CLData[wIndex] = {}
			self.ARR_CLData[wIndex].update({ "Valid"  : True })
			self.ARR_CLData[wIndex].update({ "Kind"   : wLine[0] })
			self.ARR_CLData[wIndex].update({ "Sended" : "-" })
			self.ARR_CLData[wIndex].update({ "Hour"   : wLine[1][0] })
			self.ARR_CLData[wIndex].update({ "Minute" : wLine[1][1] })
##			self.ARR_CLData[wIndex].update({ "TootFile" : wLine[2]  })
			self.ARR_CLData[wIndex].update({ "Week"   : "" })
			self.ARR_CLData[wIndex].update({ "TootFile" : wLine[3]  })
			
			#############################
			# 曜日の妥当性
			wWeeks = wLine[2].split(",")
			wSetWeeks = []
			for wWk in wWeeks :
				if wWk in wWeekly :
					wSetWeeks.append( wWk )
			
			if len(wSetWeeks)>0 :
				self.ARR_CLData[wIndex]["Week"] = ','.join( wSetWeeks )
		
		#############################
		# データの反映
		wKeylist = list( self.ARR_CLData.keys() )
		for wKey in wKeylist :
			for wLine in wCLDataList :
				wLine = wLine.split(",")
				if len(wLine)!=5 :
					continue	#フォーマットになってない
				
				wIndex = wLine[1] + ":" + wLine[2] + ":" + wLine[3]
				if wIndex not in wKeylist :
					continue	#キーなし
				
				self.ARR_CLData[wIndex]["Kind"]   = wLine[0]
				self.ARR_CLData[wIndex]["Sended"] = wLine[1]
				self.ARR_CLData[wIndex]["Hour"]   = wLine[2]
				self.ARR_CLData[wIndex]["Minute"] = wLine[3]
##				self.ARR_CLData[wIndex]["TootFile"] = wLine[4]
				self.ARR_CLData[wIndex]["Week"]   = wLine[4]
				self.ARR_CLData[wIndex]["TootFile"] = wLine[5]
				self.ARR_CLData[wIndex]["Valid"]  = True
		
		return True			#成功

	#####################################################
	def Set_CLData(self):
		#############################
		# 書き込みデータの作成
		wCLDataList = []
		
		wKeylist = list( self.ARR_CLData.keys() )
		for wKey in wKeylist :
			if self.ARR_CLData[wKey]["Valid"]==False :
				continue	#無効データ
			
			wSetLine = self.ARR_CLData[wKey]["Kind"] + ","
			wSetLine = self.ARR_CLData[wKey]["Sended"] + ","
			wSetLine = wSetLine + str(self.ARR_CLData[wKey]["Hour"]) + ","
			wSetLine = wSetLine + str(self.ARR_CLData[wKey]["Minute"]) + ","
			wSetLine = wSetLine + self.ARR_CLData[wKey]["Week"] + ","
			wSetLine = wSetLine + self.ARR_CLData[wKey]["TootFile"]
			wCLDataList.append( wSetLine )
		
		#############################
		# ファイル書き込み (改行つき)
##		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['CLDataFile']
		wFile_path = gVal.DEF_STR_FILE['MasterConfig_path'] + gVal.DEF_STR_FILE['CLDataFile']
		if CLS_File.sWriteFile( wFile_path, wCLDataList, inRT=True )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_CircleToot: Set_CLData: CLDataFile read failed: " + wFile_path )
			return False	#失敗
		
		return True			#成功



