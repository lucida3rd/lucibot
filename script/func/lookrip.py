#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：リプライ監視処理(サブ用)
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/4/18
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

###	ARR_NewTL    = []		#mastodon TL(mastodon API)

	ARR_AnapTL   = []		#TL解析パターン
	ARR_RateTL   = []		#過去TL(id)
	ARR_UpdateTL = []		#新・過去TL(id)

	ARR_RateFV   = []		#過去ふぁぼ(ふぁぼ対象id)
	ARR_UpdateFV = []		#新・過去ふぁぼ(ふぁぼid,時間)

	ARR_NewFavo   = {}		#ふぁぼ or ぶーすと
	ARR_NewFollow = {}		#ふぉろー
	ARR_NewRip    = {}		#リプライ
	ARR_Reind     = {}		#再通知

	STR_Cope = {			#処理カウンタ
		"Ind_Cope"	 : 0,		#今回受信した通知数
		"Ind_On"	 : 0,		#正常処理
		"Ind_Off"	 : 0,		#反応時間外で破棄
		"Ind_Inv"    : 0,		#条件外で破棄
		"Ind_Fail"	 : 0,		#処理失敗で破棄
		
		"Now_Cope"   : 0,		#処理した新トゥート数
		"Now_Favo"   : 0,		#処理したふぁぼ通知
		"Now_Follow" : 0,		#処理したふぉろー通知
		"Now_Rip"    : 0,		#処理したリプ
		"Now_Reind"  : 0,		#処理した再通知
		
		"dummy"     : 0	#(未使用)
	}
	
	STR_Ind = {				#通知制限
		"Count"			: 0,	#通知回数
		"TimeDate"		: ""	#規制時の時間
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
		self.VAL_ReaRIPmin = gVal.STR_Config['reaRIPmin'] * 60	#秒に変換
		
		#############################
		# 通知制限時間の算出(分→秒へ)
		self.VAL_indLimmin = gVal.STR_Config['indLimmin'] * 60	#秒に変換
		
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
		# 通知制限の読み込み
		wRes = self.Get_Indlim()
		if wRes!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __run: Get_Indlim failed" )
			return
		
		#############################
		# RIP読み込み(mastodon)
		wRes = self.Get_RIP()
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __run: Riply read failed: " + wRes['Reason'] )
			return
		
		#############################
		# TL解析パターン読み込み
		###LTLでは実装しない
		
		#############################
		# 過去ふぁぼの読み込み
		wRes = self.Get_RateFV()
		if wRes!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __run: Get_RateFV failed" )
			return
		
		#############################
		# 過去RIPの読み込み
		wRes = self.Get_RateRIP()
		if wRes!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __run: Get_RateRIP failed" )
			return
		
		#############################
		# 現時刻の取得
		wTime = CLS_OSIF.sGetTime()
		if wTime['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __run: Get time failed" )
			return
		
		wTime = str(wTime['TimeDate'])
		
		#############################
		# TLチェック
		self.ARR_UpdateTL = []
		
		#############################
		# ふぁぼ、ぶーすとチェック
		if gVal.STR_Config['IND_Favo']=="on" :
			wKeylist = self.ARR_NewFavo.keys()
			for wKey in wKeylist :
				#############################
				# チェックするので新過去ふぁぼに保管
				wSetFV = self.ARR_NewFavo[wKey]['status_id'] + "," + wTime
				self.ARR_UpdateFV.append( wSetFV )
				
				#############################
				# 過去チェックしたトゥートか
				if self.ARR_NewFavo[wKey]['status_id'] in self.ARR_RateFV :
					continue
				
				#############################
				# 通知制限か
				if self.Check_Indlim( self.ARR_NewFavo[wKey]['created_at'] )==False :
					continue
				
				#############################
				# 新トゥートへの対応
				self.__copeFavo( self.ARR_NewFavo[wKey] )
				self.STR_Cope["Now_Cope"] += 1
			
			wKeylist = self.ARR_Reind.keys()
			for wKey in wKeylist :
				#############################
				# チェックするので新過去ふぁぼに保管
				wSetFV = self.ARR_Reind[wKey]['status_id'] + "," + wTime
				self.ARR_UpdateFV.append( wSetFV )
				
				#############################
				# 過去チェックしたトゥートか
				if self.ARR_Reind[wKey]['status_id'] in self.ARR_RateFV :
					continue
				
				#############################
				# 通知制限か
				if self.Check_Indlim( self.ARR_Reind[wKey]['created_at'] )==False :
					continue
				
				#############################
				# 再通知への対応
				self.__copeReind( self.ARR_Reind[wKey] )
				self.STR_Cope["Now_Cope"] += 1
		
		#############################
		# ふぉろーチェック
		if gVal.STR_Config['IND_Follow']=="on" :
			wKeylist = self.ARR_NewFollow.keys()
			for wKey in wKeylist :
				#############################
				# チェックするので新過去TLに保管
				self.ARR_UpdateTL.append( self.ARR_NewFollow[wKey]['id'] )
				
				#############################
				# 過去チェックしたトゥートか
				if self.ARR_NewFollow[wKey]['id'] in self.ARR_RateTL :
					continue
				
				#############################
				# 新トゥートへの対応
				self.__copeFollow( self.ARR_NewFollow[wKey] )
				self.STR_Cope["Now_Cope"] += 1
		
		#############################
		# リプライチェック
		if gVal.STR_Config['RIP_Favo']=="on" :
			wKeylist = self.ARR_NewRip.keys()
			for wKey in wKeylist :
				#############################
				# チェックするので新過去TLに保管
				self.ARR_UpdateTL.append( self.ARR_NewRip[wKey]['id'] )
				
				#############################
				# 過去チェックしたトゥートか
				if self.ARR_NewRip[wKey]['id'] in self.ARR_RateTL :
					continue
				
				#############################
				# 新トゥートへの対応
				self.__copeRIP( self.ARR_NewRip[wKey] )
				self.STR_Cope["Now_Cope"] += 1
		
		#############################
		# 通知制限の保存
		wRes = self.Set_Indlim()
		if wRes!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __run: Set_Indlim failed" )
###			return
		
		#############################
		# 新・過去ふぁぼ保存
		wRes = self.Set_RateFV()
		if wRes!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __run: Set_RateFV failed" )
###			return
		
		#############################
		# 新・過去RIP保存
		wRes = self.Set_RateRIP()
		if wRes!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __run: Set_RateRIP failed" )
###			return
		
		#############################
		# 処理結果ログ
		wStr = self.CHR_LogName + " 結果: 新Riply=" + str(self.STR_Cope['Now_Cope']) + " Ans=" + str(self.STR_Cope['Now_Rip']) + " Limit=" + str(self.STR_Ind['Count']) + '\n'
		wStr = wStr + "Ind=[Cope:" + str(self.STR_Cope['Ind_Cope']) + " On:" + str(self.STR_Cope['Ind_On']) + " Off:" + str(self.STR_Cope['Ind_Off'])
		wStr = wStr + " Invalid:" + str(self.STR_Cope['Ind_Inv']) + " Failed:" + str(self.STR_Cope['Ind_Fail']) + "]"
		wStr = wStr + " Favo=" + str(self.STR_Cope['Now_Favo']) + " Follow=" + str(self.STR_Cope['Now_Follow']) + " Reind=" + str(self.STR_Cope['Now_Reind'])
		if gVal.FLG_Test_Mode==False :
			self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr )
		else:
			self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr, True )
		
		return



