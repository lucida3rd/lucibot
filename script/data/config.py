#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：環境設定処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/5/6
#####################################################
# Private Function:
#   __cnfMasterConfig_SelectDisp(self):
#   __cnfMasterConfig_Change(self):
#   __cnfMasterUser( self, inFulluser ):
#
# Instance Function:
#   MasterConfig_Disp(self):
#   CnfMasterConfig(self):
#   CnfMasterUser(self):
#   CnfAdminUser(self):
#   CnfMasterRun(self):
#   CnfMasterMainte(self):
#   GetMulticastUserList(self):
#
# Class Function(static):
#   sGetMasterConfig(cls):
#   sSetMasterConfig(cls):
#   sGetMulticast( cls, inPath ):
#
#####################################################

from osif import CLS_OSIF
from filectrl import CLS_File
from userdata import CLS_UserData
##from mastodon_use import CLS_Mastodon_Use
from gval import gVal
#####################################################
class CLS_Config() :
#####################################################

	#############################
	# 画面表示するMaster環境情報
	#   True=一括設定変更可能
	#   False=別画面で設定
	STR_View_masterConf = {
		"MasterUser"	: False,
		"AdminUser"		: False,
		"PRUser"		: False,
		
		"mTootTag"		: False,
		"iFavoTag"		: False,
		"prTag"			: False,
		
		"TwitterUser"	: False,
		"Twitter"		: True,
		"PTL_Favo"		: True,
		"PTL_Boot"		: True,
		"PTL_HRip"		: True,
		"PTL_ARip"		: True,
		"PTL_WordOpe"	: True,
		"RandToot"		: True,
		"CircleToot"	: True,
		"Traffic"		: True,
		"LookHard"		: True,
		"WordStudy"		: True,
		"LogLevel"		: True
##		"Lock"			: True,
##		"mMainte"		: False
	}

	__DEF_VIEW_MASTERCONF_LEN = 12

	#############################
	# 画面表示するUser環境情報
	#   True=一括設定変更可能
	#   False=別画面で設定
	STR_View_userConf = {
		"Multicast"		: True,
		"RIP_Favo"		: True,
		"IND_Favo"		: True,
		"IND_Favo_CW"	: True,
		"IND_Follow"	: True,
		"HTL_Boost"		: True,
##		"TrafficCnt"	: True,
##		"WordCorrect"	: True,
		"AutoFollow"	: False,
##		"Mainte"		: False,
		"JPonly"		: True
	}

	__DEF_VIEW_USERCONF_LEN = 12

#####################################################
# Init
#####################################################
	def __init__(self):
		return



#####################################################
# Master環境情報の読み込み
#####################################################
	@classmethod
	def sGetMasterConfig(cls):
		#############################
		# ファイルの存在チェック
		if CLS_File.sExist( gVal.STR_File['MasterConfig'] )!=True :
			return False	#ない
		
		#############################
		# 読み込み
		for wLine in open( gVal.STR_File['MasterConfig'], 'r'):
			#############################
			# 分解+要素数の確認
			wLine = wLine.strip()
			wGet_Line = wLine.split("=")
			if len(wGet_Line) != 2 :
				continue
			
			#############################
			# キーがあるか確認
			if wGet_Line[0] not in gVal.STR_MasterConfig :
				continue
			
			#############################
			# 更新する
			gVal.STR_MasterConfig[wGet_Line[0]] = wGet_Line[1]
		
		#############################
		# 文字→数値へ変換
		gVal.STR_MasterConfig["getPTLnum"]    = int( gVal.STR_MasterConfig["getPTLnum"] )
		gVal.STR_MasterConfig["getRandVal"]   = int( gVal.STR_MasterConfig["getRandVal"] )
		gVal.STR_MasterConfig["getRandRange"] = int( gVal.STR_MasterConfig["getRandRange"] )
		gVal.STR_MasterConfig["studyNum"]     = int( gVal.STR_MasterConfig["studyNum"] )
		gVal.STR_MasterConfig["studyMax"]     = int( gVal.STR_MasterConfig["studyMax"] )
		gVal.STR_MasterConfig["studyDay"]     = int( gVal.STR_MasterConfig["studyDay"] )
		gVal.STR_MasterConfig["clazListNum"]  = int( gVal.STR_MasterConfig["clazListNum"] )
		gVal.STR_MasterConfig["getMcDelay"]   = int( gVal.STR_MasterConfig["getMcDelay"] )
		
		#############################
		# 数値補正
		if gVal.STR_MasterConfig["getMcDelay"]<1 or gVal.STR_MasterConfig["getMcDelay"]>30 :
			gVal.STR_MasterConfig["getMcDelay"] = 5
		
		return True



