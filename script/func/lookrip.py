#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：リプライ監視処理(サブ用)
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/11/8
#####################################################
# Private Function:
#   __run(self):
#   __copeFavo( self, inROW ) :
#   __copeFollow( self, inROW ) :
#   __copeReind( self, inROW ) :
#   __copeRIP( self, inROW ) :
#   __setNewRIP( self, outARRrip, inFulluser, inTime, inToot ):
#   __setReindRIP( self, outARRrip, inFulluser, inTime, inToot, inStatusID ):
#   __getIndiTootID( self, inToot ):
#
# Instance Function:
#   __init__( self, parentObj=None ):	※親クラス実体を設定すること
#   Get_RIP(self):
#   Get_RateFV(self):
#   Set_RateFV(self):
#   Get_RateRIP(self):
#   Set_RateRIP(self):
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
class CLS_LookRIP():
#####################################################
	CHR_LogName  = "RIP監視"
	Obj_Parent   = ""		#親クラス実体

	ARR_NewTL    = {}		#mastodon TL(mastodon API)
	ARR_AnapTL   = {}		#TL解析パターン
	ARR_RateTL   = []		#過去TL(id)
	ARR_UpdateTL = []		#新・過去TL(id)
	
##	ARR_NowFavID = []		#今周処理したふぁぼID
	ARR_RateInd  = {}		#過去通知

##	ARR_RateFV   = []		#過去ふぁぼ(ふぁぼ対象id)
##	ARR_UpdateFV = []		#新・過去ふぁぼ(ふぁぼid,時間)
##
##	ARR_NewFavo   = {}		#ふぁぼ or ぶーすと
##	ARR_NewFollow = {}		#ふぉろー
##	ARR_NewRip    = {}		#リプライ
##	ARR_Reind     = {}		#再通知

	STR_Cope = {			#処理カウンタ
		"Ind_Cope"		: 0,	#今回受信した通知数
		"Ind_On"		: 0,	#正常処理
		"Ind_Off"		: 0,	#反応時間外で破棄
		"Ind_Notified"	: 0,	#通知済み
		"Ind_Inv"		: 0,	#条件外で破棄
		"Ind_Fail"		: 0,	#処理失敗で破棄
		
		"Now_Cope"		: 0,	#処理した新トゥート数
		"Now_Favo"		: 0,	#処理したふぁぼ通知
		"Now_Follow"	: 0,	#処理したふぉろー通知
		"Now_Rip"		: 0,	#処理したリプ
		"Now_Reind"		: 0,	#処理した再通知
		
		"dummy"			: 0		#(未使用)
	}
	
	STR_Ind = {				#通知制限
		"Count"			: 0,	#通知回数
		"TimeDate"		: ""	#カウント開始時間
	}
	
	
	
	VAL_ReaRIPmin = 0
	VAL_indLimmin = 0
	FLG_indLim = False
	
	DEF_TITLE_INFORMATION  = "[Info]"
	DEF_TITLE_NEW_FOLLOWER = "[New Follower]"

#####################################################
# Init
#####################################################
	def __init__( self, parentObj=None ):
		if parentObj==None :
			###親クラス実体の未設定
			CLS_OSIF.sPrn( "CLS_LookRIP: __init__: You have not set the parent class entity for parentObj" )
			return
		
		#############################
		# 反応リプライ時間範囲の算出(分→秒へ)
		self.VAL_ReaRIPmin = gVal.DEF_STR_TLNUM['reaRIPmin'] * 60	#秒に変換
		
		#############################
		# 通知制限時間の算出(分→秒へ)
		self.VAL_indLimmin = gVal.DEF_STR_TLNUM['indLimmin'] * 60	#秒に変換
		
		self.Obj_Parent = parentObj
		self.__run()	#処理開始
		return



#####################################################
# 処理実行
#####################################################
	def __run(self):
		#############################
		# 開始ログ
		self.Obj_Parent.OBJ_Mylog.Log( 'b', self.CHR_LogName + " 開始" )
		
		#############################
		# TL解析パターン読み込み
		if self.Get_Anap()!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __run: Pattern RIP read failed" )
			return
		
		#############################
		# 通知制限の読み込み
		wRes = self.Get_Indlim()
		if wRes!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __run: Get_Indlim failed" )
			return
		
		#############################
		# 過去通知の読み込み
		#   =RIPを読む前に呼ぶこと
		wRes = self.Get_RateInd()
		if wRes!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __run: Get_RateInd failed" )
			return
		
		#############################
		# RIP読み込み(mastodon)
		wRes = self.Get_RIP()
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __run: Riply read failed: " + wRes['Reason'] )
			return
		
		#############################
		# 過去RIPの読み込み
		wRes = self.Get_RateRIP()
		if wRes!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __run: Get_RateRIP failed" )
			return
##		if len(self.ARR_RateTL)==0 and len(self.ARR_NewTL)>0 :
##			self.Init_RateRIP()
##			if gVal.FLG_Test_Mode==False :
##				self.Obj_Parent.OBJ_Mylog.Log( 'b', self.CHR_LogName + " RIP過去TL初期化" )
##			else :
##				self.Obj_Parent.OBJ_Mylog.Log( 'b', self.CHR_LogName + " RIP過去TL初期化", inView=True )
##			return
		
		#############################
		# TLチェック
		self.ARR_UpdateTL = []
##		for wROW in self.ARR_NewTL :
		wKeyList = self.ARR_NewTL.keys()
		for wKey in wKeyList :
			wROW = self.ARR_NewTL[wKey]
			#############################
			# チェックするので新過去TLに保管
			self.ARR_UpdateTL.append( wROW['id'] )
			
			#############################
			# 過去チェックしたトゥートか
			#   であればスキップする
			wFlg_Rate = False
			for wRow_Rate in self.ARR_RateTL :
				if str(wRow_Rate) == str(wROW['id']) :
					wFlg_Rate = True
					break
			
			if wFlg_Rate == True :
				continue
			
			#############################
			# ふぁぼ、ブースト、再通知の場合
			#   通知制限か
			if wROW['type']=="favourite" or wROW['type']=="reblog" or wROW['type']=="reind" :
				if self.Check_Indlim( wROW['created_at'] )==False :
					continue
			
			#############################
			# 新トゥートへの対応
			self.__cope( wROW )
			self.STR_Cope["Now_Cope"] += 1
		
		#############################
		# 通知制限の保存
		wRes = self.Set_Indlim()
		if wRes!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __run: Set_Indlim failed" )