#####################################################
# 新ふぁぼ、ぶーすと通知への対応
#####################################################
	def __copeFavo( self, inROW ) :
		#############################
		# 自アカウント情報
		wAccount = self.Obj_Parent.CHR_Account.split("@")
		
		#############################
		# ファボられたトゥートURL
		wToot_Url = "https://" + wAccount[1] + gVal.DEF_TOOT_SUBURL + inROW['status_id']
		
		#############################
		# spoiler_textが設定されていたら、そちらで通知を出す
		if inROW['spoiler_text'] != "" :
			wCont = inROW['spoiler_text']
		
		#############################
		# トゥートが140字超えの場合、切り払う
		else :
			if len(inROW['content'])>140 :
				wCont = inROW['content'][0:139] + "(以下略)"
			else:
				wCont = inROW['content']
		
		#############################
		# 画像(サムネ)があればURLを付ける
##		for wMediaURL in inROW['media_attachments'] :
##			wCont = wCont + " " + wMediaURL
		if len( inROW['media_attachments'] )>0 :
			wCont = wCont + "【画像あり】"
		
		#############################
		# トゥートの組み立て
		
		#############################
		# CWトゥートで送信
		if gVal.STR_Config['IND_Favo_CW']=="on" :
			#############################
			# タイトルの組み立て
			wSpoText = self.DEF_TITLE_INFORMATION + "注目されたトゥート"
			
			#############################
			# トゥートの組み立て
			wToot = "以下のトゥートが注目されました。:" + '\n'
			wToot = wToot + wCont + " " + gVal.STR_MasterConfig['iFavoTag'] + '\n'
			wToot = wToot + "https://" + wAccount[1] + gVal.DEF_TOOT_SUBURL + inROW['status_id']
			
			#############################
			# 管理者がいれば通知する
			if gVal.STR_MasterConfig['AdminUser']!="" and gVal.STR_MasterConfig['AdminUser']!=self.Obj_Parent.CHR_Account:
				wToot = wToot + '\n' + "[Admin] @" + gVal.STR_MasterConfig['AdminUser']
			
			#############################
			# トゥートの送信
			wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wToot, spoiler_text=wSpoText, visibility=inROW['visibility'] )
		
		#############################
		# ノーマルのトゥートで送信
		else :
			#############################
			# トゥートの組み立て
			wToot = self.DEF_TITLE_INFORMATION + " 以下のトゥートが注目されました。:" + '\n'
			wToot = wToot + wCont + " " + gVal.STR_MasterConfig['iFavoTag'] + '\n'
			wToot = wToot + "https://" + wAccount[1] + gVal.DEF_TOOT_SUBURL + inROW['status_id']
			
			#############################
			# 管理者がいれば通知する
			if gVal.STR_MasterConfig['AdminUser']!="" and gVal.STR_MasterConfig['AdminUser']!=self.Obj_Parent.CHR_Account:
				wToot = wToot + '\n' + "[Admin] @" + gVal.STR_MasterConfig['AdminUser']
			
			#############################
			# トゥートの送信
			wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wToot, visibility=inROW['visibility'] )
		
		#############################
		# 結果判定
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __copeFavo: Mastodon error: " + wRes['Reason'] )
			return
		
		self.STR_Ind['Count'] += 1	#通知制限カウント
		self.STR_Cope['Now_Favo'] += 1
		return