#####################################################
# Master環境情報の書き込み
#####################################################
	@classmethod
	def sSetMasterConfig(cls):
		#############################
		# 書き込みデータを作成
		wSetLine = []
		wKeylist = gVal.STR_MasterConfig.keys()
		for iKey in wKeylist :
			wLine = iKey + "=" + str(gVal.STR_MasterConfig[iKey]) + '\n'
			wSetLine.append(wLine)
		
		#############################
		# ファイル上書き書き込み
		if CLS_File.sWriteFile( gVal.STR_File['MasterConfig'], wSetLine )!=True :
			return False	#失敗
		
		return True



#####################################################
# Master環境情報 表示
#####################################################
	def MasterConfig_Disp(self):
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ出力
		wStr = "--------------------" + '\n'
		wStr = wStr + " Master環境情報" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
		wKeylist = self.STR_View_masterConf.keys()
		for iKey in wKeylist :
			wLen = len(iKey)
			if self.__DEF_VIEW_MASTERCONF_LEN>wLen :
				wKeyname = iKey + ( " " * ( self.__DEF_VIEW_MASTERCONF_LEN-wLen ))
			else :
				wKeyname = iKey
			
			wNum = str(gVal.STR_MasterConfig[iKey])
			if wNum=="" :
				wNum = "(None)"
			
			wStr = wStr + wKeyname + " : " + wNum + '\n'
		
		CLS_OSIF.sPrn( wStr )
		return



#####################################################
# Master環境情報 操作
#####################################################
	def CnfMasterConfig(self):
		#############################
		# ファイルの存在チェック
		if CLS_File.sExist( gVal.STR_File['MasterConfig'] )!=True :
			###ありえない
			CLS_OSIF.sPrn( "CLS_Config: CnfMasterConfig: MasterConfig file is not found : " + gVal.STR_File['MasterConfig'] )
			return False	#ない
		
		#############################
		# 選択画面を表示する
		self.MasterConfig_Disp()
		wSelect = self.__cnfMasterConfig_SelectDisp()
		if wSelect=='c' :
			###変更してセーブ
			self.__cnfMasterConfig_Change()
			self.sSetMasterConfig()
			CLS_OSIF.sPrn( "変更した内容でMaster環境情報をセーブしました。" + '\n' )
		elif wSelect=='s' :
			###セーブ
			CLS_Config.sSetMasterConfig()
			CLS_OSIF.sPrn( "Master環境情報をセーブしました。" + '\n' )
		
		return True

	#####################################################
	# 選択メニュー表示
	#####################################################
	def __cnfMasterConfig_SelectDisp(self):
		wStr = "操作メニューキーを押してください" + '\n'
		wStr = wStr + "c: 変更 / s:セーブ+終了 / other:なにもせず終了"
		CLS_OSIF.sPrn( wStr )
		wSelect = CLS_OSIF.sInp( "選択？=> " )
		return wSelect

	#####################################################
	# 変更メニュー表示
	#####################################################
	def __cnfMasterConfig_Change(self):
		wKeylist = self.STR_View_masterConf.keys()
		for iKey in wKeylist :
			#############################
			# 表示しないメニューは排除
			if iKey=='Twitter' and gVal.STR_MasterConfig['twAS']=="" :
				###twitterのキー設定がされていなければメニューを出さない
				gVal.STR_MasterConfig[iKey] = "off"
				continue
			
			if self.STR_View_masterConf[iKey]==False :
				###これらは別メニューで変更させる
				continue
			
			#############################
			# ON/OFFの文字作成
			wStr = iKey + "= " + str( gVal.STR_MasterConfig[iKey]) + " : "
			if gVal.STR_MasterConfig[iKey]=="on" :
				wStr = wStr + "c: on→off"
				wChg = "off"
			else:
				wStr = wStr + "c: off→on"
				wChg = "on"
			
			wStr = wStr + " / other: 変更しない"
			
			#############################
			# 変更メニューの表示
			CLS_OSIF.sPrn( wStr )
			wSelect = CLS_OSIF.sInp( "選択? => " )
			
			if wSelect=="c" :
				###変更する
				gVal.STR_MasterConfig[iKey] = wChg
		
		#############################
		# タグの変更
		wStr = "mTootTag= " + str( gVal.STR_MasterConfig["mTootTag"]) + " : "
		wStr = wStr + "c: 変更する / othwe: 変更しない"
		CLS_OSIF.sPrn( wStr )
		wSelect = CLS_OSIF.sInp( "選択? => " )
		if wSelect=="c" :
			###変更する
			wTag = CLS_OSIF.sInp( "タグ? => " )
			if CLS_OSIF.sChkREMString( wTag )==True :
				gVal.STR_MasterConfig["mTootTag"] = wTag
		
		wStr = "iFavoTag= " + str( gVal.STR_MasterConfig["iFavoTag"]) + " : "
		wStr = wStr + "c: 変更する / othwe: 変更しない"
		CLS_OSIF.sPrn( wStr )
		wSelect = CLS_OSIF.sInp( "選択? => " )
		if wSelect=="c" :
			###変更する
			wTag = CLS_OSIF.sInp( "タグ? => " )
			if CLS_OSIF.sChkREMString( wTag )==True :
				gVal.STR_MasterConfig["iFavoTag"] = wTag
		
		wStr = "prTag= " + str( gVal.STR_MasterConfig["prTag"]) + " : "
		wStr = wStr + "c: 変更する / othwe: 変更しない"
		CLS_OSIF.sPrn( wStr )
		wSelect = CLS_OSIF.sInp( "選択? => " )
		if wSelect=="c" :
			###変更する
			wTag = CLS_OSIF.sInp( "タグ? => " )
			if CLS_OSIF.sChkREMString( wTag )==True :
				gVal.STR_MasterConfig["prTag"] = wTag
		
		return