###			return
		
		#############################
		# 過去通知 保存
		wRes = self.Set_RateInd()
		if wRes!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __run: Set_RateInd failed" )
			return
		
		#############################
		# 新・過去RIP保存
		wRes = self.Set_RateRIP()
		if wRes!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __run: Set_RateRIP failed" )
			return
		
		#############################
		# 処理結果ログ
		wStr = self.CHR_LogName + " 結果: 新Riply=" + str(self.STR_Cope['Now_Cope']) + " Ans=" + str(self.STR_Cope['Now_Rip']) + " Limit=" + str(self.STR_Ind['Count']) + '\n'
		wStr = wStr + "Ind=[Cope:" + str(self.STR_Cope['Ind_Cope']) + " On:" + str(self.STR_Cope['Ind_On']) + " Off:" + str(self.STR_Cope['Ind_Off'])
		wStr = wStr + " Notified:" + str(self.STR_Cope['Ind_Notified']) + " Invalid:" + str(self.STR_Cope['Ind_Inv']) + " Failed:" + str(self.STR_Cope['Ind_Fail']) + "]" + '\n'
		wStr = wStr + "Favo=" + str(self.STR_Cope['Now_Favo']) + " Follow=" + str(self.STR_Cope['Now_Follow']) + " Reind=" + str(self.STR_Cope['Now_Reind'])

		if gVal.FLG_Test_Mode==False :
			self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr )
		else:
			self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr, True )
		
		return



#####################################################
# 新トゥートへの対応
#####################################################
	def __cope( self, inROW ) :
		#############################
		# 種別：ふぁぼ or ブースト
		if inROW['type']=="favourite" or inROW['type']=="reblog" :
			self.__copeFavo( inROW )
		
		#############################
		# 種別：再通知
		elif inROW['type']=="reind" :
			self.__copeReind( inROW )
		
		#############################
		# 種別：フォロー
		elif inROW['type']=="follow" :
			self.__copeFollow( inROW )
		
		#############################
		# 種別：めんしょん
		elif inROW['type']=="mention" :
			self.__copeRIP( inROW )
		
		return



#####################################################
# 新ふぁぼ、ぶーすと通知への対応
#####################################################
	def __copeFavo( self, inROW ) :
		#############################
		# ユーザ名の変換
		wFulluser = CLS_UserData.sUserCheck( self.Obj_Parent.CHR_Account )
		if wFulluser['Result']!=True :
			###今のところ通らないルート
			return False
		wDomain = wFulluser['Domain']
		
		#############################
		# ファボられたトゥートURL
		wToot_Url = "https://" + wDomain + gVal.DEF_TOOT_SUBURL + inROW['status_id']
		
		#############################
		# トゥートが140字超えの場合、切り払う
		if len(inROW['content'])>140 :
			wCHR_Body = inROW['content'][0:139] + "(以下略)"
		else:
			wCHR_Body = inROW['content']
		
		#############################
		# CW付きの場合
		if inROW['spoiler_text'] != "" :
			wCHR_Body = inROW['spoiler_text'] + '\n' + wCHR_Body
		
		#############################
		# 画像(サムネ)があればURLを付ける
		if len( inROW['media_attachments'] )>0 :
			wCHR_Body = wCHR_Body + "【画像あり】"
		
		#############################
		# タイトルの組み立て
		wCHR_Title = "[注目されたトゥート]"
		
		#############################
		# トゥートの組み立て
		wCHR_Toot = "以下のトゥートが注目されました。:" + '\n'
		wCHR_Toot = wCHR_Toot + wCHR_Body + '\n' + wToot_Url + '\n' + "#" + gVal.STR_MasterConfig['iActionTag']
		
		#############################
		# トゥートの送信
		wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, spoiler_text=wCHR_Title, visibility=inROW['visibility'] )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __copeFavo: Mastodon error: " + wRes['Reason'] )
			return False
		
		self.STR_Ind['Count'] += 1	#通知制限カウント
		self.STR_Cope['Now_Favo'] += 1
		return True



#####################################################
# 再通知への対応
#####################################################
	def __copeReind( self, inROW ) :
		#############################
		# タイトルの組み立て
		wCHR_Title = inROW['spoiler_text']
		
		#############################
		# トゥートの組み立て
		wCHR_Toot = inROW['content']
		
		#############################
		# タグの付け直し
		wTag = "#" + gVal.STR_MasterConfig['iActionTag']
		wCHR_Toot.strip( wTag )
		wCHR_Toot = wCHR_Toot + '\n' + "#" + gVal.STR_MasterConfig['iActionTag']
		
		#############################
		# トゥートの送信
		wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, spoiler_text=wCHR_Title, visibility=inROW['visibility'] )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __copeReind: Mastodon error: " + wRes['Reason'] )
			return False
		
		self.STR_Ind['Count'] += 1	#通知制限カウント
		self.STR_Cope['Now_Reind'] += 1
		return True



#####################################################
# 新ふぉろー通知への対応
#####################################################
	def __copeFollow( self, inROW ) :
		#############################
		# タイトルの組み立て
		wCHR_Title = self.DEF_TITLE_NEW_FOLLOWER
		
		#############################
		# トゥートの組み立て
###		wCHR_Toot = self.DEF_TITLE_NEW_FOLLOWER + " " + inROW['display_name'] + " (" + inROW['Fulluser'] + ") さんにフォローされました。"
		wCHR_Toot = inROW['display_name'] + " (" + inROW['Fulluser'] + ") さんにフォローされました。"
		wCHR_Toot = wCHR_Toot + '\n' + "#" + gVal.STR_MasterConfig['iActionTag']
		
		#############################
		# トゥートの送信
		wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, spoiler_text=wCHR_Title, visibility="public" )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __copeFollow: Mastodon error: " + wRes['Reason'] )
			return False
		
		self.STR_Cope['Now_Follow'] += 1
		return



#####################################################
# 新リプライへの対応
#####################################################
	def __copeRIP( self, inROW ) :
		#############################
		# Masterの場合、ランダムリプライ動作をおこなう
		if gVal.STR_MasterConfig['MasterUser']==self.Obj_Parent.CHR_Account :
			if self.__copeRandomReply( inROW )!=True :
				self.STR_Cope['Ind_Fail'] += 1
				return False
		
		#############################
		# Subの場合、リプライブースト動作をおこなう
		#   public、unlisted =>ブースト
		#   private、direct  =>ニコる
		else :
			if inROW['visibility']=="public" or inROW['visibility']=="unlisted" :
				wRes = self.Obj_Parent.OBJ_MyDon.Boost( inROW['status_id'] )
				if wRes['Result']!=True :
					self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __copeRIP: Mastodon error(Boost): " + wRes['Reason'] )
					return False
			else :
				wRes = self.Obj_Parent.OBJ_MyDon.Favo( inROW['status_id'] )
				if wRes['Result']!=True :
					self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __copeRIP: Mastodon error(Favo): " + wRes['Reason'] )
					return False
		
		self.STR_Cope['Now_Rip'] += 1
		return True



