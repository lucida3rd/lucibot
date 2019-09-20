#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：フォロー管理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/9/21
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
##	ARR_FollowTL   = []	#フォロー一覧
##	ARR_FollowerTL = []	#フォロワー一覧
	ARR_FollowTL   = {}	#フォロー一覧
	ARR_FollowerTL = {}	#フォロワー一覧
	
	VAL_FollowNum = 0
	VAL_Followed  = 0

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
##		self.ARR_FollowTL   = []
##		self.ARR_FollowerTL = []
		self.ARR_FollowTL   = {}
		self.ARR_FollowerTL = {}
		
		self.VAL_FollowNum = 0
		self.VAL_Followed  = 0
		return



#####################################################
# 自動フォロー処理
#####################################################
# 自動フォロー仕様 (readmeより)
# *フォローされた場合は、無条件でリフォローする。
# *フォロー以外のアクションでは、過去にフォローしたことがある場合、フォローしない。
# *収集されてないユーザはフォローしない。
# *鍵垢はフォローしない。
# *30日間活動のないユーザを自動リムーブする。
# *ユーザ収集除外リストに登録したドメイン対象になると自動リムーブする。
#####################################################
	def RunAutoFollow(self):
		#############################
		# 開始ログ
		self.Obj_Parent.OBJ_Mylog.Log( 'b', "自動フォロー 開始" )
		
		wARR_Follower = list(self.ARR_FollowerTL.keys())
		wARR_Follow   = list(self.ARR_FollowTL.keys())
		wARR_noFollow = []
		#############################
		# フォローしてない垢を洗い出す
		for wFollower in wARR_Follower :
			if wFollower not in wARR_Follow :
				wARR_noFollow.append( wFollower )
		
		#############################
		# 除外ドメインを省く
		for wFollower in wARR_noFollow[:] :
			wFulluser = CLS_UserData.sUserCheck( wFollower )
			if wFulluser['Result']!=True :
				###今のところ通らないルート
				return False
			
			if wFulluser['Domain'] in gVal.STR_DomainREM :
				wARR_noFollow.remove( wFollower )
		
		#############################
		# フォローできる条件ならフォローする
		# ・収集されているか
		# ・鍵垢ではない
		# ・30日以内の活動があるか
		for wFollower in wARR_noFollow :
			### 処理回数の上限チェック
			if self.__check_Follow()!=True :
				break
			
			### フォローの条件にあてはまるユーザか
			if self.Obj_Parent.OBJ_UserCorr.IsActiveUser( wFollower )!=True :
				continue
			
			### フォローする
			wID = self.ARR_FollowerTL[wFollower]
			wRes = self.Obj_Parent.OBJ_MyDon.Follow( id=wID )
			if wRes['Result']!=True :
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Follow: RunAutoFollow: Mastodon error: " + wRes['Reason'] )
				return False
			
			self.VAL_FollowNum += 1
			self.VAL_Followed  += 1
		
		#############################
		# 自アカウントのフォロー一覧を再取得
		wRes = self.__get_FollowTL( self.Obj_Parent.ARR_MyAccountInfo['id'] )
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Follow: RunAutoFollow: Get follow list is failed: " + wRes['Reason'] )
			return False
		
		#############################
		# 処理結果ログ
		wStr = "自動フォロー 結果: Followed=" + str(self.VAL_Followed) + " noFollow=" + str(len(wARR_noFollow))

		if gVal.FLG_Test_Mode==False :
			self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr )
		else:
			self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr, True )
		
		return True



#####################################################
# フォロワーか
#####################################################
	def Check_Follower( self, inFullser ):
##		if inFullser not in self.ARR_FollowerTL :
		wKeyList = list( self.ARR_FollowerTL.keys() )
		if inFullser not in wKeyList :
			return False	#フォロワーではない
		
		return True			#フォロワー



#####################################################
# フォロー処理可否
#####################################################
	def __check_Follow(self):
		if gVal.DEF_STR_TLNUM['FollowNum']==self.VAL_FollowNum :
			return False	#処理不可
		
		return True			#処理可能