#####################################################
# 新ふぉろー通知への対応
#####################################################
	def __copeFollow( self, inROW ) :
		#############################
		# 自アカウント情報
		wAccount = self.Obj_Parent.CHR_Account.split("@")
		
		#############################
		# トゥートの組み立て
		wToot = self.DEF_TITLE_NEW_FOLLOWER + " " + inROW['display_name'] + " (@" + inROW['Fulluser'] + ") さんにフォローされました。"
		wToot = wToot + " " + gVal.STR_MasterConfig['iFavoTag']
		
		#############################
		# 管理者がいれば通知する
		if gVal.STR_MasterConfig['AdminUser']!="" and gVal.STR_MasterConfig['AdminUser']!=self.Obj_Parent.CHR_Account:
			wToot = wToot + '\n' + "[Admin] @" + gVal.STR_MasterConfig['AdminUser']
		
		#############################
		# トゥートの送信
		wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wToot, visibility=inROW['visibility'] )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __copeFollow: Mastodon error: " + wRes['Reason'] )
			return
		
		self.STR_Cope['Now_Follow'] += 1
		return



#####################################################
# 再通知への対応
#####################################################
	def __copeReind( self, inROW ) :
		#############################
		# トゥートの組み立て
		
		#############################
		# CWトゥートで送信
		if gVal.STR_Config['IND_Favo_CW']=="on" :
			wSpoText = inROW['spoiler_text']
			wToot    = inROW['content']
			
			#############################
			# トゥートの送信
			wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wToot, spoiler_text=wSpoText, visibility=inROW['visibility'] )
		
		#############################
		# ノーマルのトゥートで送信
		else :
			wToot = inROW['content']
			
			#############################
			# トゥートの送信
			wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wToot, visibility=inROW['visibility'] )
		
		#############################
		# 結果判定
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __copeReind: Mastodon error: " + wRes['Reason'] )
			return
		
		self.STR_Ind['Count'] += 1	#通知制限カウント
		self.STR_Cope['Now_Reind'] += 1
		return