#####################################################
# ランダムリプライ *Master機能
#####################################################
	def __copeRandomReply( self, inROW ) :
		
		wFLG_Hit = False
		#############################
		#解析種類の判定
		wKeyList = self.ARR_AnapTL.keys()
		for wKey in wKeyList :
			#############################
			# 解析：通常（指定リプライ）
			if self.ARR_AnapTL[wKey]['Kind']=="r" :
				###マッチチェック
				wRes = CLS_OSIF.sRe_Search( self.ARR_AnapTL[wKey]['Pattern'], inROW['content'] )
				if not wRes :
					##アンマッチ
					continue
				###実行
				if self.NormalRipry( self.ARR_AnapTL[wKey]['File'], inROW )!=True :
					break
				wFLG_Hit = True
				break
			
			#############################
			# 解析：ワード学習
			if self.ARR_AnapTL[wKey]['Kind']=="_sys_study" :
				###マッチチェック
				wRes = CLS_OSIF.sRe_Search( self.ARR_AnapTL[wKey]['Pattern'], inROW['content'] )
				if not wRes :
					##アンマッチ
					continue
				###実行
###				if self.WordStudy( inROW, self.ARR_AnapTL[wKey]['Pattern'] )!=True :
				if self.WordStudy( inROW, wRes )!=True :
					break
				wFLG_Hit = True
				break
		
		#############################
		# パターンHitしない場合
		# 収集ワードからランダム返信する
		if wFLG_Hit==False :
			#############################
			# 学習機能が有効なら、収集ワードでリプライを返す
			if gVal.STR_MasterConfig['WordStudy']=="on" :
				if self.WordReply( inROW )!=True :
					return False
			
			#############################
			# 学習機能が無効なら、固定リプライを返す
			else :
				if self.OtherReply( inROW )!=True :
					return False
		
		#############################
		# 正常
		return True



#####################################################
# RIP取得
#####################################################
	def Get_RIP(self):
		self.ARR_NewTL = {}
##		self.ARR_NewFavo   = {}		#ふぁぼ
##		self.ARR_NewReblog = {}		#ぶーすと
##		self.ARR_NewFollow = {}		#ふぉろー
##		self.ARR_NewRip    = {}		#リプライ
		
		wGet_TootList = []
		wNext_Id = None
		wMax_Toots = gVal.DEF_STR_TLNUM["getRIPnum"]
		while (len(wGet_TootList) < wMax_Toots ):
			#############################
			# TL取得
			wRes = self.Obj_Parent.OBJ_MyDon.GetNotificationList( limit=40, max_id=wNext_Id )
			if wRes['Result']!=True :
				return wRes	#失敗
			
			wGet_Toots = wRes['Responce']	#toot list(json形式)
			
			#############################
			# 新しいトゥートが取得できなかったらループ終了
			if len( wGet_Toots ) > 0:
				wGet_TootList += wGet_Toots
			else:
				break
			
			#############################
			# configの最大取得数を超えていたらループ終了
			if len( wGet_TootList ) >= wMax_Toots :
				break
			
			#############################
			# ページネーション(次の40件を取得する設定)
			try:
				wNext_Id = wGet_Toots[-1]['id']
			except:
				###ありえない
				wRes['Reason'] = "CLS_LookRIP: Get_RIP: Page nation error"
				wRes['Result'] = False
				return wRes
		
		#############################
		# 取り込み数=0ならやめる
		if len(wGet_TootList)==0 :
			wRes['Result'] = True
			return wRes
		
		#############################
		# type別に取り込み先を振り分け
###		wFavID = []
##		self.ARR_NowFavID = []
		for wToot in wGet_TootList :
			self.STR_Cope['Ind_Cope'] += 1
			
			#############################
			# トゥートの時間 (変換＆差)
			wGetLag = CLS_OSIF.sTimeLag( str(wToot['created_at']), inThreshold=self.VAL_ReaRIPmin )
			if wGetLag['Result']!=True :
				self.STR_Cope['Ind_Fail'] += 1
				continue
			if wGetLag['Beyond']==True :

#				#############################
#				# アクション通知のふぁぼ or ぶーすとの場合、
#				# 過去通知を削除する
#				if wToot['type']=="favourite" or wToot['type']=="reblog" :
#					if "status" in wToot :
#						wID = str( wToot['status']['id'] )
#						wKeyList = list( self.ARR_RateInd.keys() )
#						if wID in wKeyList :
#							del self.ARR_RateInd[wID]
#
#							self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: Get_RIP: Rel" + wID )
#

				self.STR_Cope['Ind_Off'] += 1
				continue	#反応時間外
			
			wGetTime = str(wGetLag['InputTime'])
			
			#############################
			# 相手ユーザ名
			wFulluser = CLS_UserData.sGetFulluser( wToot['account']['username'], wToot['account']['url'] )
			if wFulluser['Result']!=True :
				self.STR_Cope['Ind_Fail'] += 1
				continue
			
			#############################
			# ふぁぼ or ぶーすと
			if wToot['type']=="favourite" or wToot['type']=="reblog" :
##				self.__getRIP_FavBoost( wToot, wFulluser['Fulluser'], wGetTime )
				self.__getRIP_FavBoost( wToot, wFulluser, wGetTime )
			
			#############################
			# ふぉろー
			elif wToot['type']=="follow" :
##				self.__getRIP_Follow( wToot, wFulluser['Fulluser'], wGetTime )
				self.__getRIP_Follow( wToot, wFulluser, wGetTime )
			
			#############################
			# めんしょん
			elif wToot['type']=="mention" :
##				self.__getRIP_Mention( wToot, wFulluser['Fulluser'], wGetTime )
				self.__getRIP_Mention( wToot, wFulluser, wGetTime )
			
			#############################
			# その他(あるの？)
			else:
				self.STR_Cope['Ind_Inv'] += 1
		
		return wRes

	#####################################################
	# ふぁぼorブースト => ふぁぼ通知
	def __getRIP_FavBoost( self, inROW, inFulluser, inTime ):
		#############################
		# 除外判定
		### Masterか(=完全スルー)
		if gVal.STR_MasterConfig['MasterUser']==self.Obj_Parent.CHR_Account :
			return
		
		### ふぁぼ通知が有効か
		if gVal.STR_MasterConfig['IND_Favo']!="on" :
			self.STR_Cope['Ind_Inv'] += 1
			return
		
		### statusなし
		if "status" not in inROW :
