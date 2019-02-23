# coding: UTF-8
#####################################################
# 十八試るしぼっと
#   Class   ：周期トゥート処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2018/11/27
#####################################################
from datetime import datetime
from datetime import timedelta
import codecs
import os
import random
import linecache
import re
import global_val
#####################################################
class CLS_CircleToot:

	ARR_CTTL = []	#CTTLデータ
	FLG_Init = False
	
	Time_CTTL_File = ""
	
	CopeCTTL = {
		"Now_Toot"  : 0,							#
		"dummy"     : 0								#(未使用)
	}



#####################################################
# Init
#####################################################
	def __init__(self):
		return



#####################################################
# メイン処理
#####################################################
	def cMain(self):
		global_val.gCLS_Mylog.cLog('c', "周期トゥート処理")
		
		#############################
		#CTTLデータ読み込み
		self.cGet_CTTL()
		
		#############################
		#CTTLデータ ロード正常か
		if self.FLG_Init!=True :
			return False
		
		#############################
		#データチェック
		index = 0
		for data in self.ARR_CTTL:
			self.cCheckData( index )
			index += 1
		
		#############################
		#CTTLデータ書き込み
		self.pSet_CTTL_Data_File()
		
		if self.CopeCTTL["Now_Toot"] > 0 :
			msg = "Toot=" + str(self.CopeCTTL["Now_Toot"])
			global_val.gCLS_Mylog.cLog('b', "周期トゥート処理完了：" + msg )
		
		return True



#####################################################
# データチェック
#   再実行は1時間経たないと有効にならない
#####################################################
	def cCheckData( self, index ):
		
		#############################
		# 現時分
		hour   = int( global_val.gOBJ_TimeDate.strftime("%H") )
		minute = int( global_val.gOBJ_TimeDate.strftime("%M") )
		
		#############################
		# 時間チェック：0～23時
		if self.ARR_CTTL[index][2]!="*" :
			if self.ARR_CTTL[index][2]!=hour :
				#############################
				# 実行済み＝戻す
				if self.ARR_CTTL[index][0]=="*" :
					self.ARR_CTTL[index][0] = "-"
				
				return	#時間ではない
			
		
		#############################
		# 分チェック or 定時チェック
		if self.ARR_CTTL[index][3]!=minute :
			#############################
			# 実行済み＝戻す
			if self.ARR_CTTL[index][0]=="*" :
				self.ARR_CTTL[index][0] = "-"
			
			return
		else :
			#############################
			# 同一分で実行済みは実行しない
			if self.ARR_CTTL[index][0]=="*" :
				return
		
		# 実行確定
		
		#############################
		# トゥートの取得
		wToot = self.pGet_Toot(self.ARR_CTTL[index][4])
		if wToot['result']!=True :
			return
		
		#############################
		#公開範囲の設定
		range = global_val.gCLS_MainProc.cGet_Visi(wToot['rang'])
		
		#############################
		#トゥート
		global_val.gCLS_Mastodon.cToot(status=wToot['toot'], visibility=range )
		
		#############################
		#トゥート済
		self.ARR_CTTL[index][0] = "*"
		return



#####################################################
# 周期トゥートデータの読み出しor作成
#####################################################
	def cGet_CTTL(self):
		#############################
		# 周期トゥートパターンファイルの日時取得
		self.Time_CTTL_File = global_val.gCLS_MainProc.cGet_File_TimeDate( global_val.gCircleToot_file )
		if self.Time_CTTL_File=="" :
			return
		
		#############################
		# 周期トゥートデータの読み出し
		if self.pGet_CTTL_Data_File()!=True :
			return
		
		#############################
		# ロード正常
		self.FLG_Init = True
		return



