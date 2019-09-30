#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：トゥート処理 (コンソール操作用)
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/9/30
#####################################################
# Private Function:
#   __manualToot_Disp( self, inFulluser ):
#   __manualToot( self, inFulluser, inDomain, inToot, inMastodon ):
#   __multicastToot_Disp( self, inFulluser, inNum ):
#   __multicastList( self, inSendlist ):
#   __multicastToot( self, inFulluser, inSendlist, inToot, inMastodon ):
#   __ManualTweet_Disp( self, inTwitter ):
#   __manualTweet( self, inTwitter, inTweet ):
#   __getTwitterTL( self, inTwitter ):
#
# Instance Function:
#   __init__(self):
#   ManualToot(self):
#   MulticastToot(self):
#   SetRange( self, inKind ):
#   ManualTweet(self):
#
# Class Function(static):
#   (none)
#
#####################################################
from osif import CLS_OSIF
from config import CLS_Config
from regist import CLS_Regist
from userdata import CLS_UserData
from traffic import CLS_Traffic

from twitter_use import CLS_Twitter_Use
##from postgresql_use import CLS_PostgreSQL_Use
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
##			"Multicast"		: "public"
			"Multicast"		: "unlisted"
		}
		
##		self.STR_TootRange['ManualToot'] = gVal.STR_defaultRange['ManualToot']
##		self.STR_TootRange['Multicast']  = gVal.STR_defaultRange['Multicast']
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
			# (ないコマンド)
			elif wCommand.find("\\")==0 :
				wStr = "そのコマンドはありません。[RT]"
				CLS_OSIF.sInp( wStr )
				continue
			
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
##		wCLS_Config = CLS_Config()
##		wRes = wCLS_Config.GetMulticastUserList()
##		if wRes['Result']!=True :
##			CLS_OSIF.sPrn( "同報配信一覧の取得に失敗しました。" )
##			return False
##		elif len(wRes['Responce'])==0 :
##			CLS_OSIF.sPrn( "同報配信先がありません。" )
##			return False
##		
##		wMulticastList = wRes['Responce']
		
		wMulticastList = CLS_UserData.sGetUserList()
##		elif len( wMulticastList )==0 :
		if len( wMulticastList )==0 :
			CLS_OSIF.sPrn( "同報配信先がありません。" )
			return False
		
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
			elif wCommand.find("\\q")>=0 :
				break
			
			#############################
			# 範囲切り替え
			elif wCommand.find("\\c")>=0 :
				self.SetRange('Multicast')
			
			#############################
			# 一覧
			elif wCommand.find("\\l")>=0 :
				self.__multicastList( wSendList )
			
			#############################
			# (ないコマンド)
			elif wCommand.find("\\")==0 :
				wStr = "そのコマンドはありません。[RT]"
				CLS_OSIF.sInp( wStr )
				continue
			
			#############################
			# トゥート
			else :
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
				CLS_OSIF.sSleep( gVal.DEF_STR_TLNUM['getMcDelay'] )
		
		wRes = CLS_OSIF.sPrn( "配信完了。[RT]" )
		return True



#####################################################
# 範囲切替 (CLS_Toot専用)
#####################################################
	def SetRange( self, inKind ):
		if inKind not in self.STR_TootRange :
			###ロジックエラー
###			global_val.gCLS_Init.cPrint( "CLS_Toot: SetRange: STR_TootRange not in key: " + inKind )
			CLS_OSIF.sPrn( "CLS_Toot: SetRange: STR_TootRange not in key: " + inKind )
			return
		
		#############################
		# 切替メニュー
		if inKind=="ManualToot" :
			wStr = '\n' + "範囲切替= p:public(公開) / u:unlisted(未収載) / l:private(非公開) / d:direct(DM)"
		else :
			## Multicast
			wStr = '\n' + "範囲切替= p:public(公開) / u:unlisted(未収載)"
		
		CLS_OSIF.sPrn( wStr )
		wRes = CLS_OSIF.sInp( "切替？=> " )
		
		#############################
		# 範囲切替 設定
		if wRes=="p" :
			self.STR_TootRange[inKind] = "public"
		elif wRes=="u" :
			self.STR_TootRange[inKind] = "unlisted"
##		elif wRes=="l" :
		elif wRes=="l" and inKind=="ManualToot" :
			self.STR_TootRange[inKind] = "private"
		elif wRes=="d" and inKind=="ManualToot" :
			self.STR_TootRange[inKind] = "direct"
		
		return