##			self.STR_Cope['Ind_Inv'] += 1
			self.STR_Cope['Ind_Fail'] += 1
			return
		
		### directの場合
		if inROW['status']['visibility']=="direct" :
			self.STR_Cope['Ind_Inv'] += 1
			return
		
		### ユーザ登録されていた
		###  =登録ユーザのふぁぼ等は通知しない
##		wUserChk = CLS_UserData.sUserCheck( inFulluser )
		wUserChk = CLS_UserData.sUserCheck( inFulluser['Fulluser'] )
		if wUserChk['Result']!=True or wUserChk['Registed']==True :
			self.STR_Cope['Ind_Inv'] += 1
			return
		
		wCont = CLS_OSIF.sDel_HTML( inROW['status']['content'] )
		### @ 入り(リプライ)のふぁぼ、ブースト
###		if CLS_OSIF.sRe_Search( "@", wCont )==0 :
##		wRes = CLS_OSIF.sRe_Search( "@", wCont )
##		if wRes :
##			if wRes.start()==0 :
##				self.STR_Cope['Ind_Inv'] += 1
##				return
		if wCont.find("@")==0 :
			self.STR_Cope['Ind_Inv'] += 1
			return
		
		### タグ付き(アクション通知以外)
##		if CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['mTootTag'], wCont )>=0 or + \
##		   CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['prTag'],    wCont )>=0 or + \
##		   CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['TrafficTag'], wCont )>=0 :
##		wRes_1 = CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['mTootTag'], wCont )
##		wRes_2 = CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['prTag'],    wCont )
##		wRes_3 = CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['TrafficTag'], wCont )
##		if wRes_1 or wRes_2 or wRes_3 :
		wRes_1 = wCont.find( gVal.STR_MasterConfig['mTootTag'] )
		wRes_2 = wCont.find( gVal.STR_MasterConfig['prTag'] )
		wRes_3 = wCont.find( gVal.STR_MasterConfig['TrafficTag'] )
		if wRes_1>=0 or wRes_2>=0 or wRes_3>=0 :
			self.STR_Cope['Ind_Inv'] += 1
			return
		
		#############################
		# アクション通知への反応 =>再通知
##		if CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['iActionTag'], wCont )>=0 :
##		wRes = CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['iActionTag'], wCont )
##		if wRes :
		if wCont.find( gVal.STR_MasterConfig['iActionTag'] )>=0 :
			### public以外の場合
			if inROW['status']['visibility']!="public" :
				self.STR_Cope['Ind_Inv'] += 1
				return
			
			###フォロー通知は除外
##			if CLS_OSIF.sRe_Search( self.DEF_TITLE_NEW_FOLLOWER, wCont )>=0 :
##			wRes = CLS_OSIF.sRe_Search( self.DEF_TITLE_NEW_FOLLOWER, wCont )
##			if wRes :
			if wCont.find( self.DEF_TITLE_NEW_FOLLOWER )>=0 :
				self.STR_Cope['Ind_Inv'] += 1
				return
			
			### 通知元のトゥートidを抜き出す
##			wID = self.__getRIP_IndiTootID( wCont )
##			if wID==-1 :
			wNetaID = self.__getRIP_IndiTootID( wCont )
			if wNetaID==-1 :
				self.STR_Cope['Ind_Inv'] += 1
				return
			
			#############################
			# 通知済みか
			#   True=  未通知、通知済みをメモ
			#   False= 通知済み
			if self.__set_RateInd( wNetaID, inTime )!=True :
				##通知済み
				self.STR_Cope['Ind_Notified'] += 1
				return
			
			#############################
			# 新リプに設定する
##			### この周では既に通知済みのID
##			wID = str( inROW['id'] )
##			if wID in self.ARR_NowFavID :
##				self.STR_Cope['Ind_Inv'] += 1
##				return
##			self.ARR_NowFavID.append( wID )
			
##			self.__getRIP_SetReindRIP( inROW, inFulluser, inTime, wID )
##			self.__getRIP_SetReindRIP( inROW, inFulluser['Fulluser'], inTime, wID )
			self.__getRIP_SetReindRIP( inROW, inFulluser['Fulluser'], inTime, wNetaID )
			self.STR_Cope['Ind_On'] += 1
			return
		
		wID = str( inROW['status']['id'] )
		#############################
		# 通知済みか
		#   True=  未通知、通知済みをメモ
		#   False= 通知済み
		if self.__set_RateInd( wID, inTime )==False :
			##通知済み
			self.STR_Cope['Ind_Notified'] += 1
			return
		
		#############################
		# 新リプに設定する
##		### この周では既に通知済みのID
##		wID = str( inROW['id'] )
##		if wID in self.ARR_NowFavID :
##			self.STR_Cope['Ind_Inv'] += 1
##			return
##		self.ARR_NowFavID.append( wID )
##		
##		self.__getRIP_SetNewRIP( inROW, inFulluser, inTime )
		self.__getRIP_SetNewRIP( inROW, inFulluser['Fulluser'], inTime )
		self.STR_Cope['Ind_On'] += 1
		return

##	CLS_OSIF.sPrn( "xxx1: " + wID )

	#####################################################
	# フォロー => フォロー通知
	def __getRIP_Follow( self, inROW, inFulluser, inTime ):
		#############################
		# 除外判定
		### Masterか(=完全スルー)
		if gVal.STR_MasterConfig['MasterUser']==self.Obj_Parent.CHR_Account :
			return
		
		### フォロー通知が有効か
		if gVal.STR_MasterConfig['IND_Follow']!="on" :
			self.STR_Cope['Ind_Inv'] += 1
			return
		
		### ユーザ登録されていた
##		wUserChk = CLS_UserData.sUserCheck( inFulluser )
		wUserChk = CLS_UserData.sUserCheck( inFulluser['Fulluser'] )
		if wUserChk['Result']!=True or wUserChk['Registed']==True :
			self.STR_Cope['Ind_Inv'] += 1
			return
		
