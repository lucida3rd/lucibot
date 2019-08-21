#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ユーザ情報収集
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/8/17
#####################################################
# Private Function:
#   __getUserInfo_Full(self) :
#   __chgUserInfo_Line( self, inKey ) :
#   __chgUserInfo_Line_Min( self, inKey ) :
#
# Instance Function:
#   __init__( self, inPath ):
#   GetUserInfo_Min(self) :
#   SetUserInfo_Min(self) :
#   GetDomainREM(self) 
#   AddUser( self, inROW ) :
#   UpdateUser( self, inKey, inROW, inAccount ) :
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
from filectrl import CLS_File
from userdata import CLS_UserData
from gval import gVal
#####################################################
class CLS_UserCorr():
#####################################################
	Obj_Parent = ""		#親クラス実体
	
	STR_UserInfo = {}	#ユーザ情報

#####################################################
# Init
#####################################################
	def __init__( self, parentObj=None ):
		if parentObj==None :
			###親クラス実体の未設定
			CLS_OSIF.sPrn( "CLS_UserCorr: __init__: You have not set the parent class entity for parentObj" )
			return
		
		self.Obj_Parent = parentObj
		return



#####################################################
# ユーザ情報データの読み込み/書き込み(Master/Sub用)
#####################################################
	def GetUserInfo_Min(self) :
		#############################
		# 初期化
		self.STR_UserInfo = {}
		wWork_UserInfo    = []
		
		#############################
		# ファイル読み込み
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.STR_File['UserinfoFile']
		if CLS_File.sReadFile( wFile_path, outLine=wWork_UserInfo )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: GetUserInfo_Min: Userinfo file read failed: " + wFile_path )
			return False	#失敗
		
		#############################
		# データをユーザ情報に読み出す
		wSetIndex = 0
		try:
			for wLine in wWork_UserInfo :
				wLine = wLine.split( gVal.DEF_DATA_BOUNDARY )	#分解
				
				wGet_UserInfo = self.__getUserInfo_Full()
				wGet_UserInfo['username'] = wLine[0]
				wGet_UserInfo['Domain']   = wLine[1]
				wGet_UserInfo['Status']   = wLine[2]
				wGet_UserInfo['Lastupdate'] = wLine[3]
				
				self.STR_UserInfo.update({ wSetIndex : wGet_UserInfo })
				wSetIndex += 1
		except ValueError as err :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: GetUserInfo_Min: Userinfo exception: " + str(err) )
			return False	#失敗
		
		return True

#####################################################
	def SetUserInfo_Min(self) :
		#############################
		# 初期化
		wWork_UserInfo = []
		
		#############################
		# データをユーザ情報に読み出す
		wKeyList = self.STR_UserInfo.keys()
		for wKey in wKeyList :
			wLine = self.__chgUserInfo_Line_Min( wKey )
			wWork_UserInfo.append( wLine )
		
		#############################
		# ファイル書き込み
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.STR_File['UserinfoFile']
		if CLS_File.sWriteFile( wFile_path, wWork_UserInfo, inRT=True )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: SetUserInfo_Min: Userinfo file write failed: " + wFile_path )
			return False	#失敗
		
		return True



#####################################################
# ユーザ情報型の取得
#####################################################
	def __getUserInfo_Full(self) :
		wUserInfo = {}
		wUserInfo.update({ "id"       : "" })
		wUserInfo.update({ "username" : "" })
		wUserInfo.update({ "Domain"   : "" })
		wUserInfo.update({ "ProfUrl"  : "" })
		
		wUserInfo.update({ "Status" : "-" })
			## @ フォローチェック予約(まだ未フォロー)
			## - フォローチェック済
			## D ドメインブロックユーザ
			## R リムーブ予約
			## X チェックもしくはフォロー失敗
			## * リストから消す
			## M 自分
		
		wUserInfo.update({ "Followed" : "-" })	#フォローしたことがある
		wUserInfo.update({ "Follow"   : "-" })	#現在フォロー状態
		wUserInfo.update({ "Follower" : "-" })	#現在フォロワーか
			## F フォロー
			## - フォローしてない
		wUserInfo.update({ "Locked"   : "-" })	#鍵
			## K 鍵垢
			## - 鍵OFF