#####################################################
# MasterUser変更(botとして使うユーザ)
#####################################################
	def CnfMasterUser( self ):
		#############################
		# ユーザ一覧の取得
		wList = CLS_UserData.sGetUserList()
		
		#############################
		# 0件の場合は、ユーザ登録させる
		if len(wList)==0 :
			wStr = "ユーザが1件も登録されていないため、MasterUserの登録ができません。" + '\n'
			wStr = wStr + "まずはユーザ登録をおこなってください。" + '\n'
			CLS_OSIF.sPrn( wStr )
			return False
		
		#############################
		# 1件しかない場合かつMasterUser登録済みの場合は変更できない
		elif len(wList)==1 and gVal.STR_MasterConfig['MasterUser']!="" :
			wStr = "ユーザが1件しか登録されていないため、MasterUserの変更はできません。" + '\n'
			wStr = wStr + "現在のMasterUser: " + gVal.STR_MasterConfig['MasterUser'] + '\n'
			CLS_OSIF.sPrn( wStr )
			return False
		
		#############################
		# 1件しかない場合かつMasterUserが未登録の場合は、
		# その1件をMasterUserに設定してしまう
		elif len(wList)==1 :
			wStr = "ユーザが1件しか登録されていないため " + wList[0] + " をMasterUserに設定します。"  + '\n'
			CLS_OSIF.sPrn( wStr )
			wRes = self.__cnfMasterUser( wList[0] )
			return wRes
		
		#############################
		# 2件以上の場合は選択する
		else :
			#############################
			# ユーザ一覧の表示
			wCLS_work = CLS_UserData()
			wCLS_work.ViewUserList()
			
			#############################
			# 登録画面
			wStr = "現在MasterUserに設定されているユーザは次のユーザです。: " + gVal.STR_MasterConfig['MasterUser'] + '\n'
			wStr = wStr + "MasterUser(mastodon上でbotとして使うユーザ)をドメインを含めて入力してください。 例= " + gVal.DEF_EXAMPLE_ACCOUNT
			CLS_OSIF.sPrn( wStr )
			wMasterUser = CLS_OSIF.sInp( "MasterUser？ => " )
			
			wFLG = False
			for iKey in wList :
				if wMasterUser==iKey :
					wFLG = True
			
			if wFLG!=True :
				CLS_OSIF.sPrn( "登録されていないユーザです。変更をキャンセルします。" )
				return False
			
			wRes = self.__cnfMasterUser( wMasterUser )
			if wRes!=True :
				return False
		
		return True

	#####################################################
	# MasterUser変更
	#####################################################
	def __cnfMasterUser( self, inFulluser ):
		#############################
		# 変更＆反映
		gVal.STR_MasterConfig['MasterUser'] = inFulluser 
		wRes = self.sSetMasterConfig()
		if wRes!=True :
			return False
		
		wStr = inFulluser + " をMasterUserに設定しました。" + '\n'
		wStr = wStr + "このユーザをmastodon上でbotとして動作させます。" + '\n'
		wStr = wStr + "Master環境情報をセーブしました: " + gVal.STR_File['MasterConfig'] + '\n'
		CLS_OSIF.sPrn( wStr )
		CLS_OSIF.sInp( "確認したらリターンキーを押してください。[RT]" )
		return True