#####################################################
# 新リプライへの対応
#####################################################
	def __copeRIP( self, inROW ) :
		#############################
		# directかprivateリプライの場合はニコる
		if inROW['visibility']=="direct" or \
		   ( inROW['visibility']=="private" and gVal.STR_Config['IND_Favo_Unl']!="on" ) :

			wRes = self.Obj_Parent.OBJ_MyDon.Favo( inROW['status_id'] )
			if wRes['Result']!=True :
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __copeRIP: Favo error: " + wRes['Reason'] )
				return
		
		#############################
		# public、unlistedの場合はブーストする
		else :
			wRes = self.Obj_Parent.OBJ_MyDon.Boost( inROW['status_id'] )
			if wRes['Result']!=True :
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: __copeRIP: Boost error: " + wRes['Reason'] )
				return
		
		self.STR_Cope['Now_Rip'] += 1
		return



#####################################################
# RIP取得
#####################################################
	def Get_RIP(self):
###		self.ARR_NewTL = []
		self.ARR_NewFavo   = {}		#ふぁぼ
		self.ARR_NewReblog = {}		#ぶーすと
		self.ARR_NewFollow = {}		#ふぉろー
		self.ARR_NewRip    = {}		#リプライ
		
		wGet_TootList = []
		wNext_Id = None
		wMax_Toots = gVal.STR_Config["getRIPnum"]
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
		wFavID = []
		for wToot in wGet_TootList :
			self.STR_Cope['Ind_Cope'] += 1
			
			#############################
			# トゥートの時間 (変換＆差)
			wGetLag = CLS_OSIF.sTimeLag( str(wToot['created_at']), inThreshold=self.VAL_ReaRIPmin )
			if wGetLag['Result']!=True :
				self.STR_Cope['Ind_Fail'] += 1
				continue
			if wGetLag['Beyond']==True :
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
			if ( wToot['type']=="favourite" or wToot['type']=="reblog" ) \
			  and gVal.STR_Config['IND_Favo']=="on" :
				### タグなしcontents
				wCont = CLS_OSIF.sDel_HTML( wToot['status']['content'] )
				wInde = wCont.find( "[Admin]" )
				if wInde>=0 :
					wCont = wCont[0:wInde]
				
				### @ 入り(リプライ)のふぁぼ、ブーストは通知しない
				if wCont.find("@") >= 0 :
					self.STR_Cope['Ind_Inv'] += 1
					continue
				### directの場合、通知しない
				if wToot['status']['visibility']=="direct" :
					self.STR_Cope['Ind_Inv'] += 1
					continue
				### privateの場合、configで有効でなければ通知しない
				if wToot['status']['visibility']=="private" and gVal.STR_Config['IND_Favo_Unl']!="on" :
					self.STR_Cope['Ind_Inv'] += 1
					continue
				### ユーザ登録されていたら通知しない
				wUserChk = CLS_UserData.sUserCheck( wFulluser['Fulluser'] )
				if wUserChk['Result']!=True or wUserChk['Registed']==True :
					self.STR_Cope['Ind_Inv'] += 1
					continue
				
				### 通知のふぁぼ、ぶーすとか
				if wCont.find( gVal.STR_MasterConfig['iFavoTag'] ) >= 0 :
					### ふぉろー通知のふぁぼ、ぶーすとは通知しない
					if wCont.find( self.DEF_TITLE_NEW_FOLLOWER ) == 0 :
						self.STR_Cope['Ind_Inv'] += 1
						continue
					
					### 通知の再通知
					### 通知元のトゥートidを抜き出す
					wID = self.__getIndiTootID( wCont )
					if wID==-1 :
						self.STR_Cope['Ind_Inv'] += 1
						continue
					
