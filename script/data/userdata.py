#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ユーザデータ
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/11/19
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   __init__(self):
#   ViewUserList(self):
#
# Class Function(static):
#   sGetUserList(cls):
#   sGetUserPath( cls, inFulluser ):
#   sUserCheck( cls, inFulluser ):
#   sGetFulluser( cls, inUsername, inUrl ):
#   sCheckTrafficUser( cls, inUsername ):
#   sChangeTrafficUser( cls, inUsername ):
#   sGetTrafficUser(cls):
#   sGetRange( cls, inRange ):
#   sCheckRange( cls, inRange ):
#   sChkHitPatt( cls, inHitPatt, inPatt ):
#
#####################################################

from osif import CLS_OSIF
from filectrl import CLS_File
##from mastodon_use import CLS_Mastodon_Use
from gval import gVal
#####################################################
class CLS_UserData() :
#####################################################

	STR_RANGE = {
		"p"	:	"public",
		"u"	:	"unlisted",
		"l"	:	"private",
		"d"	:	"direct"
	}
	DEF_RANGE = "unlisted"

	##登録禁止サーバ(間違えやすいドメインとか)
	DEF_ARR_NO_REGISTDOMAIN = [
		"yahoo.co.jp",
		"ybb.ne.jp",
		"gmail.com",
		"outlook.jp",
		"outlook.com",
		"hotmail.co.jp",
		"live.jp",
		"(dummy)"
	]

#####################################################
# Init
#####################################################
	def __init__(self):
		return



#####################################################
# 一覧表示
#   コンソールへの出力機能
#####################################################
##	def ViewUserList( self, inMulticastList=[] ):
	def ViewUserList(self):
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ出力
		wStr = "--------------------" + '\n'
		wStr = wStr + " 登録ユーザ一覧" + '\n'
		wStr = wStr + "--------------------"
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# データフォルダの一覧(トップだけ)取得
		wList = self.sGetUserList()
		if len(wList)==0 :
			CLS_OSIF.sPrn( "ユーザ登録がありません" )
			return
		
##		#############################
##		# 同報配信設定ユーザ一覧の取得
##		wRes = self.GetMulticastUserList()
##		if wRes['Result']!=True :
##			CLS_OSIF.sPrn( wRes['Reason'] )
##			return
##		
##		wMulticastList = wRes['Responce']
		
		#############################
		# 表示
		wStr = ""
		for f in wList :
			#############################
			# MasterUserフラグ
			if gVal.STR_MasterConfig['MasterUser']==f :
				wStr = wStr + "*"
			else:
				wStr = wStr + " "
			
##			#############################
##			# PR Userフラグ
##			if gVal.STR_MasterConfig['PRUser']==f :
##				wStr = wStr + "P"
##			else:
##				wStr = wStr + " "
			
##			#############################
##			# 同報配信ユーザフラグ
##			if f in inMulticastList :
##				wStr = wStr + "M"
##			else:
##				wStr = wStr + " "
			
			#############################
			# ユーザ名
			wStr = wStr + " " + f + '\n'
		
		CLS_OSIF.sPrn( wStr )
		return



#####################################################
# ユーザ一覧取得
#####################################################
	@classmethod
	def sGetUserList(cls):
		wList = CLS_File.sLs( gVal.DEF_USERDATA_PATH )
		
		#############################
		# masterConfigを抜く
		if gVal.DEF_MASTERCONFIG_NAME in wList :
			wList.remove( gVal.DEF_MASTERCONFIG_NAME )
		
		return wList



