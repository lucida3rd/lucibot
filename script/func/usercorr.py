#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ユーザ情報収集
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/9/5
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   __init__( self, parentObj=None ):
#   GetDomainREM(self) :
#   AddUser( self, inROW ) :
#
# Class Function(static):
#   (none)
#
#####################################################
from postgresql_use import CLS_PostgreSQL_Use

from osif import CLS_OSIF
from filectrl import CLS_File
from userdata import CLS_UserData
from gval import gVal
#####################################################
class CLS_UserCorr():
#####################################################
	Obj_Parent = ""		#親クラス実体
	
	ARR_UpdateUser = []			#今回関わったユーザ
	
	STR_Stat = {
		"Cope"			: 0,	#今回の処理ユーザ数
		"UserAdd"		: 0,	#今回の登録ユーザ数
		"UserUpdate"	: 0		#今回の更新ユーザ数
	}

#####################################################
# Init
#####################################################
	def GetUserCorrectStat(self):
		return self.STR_Stat



#####################################################
# Init
#####################################################
	def __init__( self, parentObj=None ):
		if parentObj==None :
			###親クラス実体の未設定
			CLS_OSIF.sPrn( "CLS_UserCorr: __init__: You have not set the parent class entity for parentObj" )
			return
		
		self.Obj_Parent = parentObj
		self.ARR_UpdateUser = []	#今回関わったユーザ
		return



#####################################################
# 除外ドメイン読み込み
#####################################################
	def GetDomainREM(self) :
		#############################
		# 初期化
		gVal.STR_DomainREM = []
		
		#############################
		# ファイル読み込み
		wFile_path = gVal.DEF_STR_FILE['DomainREMFile']
		if CLS_File.sReadFile( wFile_path, outLine=gVal.STR_DomainREM )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: GetDomainREM: DomainREM file read failed: " + wFile_path )
			return False	#失敗
		
		return True			#成功



#####################################################
# ユーザ収集への追加
#   辞書型で登録する
#####################################################
	def AddUser( self, inROW ) :
		wAccount = inROW['account']
		#############################
		# ユーザ名の変換
		wFulluser = CLS_UserData.sGetFulluser( wAccount['username'], wAccount['url'] )
		if wFulluser['Result']!=True :
			###今のところ通らないルート
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: AddUser: sGetFulluser failed: " + wFulluser['Reason'] )
			return False	#スルー
		
		#############################
		# 除外トゥート
		###自分
		if wFulluser['Fulluser'] == self.Obj_Parent.CHR_Account :
			return False		#スルーする
		
		###外人 (日本人限定=ON時)
		if inROW['language']!="ja" and gVal.STR_MasterConfig["JPonly"]=="on" :
			self.Obj_Parent.OBJ_Mylog.Log( 'c', "CLS_UserCorr: AddUser: 日本人以外を検出(登録除外): " + wFulluser['Fulluser'] )
			return False		#スルーする
		
		###除外ドメイン
		if wFulluser['Domain'] in gVal.STR_DomainREM :
			self.Obj_Parent.OBJ_Mylog.Log( 'c', "CLS_UserCorr: AddUser: 除外ドメインを検出(登録除外): " + wFulluser['Fulluser'] )
			return False		#スルーする
		
		###今回関わったユーザ
		if wFulluser['Fulluser'] in self.ARR_UpdateUser :
			return False		#スルーする
		self.ARR_UpdateUser.append( wFulluser['Fulluser'] )
		
		# ここまでで登録処理確定
		#############################
		self.STR_Stat['Cope'] += 1
		
		#############################
		# セット用領域の作成
		wUserData = {}
		wUserData.update({ "id"       : wFulluser['Fulluser'] })
		wUserData.update({ "username" : str( inROW['account']['display_name'] ) })
		wUserData.update({ "domain"   : wFulluser['Domain'] })
		wUserData.update({ "status"   : "-" })
		wUserData.update({ "followed" : False })
		wUserData.update({ "locked"   : False })
		wUserData.update({ "lupdate"  : "" })
			## status
			##   @ フォローチェック予約(まだ未フォロー)
			##   - フォローチェック済
			##   D ドメインブロックユーザ
			##   R リムーブ予約
			##   X チェックもしくはフォロー失敗
			##   * リストから消す
		
		#############################
		# ステータスの設定
		###鍵の有無
		if wAccount['locked']==True :
			wUserData['locked'] = True
		
		###更新時間 (mastodon時間)
		wTime = CLS_OSIF.sGetTimeformat( inROW['created_at'] )
		if wTime['Result']==True :
			wUserData['lupdate'] = wTime['TimeDate']
		
		#############################
		# DB接続
		wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: AddUser: DB Connect test is failed: " + wRes['Reason'] )
			wOBJ_DB.Close()
			return False
		
