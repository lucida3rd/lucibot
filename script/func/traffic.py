#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：トラヒック処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/8/28
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
# トラヒック設計仕様
#・計測対象アカウントの制御は、ユーザクラスでおこなう。
#・MasterUserのドメインはデフォルトで計測対象となる。
#  その他は、toot/traffic.txtでドメインを指定する。
#・計測用のアカウントは、ユーザ登録時に
#  data/_traffic.txtに登録される。
#  既に同じドメインのものが登録されている場合はおこなわない。
#  ユーザ削除されると、同じドメインの別のアカウントを登録する。
#  ない場合はそのドメインは計測対象から外れる。
#・MasterUserのドメインで他のアカウントが登録されたときは、
#  そのアカウントが計測対象となる。
#・計測対象はLocalTLからおこなう。この際、言語は問わないこと。
#
#####################################################
from postgresql_use import CLS_PostgreSQL_Use

from osif import CLS_OSIF
from filectrl import CLS_File
from userdata import CLS_UserData
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
# ドメイン追加
#####################################################
##	def AddDomain(self) :
##		#############################
##		# ドメインの抽出
##		wDomain = self.Obj_Parent.CHR_Account.split("@")
##		if len(wDomain)!=2 :
##			##失敗
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: AddDomain: Illigal admin_id: " + self.Obj_Parent.CHR_Account )
##			return False
##		wDomain = wDomain[1]
##		
##		#############################
##		# DB接続情報ファイルのチェック
##		wFile_path = gVal.STR_File['DBinfo_File']
##		if CLS_File.sExist( wFile_path )!=True :
##			##失敗
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: AddDomain: Database file is not found: " + wFile_path + " domain=" + wDomain )
##			return False
##		
##		#############################
##		# DB接続
##		wOBJ_DB = CLS_PostgreSQL_Use( wFile_path )
##		wRes = wOBJ_DB.GetIniStatus()
##		if wRes['Result']!=True :
##			##失敗
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: AddDomain: DB Connect test is failed: " + wRes['Reason'] + " domain=" + wDomain )
##			wOBJ_DB.Close()
##			return False
##		
##		#############################
##		# ドメイン存在チェック
##		wQuery = "select * from TBL_TRAFFIC_DATA where exists (select domain from " +  \
##					wDomain + ") ;"
##		
##		wRes = wOBJ_DB.RunQuery( wQuery )
##		if wRes['Result']!=True :
##			##失敗
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: AddDomain: Run Query is failed: " + wRes['Reason'] + " domain=" + wDomain )
##			wOBJ_DB.Close()
##			return False
##		
##		if len( wRes['Responce']['Data'] )>0 :
##			##既に存在している
##			wOBJ_DB.Close()
##			return True
##		
##		#############################
##		# ドメイン追加
##		wQuery = "insert into TBL_TRAFFIC_DATA values (" + \
##					"'" + wDomain + "'," + \
##					"1," + \
##					"0," + \
##					") ;"
##		
##		self.Obj_Parent.OBJ_Mylog.Log( 'b', "TBL_TRAFFIC_DATA ドメイン追加: " + wDomain )
##		
##		wRes = wOBJ_DB.RunQuery( wQuery )
##		if wRes['Result']!=True :
##			##失敗
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: AddDomain: Add Domain is failed: " + wRes['Reason'] + " domain=" + wDomain )
##			wOBJ_DB.Close()
##			return False
##		
##		#############################
##		# DB切断
##		wOBJ_DB.Close()
##		return True