#####################################################
# 同報配信ユーザ一覧取得
#####################################################
##	def __GetMuticastUserList(self) :
##		wMList = {
##			"Result"   : False,
##			"List"     : "",
##		}
##		
##		#############################
##		# 存在しないドメインの削除
##		wRes = self.DelDomain()
##		if wRes!=True :
##			##失敗
##			return wMList
##		
##		#############################
##		# DB接続情報ファイルのチェック
##		wFile_path = gVal.STR_File['DBinfo_File']
##		if CLS_File.sExist( wFile_path )!=True :
##			##失敗
##			CLS_OSIF.sPrn( "CLS_Toot: GetMuticastUserList: Database file is not found: " + wFile_path )
##			return wMList
##		
##		#############################
##		# DB接続
##		wOBJ_DB = CLS_PostgreSQL_Use( wFile_path )
##		wRes = wOBJ_DB.GetIniStatus()
##		if wRes['Result']!=True :
##			##失敗
##			CLS_OSIF.sPrn( "CLS_Toot: GetMuticastUserList: DB Connect test is failed: " + wRes['Reason'] )
##			wOBJ_DB.Close()
##			return wMList
##		
##		#############################
##		# レコードの取得
##		wQuery = "select * from TBL_TRAFFIC_DATA ;"
##		
##		wRes = wOBJ_DB.RunQuery( wQuery )
##		if wRes['Result']!=True :
##			##失敗
##			CLS_OSIF.sPrn( "CLS_Toot: GetMuticastUserList: Run Query is failed: " + wRes['Reason'] )
##			wOBJ_DB.Close()
##			return wMList
##		
##		if len( wRes['Responce']['Data'] )!=1 :
##			##存在しない
##			CLS_OSIF.sPrn( "CLS_Toot: GetMuticastUserList: Domain is not found" )
##			wOBJ_DB.Close()
##			return wMList
##		
##		#############################
##		# DB切断
##		wOBJ_DB.Close()
##		
##		#############################
##		# ユーザ一覧の取得
##		#   ただしMaster Userは除く
##		wMList['List'] = []
##		for wLineTap in wRes['Responce']['Data'] :
##			wGetTap = []
##			for wCel in wLineTap :
##				wCel = wCel.strip()
##				wGetTap.append( wCel )
##				## [0] ..domain
##				## [1] ..admin_id
##				## [2] ..count
##				## [3] ..rat_count
##			if gVal.STR_MasterConfig['MasterUser']==wGetTap[1] :
##				continue
##			wMList['List'].append( wGetTap[1] )
##		
##		#############################
##		# 正常
##		wMList['Result'] = True
##		return wMList



#####################################################
# 手動ついーと (Twitter)
#####################################################
	def ManualTweet(self):
		#############################
		# Twitterが有効か？
		if gVal.STR_MasterConfig['Twitter']!="on" :
			###失敗
			CLS_OSIF.sPrn( "Twitter設定が有効ではありません。" )
			return False
		
		CLS_OSIF.sPrn( "Twitterと接続しています......" )
		#############################
		# Twitterと接続 (クラス生成)
##		wCLS_Twitter = CLS_Twitter_Use( gVal.STR_File['Twitter_File'] )
		wCLS_Twitter = CLS_Twitter_Use( gVal.DEF_STR_FILE['Twitter_File'], gVal.DEF_STR_TLNUM['getTwitTLnum'] )
		wStat = wCLS_Twitter.GetIniStatus()
		if wStat['Result']!=True :
			###失敗
			CLS_OSIF.sPrn( "CLS_Toot: ManualTweet: Twitter connect failed: " + wStat['Reason'] )
			return False
		
		#############################
		# コンソール
		while True :
			#############################
			# コマンド画面表示
			wCommand = self.__ManualTweet_Disp( wCLS_Twitter )
			
			#############################
			# 継続
			if wCommand=="" :
				continue
			
			#############################
			# 終了
			elif wCommand.find("\\q")>=0 :
				break
			
			#############################
			# タイムライン読み込み
			elif wCommand.find("\\g")>=0 :
				self.__getTwitterTL( wCLS_Twitter )
			
##			#############################
##			# リスト読み込み
##			elif wCommand.find("\\l")>=0 :
##				self.__getTwitterList( wCLS_Twitter )
##			
			#############################
			# トゥート
			else :
				self.__manualTweet( wCLS_Twitter, wCommand )
		
		return

	#############################
	# 画面
	def __ManualTweet_Disp( self, inTwitter ):
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ出力
		wStr = "--------------------" + '\n'
		wStr = wStr + " 手動ついーとモード" + '\n'
		wStr = wStr + "--------------------" + '\n'
		wStr = wStr + "アカウント: " + inTwitter.GetUsername() + '\n'
		wStr = wStr + "Mode   : " + inTwitter.STR_TWITTERdata['Mode']
		if inTwitter.STR_TWITTERdata['Mode']=="list" :
			wStr = wStr + " / ListID= " + str(inTwitter.STR_TWITTERdata['List'])
		wStr = wStr + '\n'
		wStr = wStr + "NoReply: " + inTwitter.STR_TWITTERdata['NoReply'] + '\n'
		wStr = wStr + "Retweet: " + inTwitter.STR_TWITTERdata['Retweet'] + '\n'
