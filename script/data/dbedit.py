#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：データベース編集
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/8/26
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
from filectrl import CLS_File
##from userdata import CLS_UserData
from postgresql_use import CLS_PostgreSQL_Use

from gval import gVal
#####################################################
class CLS_DBedit():
#####################################################

	ARR_Domains = []	#ドメイン一覧

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
			
			#############################
			# ***隠し***  ドメイン情報 取得
			elif wCommand.find("\\ml")>=0 :
				self.__getMstdnDomains()
			
			#############################
			# ***隠し***  新ドメインチェック
			elif wCommand.find("\\mc")>=0 :
				self.__checkMstdnNewDomains()
			
			#############################
			# ***隠し***  ドメインブロック コメントサーチ
			elif wCommand.find("\\mb")>=0 :
				self.__searchMstdnDomainBlock()
		
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



#####################################################
# 隠し機能用
#####################################################
	#############################
	# ドメイン情報 取得
	def __getMstdnDomains(self):
		#############################
		# mastodonからドメイン情報を取得
		wQuery = "select distinct domain from accounts;"
		
		wRes = self.__oneRunQueryMstdn( wQuery )
		if wRes['Result']!=True :
			##失敗
			CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
			return
		
		#############################
		# ファイルに取得
		self.ARR_Domains = []
		for wLineTap in wRes['Responce']['Data'] :
			for wCel in wLineTap :
				wCel = str(wCel)
				wCel = wCel.strip()
				self.ARR_Domains.append( wCel )
		self.__setDomainsFile()
		
		#############################
		# 件数表示
		wStr = str(len( self.ARR_Domains )) + " 件取得しました" + '\n'
		CLS_OSIF.sPrn( wStr )
		CLS_OSIF.sInp( '\n' + "リターンキーを押すと戻ります。[RT]" )
		return

	#############################
	# 新ドメインチェック
	def __checkMstdnNewDomains(self):
		#############################
		# ドメイン情報 読み込み
		self.__getDomainsFile()
		if len( self.ARR_Domains )==0 :
			##失敗
			CLS_OSIF.sInp( "まず mlでドメインを取得してください。[RT]" )
			return
		
		#############################
		# mastodonからドメイン情報を取得
		wQuery = "select distinct domain from accounts;"
		
		wRes = self.__oneRunQueryMstdn( wQuery )
		if wRes['Result']!=True :
			##失敗
			CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
			return
		
		#############################
		# 新ドメインだけ抜きとる
		wNewDomains = []
		for wLineTap in wRes['Responce']['Data'] :
			for wCel in wLineTap :
				wCel = str(wCel)
				wCel = wCel.strip()
			if wCel not in self.ARR_Domains :
				wNewDomains.append( wCel )
		
		#############################
		# 新ドメインの表示
		if len(wNewDomains)>0 :
			wStr = "-----------------------" + '\n'
			wStr = wStr + "新しく検知したドメイン" + '\n'
			wStr = wStr + "-----------------------" + '\n'
			for wLine in wNewDomains :
				wStr = wStr + wLine + '\n'
			CLS_OSIF.sPrn( wStr )
		else :
			wStr = "新しく検知したドメインはありません。" + '\n'
			CLS_OSIF.sPrn( wStr )
		
		CLS_OSIF.sInp( '\n' + "リターンキーを押すと戻ります。[RT]" )
		return

	#############################
	# ドメインブロック コメントサーチ
	def __searchMstdnDomainBlock(self):
		#############################
		# ドメイン情報 読み込み
		self.__getDomainsFile()
		if len( self.ARR_Domains )==0 :
			##失敗
			CLS_OSIF.sInp( "まず mlでドメインを取得してください。[RT]" )
			return
		
		#############################
		# サーチするコメントを指定
		wStr = "ドメインブロックサーチするコメント(公開)を入力してください" + '\n'
		CLS_OSIF.sPrn( wStr )
		wInput = CLS_OSIF.sInp( "コメント？=> " )
		if wInput=="" :
			return
		
		#############################
		# mastodonからドメインブロックを取得
##		wQuery = "select domain from domain_blocks where public_comment = '\%" + str(wInput) + "\%';"
##		wQuery = "select domain from domain_blocks where public_comment like '%" + str(wInput) + "%';"
		wQuery = "select domain from domain_blocks where public_comment like '%" + str(wInput) + "%' order by domain;"

		CLS_OSIF.sPrn( wQuery )

		
		wRes = self.__oneRunQueryMstdn( wQuery )
		if wRes['Result']!=True :
			##失敗
			CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
			return
		
		##対象なし
		if len(wRes['Responce']['Data'])==0 :
			wStr = "対象ドメインはありません。" + '\n'
			CLS_OSIF.sPrn( wStr )
			CLS_OSIF.sInp( '\n' + "リターンキーを押すと戻ります。[RT]" )
			return
		
		#############################
		# ドメインの表示
		wStr = "-----------------------" + '\n'
		wStr = wStr + "検知したドメイン" + '\n'
		wStr = wStr + "-----------------------" + '\n'
		for wLineTap in wRes['Responce']['Data'] :
			for wCel in wLineTap :
				wCel = str(wCel)
				wCel = wCel.strip()
			wStr = wStr + wCel + '\n'
		
		CLS_OSIF.sPrn( wStr )
		CLS_OSIF.sInp( '\n' + "リターンキーを押すと戻ります。[RT]" )
		return


#####################################################
	#####################################################
	# ドメイン情報 読み込み
	def __getDomainsFile(self):
		#############################
		# 読み出し先初期化
		self.ARR_Domains = []
		
		#############################
		# ファイル読み込み
		wFile_path = gVal.STR_File['MstdnDomains_File']
		if CLS_File.sReadFile( wFile_path, outLine=self.ARR_Domains )!=True :
			wStr = "CLS_DBedit: __getDomainsFile: MstdnDomains_File read is failed: " + gVal.STR_File['MstdnDomains_File']
			CLS_OSIF.sPrn( wStr )
			return False	#失敗
		
		return True			#成功

	#####################################################
	# ドメイン情報 書き込み
	def __setDomainsFile(self):
		#############################
		# ファイル書き込み (改行つき)
		wFile_path = gVal.STR_File['MstdnDomains_File']
		if CLS_File.sWriteFile( wFile_path, self.ARR_Domains, inRT=True )!=True :
			wStr = "CLS_DBedit: __setDomainsFile: MstdnDomains_File write is failed: " + gVal.STR_File['MstdnDomains_File']
			CLS_OSIF.sPrn( wStr )
			return False	#失敗
		
		return True			#成功

	#####################################################
	# 1クエリ実行 (mastodon)
	def __oneRunQueryMstdn( self, inQuery ):
		#############################
		# DB接続
		wOBJ_DB = CLS_PostgreSQL_Use( gVal.STR_File['MstdnInfo_File'] )
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			##失敗
			wStr = "CLS_DBedit: __oneRunQueryMstdn: DB Connect test is failed: " + wRes['Reason']
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