##					CLS_OSIF.sPrn( "xxx1: " + wID )
					### この周では既に通知を出してるid
					if wID in wFavID :
						self.STR_Cope['Ind_Inv'] += 1
						continue
					
					wFavID.append( wID )	#被り防止
					self.__setReindRIP( self.ARR_Reind, wFulluser['Fulluser'], wGetTime, wToot, wID )
					self.STR_Cope['Ind_On'] += 1
					continue
				
				wID = str(wToot['status']['id'])
				### この周では既に通知を出してるid
				if wID in wFavID :
					self.STR_Cope['Ind_Inv'] += 1
					continue
				
				wFavID.append( wID )	#被り防止
				self.__setNewRIP( self.ARR_NewFavo, wFulluser['Fulluser'], wGetTime, wToot )
				self.STR_Cope['Ind_On'] += 1
			
			#############################
			# ふぉろー
			elif wToot['type']=="follow" and gVal.STR_Config['IND_Follow']=="on" :
				### ユーザ登録されていたら通知しない
				wUserChk = CLS_UserData.sUserCheck( wFulluser['Fulluser'] )
				if wUserChk['Result']!=True or wUserChk['Registed']==True :
					self.STR_Cope['Ind_Inv'] += 1
					continue
				
				self.__setNewRIP( self.ARR_NewFollow, wFulluser['Fulluser'], wGetTime, wToot )
				self.STR_Cope['Ind_On'] += 1
			
			#############################
			# めんしょん
			elif wToot['type']=="mention" and gVal.STR_Config['RIP_Favo']=="on" :
				### 通知付きのめんしょんは反応しない(=adminへの通知)
				wCont = CLS_OSIF.sDel_HTML( wToot['status']['content'] )
				if wCont.find( gVal.STR_MasterConfig['iFavoTag'] ) >= 0 :
					self.STR_Cope['Ind_Inv'] += 1
					continue
				
				### PRトゥートには反応しない(=adminへの通知)
				if wCont.find( gVal.STR_MasterConfig['prTag'] ) >= 0 :
					self.STR_Cope['Ind_Inv'] += 1
					continue
				
				### ユーザ登録されていたら反応しない(恥ずかしい)
				wUserChk = CLS_UserData.sUserCheck( wFulluser['Fulluser'] )
				if wUserChk['Result']!=True or wUserChk['Registed']==True :
					self.STR_Cope['Ind_Inv'] += 1
					continue
				
				self.__setNewRIP( self.ARR_NewRip, wFulluser['Fulluser'], wGetTime, wToot )
				self.STR_Cope['Ind_On'] += 1
			
			#############################
			# その他(あるの？)
			else:
				self.STR_Cope['Ind_Inv'] += 1
		
		return wRes

	#####################################################
	# 辞書に追加
	def __setNewRIP( self, outARRrip, inFulluser, inTime, inToot ):
		#############################
		# 辞書の枠生成
		wIndex = len( outARRrip )
		outARRrip.update({ wIndex : "" })
		outARRrip[wIndex] = {}
		
		#############################
		# 相手、時間、通知id
		outARRrip[wIndex].update({ "id"           : str( inToot['id'] ) })
		outARRrip[wIndex].update({ "Fulluser"     : inFulluser })
		outARRrip[wIndex].update({ "display_name" : inToot['account']['display_name'] })
		outARRrip[wIndex].update({ "Timedate"     : inTime })
		outARRrip[wIndex].update({ "visibility"   : "public" })
		outARRrip[wIndex].update({ "created_at"   : inToot['created_at'] })
		
		#############################
		# 公開範囲
		if "status" in inToot :
			outARRrip[wIndex]['visibility'] = inToot['status']['visibility']
		
		#############################
		# トゥートid、コメント
		#   ふぁぼ、ぶーすと、りぷらいの時
		outARRrip[wIndex].update({ "status_id" : None })
		outARRrip[wIndex].update({ "content"   : None })
		outARRrip[wIndex].update({ "spoiler_text"      : None })
		outARRrip[wIndex].update({ "media_attachments" : [] })
		
		if "status" in inToot :
			outARRrip[wIndex]['status_id'] = str(inToot['status']['id'])
			outARRrip[wIndex]['content']   = CLS_OSIF.sDel_HTML( inToot['status']['content'] )
			outARRrip[wIndex]['spoiler_text'] = CLS_OSIF.sDel_HTML( inToot['status']['spoiler_text'] )
			if "media_attachments" in inToot['status'] :
				for wMedia in inToot['status']['media_attachments'] :
					outARRrip[wIndex]['media_attachments'].append( wMedia['preview_url'] )
		
		return

	#####################################################
	# 辞書に追加 (通知の再通知)
	def __setReindRIP( self, outARRrip, inFulluser, inTime, inToot, inStatusID ):
		#############################
		# 辞書の枠生成
		wIndex = len( outARRrip )
		outARRrip.update({ wIndex : "" })
		outARRrip[wIndex] = {}
		
		wCont = inToot['status']['content']
		wCont = wCont.replace( "</span></a></p><p>[Admin] <span class=\"h-card\">", '\n'+"[Admin] " )
		wCont = wCont.replace( "<br />", '\n' )
		wCont = CLS_OSIF.sDel_HTML( wCont )
		
		#############################
		# 相手、時間、通知id
		outARRrip[wIndex].update({ "id"           : str( inToot['id'] ) })
		outARRrip[wIndex].update({ "Fulluser"     : inFulluser })
		outARRrip[wIndex].update({ "display_name" : inToot['account']['display_name'] })
		outARRrip[wIndex].update({ "Timedate"     : inTime })
		outARRrip[wIndex].update({ "visibility"   : inToot['status']['visibility'] })
		outARRrip[wIndex].update({ "created_at"   : inToot['created_at'] })
		outARRrip[wIndex].update({ "status_id" : str( inStatusID ) })
		outARRrip[wIndex].update({ "content"   : wCont })
		outARRrip[wIndex].update({ "spoiler_text"      : CLS_OSIF.sDel_HTML( inToot['status']['spoiler_text'] ) })
		outARRrip[wIndex].update({ "media_attachments" : [] })
		return

	#####################################################
	# 通知元のidを返す
	def __getIndiTootID( self, inToot ):
		#############################
		# URLの検索キー
		wAccount = self.Obj_Parent.CHR_Account.split("@")
		wCHR_Serch = "https://" + wAccount[1] + gVal.DEF_TOOT_SUBURL
		
		wIndex = inToot.find( wCHR_Serch )
		if wIndex==-1 :
			return -1
		
		wIndex = wIndex + len(wCHR_Serch)
		wCHR_id = inToot[wIndex:]
		wCHR_id = wCHR_id.split("[Admin]")
		wCHR_id = wCHR_id[0]
		return wCHR_id