#####################################################
# ドメイン削除
#####################################################
##	def DelDomain(self) :
##		#############################
##		# ユーザ一覧の抽出
##		wList = CLS_UserData.sGetUserList()
##		if len(wList)==0 :
##			return True
##		
##		#############################
##		# DB接続情報ファイルのチェック
##		wFile_path = gVal.STR_File['DBinfo_File']
##		if CLS_File.sExist( wFile_path )!=True :
##			##失敗
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: DelDomain: Database file is not found: " + wFile_path )
##			return False
##		
##		#############################
##		# DB接続
##		wOBJ_DB = CLS_PostgreSQL_Use( wFile_path )
##		wRes = wOBJ_DB.GetIniStatus()
##		if wRes['Result']!=True :
##			##失敗
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: DelDomain: DB Connect test is failed: " + wRes['Reason'] )
##			wOBJ_DB.Close()
##			return False
##		
##		#############################
##		# ドメイン存在チェック
##		wQuery = "select * from TBL_TRAFFIC_DATA where exists (select domain from " +  \
##					wDomain + ") ;"
##		
##		wRes = wOBJ_DB.RunQuery( wQuery )
##		if wRes['Result']!=True :
##			##失敗
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: DelDomain: Run Query is failed: " + wRes['Reason'] )
##			wOBJ_DB.Close()
##			return False
##		
##		if len( wRes['Responce']['Data'] )!=1 :
##			##存在しない
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: DelDomain: Domain is not found: " )
##			wOBJ_DB.Close()
##			return False
##		
##		#############################
##		# ドメイン情報の辞書化
##		wDomainCheck = {}
##		for wLineTap in wRes['Responce']['Data'] :
##			wGetTap = []
##			for wCel in wLineTap :
##				wCel = wCel.strip()
##				wGetTap.append( wCel )
##				## [0] ..domain
##				## [1] ..count
##				## [2] ..rat_count
##			
##			wDomainCheck({ wGetTap[0] : "" })
##			wDomainCheck[wIndex]({ "exist"  : False })
##		
##		#############################
##		# ドメイン存在時にexist=true
##		for wCel in wList :
##			wDomainCheck[wCel]["exist"] = True
##		
##		#############################
##		# 存在しないドメインを削除する
##		wKeyList = wDomainCheck.keys()
##		for wCel in wKeyList :
##			if wDomainCheck[wCel]["exist"]==False :
##				wQuery = "delete from TBL_TRAFFIC_DATA where domain = " + wCel + \
##							") ;"
##			
##			self.Obj_Parent.OBJ_Mylog.Log( 'b', "TBL_TRAFFIC_DATA ドメイン削除: " + wCel )
##			
##			wRes = wOBJ_DB.RunQuery( wQuery )
##			if wRes['Result']!=True :
##				##失敗
##				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: DelDomain: Delete Domain is failed: " + wRes['Reason'] )
##				wOBJ_DB.Close()
##				return False
##		
##		#############################
##		# DB切断
##		wOBJ_DB.Close()
##		return True



#####################################################
# カウントアップ
#####################################################
	def Countup(self):
##		#############################
##		# 読み出し先初期化
##		wCount = []
##		
##		#############################
##		# ファイル読み込み
##		wFile_path = self.Obj_Parent.CHR_User_path + gVal.STR_File['TrafficFile']
##		if CLS_File.sReadFile( wFile_path, outLine=wCount )!=True :
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Countup: Traffic count file read failed: " + wFile_path )
##			return False	#失敗
##		
##		#############################
##		# データチェック
##		#   空の時、リセット
##		if len(wCount)==0 :
##			wCount.append( "0,0" )
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Countup: Traffic counter value null(Crash?). Counter Reset." )
##		
##		#############################
##		# データ整形
##		try:
##			wCount = wCount[0].split(",")
##			wCount[0] = int( wCount[0] )	# 現カウント
##			wCount[1] = int( wCount[1] )	# 1時間前のカウント
##		except ValueError as err :
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Countup: Traffic count exception: " + str(err) )
##			return False	#失敗
##		
##		#############################
##		# 1時間経ってる周回か
##		if gVal.STR_TimeInfo['OneHour']==True :
##			wCount[1] = wCount[0]
##			wCount[0] = 1
##		#############################
##		# カウントアップ
##		else:
##			wCount[0] += 1
##		
##		#############################
##		# 書き込み用データ整形
##		wLine = str( wCount[0] ) + "," + str( wCount[1] )
##		
##		#############################
##		# ファイル書き込み
##		wSetLine = []
##		wSetLine.append( wLine )
##		if CLS_File.sWriteFile( wFile_path, wSetLine )!=True :
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Countup: Traffic count file write failed: " + wFile_path )
##			return False	#失敗

		#############################
		# ドメインの抽出
		wDomain = self.Obj_Parent.CHR_Account.split("@")
		if len(wDomain)!=2 :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Countup: Illigal admin_id: " + self.Obj_Parent.CHR_Account )
			return False
		wDomain = wDomain[1]
		