#####################################################
# AdminUser変更(通知先ユーザ)
#####################################################
	def CnfAdminUser(self):
		#############################
		# ファイルの存在チェック
		if CLS_File.sExist( gVal.STR_File['MasterConfig'] )!=True :
			###ありえない
			CLS_OSIF.sPrn( "CLS_Config: cCnfAdminUser: masterConfig file is not found : " + gVal.STR_File['MasterConfig'] )
			return False	#ない
		
		#############################
		# 変更メニュー表示
		if gVal.STR_MasterConfig['AdminUser']=="" :
			wStr = "現在AdminUserは設定されていません。設定することで登録ユーザから通知を受け取ることができるようになります。"
			wSt2 = "AdminUserの設定をおこないますか？(y/N)=> "
		else :
			wStr = "現在AdminUserは次のアカウントが設定されています。: " + gVal.STR_MasterConfig['AdminUser']
			wSt2 = "AdminUserの設定をおこないますか？(y:変更 /D:解除 /other: キャンセル)=> "
		
		CLS_OSIF.sPrn( wStr )
		wSelect = CLS_OSIF.sInp( wSt2 )
		if wSelect=="D" :
			###削除
			gVal.STR_MasterConfig['AdminUser'] = ""
			self.sSetMasterConfig()
			CLS_OSIF.sPrn( "AdminUserの設定を解除しました。" + '\n' )
			CLS_OSIF.sPrn( "設定内容をMaster環境情報にセーブしました: " + gVal.STR_File['MasterConfig'] + '\n' )
			return True
		elif wSelect!="y" :
			###設定しない
			CLS_OSIF.sPrn( "キャンセルされました" )
			return True
		
		#############################
		# 名前入力
		wStr = "AdminUser(通知先アカウント)をドメインを含めて入力してください。 例= " + gVal.DEF_EXAMPLE_ACCOUNT + '\n'
		wStr = wStr + "  ※ユーザ登録してないユーザも指定できます"
		CLS_OSIF.sPrn( wStr )
		wAdminUser = CLS_OSIF.sInp("AdminUser？ => ")
		if wAdminUser=="" or \
		   gVal.STR_MasterConfig['AdminUser'] ==wAdminUser :
			###設定しない
			CLS_OSIF.sPrn( "キャンセルされました" )
			return True
		
		#############################
		# ユーザ名の妥当性チェック
		wSTR_user = CLS_UserData.sUserCheck( wAdminUser )
		if wSTR_user['Result']!=True :
			return False
		
		#############################
		# 通信テスト
		CLS_OSIF.sPrn( "通信テスト中..." )
		if CLS_OSIF.sPing( wSTR_user['Domain'] )!=True :
			CLS_OSIF.sPrn( "mastodonとの通信テストに失敗したため、設定をキャンセルします。" )
			return False
		
		CLS_OSIF.sPrn( "通信OK" )
		
		#############################
		# 変更
		gVal.STR_MasterConfig['AdminUser'] = wAdminUser
		self.sSetMasterConfig()
		CLS_OSIF.sPrn( "設定内容をMaster環境情報にセーブしました: " + gVal.STR_File['MasterConfig'] + '\n' )
		return True



