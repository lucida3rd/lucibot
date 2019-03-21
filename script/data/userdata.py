#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ユーザデータ
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/13
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   ViewUserList(self):
#
# Class Function(static):
#   sGetUserList(cls):
#   sGetUserPath( cls, inFulluser ):
#   sUserCheck( cls, inFulluser ):
#   sGetFulluser( cls, inUsername, inUrl ):
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

#####################################################
# Init
#####################################################
	def __init__(self):
		return



#####################################################
# 一覧表示
#   コンソールへの出力機能
#####################################################
	def ViewUserList( self, inMulticastList=[] ):
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
			
			#############################
			# PR Userフラグ
			if gVal.STR_MasterConfig['PRUser']==f :
				wStr = wStr + "P"
			else:
				wStr = wStr + " "
			
			#############################
			# 同報配信ユーザフラグ
			if f in inMulticastList :
				wStr = wStr + "M"
			else:
				wStr = wStr + " "
			
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
		if wUser[1] in gVal.STR_NoRegistDomain :
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
# 範囲の変換
#####################################################
	@classmethod
	def sGetRange( cls, inRange ):
		wKeylist = cls.STR_RANGE.keys()
		if inRange not in wKeylist :
			return cls.DEF_RANGE
		
		return cls.STR_RANGE[inRange]