##		#############################
##		# DB接続情報ファイルのチェック
##		wFile_path = gVal.STR_File['DBinfo_File']
##		if CLS_File.sExist( wFile_path )!=True :
##			##失敗
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Countup: Database file is not found: " + wFile_path + " domain=" + wDomain )
##			return False
##		
		#############################
		# DB接続
		wOBJ_DB = CLS_PostgreSQL_Use( wFile_path )
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Countup: DB Connect test is failed: " + wRes['Reason'] + " domain=" + wDomain )
			wOBJ_DB.Close()
			return False
		
		#############################
		# ドメイン存在チェック
##		wQuery = "select * from TBL_TRAFFIC_DATA where exists (select domain from " +  \
##					wDomain + ") ;"
##		wQuery = "select exists (select * from TBL_TRAFFIC_DATA where domain = '" + wDomain + "');"
##		
##		wRes = wOBJ_DB.RunQuery( wQuery )
##		wRes = wOBJ_DB.GetQueryStat()
		wQuery = "domain = '" + wDomain + "'"
		wDBRes = wOBJ_DB.RunExist( inObjTable="TBL_TRAFFIC_DATA", inWhere=wQuery )
		wDBRes = wOBJ_DB.GetQueryStat()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Countup: Run Query is failed: " + wRes['Reason'] + " domain=" + wDomain )
			wOBJ_DB.Close()
			return False
		
##		if len( wRes['Responce']['Data'] )!=1 :
		if wRes['Responce']!=True :
			##存在しない
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Countup: Domain is not found: " + " domain=" + wDomain )
			wOBJ_DB.Close()
			return False
		
		#############################
		# カウント値の取り出し
		for wLineTap in wRes['Responce']['Data'] :
			wGetTap = []
			for wCel in wLineTap :
				wCel = wCel.strip()
				wGetTap.append( wCel )
				## [0] ..domain
				## [1] ..count
				## [2] ..rat_count
		
		wCount    = int( wGetTap[1] )
		wRatCount = int( wGetTap[2] )
		
		#############################
		# カウントを取るユーザか？
		if wGetTap[1]!=self.Obj_Parent.CHR_Account :
			##対象外
			wOBJ_DB.Close()
			return True
		
		#############################
		# 1時間経ってる周回か
		if gVal.STR_TimeInfo['OneHour']==True :
			wRatCount = wCount
			wCount    = 1
		#############################
		# カウントアップ
		else:
			wCount += 1
		
		#############################
		# テーブルの更新
		wQuery = "update TBL_TRAFFIC_DATA set domain = " + wDomain + " where " + \
					"count = " + wCount + " " + \
					"rat_count = " + wRatCount + " " + \
					";"
		
		wRes = wOBJ_DB.RunQuery( wQuery )
		wRes = wOBJ_DB.GetQueryStat()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Countup: Update Count is failed: " + wRes['Reason'] + " domain=" + wDomain )
			wOBJ_DB.Close()
			return False
		
		#############################
		# DB切断
		wOBJ_DB.Close()
		return True			#成功



#####################################################
# カウントリセット
#####################################################
##	def CountReset(self):
##		#############################
##		# パス設定
##		wFile_path = self.Obj_Parent.CHR_User_path + gVal.STR_File['TrafficFile']
##		
##		#############################
##		# 書き込み用データ整形
##		wLine = "0,0"
##		
##		#############################
##		# ファイル書き込み
##		wSetLine = []
##		wSetLine.append( wLine )
##		if CLS_File.sWriteFile( wFile_path, wSetLine )!=True :
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: CountReset: Traffic count file write failed: " + wFile_path )
##			return False	#失敗
##		
##		self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: CountReset: トラヒックカウント リセット済" )
##		return True			#成功