#####################################################
# PR User変更(宣伝ユーザ)
#####################################################
	def CnfPRUser(self):
		#############################
		# ファイルの存在チェック
		if CLS_File.sExist( gVal.STR_File['MasterConfig'] )!=True :
			###ありえない
			CLS_OSIF.sPrn( "CLS_Config: CnfPRUser: masterConfig file is not found : " + gVal.STR_File['MasterConfig'] )
			return False	#ない
		
		#############################
		# 変更メニュー表示
		if gVal.STR_MasterConfig['PRUser']=="" :
			wStr = "現在PR Userは設定されていません。設定することで登録ユーザから通知を受け取ることができるようになります。"
			wSt2 = "PR Userの設定をおこないますか？(y/N)=> "
		else :
			wStr = "現在PR Userは次のアカウントが設定されています。: " + gVal.STR_MasterConfig['PRUser']
			wSt2 = "PR Userの設定をおこないますか？(y:変更 /D:解除 /other: キャンセル)=> "
		
		CLS_OSIF.sPrn( wStr )
		wSelect = CLS_OSIF.sInp( wSt2 )
		if wSelect=="D" :
			###削除
			gVal.STR_MasterConfig['PRUser'] = ""
			self.sSetMasterConfig()
			CLS_OSIF.sPrn( "PR Userの設定を解除しました。" + '\n' )
			CLS_OSIF.sPrn( "設定内容をMaster環境情報にセーブしました: " + gVal.STR_File['MasterConfig'] + '\n' )
			return True
		elif wSelect!="y" :
			###設定しない
			CLS_OSIF.sPrn( "キャンセルされました" )
			return True
		
		#############################
		# 名前入力
		wStr = "PR User(宣伝アカウント)をドメインを含めて入力してください。 例= " + gVal.DEF_EXAMPLE_ACCOUNT + '\n'
		wStr = wStr + "  ※ユーザ登録している、MasterUser以外のユーザを指定できます"
		CLS_OSIF.sPrn( wStr )
		wPRUser = CLS_OSIF.sInp("PR User？ => ")
		if wPRUser=="" or \
		   gVal.STR_MasterConfig['PRUser'] ==wPRUser :
			###設定しない
			CLS_OSIF.sPrn( "キャンセルされました" )
			return True
		
		if wPRUser==gVal.STR_MasterConfig['MasterUser'] :
			###設定しない
			CLS_OSIF.sPrn( "MasterUserは指定できません。キャンセルします。" )
			return True
		
		# ユーザ一覧の取得
		wList = CLS_UserData.sGetUserList()
		if wPRUser not in wList :
			###設定しない
			CLS_OSIF.sPrn( "登録されていないユーザは設定できません。キャンセルします。" )
			return True
		
		#############################
		# 変更
		gVal.STR_MasterConfig['PRUser'] = wPRUser
		self.sSetMasterConfig()
		CLS_OSIF.sPrn( "設定内容をMaster環境情報にセーブしました: " + gVal.STR_File['MasterConfig'] + '\n' )
		return True



#####################################################
# master運用操作
#####################################################
	def CnfMasterRun(self):
		#############################
		# ファイルの存在チェック
		if CLS_File.sExist( gVal.STR_File['MasterConfig'] )!=True :
			###ありえない
			CLS_OSIF.sPrn( "CLS_Config: cCnfMasterRun: masterConfig file is not found : " + gVal.STR_File['MasterConfig'] )
			return False	#ない
		
		#############################
		# メニューの表示
		wStr = '\n' + "botの運用を設定します。現在の設定。 mRun= " + gVal.STR_MasterConfig['mRun']
		CLS_OSIF.sPrn( wStr )
		
		wStr = ""
		if gVal.STR_MasterConfig['mRun']=="on" :
			wStr = wStr + "c: on→off"
			wChg = "off"
		else:
			wStr = wStr + "c: off→on"
			wChg = "on"
		
		wStr = wStr + " / other: 変更しない => "
		wSelect = input( wStr )
		
		if wSelect!="c" :
			###変更しない
			CLS_OSIF.sPrn( "キャンセルされました" )
			return True
		
		#############################
		# 変更
		gVal.STR_MasterConfig['mRun'] = wChg
		self.sSetMasterConfig()
		
		wStr = "botの運用設定を変更しました。 mRun= " + wChg + '\n'
		wStr = wStr + "変更した内容でMaster環境情報をセーブしました: " + gVal.STR_File['MasterConfig'] + '\n'
		CLS_OSIF.sPrn( wStr )
		return True