##		###外人 (日本人限定=ON時)
##		if inROW['status']['language']!="ja" and gVal.STR_MasterConfig["JPonly"]=="on" :
##			self.STR_Cope['Ind_Inv'] += 1
##			return
		
		###除外ドメイン
		if inFulluser['Domain'] in gVal.STR_DomainREM :
			self.STR_Cope['Ind_Inv'] += 1
			return
		
		### 有効なユーザか
		if self.Obj_Parent.OBJ_UserCorr.IsActiveUser( inFulluser['Fulluser'] )!=True :
			self.STR_Cope['Ind_Inv'] += 1
			return
		
		#############################
		# 新リプに設定する
##		self.__getRIP_SetNewRIP( inROW, inFulluser, inTime )
		self.__getRIP_SetNewRIP( inROW, inFulluser['Fulluser'], inTime )
		self.STR_Cope['Ind_On'] += 1
		return

	#####################################################
	# めんしょん
	def __getRIP_Mention( self, inROW, inFulluser, inTime ):
		#############################
		# 除外判定
		###  Subの場合、リプライブーストが有効か
		if gVal.STR_MasterConfig['MasterUser']!=self.Obj_Parent.CHR_Account and \
		   gVal.STR_MasterConfig['RIP_Favo']!="on" :
			self.STR_Cope['Ind_Inv'] += 1
			return
		
		### statusなし
		if "status" not in inROW :
##			self.STR_Cope['Ind_Inv'] += 1
			self.STR_Cope['Ind_Fail'] += 1
			return
		
##		### directの場合
##		if inROW['status']['visibility']=="direct" :
##			self.STR_Cope['Ind_Inv'] += 1
##			return
##		
##		### ユーザ登録されていた
##		wUserChk = CLS_UserData.sUserCheck( wFulluser['Fulluser'] )
##		if wUserChk['Result']!=True or wUserChk['Registed']==True :
##			self.STR_Cope['Ind_Inv'] += 1
##			return
##		
		
		###外人 (日本人限定=ON時)
		if inROW['status']['language']!="ja" and gVal.STR_MasterConfig["JPonly"]=="on" :
			self.STR_Cope['Ind_Inv'] += 1
			return
		
		###除外ドメイン
		if inFulluser['Domain'] in gVal.STR_DomainREM :
			self.STR_Cope['Ind_Inv'] += 1
			return
		
		### 有効なユーザか
		if self.Obj_Parent.OBJ_UserCorr.IsActiveUser( inFulluser['Fulluser'] )!=True :
			self.STR_Cope['Ind_Inv'] += 1
			return
		
		wCont = CLS_OSIF.sDel_HTML( inROW['status']['content'] )
		### タグ付き(アクション通知以外)
##		if CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['iActionTag'], wCont )>=0 or + \
##		   CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['mTootTag'], wCont )>=0 or + \
##		   CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['prTag'],    wCont )>=0 or + \
##		   CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['TrafficTag'], wCont )>=0 :
##		wRes_1 = CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['iActionTag'], wCont )
##		wRes_2 = CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['mTootTag'], wCont )
##		wRes_3 = CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['prTag'],    wCont )
##		wRes_4 = CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['TrafficTag'], wCont )
##		wRes_5 = CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['SystemTag'], wCont )
##		if wRes_1 or wRes_2 or wRes_3 or wRes_4 :
##		if wRes_1 or wRes_2 or wRes_3 or wRes_4 or wRes_5 :
		wRes_1 = wCont.find( gVal.STR_MasterConfig['iActionTag'] )
		wRes_2 = wCont.find( gVal.STR_MasterConfig['mTootTag'] )
		wRes_3 = wCont.find( gVal.STR_MasterConfig['prTag'] )
		wRes_4 = wCont.find( gVal.STR_MasterConfig['TrafficTag'] )
		wRes_5 = wCont.find( gVal.STR_MasterConfig['SystemTag'] )
		if wRes_1>=0 or wRes_2>=0 or wRes_3>=0 or wRes_4>=0 or wRes_5>=0 :
			self.STR_Cope['Ind_Inv'] += 1
			return
		
		#############################
		# 新リプに設定する
##		### この周では既に通知済みのID
##		wID = str( inROW['id'] )
##		if wID in self.ARR_NowFavID :
##			self.STR_Cope['Ind_Inv'] += 1
##			return
##		self.ARR_NowFavID.append( wID )
##		
##		self.__getRIP_SetNewRIP( inROW, inFulluser, inTime )
		self.__getRIP_SetNewRIP( inROW, inFulluser['Fulluser'], inTime )
		self.STR_Cope['Ind_On'] += 1
		return

	#####################################################
	# 辞書に追加
	def __getRIP_SetNewRIP( self, inROW, inFulluser, inTime ):
		#############################
		# 辞書の枠生成
		wIndex = self.__getRIP_CreateData()
		
		#############################
		# 相手、時間、通知id
		self.ARR_NewTL[wIndex]['type'] = inROW['type']
		self.ARR_NewTL[wIndex]['id']   = str( inROW['id'] )
		self.ARR_NewTL[wIndex]['Fulluser']   = inFulluser
		self.ARR_NewTL[wIndex]['display_name'] = inROW['account']['display_name']
		self.ARR_NewTL[wIndex]['Timedate']   = inTime
		self.ARR_NewTL[wIndex]['created_at'] = inROW['created_at']
		
		#############################
		# トゥートid、コメント
		#   ふぁぼ、ぶーすと、りぷらいの時
		### statusなし
		if "status" in inROW :
			self.ARR_NewTL[wIndex]['visibility'] = inROW['status']['visibility']
			
			self.ARR_NewTL[wIndex]['status_id'] = str(inROW['status']['id'])
			self.ARR_NewTL[wIndex]['content']   = CLS_OSIF.sDel_HTML( inROW['status']['content'] )
			self.ARR_NewTL[wIndex]['spoiler_text'] = CLS_OSIF.sDel_HTML( inROW['status']['spoiler_text'] )
			
			### 画像付き
			self.ARR_NewTL[wIndex]['media_attachments'] = []
			if "media_attachments" in inROW['status'] :
				for wMedia in inROW['status']['media_attachments'] :
					self.ARR_NewTL[wIndex]['media_attachments'].append( wMedia['preview_url'] )
		
		return

	#####################################################
	# 辞書に追加 (通知の再通知)
	def __getRIP_SetReindRIP( self, inROW, inFulluser, inTime, inStatusID ):
		#############################
		# 辞書の枠生成
		wIndex = self.__getRIP_CreateData()
		
		#############################
		# 相手、時間、通知id
		self.ARR_NewTL[wIndex]['type'] = "reind"	##アレンジtype
		self.ARR_NewTL[wIndex]['id']   = str( inROW['id'] )
		self.ARR_NewTL[wIndex]['Fulluser']   = inFulluser
		self.ARR_NewTL[wIndex]['display_name'] = inROW['account']['display_name']
		self.ARR_NewTL[wIndex]['Timedate']   = inTime
		self.ARR_NewTL[wIndex]['visibility'] = inROW['status']['visibility']
		self.ARR_NewTL[wIndex]['created_at'] = inROW['created_at']
		self.ARR_NewTL[wIndex]['status_id']  = str( inStatusID )
		self.ARR_NewTL[wIndex]['content']    = CLS_OSIF.sDel_HTML( inROW['status']['content'] )
		self.ARR_NewTL[wIndex]['spoiler_text'] = CLS_OSIF.sDel_HTML( inROW['status']['spoiler_text'] )
		self.ARR_NewTL[wIndex]['media_attachments'] = []
		return

	#####################################################
	# 辞書枠の生成
	def __getRIP_CreateData(self):
		#############################
		# インデックスの取得
		wKeyList = self.ARR_NewTL.keys()
		wIndex = len( wKeyList )
		
		#############################
		# 辞書の枠生成(第1層)
		self.ARR_NewTL.update({ wIndex : "" })
		self.ARR_NewTL[wIndex] = {}
		self.ARR_NewTL[wIndex].update({ "type"			: "" })
		self.ARR_NewTL[wIndex].update({ "id"			: "" })
		self.ARR_NewTL[wIndex].update({ "Fulluser"		: "" })
		self.ARR_NewTL[wIndex].update({ "display_name"	: "" })
		self.ARR_NewTL[wIndex].update({ "Timedate"		: "" })
		self.ARR_NewTL[wIndex].update({ "visibility"	: "" })
		self.ARR_NewTL[wIndex].update({ "created_at"	: "" })
		self.ARR_NewTL[wIndex].update({ "status_id"		: "" })
		self.ARR_NewTL[wIndex].update({ "content"		: "" })
		self.ARR_NewTL[wIndex].update({ "spoiler_text"	: "" })
		self.ARR_NewTL[wIndex].update({ "media_attachments" : [] })
		return wIndex

	#####################################################
	# 通知元のidを返す