#####################################################
# ユーザパス取得
#   Resultはフォルダがあるか、ないか
#####################################################
	@classmethod
	def sGetUserPath( cls, inFulluser ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# フォルダの存在チェック
		wFilename = gVal.DEF_USERDATA_PATH + inFulluser + "/"
##		if CLS_File.sExist( wFilename )!=True :
##			wRes['Reason'] = "CLS_UserData: sGetUserPath: User Folder is not found: " + wFilename
##			return wRes
		if CLS_File.sExist( wFilename )==True :
			wRes['Result'] = True
		
		wRes['Responce'] = wFilename
##		wRes['Result'] = True
		return wRes



#####################################################
# ユーザ名の妥当性チェック
#  and 重複チェック
#####################################################
	@classmethod
	def sUserCheck( cls, inFulluser ):
		
		#############################
		# 応答データ
		wRes = {
			"Result"	: False,
			"User"		: "",
			"Domain"	: "",
			"Reason"	: "",
			"Registed"	: False,
		}
		
		#############################
		# ユーザ名とドメイン名の分解＆チェック
		wUser = inFulluser.split("@")
		if len(wUser)!=2 :
			wRes['Reason'] = "ドメインを含めて入力してください: 例= " + gVal.DEF_EXAMPLE_ACCOUNT
			return wRes
		
		#############################
		# 禁止ドメインのチェック(たぶん入力間違え)
###		if wUser[1] in gVal.STR_NoRegistDomain :
		if wUser[1] in cls.DEF_ARR_NO_REGISTDOMAIN :
			wRes['Reason'] = "そのドメインは禁止されています。(or入力誤り)"
			return wRes
		
		#############################
		# チェックOK
		wRes['User']   = wUser[0]
		wRes['Domain'] = wUser[1]
		wRes['Result'] = True
		
		#############################
		# 重複チェック
		wRes['Registed'] = CLS_File.sFolderExist( gVal.DEF_USERDATA_PATH, inFulluser )
		return wRes



#####################################################
# ユーザ名の変換
#####################################################
	@classmethod
	def sGetFulluser( cls, inUsername, inUrl ):
		
		#############################
		# 応答データ
		wRes = {
			"Result"	: False,
			"Fulluser"	: "",
			"Username"	: "",
			"Domain"	: "",
			"Reason"	: ""
		}
		
		#############################
		# URLからドメインを取得
		wIndex  = inUrl.find('/@')
		wDomain = inUrl[8:wIndex]
		# https://
		wIndex = wDomain.find('/')
		if wIndex>=0 :
			wDomain = wDomain[0:wIndex]
		
		#############################
		# 返す
		wRes['Fulluser'] = inUsername + '@' + wDomain
		wRes['Username'] = inUsername
		wRes['Domain']   = wDomain
		wRes['Result']   = True
		return wRes



#####################################################
# トラヒックユーザ チェック
#####################################################
	@classmethod
	def sCheckTrafficUser( cls, inUsername ):
		#############################
		# 名前の妥当性チェック
		wResUser = cls.sUserCheck( inUsername )
			##	"Result"	: False,
			##	"User"		: "",
			##	"Domain"	: "",
			##	"Reason"	: "",
			##	"Registed"	: False,
		if wResUser['Result']!=True :
			return False	#不正
		
		#############################
		# 読み出し先初期化
		wTrafficUser = []
		
		#############################
		# ファイル読み込み
		wFile_path = gVal.DEF_STR_FILE['TrafficFile']
		if CLS_File.sReadFile( wFile_path, outLine=wTrafficUser )!=True :
			return False	#失敗
		
		#############################
		# 対象ユーザか
		if inUsername in wTrafficUser :
			return True	#対象外
		
		return False		#対象ではない



#####################################################
# ハード監視ユーザ チェック
#####################################################
	@classmethod
	def sCheckHardUser( cls, inUsername ):
		#############################
		# ハード監視対象ユーザ
		#   ・トラヒック監視ユーザの1番目か
		#   ・1番目がMasuerUserの場合は2番目か
		
		#############################
		# 名前の妥当性チェック
		wResUser = cls.sUserCheck( inUsername )
			##	"Result"	: False,
			##	"User"		: "",
			##	"Domain"	: "",
			##	"Reason"	: "",
			##	"Registed"	: False,
		if wResUser['Result']!=True :
			return False	#不正
		
		#############################
		# 読み出し先初期化
		wTrafficUser = []
		
		#############################
		# ファイル読み込み
		wFile_path = gVal.DEF_STR_FILE['TrafficFile']
		if CLS_File.sReadFile( wFile_path, outLine=wTrafficUser )!=True :
			return False	#失敗
		
		#############################
		# 何番目かをIndexで取得する
		wI = 0
		wIndex = -1
		for wUser in wTrafficUser :
			if inUsername==wUser :
				wIndex = wI
				break
			wI += 1
##		if wIndex==-1 :
##			return False	#トラヒックユーザではない
##		
##		#############################
##		# 1番目でSubUserの場合は確定
##		if wIndex==0 :
##			if gVal.STR_MasterConfig['MasterUser']!=wTrafficUser[0] :
##				return True	#確定
##		
##		#############################
##		# 2番目であれば確定
##		#   *この時点で1番目はMasterUserなので
##		if wIndex==1 :
##			return True	#確定
##		
		#############################
		# トラヒックユーザの登録がある場合
		if len(wTrafficUser)>0 :
			if wIndex==-1 :
				return False	#トラヒックユーザではない
			
			#############################
			# 1番目がSubUser かつ対象の場合 =確定
			if gVal.STR_MasterConfig['MasterUser']!=wTrafficUser[0] and \
			   wTrafficUser[0] == inUsername :
				return True	#確定
			
			#############################
			# 1番目がMasterUser かつ自分が2番目だった場合 =確定
			elif gVal.STR_MasterConfig['MasterUser']==wTrafficUser[0] and \
			     wTrafficUser[1] == inUsername :
				return True	#確定
		
		#############################
		# その他で自分がMasterUserだった場合 =確定
		else :
			if gVal.STR_MasterConfig['MasterUser']==inUsername :
				return True	#確定
		
		return False		#対象ではない



#####################################################
# トラヒックユーザ取得
#####################################################
	@classmethod
	def sGetTrafficUser(cls):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# 読み出し先初期化
		wTrafficUser = []
		
		#############################
		# ファイル読み込み
		wFile_path = gVal.DEF_STR_FILE['TrafficFile']
		if CLS_File.sReadFile( wFile_path, outLine=wTrafficUser )!=True :
			return wRes	#失敗
		
		wRes['Responce'] = wTrafficUser
		wRes['Result']   = True
		return wRes	#OK



#####################################################
# トラヒックユーザ切替
#   入力ユーザが計測ユーザの場合、同一ドメインの別ユーザに切り替える
#####################################################
	@classmethod
	def sChangeTrafficUser( cls, inUsername ):
		#############################
		# 名前の妥当性チェック
		wResUser = cls.sUserCheck( inUsername )
			##	"Result"	: False,
			##	"User"		: "",
			##	"Domain"	: "",
			##	"Reason"	: "",
			##	"Registed"	: False,
		if wResUser['Result']!=True :
			return False	#不正
		
		#############################
		# 読み出し先初期化
		wTrafficUser = []
		
		#############################
		# ファイル読み込み
		wFile_path = gVal.DEF_STR_FILE['TrafficFile']
		if CLS_File.sReadFile( wFile_path, outLine=wTrafficUser )!=True :
			return False	#失敗
		
		#############################
		# 計測ユーザか
		if inUsername not in wTrafficUser :
			return True	#対象外
		
		##自分は抜いておく
		wTrafficUser.remove( inUsername )
		
		#############################
		# 同一ドメインの別ユーザを検索
		wUserList = cls.sGetUserList()
		wNewUser  = None
		for wLine in wUserList :
			if wLine==inUsername :
				continue	#自分は除く
			
			wDomain = wLine.split("@")
			if wDomain[1]==wResUser['Domain'] :
				wNewUser = wLine
				break
		
		if wNewUser==None :
			##ありえない
			return False
		
		#############################
		# 切替
		wTrafficUser.append( wNewUser )
		
		#############################
		# ファイル書き込み (改行つき)
		wFile_path = gVal.DEF_STR_FILE['TrafficFile']
		if CLS_File.sWriteFile( wFile_path, wTrafficUser, inRT=True )!=True :
			return False	#失敗
		
		return True	#正常



#####################################################
# 範囲の変換
#####################################################
	@classmethod
	def sGetRange( cls, inRange ):
		wKeylist = cls.STR_RANGE.keys()
		if inRange not in wKeylist :
			return cls.DEF_RANGE
		
		return cls.STR_RANGE[inRange]



#####################################################
# 範囲チェック
#####################################################
	@classmethod
	def sCheckRange( cls, inRange ):
		wKeylist = cls.STR_RANGE.keys()
		for wKey in wKeylist :
			if cls.STR_RANGE[wKey]==inRange :
				return True
		
		return False



#####################################################
# ヒットチェック
#####################################################
##	@classmethod
##	def sChkHitPatt( cls, inHitPatt, inPatt ):
##		wFlg = False
##		for patt in inHitPatt:
##			if patt == inPatt:
##				wFlg = True
##				break
##		
##		return wFlg