#####################################################
# 自動リムーブ
#####################################################
	def __autoRemove(self):
		
		wARR_Remove = []
		#############################
		# 除外ドメインのフォローを洗い出す
		# いたら即リムーブする
		wARR_FollowList = list( self.ARR_FollowTL )
		for wUser in wARR_FollowList :
			wDomain = wUser.split("@")
			if len(wDomain)!=2 :
				continue
			wDomain = wDomain[1]
			if wDomain in gVal.STR_DomainREM :
				wARR_Remove.append( wUser )
		
		###対象がいたらリムーブ
		wRemoveNum = 0
		if len(wARR_Remove)>0 :
			for wKey in wARR_Remove :
				###処理可か
				if self.__check_Follow()!=True :
					break
				
				###リムーブ
				wRes = self.Obj_Parent.OBJ_MyDon.Remove( id=self.ARR_FollowTL[wKey] )
				if wRes['Result']!=True :
					self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Follow: __autoRemove: Mastodon error(Domain remove): " + wRes['Reason'] )
					return False
				self.VAL_FollowNum += 1
				wRemoveNum += 1
			
			if wRemoveNum>0 :
				### 自アカウントのフォロー一覧を再取得
				wRes = self.__get_FollowTL( self.Obj_Parent.ARR_MyAccountInfo['id'] )
				if wRes['Result']!=True :
					##失敗
					self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Follow: __autoRemove: Get follow list is failed: " + wRes['Reason'] )
					return False
				
				### 終わり
				wStr = "自動リムーブ: 除外ドメイン対象を処理しました: RemoveNum=" + str( wRemoveNum )
				self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr )
				return True	#リムーブした
		
		#############################
		# 30日間活動してないアカウントが
		# いたら即リムーブする
		
		wARR_Folow = list( self.ARR_FollowTL.keys() )
		###古いユーザを取得
		wARR_Remove = self.Obj_Parent.OBJ_UserCorr.GetOldUser( wARR_Folow )
		
		###対象がいたらリムーブ
		wRemoveNum = 0
		if len(wARR_Remove)>0 :
			for wKey in wARR_Remove :
				###処理可か
				if self.__check_Follow()!=True :
					break
				
				###リムーブ
				wRes = self.Obj_Parent.OBJ_MyDon.Remove( id=self.ARR_FollowTL[wKey] )
				if wRes['Result']!=True :
					self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Follow: __autoRemove: Mastodon error(Old user remove): " + wRes['Reason'] )
					return False
				
				self.VAL_FollowNum += 1
				wRemoveNum += 1
			
			if wRemoveNum>0 :
				### 自アカウントのフォロー一覧を再取得
				wRes = self.__get_FollowTL( self.Obj_Parent.ARR_MyAccountInfo['id'] )
				if wRes['Result']!=True :
					##失敗
					self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Follow: __autoRemove: Get follow list is failed(Old user remove): " + wRes['Reason'] )
					return False
				
				### 終わり
				wStr = "自動リムーブ: 一定期間活動のないユーザを処理しました: RemoveNum=" + str( wRemoveNum )
				self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr )
				return True	#リムーブした
		
		return False	#リムーブしてないので



#####################################################
# フォロー一覧取得・保存
#####################################################
	def Get_FollowLists(self):
		#############################
		# 読み出し先初期化