#####################################################
# 周期トゥートデータ読み出し
#####################################################
	def pGet_CTTL_Data_File(self):
		if os.path.exists(global_val.gCircleTootDat_file)==False :
			global_val.gCLS_Mylog.cLog('a', "CLS_CircleToot：pGet_CTTL_Data_File：ファイルがない：" + global_val.gCircleTootDat_file )
			return False
		
		#############################
		# 周期トゥートデータ読み出し
		flg_load = False
		wCTTL = []
		for line in codecs.open( global_val.gCircleTootDat_file, 'r', 'utf-8'):	#ファイルを開く
			line = line.strip()
			lines = line.split(",")
			wCTTL.append(lines)
		
		if len(wCTTL)<=0 :
			flg_load = True	#初期状態はロード
		else :
		#############################
		# 周期トゥートファイルが更新されているか
			if self.Time_CTTL_File!=wCTTL[0][0] :
				flg_load = True	#更新ありはロード
		
		#############################
		# 周期トゥート解析パターンからロード
		if flg_load==True :
			if self.pGet_CTTL_ptt_File()!=True :
				return False
			
			return True
		
		#############################
		# データを構築
		for line in wCTTL :
			if len(line)!=5 :
				continue
			
			slines = []
			slines.append(line[0])
			slines.append(line[1])
			if line[2]!="*" :
				line[2] = int(line[2])
			slines.append(line[2])
			slines.append(int(line[3]))
			slines.append(line[4])
			self.ARR_CTTL.append(slines)
		
		return True



#####################################################
# 周期トゥートデータ書き出し
#####################################################
	def pSet_CTTL_Data_File(self):
		if os.path.exists(global_val.gCircleTootDat_file)==False :
			global_val.gCLS_Mylog.cLog('a', "CLS_CircleToot：pSet_CTTL_Data_File：ファイルがない：" + global_val.gCircleTootDat_file )
			return False
		
		#############################
		# 周期トゥートデータトファイルのオープン
		file = codecs.open( global_val.gCircleTootDat_file, 'w', 'utf-8')
		file.close()
		file = codecs.open( global_val.gCircleTootDat_file, 'w', 'utf-8')
		
		#############################
		# データを作成
		setline = []
		line = self.Time_CTTL_File + '\n'
		setline.append(line)
		
		for lines in self.ARR_CTTL :
			line = ""
			line = line + lines[0] + ','
			line = line + lines[1] + ','
			line = line + str(lines[2]) + ','
			line = line + str(lines[3]) + ','
			line = line + lines[4] + '\n'
			setline.append(line)
		
		#############################
		# 書き込んで閉じる
		file.writelines( setline )
		file.close()
		
		return True



#####################################################
# 周期トゥート解析パターン読み出しと構築
#####################################################
	def pGet_CTTL_ptt_File(self):
		if os.path.exists(global_val.gCircleToot_file)==False :
			global_val.gCLS_Mylog.cLog('a', "CLS_CircleToot：cGet_CTTL：ファイルがない：" + global_val.gCircleToot_file )
			return False
		
		self.ARR_CTTL = []
		for line in codecs.open( global_val.gCircleToot_file, 'r', 'utf-8'):	#ファイルを開く
			line = line.strip()
			lines = line.split(global_val.gCHR_Border)
			
			#############################
			# ファイルの形式を確認
			if len(lines)!=3 :
				continue
			
			if lines[0]!="t" :
				continue
			
			wtms = lines[1].split(":")
			if len(wtms)!=2 :
				continue
			
			if wtms[0]!="*" :
				wtms[0] = int(wtms[0])
				if wtms[0]<0 or wtms[0]>23 :
					continue
			
			wtms[1] = int(wtms[1])
			if wtms[1]<0 or wtms[1]>59 :
				continue
			
			#############################
			# データを構築
			slines = []
			slines.append("-")
			slines.append(lines[0])
			slines.append(wtms[0])
			slines.append(wtms[1])
			slines.append(lines[2])
			self.ARR_CTTL.append(slines)
		
		global_val.gCLS_Mylog.cLog('c', "周期トゥート再ロード" )
		return True



#####################################################
# トゥート作成
#####################################################
	def pGet_Toot(self,fname):
		wResult = {}
		wResult.update({ "result" : False })
		wResult.update({ "rang"   : "" })
		wResult.update({ "toot"   : "" })
		
		fname = global_val.gCircleToot_folder + fname
		if os.path.exists( fname )==False :
			global_val.gCLS_Mylog.cLog('a', "CLS_CircleToot：pGet_Toot：ファイルがない：" + fname )
			return wResult
		
		index = 0
		for line in codecs.open( fname, 'r', 'utf-8'):	#ファイルを開く
			if index==0 :
				wResult['rang'] = line.strip()
			else :
				wResult['toot'] += line
			index += 1
		
		wResult['result'] = True
		return wResult



