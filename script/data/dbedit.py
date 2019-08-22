#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：データベース編集
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/8/23
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   __init__(self):
#   MasterSetup(self):
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
##from filectrl import CLS_File
##from userdata import CLS_UserData
from postgresql_use import CLS_PostgreSQL_Use

from gval import gVal
#####################################################
class CLS_DBedit():
#####################################################

#####################################################
# 初期化
#####################################################
	def __init__(self):
		return



#####################################################
# コンソール表示
#####################################################
	def View(self):
		#############################
		# コンソール
		while True :
			#############################
			# コマンド画面表示
			wCommand = self.__View_Disp()
			
			#############################
			# 継続
			if wCommand=="" :
				continue
			
			#############################
			# 終了
			elif wCommand.find("\\q")>=0 :
				break
			
			#############################
			# テーブル一覧
			elif wCommand.find("\\l")>=0 :
				self.__viewTblList()
			





		
		return

	#############################
	# 画面
	def __View_Disp(self):
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ出力
		wStr = "-----------------------" + '\n'
		wStr = wStr + " データベース エディタ" + '\n'
		wStr = wStr + "-----------------------" + '\n'
##		wStr = wStr + "DB Name: " + self.STR_DBdata['database'] + '\n'
		wStr = wStr + "コマンド= [\\q] 終了 / [\\l] 一覧"
		CLS_OSIF.sPrn( wStr )
		wCommand = CLS_OSIF.sInp( "コマンド？=> " ).strip()
		return wCommand



#####################################################
# テーブル一覧
#####################################################
	def __viewTblList(self):
		#############################
		# 一覧の取得
##		wQuery = "select tablename from pg_tables where tablename not like 'pg_%' and schemaname like 'public';"
##		wQuery = "select t2.relname , t2.reltuples from pg_stat_user_tables as t1 inner join pg_class as t2 on t1.relname = t2.relname order by t2.relname;"
		wQuery = "select relname, n_live_tup from pg_stat_user_tables where schemaname='public';"
		
		wRes = self.__oneRunQuery( wQuery )
		if wRes['Result']!=True :
			##失敗
			CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
			return
		
		if len(wRes['Responce']['Data'])==0 :
			##滅多にありえない
			CLS_OSIF.sInp( "データベースが初期化されていません。[RT]" )
			return
		
		#############################
		# ヘッダ出力
		wStr = "-----------------------" + '\n'
		wStr = wStr + "レコード数   テーブル名" + '\n'
		wStr = wStr + "-----------------------"
		CLS_OSIF.sPrn( wStr )
###		print( str(wRes['Responce']['Data']) )
		
		##データの表示
		for wLineTap in wRes['Responce']['Data'] :
			wGetTap = []
			for wCel in wLineTap :
				wCel = str(wCel)
				wCel = wCel.strip()
				wGetTap.append( wCel )
				## [0]..テーブル名
				## [1]..レコード数
			wStr = wGetTap[1] + ( " " * ( 13 - len(wGetTap[1]) )) + wGetTap[0]
			CLS_OSIF.sPrn( wStr )
		
		#############################
		CLS_OSIF.sInp( '\n' + "リターンキーを押すと戻ります。[RT]" )
		return



#####################################################
# 1クエリ実行
#####################################################
	def __oneRunQuery( self, inQuery ):
		#############################
		# DB接続
		wOBJ_DB = CLS_PostgreSQL_Use( gVal.STR_File['DBinfo_File'] )
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			##失敗
			wStr = "CLS_DBedit: __oneRunQuery: DB Connect test is failed: " + wRes['Reason']
			CLS_OSIF.sPrn( wStr )
			wOBJ_DB.Close()
			return wRes
		
		#############################
		# クエリ実行
		wRes = wOBJ_DB.RunQuery( inQuery )
		##	"Result"	: False
		##	"Reason"	: None
		##	"Responce"	: None
		
		#############################
		# DB切断
		wOBJ_DB.Close()
		
		wRes = wOBJ_DB.GetQueryStat()
		return wRes