##		self.ARR_FollowTL = []
##		self.ARR_FollowerTL = []
		self.ARR_FollowTL   = {}
		self.ARR_FollowerTL = {}
		self.FLG_Update = False
		
		wARR_GetFile = []
		#############################
		# フォローファイル読み込み
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['FollowListFile']
##		if CLS_File.sReadFile( wFile_path, outLine=self.ARR_FollowTL )!=True :
		if CLS_File.sReadFile( wFile_path, outLine=wARR_GetFile )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Follow: Get_FollowLists: Get follow list file is failed: " + wFile_path )
			return False	#失敗
		###詰め込む
		for wLine in wARR_GetFile :
			if len(wLine)==0 :
				continue
			wLine = wLine.split( gVal.DEF_DATA_BOUNDARY )
			if len(wLine)!=2 :
				continue
			self.ARR_FollowTL.update({ wLine[1] : wLine[0] })
		
		wARR_GetFile = []
		#############################
		# フォロワーファイル読み込み
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['FollowerListFile']
##		if CLS_File.sReadFile( wFile_path, outLine=self.ARR_FollowerTL )!=True :
		if CLS_File.sReadFile( wFile_path, outLine=wARR_GetFile )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Follow: Get_FollowLists: Get follower list file is failed: " + wFile_path )
			return False	#失敗
		###詰め込む
		for wLine in wARR_GetFile :
			if len(wLine)==0 :
				continue
			wLine = wLine.split( gVal.DEF_DATA_BOUNDARY )
			if len(wLine)!=2 :
				continue
			self.ARR_FollowerTL.update({ wLine[1] : wLine[0] })
		
		#############################
		# 自動リムーブ
		self.__autoRemove()
		
		#############################
		# bot起動の最初か、1時間経っていればmastodonから取得する
		#  *** フォロー・フォロワーがいないと常に取りにいってしまう
		wARR_FollowList   = list( self.ARR_FollowTL )
		wARR_FollowerList = list( self.ARR_FollowerTL )
##		if len(self.ARR_FollowTL)>0 or len(self.ARR_FollowerTL)>0 :
##			if gVal.STR_TimeInfo['OneDay']==False :
		if len(wARR_FollowList)>0 or len(wARR_FollowerList)>0 :
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
		
		wARR_SetFile = []
		#############################
		# フォロー一覧
		wKeyList = list( self.ARR_FollowTL.keys() )
		for wUser in wKeyList :
			wLine = self.ARR_FollowTL[wUser] + gVal.DEF_DATA_BOUNDARY + wUser
			wARR_SetFile.append( wLine )
		
		#############################
		# フォローファイル書き込み (改行つき)
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['FollowListFile']
##		if CLS_File.sWriteFile( wFile_path, self.ARR_FollowTL, inRT=True )!=True :
		if CLS_File.sWriteFile( wFile_path, wARR_SetFile, inRT=True )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Follow: Set_FollowLists: Set follow list file is failed: " + wFile_path )
			return False	#失敗
		
		wARR_SetFile = []
		#############################
		# フォロワー一覧
		wKeyList = list( self.ARR_FollowerTL.keys() )
		for wUser in wKeyList :
			wLine = self.ARR_FollowerTL[wUser] + gVal.DEF_DATA_BOUNDARY + wUser
			wARR_SetFile.append( wLine )
		
		#############################
		# フォロワーファイル書き込み (改行つき)
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['FollowerListFile']
##		if CLS_File.sWriteFile( wFile_path, self.ARR_FollowerTL, inRT=True )!=True :
		if CLS_File.sWriteFile( wFile_path, wARR_SetFile, inRT=True )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Follow: Set_FollowLists: Set follower list file is failed: " + wFile_path )
			return False	#失敗
		
		wStr = "フォローリスト更新あり: follow=" + str(len(self.ARR_FollowTL)) + " follower=" + str(len(self.ARR_FollowerTL))
		self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr )
		return True			#成功



	#####################################################
	def __get_FollowTL( self, inMyID):
##		self.ARR_FollowTL = []
		self.ARR_FollowTL = {}
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
##			self.ARR_FollowTL.append( wFulluser['Fulluser'] )
			self.ARR_FollowTL.update({ wFulluser['Fulluser'] : str(wAccount['id']) })
		
		return wRes

	#####################################################
	def __get_FollowerTL( self, inMyID ):
##		self.ARR_FollowerTL = []
		self.ARR_FollowerTL = {}
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
##			self.ARR_FollowerTL.append( wFulluser['Fulluser'] )
			self.ARR_FollowerTL.update({ wFulluser['Fulluser'] : str(wAccount['id']) })
		
		return wRes