#####################################################
# masterメンテ操作
#####################################################
##	def CnfMasterMainte(self):
##		#############################
##		# ファイルの存在チェック
##		if CLS_File.sExist( gVal.STR_File['MasterConfig'] )!=True :
##			###ありえない
##			CLS_OSIF.sPrn( "CLS_Config: cCnfMasterMainte: masterConfig file is not found : " + gVal.STR_File['MasterConfig'] )
##			return False	#ない
##		
##		#############################
##		# メニューの表示
##		wStr = '\n' + "botをメンテナンス設定します。現在の設定。 mMainte= " + gVal.STR_MasterConfig['mMainte']
##		CLS_OSIF.sPrn( wStr )
##		
##		wStr = ""
##		if gVal.STR_MasterConfig['mMainte']=="on" :
##			wStr = wStr + "c: on→off"
##			wChg = "off"
##		else:
##			wStr = wStr + "c: off→on"
##			wChg = "on"
##		
##		wStr = wStr + " / other: 変更しない => "
##		wSelect = input( wStr )
##		
##		if wSelect!="c" :
##			###変更しない
##			CLS_OSIF.sPrn( "キャンセルされました" )
##			return True
##		
##		#############################
##		# 変更
##		gVal.STR_MasterConfig['mMainte'] = wChg
##		self.sSetMasterConfig()
##		
##		wStr = "botをメンテナンス設定を変更しました。 mMainte= " + wChg + '\n'
##		wStr = wStr + "変更した内容でMaster環境情報をセーブしました: " + gVal.STR_File['MasterConfig'] + '\n'
##		CLS_OSIF.sPrn( wStr )
##		return True



