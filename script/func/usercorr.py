#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ユーザ情報収集
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/9/14
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
# 活動している有効なユーザか判定
#####################################################
	def IsActiveUser( self, inFulluser ) :
		
		wARR_Users = []
		#############################
		# 指定日付の抽出
		wLag = gVal.DEF_STR_TLNUM['AutoRemoveDays'] * 24 * 60 * 60
		wLagTime = CLS_OSIF.sTimeLag( inThreshold=wLag, inTimezone=-1 )
		if wLagTime['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: IsActiveUser: sTimeLag is failed" )
			return False
		
		#############################
		# DB接続
		wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: IsActiveUser: DB Connect test is failed: " + wRes['Reason'] )
			wOBJ_DB.Close()
			return False
		
		#############################
		# 一定期間活動があるユーザか
##		wQuery = "id = '" + inFulluser + "' and " + \
##					"lupdate >= timestamp '" + str(wLagTime['RateTime']) + "'"
##		
##		wDBRes = wOBJ_DB.RunExist( inObjTable="TBL_USER_DATA", inWhere=wQuery )
##		wDBRes = wOBJ_DB.GetQueryStat()
##		if wDBRes['Result']!=True :
##			##失敗
##			wRes['Reason'] = "CLS_UserCorr: IsActiveUser: Run Query is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query']
##			wOBJ_DB.Close()
##			return False
##		
##		### 収集していないか、期間活動外
##		if wDBRes['Responce']==False :
##			wOBJ_DB.Close()
##			return False
##		
		wQuery = "select locked from TBL_USER_DATA where " + \
					"id = '" + inFulluser + "' and " + \
					"lupdate >= timestamp '" + str(wLagTime['RateTime']) + "' " + \
					";"
		
		wDBRes = wOBJ_DB.RunQuery( wQuery )
		wDBRes = wOBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_UserCorr: IsActiveUser: Run Query is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query']
			wOBJ_DB.Close()
			return False
		
		### 収集していないか、期間活動外
		if len(wDBRes['Responce']['Data'])==0 :
			wOBJ_DB.Close()
			return False
		
		### 鍵垢か
		wChgList = []
		if wOBJ_DB.ChgList( wDBRes['Responce']['Data'], outList=wChgList )!=True :
			##ないケースかも
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: IsActiveUser: Select data is Zero" )
			wOBJ_DB.Close()
			return False
		if wChgList[0][0]==True :
			wOBJ_DB.Close()
			return False	#鍵つき
		
		#############################
		# DB切断
		wOBJ_DB.Close()
		
		###有効なユーザ
		return True



#####################################################
# 一定期間活動のないユーザ一覧
#####################################################
	def GetOldUser( self, inARR_Follow ) :
		
		wARR_Users = []
		#############################
		# 指定日付の抽出
		wLag = gVal.DEF_STR_TLNUM['AutoRemoveDays'] * 24 * 60 * 60
		wLagTime = CLS_OSIF.sTimeLag( inThreshold=wLag, inTimezone=-1 )
		if wLagTime['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: GetOldUser: sTimeLag is failed" )
			return wARR_Users
		
		#############################
		# DB接続
		wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: GetOldUser: DB Connect test is failed: " + wRes['Reason'] )
			wOBJ_DB.Close()
			return wARR_Users
		
		#############################
		# 古いユーザ取得
		wQuery = "select id from TBL_USER_DATA where lupdate < " + \
					"timestamp '" + str(wLagTime['RateTime']) + "' " + \
					";"
		wDBRes = wOBJ_DB.RunQuery( wQuery )
		wDBRes = wOBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: GetOldUser: Run Query is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
			wOBJ_DB.Close()
			return wARR_Users
		
		#############################
		# 取得あればローカルに詰める
		wARR_OldUsers = []
		wOBJ_DB.ChgList( wDBRes['Responce']['Data'], outList=wARR_OldUsers )
		
		#############################
		# DB切断
		wOBJ_DB.Close()
		
		#############################
		# フォロー者のなかからリムーブ対象のユーザを出力
		for wUser in inARR_Follow :
			if wUser in wARR_OldUsers :
				wARR_Users.append( wUser )
		
		return wARR_Users



#####################################################
# ユーザ収集への追加
#   辞書型で登録する
#####################################################
	def AddUser( self, inROW, inUser ) :
##		wAccount = inROW['account']
##		#############################
##		# ユーザ名の変換
##		wFulluser = CLS_UserData.sGetFulluser( wAccount['username'], wAccount['url'] )
##		if wFulluser['Result']!=True :
##			###今のところ通らないルート
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: AddUser: sGetFulluser failed: " + wFulluser['Reason'] )
##			return False	#スルー
		
		#############################
		# 除外トゥート
##		###自分
##		if wFulluser['Fulluser'] == self.Obj_Parent.CHR_Account :
##			return False		#スルーする
##		
##		###外人 (日本人限定=ON時)
##		if inROW['language']!="ja" and gVal.STR_MasterConfig["JPonly"]=="on" :
##			self.Obj_Parent.OBJ_Mylog.Log( 'c', "CLS_UserCorr: AddUser: 日本人以外を検出(登録除外): " + wFulluser['Fulluser'] )
##			return False		#スルーする
##		
##		###除外ドメイン
##		if wFulluser['Domain'] in gVal.STR_DomainREM :
##			self.Obj_Parent.OBJ_Mylog.Log( 'c', "CLS_UserCorr: AddUser: 除外ドメインを検出(登録除外): " + wFulluser['Fulluser'] )
##			return False		#スルーする
##		
		###今回関わったユーザ
		if inUser['Fulluser'] in self.ARR_UpdateUser :
			return False		#スルーする
		self.ARR_UpdateUser.append( inUser['Fulluser'] )
		
		# ここまでで登録処理確定
		#############################
		self.STR_Stat['Cope'] += 1
		
		#############################
		# postgreSQL対策で ' 文字を消す
		wResReplace = CLS_OSIF.sRe_Replace( "'", str( inROW['account']['display_name'] ), "''" )
		###	"Result"	: False,
		###	"Match"		: False,
		###	"After"		: None
		if wResReplace['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: AddUser: sRe_Replace is failed: display_name=" + str( inROW['account']['display_name'] ) )
			return False
		if wResReplace['Match']==True :
			wDisplay_Name = wResReplace['After']
		else :
			wDisplay_Name = str( inROW['account']['display_name'] )
		
		#############################
		# セット用領域の作成
		wUserData = {}
		wUserData.update({ "id"       : inUser['Fulluser'] })
###		wUserData.update({ "username" : str( inROW['account']['display_name'] ) })
		wUserData.update({ "username" : wDisplay_Name })
		wUserData.update({ "domain"   : inUser['Domain'] })
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
##		if wAccount['locked']==True :
		if inROW['account']['locked']==True :
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
###			wUserData['status']   = wChgList[3]
###			wUserData['followed'] = wChgList[4]
			wUserData['status']   = wChgList[0][3]
			wUserData['followed'] = wChgList[0][4]
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
##			self.Obj_Parent.OBJ_Mylog.Log( 'c', "CLS_UserCorr: AddUser: ユーザ追加: " + inUser['Fulluser'] )
			self.STR_Stat['UserAdd'] += 1
		else :
##			self.Obj_Parent.OBJ_Mylog.Log( 'c', "CLS_UserCorr: AddUser: ユーザ更新: " + inUser['Fulluser'] )
			self.STR_Stat['UserUpdate'] += 1
		
		return True



