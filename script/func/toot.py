#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：トゥート処理 (コンソール操作用)
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/6
#####################################################
# Private Function:
#   __manualToot_Disp( self, inFulluser ):
#   __manualToot( self, inFulluser, inDomain, inToot, inMastodon ):
#   __multicastToot_Disp( self, inFulluser, inNum ):
#   __multicastList( self, inSendlist ):
#   __multicastToot( self, inFulluser, inSendlist, inToot, inMastodon ):
#
# Instance Function:
#   __init__(self):
#   ManualToot(self):
#   MulticastToot(self):
#   SetRange( self, inKind ):
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
from config import CLS_Config
from regist import CLS_Regist
from userdata import CLS_UserData
from mastodon_use import CLS_Mastodon_Use
from gval import gVal
#####################################################
class CLS_Toot():
#####################################################
	STR_TootRange = ""

#####################################################
# Init
#####################################################
	def __init__(self):
		
		self.STR_TootRange = {
			"ManualToot"	: "public",
			"Multicast"		: "public"
		}
		
		self.STR_TootRange['ManualToot'] = gVal.STR_defaultRange['ManualToot']
		self.STR_TootRange['Multicast']  = gVal.STR_defaultRange['Multicast']
		return



#####################################################
# 手動トゥート
#####################################################
	def ManualToot(self):
		#############################
		# MasterUserユーザチェック
		wFulluser = gVal.STR_MasterConfig['MasterUser']
		wSTR_user = CLS_UserData.sUserCheck( wFulluser )
		if wSTR_user['Result']!=True :
			###config書き換えたかなんかしたろ？
			CLS_OSIF.sPrn( "CLS_Toot: ManualToot: Failer user name: " + wFulluser )
			return False
		
		CLS_OSIF.sPrn( "mastodonと通信中..." )
		#############################
		# mastodonクラス生成
		wCLS_work = CLS_Regist()
		wRes = wCLS_work.CreateMastodon( wFulluser )
		if wRes['Result']!=True :
			CLS_OSIF.sPrn( "mastodonと接続できないため中止します。 domain=" + wSTR_user['Domain'] )
			return False
		
		#############################
		# コンソール
		while True :
			#############################
			# コマンド画面表示
			wCommand = self.__manualToot_Disp( wFulluser )
			
			#############################
			# 継続
			if wCommand=="" :
				continue
			
			#############################
			# 終了
##			elif wCommand=="\q" :
			elif wCommand.find("\\q")>=0 :
				break
			
			#############################
			# 範囲切り替え
##			elif wCommand=="\c" :
			elif wCommand.find("\\c")>=0 :
				self.SetRange('ManualToot')
			
			#############################
			# トゥート
			else :
				wRes = wCLS_work.GetMastodon( wFulluser )
				if wRes['Result']!=True :
					wStr = "mastodon取得NG: user=" + wFulluser + '\n'
					wStr = wStr + "    " + wRes['Reason']
					CLS_OSIF.sPrn( wStr )
					return False
				
				self.__manualToot( wFulluser, wSTR_user['Domain'], wCommand, wRes['Responce'] )
		
		return

	#############################
	# 画面
	def __manualToot_Disp( self, inFulluser ):
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ出力
		wStr = "--------------------" + '\n'
		wStr = wStr + " 手動トゥートモード" + '\n'
		wStr = wStr + "--------------------" + '\n'
		wStr = wStr + "アカウント: " + inFulluser + '\n'
		wStr = wStr + "公開モード: " + self.STR_TootRange['ManualToot'] + '\n' + '\n'
		wStr = wStr + "コマンド= [\\q] 終了 / [\\c] 範囲切替 / [other] トゥート!!"
		CLS_OSIF.sPrn( wStr )
		wCommand = CLS_OSIF.sInp( "コマンド？=> " )
		return wCommand

	#############################
	# トゥート (CLS_Toot専用)
	def __manualToot( self, inFulluser, inDomain, inToot, inMastodon ):
		#############################
		# 分かるよう加工
		wTag = '\n' + gVal.STR_MasterConfig['mTootTag'] + " @" + inFulluser
		wToot = inToot + wTag
		
		wMaxToot = 500 - len(wTag)
		if len(wToot)>500 :
			wRes = CLS_OSIF.sInp( str(wMaxToot) + " 文字以上は送信できません。[RT]" )
			return False
		
		CLS_OSIF.sPrn( "mastodonに送信中..." )
		#############################
		# IP疎通チェック
		if CLS_OSIF.sPing( inDomain )!=True:
			wRes = CLS_OSIF.sInp( "mastodonと接続できないため送信できませんでした。[RT]" )
			return False
		
		#############################
		#トゥート
		wRes = inMastodon.Toot( status=wToot, visibility=self.STR_TootRange['ManualToot'] )
		if wRes['Result']!=True :
			CLS_OSIF.sPrn( "mastodon API Error: " + wRes['Reason'] )
			wRes = CLS_OSIF.sInp( "継続します。[RT]" )
			return False
		
		wRes = CLS_OSIF.sInp( "トゥートの送信を正常におこないました。[RT]" )
		return True