###	def __getIndiTootID( self, inToot ):
	def __getRIP_IndiTootID( self, inToot ):
		#############################
		# URLの検索キー
		wAccount = self.Obj_Parent.CHR_Account.split("@")
		wCHR_Serch = "https://" + wAccount[1] + gVal.DEF_TOOT_SUBURL
		
		wIndex = inToot.find( wCHR_Serch )
		if wIndex==-1 :
			return -1
		
		wIndex = wIndex + len(wCHR_Serch)
		wCHR_id = inToot[wIndex:]
		wCHR_id = wCHR_id.split("#")
		wCHR_id = wCHR_id[0]
		return wCHR_id



#####################################################
# 過去通知取得・保存
#####################################################
	def Get_RateInd(self):
		#############################
		# 読み出し先初期化
		wRateList = []
		
		#############################
		# ファイル読み込み
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['Rate_IndFile']
		if CLS_File.sReadFile( wFile_path, outLine=wRateList )!=True :
			return False	#失敗
		
		#############################
		# 過去ふぁぼの作成
		# 反応時間内のidを詰め込む
		self.ARR_RateInd = {}
		for wLine in wRateList :
			wFavData = wLine.split(",")
			if len(wFavData)<2 :
				continue	#不正
			wGetLag  = CLS_OSIF.sTimeLag( wFavData[1], inThreshold=self.VAL_ReaRIPmin, inTimezone=-1 )
				### *タイムゾーンは補正済
			if wGetLag['Result']!=True :
				continue
##			if wGetLag['Beyond']==True :
###				print("xxA: Beyond: " + wFavData[1] + " RIPmin=" + str(self.VAL_ReaRIPmin) + " Lag=" + str(wGetLag['RateSec']) )
##				continue	#反応時間外
			
			#############################
			# 辞書に詰める
##			self.__set_RateInd( wFavData[0], wFavData[1], True )
			self.__set_RateInd( wFavData[0], wFavData[1], wGetLag['Beyond'] )
		
		return True			#成功

	#####################################################
	def __is_RateInd( self, inID ):
		wKeyList = list( self.ARR_RateInd.keys() )
		if inID not in wKeyList :
			return False	# 未通知
		return True			# 通知済み

	#####################################################
##	def __set_RateInd( self, inID, inCreatedAt, inFlgInit=False ):
	def __set_RateInd( self, inID, inCreatedAt, inFLG_Beyond=False ):
		#############################
		# 通知済みか
		if self.__is_RateInd( inID )==True :
			# 通知の時間が違っていたら情報を更新する
			if self.ARR_RateInd[inID]['created_at']!=inCreatedAt :
				self.ARR_RateInd[inID]['created_at'] = inCreatedAt
				self.ARR_RateInd[inID]['beyond']     = False		#次の周で消す判定させる
			return False	# 通知済みのため詰めない
		
		#############################
		# 辞書に詰める
		self.ARR_RateInd.update({ inID : "" })
		self.ARR_RateInd[inID] = {}
		self.ARR_RateInd[inID].update({ "created_at" : inCreatedAt })
		self.ARR_RateInd[inID].update({ "beyond"     : inFLG_Beyond })
		return True	#成功

	#####################################################
	def Set_RateInd(self):
		#############################
		# 書き込み先初期化
		wRateList = []
		
		#############################
		# リストに詰める
		wKeyList = list( self.ARR_RateInd.keys() )
		for wKey in wKeyList :
			if self.ARR_RateInd[wKey]['beyond']==True :
				continue	#通知解除
			wLine = wKey + "," + self.ARR_RateInd[wKey]['created_at']
			wRateList.append( wLine )
		
		#############################
		# ファイル書き込み (改行つき)
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['Rate_IndFile']
		if CLS_File.sWriteFile( wFile_path, wRateList, inRT=True )!=True :
			return False	#失敗
		
		return True			#成功



#####################################################
# 過去RIP取得・保存
#####################################################
	def Get_RateRIP(self):
		#############################
		# 読み出し先初期化
		self.ARR_RateTL = []
		
		#############################
		# ファイル読み込み
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['Rate_RipFile']
		if CLS_File.sReadFile( wFile_path, outLine=self.ARR_RateTL )!=True :
			return False	#失敗
		
		return True			#成功

	#####################################################
	def Set_RateRIP(self):
		#############################
		# ファイル書き込み (改行つき)
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['Rate_RipFile']
		if CLS_File.sWriteFile( wFile_path, self.ARR_UpdateTL, inRT=True )!=True :
			return False	#失敗
		
		return True			#成功