###		wUserInfo.update({ "Score"      : 0 })
		wUserInfo.update({ "Lastupdate" : "" })
		wUserInfo.update({ "Lastcheck"  : "" })
		
		return wUserInfo



#####################################################
# ユーザ情報書き出し型への変換
#####################################################
	def __chgUserInfo_Line( self, inKey ) :
		wUserInfo = ""
		wUserInfo = wUserInfo + str(self.STR_UserInfo[inKey]['id'])  + gVal.DEF_DATA_BOUNDARY
		wUserInfo = wUserInfo + self.STR_UserInfo[inKey]['username'] + gVal.DEF_DATA_BOUNDARY
		wUserInfo = wUserInfo + self.STR_UserInfo[inKey]['Domain']   + gVal.DEF_DATA_BOUNDARY
		wUserInfo = wUserInfo + self.STR_UserInfo[inKey]['ProfUrl']  + gVal.DEF_DATA_BOUNDARY
		
		wUserInfo = wUserInfo + self.STR_UserInfo[inKey]['Status'] + gVal.DEF_DATA_BOUNDARY
		
		wUserInfo = wUserInfo + self.STR_UserInfo[inKey]['Followed'] + gVal.DEF_DATA_BOUNDARY
		wUserInfo = wUserInfo + self.STR_UserInfo[inKey]['Follow']   + gVal.DEF_DATA_BOUNDARY
		wUserInfo = wUserInfo + self.STR_UserInfo[inKey]['Follower'] + gVal.DEF_DATA_BOUNDARY
		wUserInfo = wUserInfo + self.STR_UserInfo[inKey]['Locked']   + gVal.DEF_DATA_BOUNDARY
		
###		wUserInfo = wUserInfo + str(self.STR_UserInfo[inKey]['Score']) + gVal.DEF_DATA_BOUNDARY
		wUserInfo = wUserInfo + self.STR_UserInfo[inKey]['Lastupdate'] + gVal.DEF_DATA_BOUNDARY
		wUserInfo = wUserInfo + self.STR_UserInfo[inKey]['Lastcheck']
		
		return wUserInfo

#####################################################
	def __chgUserInfo_Line_Min( self, inKey ) :
		wUserInfo = ""
		wUserInfo = wUserInfo + self.STR_UserInfo[inKey]['username'] + gVal.DEF_DATA_BOUNDARY
		wUserInfo = wUserInfo + self.STR_UserInfo[inKey]['Domain']   + gVal.DEF_DATA_BOUNDARY
		wUserInfo = wUserInfo + self.STR_UserInfo[inKey]['Status']   + gVal.DEF_DATA_BOUNDARY
		wUserInfo = wUserInfo + str(self.STR_UserInfo[inKey]['Lastupdate'])
		return wUserInfo



#####################################################
# 除外ドメイン読み込み
#####################################################
	def GetDomainREM(self) :
		#############################
		# 初期化
		gVal.STR_DomainREM = []
		
		#############################
		# ファイル読み込み
		wFile_path = gVal.STR_File['DomainREMFile']
		if CLS_File.sReadFile( wFile_path, outLine=gVal.STR_DomainREM )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: GetDomainREM: DomainREM file read failed: " + wFile_path )
			return False	#失敗
		
		return True			#成功



#####################################################
# ユーザ収集への追加
#   辞書型で登録する
#####################################################
	def AddUser( self, inROW ) :
		#############################
		# 収める枠を取得(辞書型)
		wUserInfo = self.__getUserInfo_Full()
		
		wAccount       = inROW['account']
		wAccount['id'] = int(wAccount['id'])
		#############################
		# ユーザ名の変換
		wFulluser = CLS_UserData.sGetFulluser( wAccount['username'], wAccount['url'] )
		if wFulluser['Result']!=True :
			###今のところ通らないルート
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: AddUser: sGetFulluser failed: " + wFulluser['Reason'] )
			return False	#スルー
		
		#############################
		# 既に存在していれば、情報を更新する
		wKeyList = self.STR_UserInfo.keys()
		for wKey in wKeyList :
			if self.STR_UserInfo[wKey]['username']==wFulluser['Username'] and \
			   self.STR_UserInfo[wKey]['Domain']==wFulluser['Domain'] :
				wRes = self.UpdateUser( wKey, inROW, wFulluser )
				return wRes	#常にTrue
		
		#############################
		# 自分か
		if wFulluser['Fulluser'] == self.Obj_Parent.CHR_Account :
			wUserInfo['Status'] = "M"
			self.Obj_Parent.OBJ_Mylog.Log( 'b', "CLS_UserCorr: AddUser: ユーザ情報に自分が追加された(Status=M): " + wFulluser['Fulluser'] )
		
		#############################
		# 外人か (日本人限定=ON時)