#####################################################
# 同報配信トゥート
#####################################################
	def MulticastToot(self):
		#############################
		# 同報配信ユーザ一覧の取得
		wCLS_Config = CLS_Config()
		wRes = wCLS_Config.GetMulticastUserList()
		if wRes['Result']!=True :
			CLS_OSIF.sPrn( "同報配信一覧の取得に失敗しました。" )
			return False
		elif len(wRes['Responce'])==0 :
			CLS_OSIF.sPrn( "同報配信先がありません。" )
			return False
		
		wMulticastList = wRes['Responce']
		
		#############################
		# MasterUserユーザチェック
		wFulluser = gVal.STR_MasterConfig['MasterUser']
		wSTR_user = CLS_UserData.sUserCheck( wFulluser )
		if wSTR_user['Result']!=True :
			###config書き換えたかなんかしたろ？
			CLS_OSIF.sPrn( "CLS_Toot: MulticastToot: Failer user name: " + wFulluser )
			return False
		
		CLS_OSIF.sPrn( "mastodonと通信中..." )
		#############################
		# mastodonクラス生成
		wCLS_work = CLS_Regist()
		wRes = wCLS_work.CreateMastodon( wFulluser )
		if wRes['Result']!=True :
			CLS_OSIF.sPrn( "mastodonと接続できないため中止します。 domain=" + wSTR_user['Domain'] )
			return False
		
		CLS_OSIF.sPrn( "同報配信先一覧の作成中..." )
		#############################
		# 配信先一覧(MasterUser)
		wSendList = {}
		wSendList.update({ wFulluser : "" })
		wSendList[wFulluser] = {}
		wSendList[wFulluser].update({ "fulluser" : wFulluser })
		wSendList[wFulluser].update({ "domain"   : wSTR_user['Domain'] })
		
		#############################
		# 同報配信先ユーザのクラス作成
		for wUser in wMulticastList :
			#############################
			# ユーザチェック
			wSTR_user = CLS_UserData.sUserCheck( wUser )
			if wSTR_user['Result']!=True :
				continue
			
			#############################
			# mastodonクラス生成
			wRes = wCLS_work.CreateMastodon( wUser )
			if wRes['Result']!=True :
				continue
			
			#############################
			# 配信先一覧
			wSendList.update({ wUser : "" })
			wSendList[wUser] = {}
			wSendList[wUser].update({ "fulluser" : wUser })
			wSendList[wUser].update({ "domain"   : wSTR_user['Domain'] })
		
		#############################
		# 配信先数のチェック
		if len(wSendList) <= 1 :
			CLS_OSIF.sPrn( "接続可能な同報配信先がありません。" )
			return False
		
		#############################
		# コンソール
		while True :
			#############################
			# コマンド画面表示
			wCommand = self.__multicastToot_Disp( wFulluser, len(wSendList) )
			
			#############################
			# 継続
			if wCommand=="" :
				continue
			
			#############################
			# 終了
##			elif wCommand=="\q" :
			elif wCommand.find("\\q")>=0 :
				break
			
			#############################
			# 範囲切り替え
##			elif wCommand=="\c" :
			elif wCommand.find("\\c")>=0 :
				self.SetRange('Multicast')
			
			#############################
			# 一覧
##			elif wCommand=="\l" :
			elif wCommand.find("\\l")>=0 :
				self.__multicastList( wSendList )
			
			#############################
			# トゥート
			else :