#####################################################
# User環境情報の読み込み
#####################################################
	@classmethod
	def sGetUserConfig( cls, inFulluser ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# ファイルパスの存在チェック
		wGetRes = CLS_UserData.sGetUserPath( inFulluser )
##		if wGetRes['Result']!=True :
##			wRes['Reason'] = wGetRes['Reason']
##			return wRes	#失敗
		
		wFilename = wGetRes['Responce'] + gVal.STR_File['UserConfig']
		if CLS_File.sExist( wFilename )!=True :
			wRes['Reason'] = "CLS_Config: sGetUserConfig: Can't find Config file: " + wFilename
			return wRes
		
		#############################
		# 初期化 onのところは全てoff (新要素対策)
		wKeylist = list(gVal.STR_Config.keys())
		for wKey in wKeylist :
			if gVal.STR_Config[wKey] == "on" :
				gVal.STR_Config[wKey] = "off"
		
		#############################
		# 読み込み
		for wLine in open( wFilename, 'r'):
			#############################
			# 分解+要素数の確認
			wLine = wLine.strip()
			wGet_Line = wLine.split("=")
			if len(wGet_Line) != 2 :
				continue
			
			#############################
			# キーがあるか確認
			if wGet_Line[0] not in gVal.STR_Config :
				continue
			
			#############################
			# 更新する
			gVal.STR_Config[wGet_Line[0]] = wGet_Line[1]
		
		#############################
		# 文字→数値へ変換
		gVal.STR_Config["getLTLnum"] = int( gVal.STR_Config["getLTLnum"] )
		gVal.STR_Config["getRIPnum"] = int( gVal.STR_Config["getRIPnum"] )
		gVal.STR_Config["reaRIPmin"] = int( gVal.STR_Config["reaRIPmin"] )
		gVal.STR_Config["getHTLnum"] = int( gVal.STR_Config["getHTLnum"] )
		gVal.STR_Config["getFollowMnum"] = int( gVal.STR_Config["getFollowMnum"] )
		gVal.STR_Config["indLimmin"] = int( gVal.STR_Config["indLimmin"] )
		gVal.STR_Config["indLimcnt"] = int( gVal.STR_Config["indLimcnt"] )
		
		wRes['Responce'] = wFilename
		wRes['Result'] = True
		return wRes



#####################################################
# User環境情報の書き込み
#####################################################
	@classmethod
	def sSetUserConfig( cls, inFulluser ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# ファイルパスの存在チェック
		wGetRes = CLS_UserData.sGetUserPath( inFulluser )
##		if wGetRes['Result']!=True :
##			wRes['Reason'] = wGetRes['Reason']
##			return wRes	#失敗
		
		wFilename = wGetRes['Responce'] + gVal.STR_File['UserConfig']
		if CLS_File.sExist( wFilename )!=True :
			wRes['Reason'] = "CLS_Config: sSetUserConfig: Can't find Config file: " + wFilename
			return wRes
		
		#############################
		# 書き込みデータを作成
		wSetLine = []
		wKeylist = gVal.STR_Config.keys()
		for iKey in wKeylist :
			wLine = iKey + "=" + str(gVal.STR_Config[iKey]) + '\n'
			wSetLine.append(wLine)
		
		#############################
		# ファイル上書き書き込み
		if CLS_File.sWriteFile( wFilename, wSetLine )!=True :
			return False	#失敗
		
		wRes['Result'] = True
		return wRes



#####################################################
# User環境情報 表示
#####################################################
	def UserConfig_Disp( self, inFulluser=None ):
		#############################
		# ユーザ名がない場合、名前を入力する
		if inFulluser==None :
			wStr = "表示するユーザ名をドメインを含めて入力してください。 例= " + gVal.DEF_EXAMPLE_ACCOUNT
			CLS_OSIF.sPrn( wStr )
			inFulluser = CLS_OSIF.sInp( "\\q:戻る / User？=> " )
##			if inFulluser=="\q" :
			if inFulluser.find("\\q")>=0 :
				return True
		
		#############################
		# Configファイル読み込み
		wRes = self.sGetUserConfig( inFulluser )
		if wRes['Result']!=True :
			CLS_OSIF.sPrn( "指定のユーザは登録されていません。: " + wRes['Reason'] )
			return False
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ出力
		wStr = "--------------------" + '\n'
		wStr = wStr + " User環境情報" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
		wStr = wStr + "User : " + inFulluser + '\n'
		wKeylist = self.STR_View_userConf.keys()
		for iKey in wKeylist :
			wLen = len(iKey)
			if self.__DEF_VIEW_USERCONF_LEN>wLen :
				wKeyname = iKey + ( " " * ( self.__DEF_VIEW_USERCONF_LEN-wLen ))
			else :
				wKeyname = iKey
			
			wStr = wStr + wKeyname + " : " + str(gVal.STR_Config[iKey]) + '\n'
		
		CLS_OSIF.sPrn( wStr )
		return True

	#############################
	# 一覧 (CLS_Config専用)
	def __userList(self):
		wList = CLS_UserData.sGetUserList()
		if len(wList)==0 :
			CLS_OSIF.sInp( "ユーザの登録がありません。[RT]" )
			return
		
		wStr = '\n' + "ユーザ一覧" + '\n'
		for iKey in wList :
			wStr = wStr + iKey + '\n'
		
		CLS_OSIF.sPrn( wStr )
		CLS_OSIF.sInp( "ユーザ一覧を出力しました。[RT]" )
		return



#####################################################
# User環境情報 操作
#####################################################
	def CnfUserConfig(self):
		while True:
			#############################
			# ユーザ名がない場合、名前を入力する
			wStr = "変更操作するユーザ名をドメインを含めて入力してください。 例= " + gVal.DEF_EXAMPLE_ACCOUNT
			CLS_OSIF.sPrn( wStr )
			inFulluser = CLS_OSIF.sInp( "\\q:戻る / \\l:一覧 / User？=> " )
##			if inFulluser=="\q" :	#終了
			if inFulluser.find("\\q")>=0 :	#終了
				break
##			elif inFulluser=="\l" :	#終了
			elif inFulluser.find("\\l")>=0 :	#終了
				self.__userList()
				continue
			
			#############################
			# ファイル読み込み＆選択画面を表示する
			wRes = self.UserConfig_Disp( inFulluser )
			if wRes!=True :
				continue
			
			wSelect = self.__cnfUserConfig_SelectDisp()
			if wSelect=="c" :
				###変更してセーブ
				self.__cnfUserConfig_Change()
				self.sSetUserConfig( inFulluser )
				CLS_OSIF.sPrn( "変更した内容でUser環境情報をセーブしました。" + '\n' )
				break
##			elif wSelect=="s" :
##				###セーブ
##				CLS_Config.sSetUserConfig( inFulluser )
##				CLS_OSIF.sPrn( "User環境情報をセーブしました。" + '\n' )
##				break
			
		return True

	#####################################################
	# 選択メニュー表示
	#####################################################
	def __cnfUserConfig_SelectDisp(self):
		wStr = "操作メニューキーを押してください" + '\n'
##		wStr = wStr + "c: 変更 / s:セーブ+終了 / other:なにもせず終了"
		wStr = wStr + "c: 変更 / other:なにもせず終了"
		CLS_OSIF.sPrn( wStr )
		wSelect = CLS_OSIF.sInp( "選択？=> " )
		return wSelect

	#####################################################
	# 変更メニュー表示
	#####################################################
	def __cnfUserConfig_Change(self):
		wKeylist = self.STR_View_userConf.keys()
		for iKey in wKeylist :
			#############################
			# 表示しないメニューは排除
			if self.STR_View_userConf[iKey]==False :
				###これらは別メニューで変更させる
				continue
			
			#############################
			# ON/OFFの文字作成
			wStr = iKey + "= " + str( gVal.STR_Config[iKey]) + " : "
			if gVal.STR_Config[iKey]=="on" :
				wStr = wStr + "c: on→off"
				wChg = "off"
			else:
				wStr = wStr + "c: off→on"
				wChg = "on"
			
			wStr = wStr + " / other: 変更しない"
			
			#############################
			# 変更メニューの表示
			CLS_OSIF.sPrn( wStr )
			wSelect = CLS_OSIF.sInp( "選択? => " )
			
			if wSelect=="c" :
				###変更する
				gVal.STR_Config[iKey] = wChg
		
		return



#####################################################
# 同報配信設定だけ読み込んで、
# 'on'だったらTrue、それ以外はFalseを返す
#####################################################
	@classmethod
	def sGetMulticast( cls, inPath ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# ファイルの存在チェック
		if CLS_File.sExist( inPath )!=True :
			###ありえない
			wRes['Reason'] = "CLS_Config: cGetMulticast: config file is not found : " + inPath
			wRes['Responce'] = False	#いちお結果としてoffを返す
			return wRes
		
		#############################
		# ファイルを開く
		wCHR_flag = ""
		for wLine in open( inPath, 'r'):
			#############################
			# 分解+要素数の確認
			wLine = wLine.strip()
			wGetLine = wLine.split("=")
			if len(wGetLine) != 2 :
				continue
			
			#############################
			# 同報配信キーか
			if wGetLine[0]=='Multicast' :
				wCHR_flag = wGetLine[1]
				break
		
		#############################
		# 取得できたか
		if wCHR_flag=="on" :
			wRes['Responce'] = True		#'on'
		else:
			wRes['Responce'] = False	#'off' または見つからないor壊れてる
		
		wRes['Result'] = True
		return wRes



#####################################################
# 同報配信ユーザ一覧の作成
#####################################################
	def GetMulticastUserList(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		wMulticastList = []
		
		#############################
		# データフォルダの一覧(トップだけ)取得
		wList = CLS_UserData.sGetUserList()
		
		if len(wList)==0 :
			###イレギュラー...
			wRes['Reason'] = "CLS_Config: GetMulticastUserList: No user registration"
			return wRes
		
		#############################
		# MasterUserが設定されていたら
		# 同報配信元には配信しないので抜く
		if gVal.STR_MasterConfig['MasterUser']!="" :
			if gVal.STR_MasterConfig['MasterUser'] in wList :
				wList.remove( gVal.STR_MasterConfig['MasterUser'] )
		
		#############################
		# 登録ユーザのconfigから Multicast値 を読み込む
		for iKey in wList :
			wGetPath = CLS_UserData.sGetUserPath( iKey )
##			if wGetPath['Result']!=True :
##				continue
			
			wGetRes = self.sGetMulticast( wGetPath['Responce'] + gVal.STR_File['UserConfig'] )
			if wGetRes['Result']==False :
				continue
			
			if wGetRes['Responce']==True :
				wMulticastList.append( iKey )
		
		wRes['Responce'] = wMulticastList
		wRes['Result'] = True
		return wRes