#####################################################
# 過去ふぁぼ取得・保存
#####################################################
	def Get_RateFV(self):
		#############################
		# 読み出し先初期化
		wRateList = []
		
		#############################
		# ファイル読み込み
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.STR_File['Rate_FavFile']
		if CLS_File.sReadFile( wFile_path, outLine=wRateList )!=True :
			return False	#失敗
		
		#############################
		# 過去ふぁぼの作成
		# 反応時間内のidを詰め込む
		self.ARR_RateFV = []
		for wLine in wRateList :
			wFavData = wLine.split(",")
			wGetLag  = CLS_OSIF.sTimeLag( wFavData[1], inThreshold=self.VAL_ReaRIPmin )
			if wGetLag['Result']!=True :
				continue
			if wGetLag['Beyond']==True :
				continue	#反応時間外
			
			self.ARR_RateFV.append( wFavData[0] )
		
		return True			#成功

	#####################################################
	def Set_RateFV(self):
		#############################
		# ファイル書き込み (改行つき)
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.STR_File['Rate_FavFile']
		if CLS_File.sWriteFile( wFile_path, self.ARR_UpdateFV, inRT=True )!=True :
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
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.STR_File['Rate_RipFile']
		if CLS_File.sReadFile( wFile_path, outLine=self.ARR_RateTL )!=True :
			return False	#失敗
		
		return True			#成功

	#####################################################
	def Set_RateRIP(self):
		#############################
		# ファイル書き込み (改行つき)
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.STR_File['Rate_RipFile']
		if CLS_File.sWriteFile( wFile_path, self.ARR_UpdateTL, inRT=True )!=True :
			return False	#失敗
		
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
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.STR_File['IndLim_File']
		if CLS_File.sReadFile( wFile_path, outLine=wARR_Lim )!=True :
			return False	#失敗
		
		wARR_Lim = wARR_Lim[0].split(",")
		if len( wARR_Lim )!= 2 :
			return False	#失敗
		
		#############################
		# データに取り込む
		self.STR_Ind['Count'] = int(wARR_Lim[0])
		self.STR_Ind['TimeDate'] = wARR_Lim[1]
		
		#############################
		# 制限時間が過ぎたか
		wGetLag = CLS_OSIF.sTimeLag( self.STR_Ind['TimeDate'], inThreshold=self.VAL_indLimmin )
		if wGetLag['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookRIP: Get_Indlim: Time lag calculation failure" )
		else :
			if wGetLag['Beyond']==True :
			#############################
			# 通知制限が過ぎたので制限解除
				self.STR_Ind['Count'] = 0
				self.STR_Ind['TimeDate'] = ""
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
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.STR_File['IndLim_File']
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
		if self.STR_Ind['Count']<gVal.STR_Config['indLimcnt'] :
			return True		#制限なし
		
		#############################
		# 規制中
		if self.STR_Ind['TimeDate']!="" :
			self.STR_Ind['Count'] += 1	#カウントはする
			self.FLG_indLim = True
			return False	#制限
		
		#############################
		# 制限開始
		self.STR_Ind['Count'] += 1	#カウントはする
		self.STR_Ind['TimeDate'] = str(inCreateAt)
		self.FLG_indLim = True
		self.Obj_Parent.OBJ_Mylog.Log( 'c', "CLS_LookRIP: Check_Indlim: 通知制限 [開始]" )
		
		#############################
		# 管理者がいれば通知する
		if gVal.STR_MasterConfig['AdminUser']!="" and gVal.STR_MasterConfig['AdminUser']!=self.Obj_Parent.CHR_Account:
			wToot = "@" + gVal.STR_MasterConfig['AdminUser'] + " " + "[info] 通知制限開始: " + str(gVal.STR_Config['indLimmin']) + "分"
			wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wToot, visibility="direct" )
		
		return False	#制限