##				self.__multicastToot( wFulluser, wSendList, wCommand, wRes['Responce'] )
				self.__multicastToot( wFulluser, wSendList, wCommand, wCLS_work )
		
		return

	#############################
	# 画面
	def __multicastToot_Disp( self, inFulluser, inNum ):
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ出力
		wStr = "--------------------" + '\n'
		wStr = wStr + " 同報配信トゥートモード" + '\n'
		wStr = wStr + "--------------------" + '\n'
		wStr = wStr + "Masterアカウント: " + inFulluser + '\n'
		wStr = wStr + "同報配信先数    : " + str(inNum) + '\n'
		wStr = wStr + "公開モード: " + self.STR_TootRange['Multicast'] + '\n' + '\n'
		wStr = wStr + "コマンド= [\\q] 終了 / [\\c] 範囲切替 / [\\l] 配信先一覧 / [other] トゥート!!"
		CLS_OSIF.sPrn( wStr )
		wCommand = CLS_OSIF.sInp( "コマンド？=> " )
		return wCommand

	#############################
	# 一覧 (CLS_Toot専用)
	def __multicastList( self, inSendlist ):
		wStr = '\n' + "配信先一覧" + '\n'
		wKeylist = inSendlist.keys()
		for iKey in wKeylist :
			wStr = wStr + iKey + '\n'
		
		CLS_OSIF.sPrn( wStr )
		wCommand = CLS_OSIF.sInp( "同報配信先を出力しました。[RT]" )
		return

	#############################
	# トゥート (CLS_Toot専用)
	def __multicastToot( self, inFulluser, inSendlist, inToot, inSTR_Mastodon ):
		#############################
		# 分かるよう加工
		wTtl = "[Multicast] "
		wTag = '\n' + gVal.STR_MasterConfig['mTootTag'] + " @" + inFulluser
		wToot = wTtl + inToot + wTag
		
		wMaxToot = 500 - ( len(wTtl) + len(wTag) )
		if len(wToot)>500 :
			wRes = CLS_OSIF.sInp( str(wMaxToot) + " 文字以上は送信できません。[RT]" )
			return False
		
		CLS_OSIF.sPrn( "mastodonに配信中..." )
		wKeylist = inSendlist.keys()
		wListLen = len( wKeylist )
		wSend = 0
		for iKey in wKeylist :
			#############################
			# mastodonオブジェクト取得
			wMastodon = inSTR_Mastodon.GetMastodon( iKey )
			if wMastodon['Result']!=True :
				wStr = "mastodon取得NG: user=" + iKey + '\n'
				wStr = wStr + "    " + wMastodon['Reason']
				CLS_OSIF.sPrn( wStr )
				continue
			
			#############################
			# IP疎通チェック
			if CLS_OSIF.sPing( inSendlist[iKey]['domain'] )!=True:
				CLS_OSIF.sPrn( "通信NG: " + inSendlist[iKey]['domain'] )
				continue
			
			#############################
			#トゥート
			wRes = wMastodon['Responce'].Toot( status=wToot, visibility=self.STR_TootRange['Multicast'] )
			if wRes['Result']!=True :
				CLS_OSIF.sPrn( "mastodon API Error: " + wRes['Reason'] + ": account= " + iKey )
				continue
			
			CLS_OSIF.sPrn( "送信OK: " + inSendlist[iKey]['domain'] )
			
			#############################
			#カウント
			wSend += 1
			if wListLen>wSend :
				###送り切ってなければディレイする
				CLS_OSIF.sSleep( gVal.STR_MasterConfig['getMcDelay'] )
		
		wRes = CLS_OSIF.sPrn( "配信完了。[RT]" )
		return True



#####################################################
# 範囲切替 (CLS_Toot専用)
#####################################################
	def SetRange( self, inKind ):
		if inKind not in self.STR_TootRange :
			###ロジックエラー
			global_val.gCLS_Init.cPrint( "CLS_Toot: SetRange: STR_TootRange not in key: " + inKind )
			return
		
		#############################
		# 切替メニュー
		wStr = '\n' + "範囲切替= p:public(公開) / u:unlisted(未収載) / l:private(非公開)"
		CLS_OSIF.sPrn( wStr )
		wRes = CLS_OSIF.sInp( "切替？=> " )
		
		#############################
		# 範囲切替 設定
		if wRes=="p" :
			self.STR_TootRange[inKind] = "public"
		elif wRes=="u" :
			self.STR_TootRange[inKind] = "unlisted"
		elif wRes=="l" :
			self.STR_TootRange[inKind] = "private"
		
		return