##	#####################################################
##	def Init_RateRIP(self):
##		#############################
##		# IDを詰め込む
##		self.ARR_UpdateTL = []
##		wKeyList = self.ARR_NewTL.keys()
##		for wKey in wKeyList :
##			self.ARR_UpdateTL.append( self.ARR_NewTL[wKey]['id'] )
##		
##		#############################
##		# ファイル書き込み (改行つき)
##		self.Set_RateRIP()
##		return



#####################################################
# TL解析パターン読み出し
#####################################################
	def Get_Anap(self):
		#############################
		# 読み出し先初期化
		self.ARR_AnapTL = {}
		wAnapList = []	#解析パターンファイル
		
		#############################
		# ファイル読み込み
		wFile_path = gVal.DEF_STR_FILE['PatternRIPFile']
		if CLS_File.sReadFile( wFile_path, outLine=wAnapList )!=True :
			return False	#失敗
		
		#############################
		# データ枠の作成
		wIndex = 0
		for wLine in wAnapList :
			wLine = wLine.split( gVal.DEF_DATA_BOUNDARY )
			if len(wLine)==2 :
				wLine.append("")	#ダミー
			if len(wLine)!=3 :
				continue	#フォーマットになってない
			if wLine[0].find("#")==0 :
				continue	#コメントアウト
			
			self.ARR_AnapTL.update({ wIndex : "" })
			self.ARR_AnapTL[wIndex] = {}
			self.ARR_AnapTL[wIndex].update({ "Kind"    : wLine[0] })
			self.ARR_AnapTL[wIndex].update({ "Pattern" : wLine[1] })
			self.ARR_AnapTL[wIndex].update({ "File"    : wLine[2] })
			wIndex += 1
		
		###なしでもOKとする
		return True			#成功



#####################################################
# 通知制限取得・保存
#####################################################
	def Get_Indlim(self):
		#############################
		# 読み出し先初期化
		wARR_Lim = []
		
		#############################
		# ファイル読み込み
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['IndLim_File']
		if CLS_File.sReadFile( wFile_path, outLine=wARR_Lim )!=True :
			return False	#失敗
		
		wARR_Lim = wARR_Lim[0].split(",")
		if len( wARR_Lim )!= 2 :
			return False	#失敗
		
		#############################
		# データに取り込む
		self.STR_Ind['Count'] = int(wARR_Lim[0])
		self.STR_Ind['TimeDate'] = wARR_Lim[1]
		
		# 0で合わせる
		if self.STR_Ind['Count']==0 or self.STR_Ind['TimeDate']=="" :
			self.STR_Ind['Count'] = 0
			self.STR_Ind['TimeDate'] = ""
			return True		#ノーカウントなら終わり
		
		#############################
		# 制限時間が過ぎたか
		wGetLag = CLS_OSIF.sTimeLag( self.STR_Ind['TimeDate'], inThreshold=self.VAL_indLimmin )
		if wGetLag['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: Get_Indlim: Time lag calculation failure" )
		else :
			if wGetLag['Beyond']==True :
			#############################
			# 通知制限が過ぎたのでクリア
				wFLG_Limit = False
				if self.STR_Ind['Count']>=gVal.DEF_STR_TLNUM['indLimcnt'] :
					wFLG_Limit = True
				self.STR_Ind['Count'] = 0
				self.STR_Ind['TimeDate'] = ""
###				self.Obj_Parent.OBJ_Mylog.Log( 'c', "CLS_LookRIP: Get_Indlim: 通知制限 [解除]" )
				if wFLG_Limit==True :
					###制限中だったら解除ログを出す
					self.Obj_Parent.OBJ_Mylog.Log( 'c', "CLS_LookRIP: Get_Indlim: 通知制限 [解除]" )
		
		return True			#成功

	#####################################################
	def Set_Indlim(self):
		#############################
		# 保存形式を整える
		wARR_Lim = []
		wLim = str(self.STR_Ind['Count']) + "," + self.STR_Ind['TimeDate']
		wARR_Lim.append( wLim )
		
		#############################
		# ファイル書き込み (改行つき)
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['IndLim_File']
		if CLS_File.sWriteFile( wFile_path, wARR_Lim )!=True :
			return False	#失敗
		
		return True			#成功


#####################################################
# 通知制限 判定
#####################################################
	def Check_Indlim( self, inCreateAt ):
		#############################
		# この周回は制限中
		if self.FLG_indLim==True :
			self.STR_Ind['Count'] += 1	#カウントはする
			return False	#制限
		
		#############################
		# 回数チェック
		if self.STR_Ind['Count']<gVal.DEF_STR_TLNUM['indLimcnt'] :
			if self.STR_Ind['Count']==0 :	#最初にカウント開始した時間をメモる
				self.STR_Ind['TimeDate'] = str(inCreateAt)
			return True		#制限なし
		
		# 規制中
		elif self.STR_Ind['Count']>gVal.DEF_STR_TLNUM['indLimcnt'] :
			self.STR_Ind['Count'] += 1	#カウントはする
			self.FLG_indLim = True
			return False	#制限
		
		#############################
		# 制限開始
		####  self.STR_Ind['Count'] == gVal.STR_Config['indLimcnt']
		self.STR_Ind['Count'] += 1	#カウントはする
		self.FLG_indLim = True
		self.Obj_Parent.OBJ_Mylog.Log( 'c', "CLS_LookRIP: Check_Indlim: 通知制限 [開始]" )
		
		#############################
		# 管理者がいれば通知する
		if gVal.STR_MasterConfig['AdminUser']!="" and gVal.STR_MasterConfig['AdminUser']!=self.Obj_Parent.CHR_Account:
##			wToot = "@" + gVal.STR_MasterConfig['AdminUser'] + " " + "[info] 通知制限開始: " + str(gVal.DEF_STR_TLNUM['indLimmin']) + "分"
##			wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wToot, visibility="direct" )
			wCHR_Title = "[通知制限開始]"
			wCHR_Toot  = "@" + gVal.STR_MasterConfig['AdminUser'] + " " + "制限時間: " + str(gVal.DEF_STR_TLNUM['indLimmin']) + "分"
			wCHR_Toot  = wCHR_Toot + '\n' + "#" + gVal.STR_MasterConfig['SystemTag']
			
			wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, spoiler_text=wCHR_Title, visibility="direct" )
			if wRes['Result']!=True :
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: Check_Indlim: Mastodon error: " + wRes['Reason'] )
				return False
		
		return False	#制限