##		wStr = wStr + "コマンド= [\\q] 終了 / [\\g] TL取得 / [\\l] List取得 / [other] ついーと!!"
		wStr = wStr + "コマンド= [\\q] 終了 / [\\g] TL取得 / [other] ついーと!!"
		CLS_OSIF.sPrn( wStr )
		wCommand = CLS_OSIF.sInp( "コマンド？=> " )
		return wCommand

	#############################
	# ついーと
	def __manualTweet( self, inTwitter, inTweet ):
		#############################
		# 文字数チェック
		wMaxToot = 140 - len( inTweet )
		if len(inTweet)>140 :
			wRes = CLS_OSIF.sInp( str(wMaxToot) + " 文字以上は送信できません。[RT]" )
			return False
		
		CLS_OSIF.sPrn( "Twitterに送信中..." )
		#############################
		#ついーと
		wRes = inTwitter.Tweet( inTweet )
		if wRes['Result']!=True :
			CLS_OSIF.sPrn( "Twitter API Error: " + wRes['Reason'] )
			wRes = CLS_OSIF.sInp( "継続します。[RT]" )
			return False
		
		wRes = CLS_OSIF.sInp( "ツイートの送信を正常におこないました。[RT]" )
		return True

	#############################
	# タイムライン取得
	def __getTwitterTL( self, inTwitter ):
		CLS_OSIF.sPrn( "タイムラインの取得中..." + '\n' )
		#############################
		# 取得
##		wRes = inTwitter.GetTL( inTLmode="user", inList=None, inReply=True, inRetweet=False )
##		wRes = inTwitter.GetTL( inTLmode="home", inList=None, inReply=True, inRetweet=True )
##		wRes = inTwitter.GetTL( inTLmode="list", inList=1006036956923363328, inReply=True, inRetweet=False )
##		wRes = inTwitter.GetTL( inTLmode="list", inList=1164128983975206912, inReply=True, inRetweet=False )
		wRes = inTwitter.GetTL()
		if wRes['Result']!=True :
			CLS_OSIF.sPrn( "Twitter API Error: " + wRes['Reason'] )
			wRes = CLS_OSIF.sInp( "継続します。[RT]" )
			return False
		
		#############################
		# 画面に表示
		for wROW in wRes['Responce'] :
			CLS_OSIF.sPrn( "Country: " + str(wROW['lang']) )
			if "possibly_sensitive" not in wROW :
				CLS_OSIF.sPrn( "Sensitive: ON" )
			CLS_OSIF.sPrn( "Locked: " + str(wROW['user']['protected']) )
			CLS_OSIF.sPrn( "Sender: " + wROW['user']['name'] + "(@" + wROW['user']['screen_name'] + ")" )
			
			CLS_OSIF.sPrn( wROW['text'] )
			CLS_OSIF.sPrn( "------------------------------------------------------------" )
		
		#############################
		# 正常
		wRes = CLS_OSIF.sInp( "タイムラインの取得を正常におこないました。[RT]" )
		return True



##	#############################
##	# リスト取得
##	def __getTwitterList( self, inTwitter ):
##		CLS_OSIF.sPrn( "タイムラインの取得中..." )
##		#############################
##		# 取得
##		wRes = inTwitter.GetLists()
##		if wRes['Result']!=True :
##			CLS_OSIF.sPrn( "Twitter API Error: " + wRes['Reason'] )
##			wRes = CLS_OSIF.sInp( "継続します。[RT]" )
##			return False
##		
##		#############################
##		# 画面に表示
##		for wROW in wRes['Responce'] :
##			CLS_OSIF.sPrn( "ID: " + str(wROW['id']) )
##			CLS_OSIF.sPrn( "Slug: " + str(wROW['slug']) )
##			CLS_OSIF.sPrn( "Mode: " + str(wROW['mode']) )
##			CLS_OSIF.sPrn( "Name: " + str(wROW['name']) + "(" + str(wROW['full_name']) + ")" )
##			CLS_OSIF.sPrn( "Disc: " + str(wROW['description']) )
##			CLS_OSIF.sPrn( "------------------------------------------------------------" )
##		
##		#############################
##		# 正常
##		wRes = CLS_OSIF.sInp( "リストの取得を正常におこないました。[RT]" )
##		return True