##		#############################
##		# ユーザ存在チェック
##		wQuery = "id = '" + wUserData['id'] + "'"
##		wDBRes = wOBJ_DB.RunExist( inObjTable="TBL_USER_DATA", inWhere=wQuery )
##		wDBRes = wOBJ_DB.GetQueryStat()
##		if wDBRes['Result']!=True :
##			##失敗
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: AddUser: Run Query is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
##			wOBJ_DB.Close()
##			return False
##		
		#############################
		# ユーザ取得
		wQuery = "select * from TBL_USER_DATA where id = '" + wUserData['id'] + "' ;"
		wDBRes = wOBJ_DB.RunQuery( wQuery )
		wDBRes = wOBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: AddUser: Run Query is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
			wOBJ_DB.Close()
			return False
		
		wFLG_AddUser = False
		#############################
		# クエリの作成
		###なければ追加
##		if wDBRes['Responce']==False :
		if len(wDBRes['Responce']['Data'])==0 :
			###ステータスがなければ、チェック候補にする
			if wUserData['status'] == "-" :
				wUserData['status'] = "@"
			
			wQuery = "insert into TBL_USER_DATA values (" + \
						"'" + wUserData['id'] + "'," + \
						"'" + wUserData['username'] + "'," + \
						"'" + wUserData['domain']   + "'," + \
						"'" + wUserData['status']   + "'," + \
						str(wUserData['followed']) + "," + \
						str(wUserData['locked'])   + "," + \
						"'" + str(wUserData['lupdate'])  + "' " + \
						") ;"
			
			wFLG_AddUser = True
		
		###あれば更新
		else :
			wChgList = []
			if wOBJ_DB.ChgList( wDBRes['Responce']['Data'], outList=wChgList )!=True :
				##ないケースかも
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: AddUser: Select data is Zero" )
				wOBJ_DB.Close()
				return False
			wChgList = wChgList[0]	#1行しかないし切る
			
			###領域に詰め直す
##			wUserData['id']       = wChgList[0]
##			wUserData['username'] = wChgList[1]
##			wUserData['domain']   = wChgList[2]
			wUserData['status']   = wChgList[3]
			wUserData['followed'] = wChgList[4]
##			wUserData['locked']   = wChgList[5]
##			wUserData['lupdate']  = wChgList[6]
			
			wQuery = "update TBL_USER_DATA set " + \
					"status = '"   + str(wUserData['status']) + "', " + \
					"locked = '"   + str(wUserData['locked']) + "', " + \
					"lupdate = '"  + str(wUserData['lupdate']) + "' " + \
					"where id = '" + wUserData['id'] + "' ;"
		
		#############################
		# クエリ実行
		wDBRes = wOBJ_DB.RunQuery( wQuery )
		wDBRes = wOBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: AddUser: DB insert is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
			wOBJ_DB.Close()
			return False
		
		#############################
		# DB切断
		wOBJ_DB.Close()
		
		#############################
		# 結果を記録
		if wFLG_AddUser==True :
			self.Obj_Parent.OBJ_Mylog.Log( 'c', "CLS_UserCorr: AddUser: ユーザ追加: " + wFulluser['Fulluser'] )
			self.STR_Stat['UserAdd'] += 1
		else :
			self.Obj_Parent.OBJ_Mylog.Log( 'c', "CLS_UserCorr: AddUser: ユーザ更新: " + wFulluser['Fulluser'] )
			self.STR_Stat['UserUpdate'] += 1
		
		return True