#####################################################
# 指定リプライ返信
#####################################################
	def NormalRipry( self, inFilename, inROW ):
		#############################
		# 候補を取得
		wARR_Line = self.__get_Rip(inFilename)
		
		#############################
		if len(wARR_Line)==0 :
			###候補がみつからない
			return False
		# [0]..Kine
		# [1]..Toot
		
		#############################
		#トゥートの組み立て
		wCHR_Toot = "@" + inROW['Fulluser'] + " " + wARR_Line[1]
		
		#############################
		#トゥート
		wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, visibility=inROW['visibility'] )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: NormalRipry: Mastodon error: " + wRes['Reason'] )
			return False
		
		return True

	#####################################################
	def __get_Rip( self, inFilename ):
		#############################
		# 読み出し先初期化
		wARR_Load = []
		
		#############################
		# ファイル読み込み
		wFile_path = gVal.DEF_STR_FILE['Toot_path'] + inFilename
		if CLS_File.sReadFile( wFile_path, outLine=wARR_Load )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __get_Rip: File read is failure: " + wFile_path )
			return []
		if len(wARR_Load)==0 :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __get_Rip: The file is empty: " + wFile_path )
			return []
		
		#############################
		# 候補一覧を取得する
		wARR_RipKouho = []
		for wLine in wARR_Load :
			###文字がない行
			if len(wLine)==0 :
				continue
			###コメントアウト
			if wLine.find("#")==0 :
				continue
			###フォーマット
			wLine = wLine.split( gVal.DEF_DATA_BOUNDARY )
			if len(wLine)!=2 :
				continue
			wARR_RipKouho.append( wLine )
		
		if len(wARR_RipKouho)==0 :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __get_Rip: Riply kouho is zero" )
			return []
		
		#############################
		# 乱数の取得
		wRand = CLS_OSIF.sGetRand( len(wARR_RipKouho) )
		if wRand<0 :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __get_Rip: sGetRand error: " + str(wRand) )
			return []
		
		#############################
		# リプを出力
		wLine = wARR_RipKouho[wRand]
		return wLine



#####################################################
# 固定リプライ返信
#####################################################
	def OtherReply( self, inROW ):
		#############################
		# 候補を取得
		wCHR_Line = self.__get_RipOther( gVal.DEF_STR_FILE['OtherRIPFile'] )
		
		#############################
		if wCHR_Line=="" :
			###候補がみつからない
			return False
		
		#############################
		#トゥートの組み立て
		wCHR_Toot = "@" + inROW['Fulluser'] + " " + wCHR_Line
		
		#############################
		#トゥート
		wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, visibility=inROW['visibility'] )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: OtherReply: Mastodon error: " + wRes['Reason'] )
			return False
		
		return True

	#####################################################
	def __get_RipOther( self, inFilepath ):
		#############################
		# 読み出し先初期化
		wARR_Load = []
		
		#############################
		# ファイル読み込み
		if CLS_File.sReadFile( inFilepath, outLine=wARR_Load )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __get_RipOther: File read is failure: " + wFile_path )
			return []
		if len(wARR_Load)==0 :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __get_RipOther: The file is empty: " + wFile_path )
			return ""
		
		#############################
		# 候補一覧を取得する
		wARR_RipKouho = []
		for wLine in wARR_Load :
			###文字がない行
			if len(wLine)==0 :
				continue
			###コメントアウト
			if wLine.find("#")==0 :
				continue
			wARR_RipKouho.append( wLine )
		
		if len(wARR_RipKouho)==0 :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __get_RipOther: Riply kouho is zero" )
			return ""
		
		#############################
		# 乱数の取得
		wRand = CLS_OSIF.sGetRand( len(wARR_RipKouho) )
		if wRand<0 :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __get_RipOther: sGetRand error: " + str(wRand) )
			return ""
		
		#############################
		# リプを出力
		wLine = wARR_RipKouho[wRand]
		return wLine



#####################################################
# ワード学習
#####################################################
##	def WordStudy( self, inROW, inPattern ):
	def WordStudy( self, inROW, inSearchAns ):
		#############################
		# 登録単語を取り出す
##		wResReplace = CLS_OSIF.sRe_Replace( inPattern, inROW['content'], "" )
##		###	"Result"	: False,
##		###	"Match"		: False,
##		###	"After"		: None
##		if wResReplace['Result']!=True :
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: WordStudy: sRe_Replace is failed: content=" + str( inROW['content'] ) )
##			return False
##		if wResReplace['Match']!=True :
##			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: WordStudy: Unmatch words: content=" + str( inROW['content'] ) )
##			return False
##		wCont = wResReplace['After']
		wIndex = inSearchAns.start()
		wCont = inROW['content'][wIndex+4:]
		
		#############################
		# 学習する
		wRes = self.Obj_Parent.OBJ_WordCorr.WordStudy( wCont )
		if wRes==True :
			###学習成功
			wCHR_Line = self.__get_RipOther( gVal.DEF_STR_FILE['StudyRIPFile'] )
			if wCHR_Line=="" :
				###候補がみつからない
				return False
			
			wCHR_Line = wCHR_Line + '\n' + "学習した文章: " + wCont
			wVisibility = inROW['visibility']
		else :
			###学習失敗
			wCHR_Line = "この単語は学習できませんでした。: " + wCont
			wVisibility = "direct"
		
		#############################
		#トゥートの組み立て
		wCHR_Toot = "@" + inROW['Fulluser'] + " " + wCHR_Line
		
		#############################
		#トゥート
		wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, visibility=wVisibility )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: WordStudy: Mastodon error: " + wRes['Reason'] )
			return False
		
		return True



#####################################################
# ワードリプライ
#####################################################
	def WordReply( self, inROW ):
		#############################
		# 候補を取得
		wCHR_Line = self.Obj_Parent.OBJ_WordCorr.GetRandToot()
		if wCHR_Line=="" :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: WordReply: GetRandToot is failed" )
			return False
		
		#############################
		#トゥートの組み立て
		wCHR_Toot = "@" + inROW['Fulluser'] + " " + wCHR_Line
		
		#############################
		#トゥート
		wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, visibility=inROW['visibility'] )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: WordReply: Mastodon error: " + wRes['Reason'] )
			return False
		
		return True



