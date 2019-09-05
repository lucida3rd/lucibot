#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：フォロー管理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/9/5
#####################################################
# Private Function:
#   __get_FollowTL( self, inMyID):
#   __get_FollowerTL( self, inMyID ):
#
# Instance Function:
#   __init__( self, parentObj=None ):
#   Check_Follower( self, inFullser ):
#   Get_FollowLists(self):
#   Set_FollowLists(self):
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
class CLS_Follow():
#####################################################
	Obj_Parent = ""		#親クラス実体
	
	FLG_Update = False
	ARR_FollowTL   = []	#フォロー一覧
	ARR_FollowerTL = []	#フォロワー一覧

#####################################################
# Init
#####################################################
	def __init__( self, parentObj=None ):
		if parentObj==None :
			###親クラス実体の未設定
			CLS_OSIF.sPrn( "CLS_Follow: __init__: You have not set the parent class entity for parentObj" )
			return
		
		self.Obj_Parent = parentObj
		
		self.FLG_Update = False
		self.ARR_FollowTL   = []
		self.ARR_FollowerTL = []
		return



#####################################################
# フォロワーか
#####################################################
	def Check_Follower( self, inFullser ):
		if inFullser not in self.ARR_FollowerTL :
			return False	#フォロワーではない
		
		return True			#フォロワー



#####################################################
# フォロー一覧取得・保存
#####################################################
	def Get_FollowLists(self):
		#############################
		# 読み出し先初期化
		self.ARR_FollowTL = []
		self.ARR_FollowerTL = []
		self.FLG_Update = False
		
		#############################
		# フォローファイル読み込み
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['FollowListFile']
		if CLS_File.sReadFile( wFile_path, outLine=self.ARR_FollowTL )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Follow: Get_FollowLists: Get follow list file is failed: " + wFile_path )
			return False	#失敗
		
		#############################
		# フォロワーファイル読み込み
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['FollowerListFile']
		if CLS_File.sReadFile( wFile_path, outLine=self.ARR_FollowerTL )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Follow: Get_FollowLists: Get follower list file is failed: " + wFile_path )
			return False	#失敗
		
		#############################
		# bot起動の最初か、1時間経っていればmastodonから取得する
		#  *** フォロー・フォロワーがいないと常に取りにいってしまう
		if len(self.ARR_FollowTL)>0 or len(self.ARR_FollowerTL)>0 :
##			if gVal.STR_TimeInfo['OneDay']==False :
			if gVal.STR_TimeInfo['OneHour']==False :
			    return True		#正常で返す
		
		#############################
		# mastodonから取得しなおす
		#############################
		# 自アカウントのフォロー一覧を取得
		wRes = self.__get_FollowTL( self.Obj_Parent.ARR_MyAccountInfo['id'] )
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Follow: Get_FollowLists: Get follow list is failed: " + wRes['Reason'] )
			return False
		
		#############################
		# 自アカウントのフォロワー一覧を取得
		wRes = self.__get_FollowerTL( self.Obj_Parent.ARR_MyAccountInfo['id'] )
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Follow: Get_FollowLists: Get follower list is failed: " + wRes['Reason'] )
			return False
		
		self.FLG_Update = True
		return True

	#####################################################
	def Set_FollowLists(self):
		#############################
		# 更新されてなければ抜ける
		if self.FLG_Update==False :
			return True
		
		#############################
		# フォローファイル書き込み (改行つき)
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['FollowListFile']
		if CLS_File.sWriteFile( wFile_path, self.ARR_FollowTL, inRT=True )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Follow: Set_FollowLists: Set follow list file is failed: " + wFile_path )
			return False	#失敗
		
		#############################
		# フォロワーファイル書き込み (改行つき)
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['FollowerListFile']
		if CLS_File.sWriteFile( wFile_path, self.ARR_FollowerTL, inRT=True )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Follow: Set_FollowLists: Set follower list file is failed: " + wFile_path )
			return False	#失敗
		
		wStr = "フォローリスト更新あり: follow=" + str(len(self.ARR_FollowTL)) + " follower=" + str(len(self.ARR_FollowerTL))
		self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr )
		return True			#成功



	#####################################################
	def __get_FollowTL( self, inMyID):
		self.ARR_FollowTL = []
		wGetList = []
		wNext_Id = None
		wMax_Toots = gVal.DEF_STR_TLNUM["getFollowTLnum"]
		while (len(wGetList) < wMax_Toots ):
			#############################
			# TL取得
			wRes = self.Obj_Parent.OBJ_MyDon.GetFollowingList( id=inMyID, limit=40, max_id=wNext_Id )
			if wRes['Result']!=True :
				return wRes	#失敗
			
			wGet_Toots = wRes['Responce']	#toot list(json形式)
			
			#############################
			# 新しいトゥートが取得できなかったらループ終了
			if len( wGet_Toots ) > 0:
				wGetList += wGet_Toots
			else:
				break
			
			#############################
			# configの最大取得数を超えていたらループ終了
			if len( wGetList ) >= wMax_Toots :
				break
			
			#############################
			# ページネーション(次の40件を取得する設定)
			try:
				wNext_Id = wGet_Toots[-1]['id']
			except:
				###ありえない
				wRes['Reason'] = "CLS_Follow: __get_FollowTL: Page nation error"
				wRes['Result'] = False
				return wRes
		
		#############################
		# IDに変換して詰める
		for wAccount in wGetList :
			###変換
			wFulluser = CLS_UserData.sGetFulluser( wAccount['username'], wAccount['url'] )
			if wFulluser['Result']!=True :
				###失敗 : 今のところ通らないルート
				continue
			
			###詰める
			self.ARR_FollowTL.append( wFulluser['Fulluser'] )
		
		return wRes

	#####################################################
	def __get_FollowerTL( self, inMyID ):
		self.ARR_FollowerTL = []
		wGetList = []
		wNext_Id = None
		wMax_Toots = gVal.DEF_STR_TLNUM["getFollowerTLnum"]
		while (len(wGetList) < wMax_Toots ):
			#############################
			# TL取得
			wRes = self.Obj_Parent.OBJ_MyDon.GetFollowersList( id=inMyID, limit=40, max_id=wNext_Id )
			if wRes['Result']!=True :
				return wRes	#失敗
			
			wGet_Toots = wRes['Responce']	#toot list(json形式)
			
			#############################
			# 新しいトゥートが取得できなかったらループ終了
			if len( wGet_Toots ) > 0:
				wGetList += wGet_Toots
			else:
				break
			
			#############################
			# configの最大取得数を超えていたらループ終了
			if len( wGetList ) >= wMax_Toots :
				break
			
			#############################
			# ページネーション(次の40件を取得する設定)
			try:
				wNext_Id = wGet_Toots[-1]['id']
			except:
				###ありえない
				wRes['Reason'] = "CLS_Follow: __get_FollowerTL: Page nation error"
				wRes['Result'] = False
				return wRes
		
		#############################
		# IDに変換して詰める
		for wAccount in wGetList :
			###変換
			wFulluser = CLS_UserData.sGetFulluser( wAccount['username'], wAccount['url'] )
			if wFulluser['Result']!=True :
				###失敗 : 今のところ通らないルート
				continue
			
			###詰める
			self.ARR_FollowerTL.append( wFulluser['Fulluser'] )
		
		return wRes