##		if inROW['language']!="ja" and gVal.STR_Config["JPonly"]=="on" :
		if inROW['language']!="ja" and gVal.STR_MasterConfig["JPonly"]=="on" :
			self.Obj_Parent.OBJ_Mylog.Log( 'c', "CLS_UserCorr: AddUser: 日本人以外を検出(登録除外): " + wFulluser['Fulluser'] )
			return False		#スルーする
		
		#############################
		# 除外ドメインか
		if wFulluser['Domain'] in gVal.STR_DomainREM :
			self.Obj_Parent.OBJ_Mylog.Log( 'c', "CLS_UserCorr: AddUser: 除外ドメインを検出(登録除外): " + wFulluser['Fulluser'] )
			return False		#スルーする
		
		# ここまでで追加確定
		#############################
		
		#############################
		# 鍵の有無
		if wAccount['locked']==True :
			wUserInfo['Locked'] = "K"
		else :
			wUserInfo['Locked'] = "-"
		
		#############################
		# 更新時間 (mastodon時間)
		wTime = CLS_OSIF.sGetTimeformat( inROW['created_at'] )
		if wTime['Result']==True :
			wUserInfo['Lastupdate'] = wTime['TimeDate']
		
		#############################
		# その他の設定
		wUserInfo['id'] = wAccount['id']
		wUserInfo['username'] = wFulluser['Username']
		wUserInfo['Domain']   = wFulluser['Domain']
		if wUserInfo['Status'] == "-" :
			wUserInfo['Status'] = "@"
		
		#############################
		# ユーザ情報に追加
		wSetIndex = len(self.STR_UserInfo)
			### Index値
			###   空の場合 0
			###   ある場合 self.STR_UserInfoの最終データのIndex値
		self.STR_UserInfo.update({ wSetIndex : wUserInfo })
		
		self.Obj_Parent.OBJ_Mylog.Log( 'c', "CLS_UserCorr: AddUser: ユーザ追加: " + wFulluser['Fulluser'] )
		return True

#####################################################
	def UpdateUser( self, inKey, inROW, inAccount ) :
		wAccount       = inROW['account']
		wAccount['id'] = int(wAccount['id'])
		
		#############################
		# 外人か (日本人限定=ON時)
##		if inROW['language']!="ja" and gVal.STR_Config["JPonly"]=="on" :
		if inROW['language']!="ja" and gVal.STR_MasterConfig["JPonly"]=="on" :
			self.STR_UserInfo[inKey]['Status'] = "X"
			self.Obj_Parent.OBJ_Mylog.Log( 'b', "CLS_UserCorr: UpdateUser: 日本人以外を検出(登録抹消): " + inAccount['Fulluser'] )
		
		#############################
		# 除外ドメインか
		if inAccount['Domain'] in gVal.STR_DomainREM :
			self.STR_UserInfo[inKey]['Status'] = "X"
			self.Obj_Parent.OBJ_Mylog.Log( 'b', "CLS_UserCorr: UpdateUser: 除外ドメインを検出(登録抹消): " + inAccount['Fulluser'] )
		
		# ここまでで追加確定
		#############################
		
		#############################
		# 鍵の有無
		if wAccount['locked']==True :
			self.STR_UserInfo[inKey]['Locked'] = "K"
		else :
			self.STR_UserInfo[inKey]['Locked'] = "-"
		
		#############################
		# 更新時間 (mastodon時間)
		wTime = CLS_OSIF.sGetTimeformat( inROW['created_at'] )
		if wTime['Result']==True :
			self.STR_UserInfo[inKey]['Lastupdate'] = wTime['TimeDate']
		
		#############################
		# その他の設定
		self.STR_UserInfo[inKey]['id'] = wAccount['id']
		
		self.Obj_Parent.OBJ_Mylog.Log( 'c', "CLS_UserCorr: UpdateUser: ユーザ情報更新: " + inAccount['Fulluser'] )
		return True



