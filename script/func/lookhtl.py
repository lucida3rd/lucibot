#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：HTL監視処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/9/13
#####################################################
# Private Function:
#   __run(self):
#   __cope( self, inROW ) :
#
# Instance Function:
#   __init__( self, parentObj=None ):	※親クラス実体を設定すること
#   Get_HTL(self):
#   Get_RateLTL(self):
#   Set_RateLTL(self):
#   Get_Anap(self):
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
class CLS_LookHTL():
#####################################################
	CHR_LogName  = "HTL監視"
	Obj_Parent   = ""		#親クラス実体

	ARR_NewTL    = []		#mastodon TL(mastodon API)
	ARR_AnapTL   = {}		#TL解析パターン
	ARR_RateTL   = []		#過去TL(id)
	ARR_UpdateTL = []		#新・過去TL(id)

	STR_Cope = {				#処理カウンタ
		"Now_Cope"		: 0,	#処理した新トゥート数
		"Now_Boot"		: 0,	#今ブーストした数
		"Now_Twitter"	: 0,	#今ブーストした数
		
		"OffTime"		: 0,	#時間外で未処理
		"Outrange"		: 0,	#範囲外
		"Invalid"		: 0,	#その他の除外
		"dummy"			: 0		#(未使用)
	}



#####################################################
# Init
#####################################################
	def __init__( self, parentObj=None ):
		if parentObj==None :
			###親クラス実体の未設定
			CLS_OSIF.sPrn( "CLS_LookHTL: __init__: You have not set the parent class entity for parentObj" )
			return
		
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
		wRes = self.Get_Anap()
		if wRes!=True :
			return	#失敗 or パターンなし
		
		#############################
		# HTL読み込み(mastodon)
		wRes = self.Get_HTL()
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookHTL: __run: HTL read failed: " + wRes['Reason'] )
			return
		
		#############################
		# 過去HTLの読み込み
		wRes = self.Get_RateHTL()
		if wRes!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookHTL: __run: Get_RateHTL failed" )
			return
		if len(self.ARR_RateTL)==0 :
			self.Init_RateHTL()
			if gVal.FLG_Test_Mode==False :
				self.Obj_Parent.OBJ_Mylog.Log( 'b', self.CHR_LogName + " HTL過去TL初期化" )
			else :
				self.Obj_Parent.OBJ_Mylog.Log( 'b', self.CHR_LogName + " HTL過去TL初期化", inView=True )
			return
		
		#############################
		# TLチェック
		self.ARR_UpdateTL = []
		for wROW in self.ARR_NewTL :
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
			# 新トゥートへの対応
			self.__cope( wROW )
			self.STR_Cope["Now_Cope"] += 1
		
		#############################
		# 新・過去HTL保存
		wRes = self.Set_RateHTL()
		if wRes!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookHTL: __run: Set_RateHTL failed" )
			return
		
		#############################
		# 処理結果ログ
		wStr = self.CHR_LogName + " 結果: 新Toot=" + str(self.STR_Cope['Now_Cope'])
		wStr = wStr + " Boost=" + str(self.STR_Cope['Now_Boot'])
		wStr = wStr + " Twitter=" + str(self.STR_Cope['Now_Twitter'])
		wStr = wStr + " OffTime=" + str(self.STR_Cope['OffTime'])
		wStr = wStr + " Outrange=" + str(self.STR_Cope['Outrange'])
		wStr = wStr + " Invalid=" + str(self.STR_Cope['Invalid'])

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
		# ユーザ名の変換
		wFulluser = CLS_UserData.sGetFulluser( inROW['account']['username'], inROW['account']['url'] )
		if wFulluser['Result']!=True :
			###今のところ通らないルート
			return False
		
		#############################
		# トゥートからHTMLタグを除去
		wCont = CLS_OSIF.sDel_HTML( inROW['content'] )
		
		#############################
		# 収集判定(一括)
		if self.__copeCorr( wFulluser, inROW, wCont )!=True :
			self.STR_Cope['Outrange'] += 1
			return	### 除外
		
		#############################
		# トゥートの時間 (変換＆差)
		wReaRIPmin = gVal.DEF_STR_TLNUM['reaRIPmin'] * 60	#秒に変換
		wGetLag = CLS_OSIF.sTimeLag( str(inROW['created_at']), inThreshold=wReaRIPmin )
		if wGetLag['Result']!=True :
			self.STR_Cope['Invalid'] += 1
			return
		if wGetLag['Beyond']==True :
			self.STR_Cope['OffTime'] += 1
			return	#反応時間外
		wGetTime = str(wGetLag['InputTime'])
		
		#############################
		#解析種類の判定
		wKeyList = self.ARR_AnapTL.keys()
		for wKey in wKeyList :
			#############################
			# 解析：ついったー転送
			if self.ARR_AnapTL[wKey]['Kind']=="t" and gVal.STR_MasterConfig['Twitter']=="on" :
				### ハード監視ユーザか
				if CLS_UserData.sCheckHardUser( self.Obj_Parent.CHR_Account )!=True :
					continue
				
				### 自分が指定ユーザか
				if self.ARR_AnapTL[wKey]['Fulluser']!="" :
					if self.ARR_AnapTL[wKey]['Fulluser']!=self.Obj_Parent.CHR_Account :
						continue
				### 無指定の場合、登録ユーザか(第三者避け)
				else :
					wUserList = CLS_UserData.sGetUserList()
					if wFulluser['Fulluser'] not in wUserList :
						continue
				
				### マッチチェック
				wPatt = "#" + self.ARR_AnapTL[wKey]['Tag']
				wRes = CLS_OSIF.sRe_Search( wPatt, wCont )
				if not wRes :
					##アンマッチ
					continue
				### 実行
				if self.TwitterBoost( inROW['id'] )!=True :
					self.STR_Cope['Invalid'] += 1
				else :
					self.STR_Cope["Now_Twitter"] += 1
			
			#############################
			# 解析：指定ブースト
			if self.ARR_AnapTL[wKey]['Kind']=="h" :
				### 自分のトゥートか
				if wFulluser['Fulluser'] == self.Obj_Parent.CHR_Account :
					continue	#自分
				
				### 自分が指定ユーザではない
				if self.ARR_AnapTL[wKey]['Fulluser']!="" :
					if self.ARR_AnapTL[wKey]['Fulluser']!=self.Obj_Parent.CHR_Account :
						continue
				### 無指定の場合、登録ユーザか(第三者避け)
				else :
					wUserList = CLS_UserData.sGetUserList()
					if wFulluser['Fulluser'] not in wUserList :
						continue
				
				### マッチチェック
				wPatt = "#" + self.ARR_AnapTL[wKey]['Tag']
				wRes = CLS_OSIF.sRe_Search( wPatt, wCont )
				if not wRes :
					##アンマッチ
					continue
				### 実行
				if self.Boost( inROW['id'] )!=True :
					self.STR_Cope['Invalid'] += 1
					break
				self.STR_Cope["Now_Boot"] += 1
				break
			
			#############################
			# 解析：指定フルブースト
			if self.ARR_AnapTL[wKey]['Kind']=="p" :
				### 自分のトゥートか
				if wFulluser['Fulluser'] == self.Obj_Parent.CHR_Account :
					continue	#自分
				
				### 自分が指定ユーザではない
				if self.ARR_AnapTL[wKey]['Fulluser']!=self.Obj_Parent.CHR_Account :
					continue	#指定ではない
				
				#対象のブーストユーザか
				if self.ARR_AnapTL[wKey]['Tag']!=wFulluser :
					continue	#指定ではない
				
				### 実行
				if self.Boost( inROW['id'] )!=True :
					self.STR_Cope['Invalid'] += 1
					break
				self.STR_Cope["Now_Boot"] += 1
				break
		
		return

	#####################################################
	def __copeCorr( self, inUser, inROW, inCont ):
		#############################
		# 除外トゥート
##		### 自分
##		if inUser['Fulluser'] == self.Obj_Parent.CHR_Account :
##			return False
		
		### 公開トゥート以外
		if inROW['visibility']!="public" :
			return False
		
		### ブーストトゥートは除外
		if inROW['reblog']!=None :
			return False
		
		### リプライは除外（先頭に@付きトゥート）
		if inCont.find('@') == 0 :
			return False
		
		### 通知類は除外
		wRes_1 = CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['iActionTag'], inCont )
		wRes_2 = CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['mTootTag'], inCont )
		wRes_3 = CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['prTag'],    inCont )
		wRes_4 = CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['TrafficTag'], inCont )
		wRes_5 = CLS_OSIF.sRe_Search( gVal.STR_MasterConfig['SystemTag'], inCont )
##		if wRes_1 or wRes_2 or wRes_3 or wRes_4 :
		if wRes_1 or wRes_2 or wRes_3 or wRes_4 or wRes_5 :
			return False
		
		return True



#####################################################
# 新トゥートへの対応
#####################################################
#	def __cope( self, inROW ) :
###		wHitPatt = []
#		
#		#公開トゥート以外は除外
#		if inROW['visibility']!="public" :
#			self.STR_Cope['Outrange'] += 1
#			return
#		
#		wCont = CLS_OSIF.sDel_HTML( inROW['content'] )
#		#リプライは除外（先頭に@付きトゥート）
#		if wCont.find('@') == 0 :
#			self.STR_Cope['Outrange'] += 1
#			return
#		
#		#通知は除外
##		if wCont.find( gVal.STR_MasterConfig['iFavoTag'] ) >= 0 :
#		if wCont.find( gVal.STR_MasterConfig['iActionTag'] ) >= 0 :
#			self.STR_Cope['Outrange'] += 1
#			return
#		
#		#ブーストトゥートは除外
#		if inROW['reblog']!=None :
#			self.STR_Cope['Outrange'] += 1
#			return
#		
#		#############################
#		# 相手ユーザ名
#		wFulluser = CLS_UserData.sGetFulluser( inROW['account']['username'], inROW['account']['url'] )
#		if wFulluser['Result']!=True :
#			self.STR_Cope['Invalid'] += 1
#			return
#		wFulluser = wFulluser['Fulluser']
#		#自分ならスキップ
#		if wFulluser == self.Obj_Parent.CHR_Account :
#			self.STR_Cope['Invalid'] += 1
#			return
#		
#		#############################
#		# トゥートの時間 (変換＆差)
###		wReaRIPmin = gVal.STR_Config['reaRIPmin'] * 60	#秒に変換
#		wReaRIPmin = gVal.DEF_STR_TLNUM['reaRIPmin'] * 60	#秒に変換
#		wGetLag = CLS_OSIF.sTimeLag( str(inROW['created_at']), inThreshold=wReaRIPmin )
#		if wGetLag['Result']!=True :
#			self.STR_Cope['Invalid'] += 1
#			return
#		if wGetLag['Beyond']==True :
#			self.STR_Cope['OffTime'] += 1
#			return	#反応時間外
#		wGetTime = str(wGetLag['InputTime'])
#		
#		wKeylist  = self.ARR_AnapTL.keys()
#		#############################
#		#解析種類の判定
#		for wKey in wKeylist :
#			wKind = self.ARR_AnapTL[wKey]['Kind']
#			
#			#############################
#			#解析：ブースト
#			if wKind == 'h' :
####				#############################
####				#既に同じ処理をしたか
###				if CLS_UserData.sChkHitPatt( wHitPatt, wKind )==True :
###					continue	#既に同じ処理した
#				
#				#############################
#				#自分が指定ユーザか
#				if self.ARR_AnapTL[wKey]['Fulluser']!="" :
#					if self.ARR_AnapTL[wKey]['Fulluser']!=self.Obj_Parent.CHR_Account :
#						continue
#				
#				#############################
#				#無指定の場合、登録ユーザか(第三者避け)
#				else :
#					wUserList = CLS_UserData.sGetUserList()
#					if wFulluser not in wUserList :
#						continue
#				
#				#############################
#				#パターンマッチ
#				wPatt = "#" + self.ARR_AnapTL[wKey]['Tag']
#				wMatch = CLS_OSIF.sRe_Search( wPatt, wCont )
#				if wMatch :
#					wRes = self.Obj_Parent.OBJ_MyDon.Boost( inROW['id'] )
#					if wRes['Result']!=True :
#						self.STR_Cope['Invalid'] += 1
#						return	#失敗
#					
#					self.STR_Cope["Now_Boot"] += 1
###					wHitPatt.append( wKind )
#					break	# 1つの実行で止めておく
#		
#			#############################
#			#解析：指定フルブースト
#			if wKind == 'p' :
###				#############################
###				#既に同じ処理をしたか
###				if CLS_UserData.sChkHitPatt( wHitPatt, wKind )==True :
###					continue	#既に同じ処理した
#				
#				#############################
#				#自分が指定ユーザではない
#				if self.ARR_AnapTL[wKey]['Fulluser']!=self.Obj_Parent.CHR_Account :
#					continue	#指定ではない
#				
#				#############################
#				#対象のブーストユーザか
#				if self.ARR_AnapTL[wKey]['Tag']==wFulluser :
#					wRes = self.Obj_Parent.OBJ_MyDon.Boost( inROW['id'] )
#					if wRes['Result']!=True :
#						self.STR_Cope['Invalid'] += 1
#						return	#失敗
#					
#					self.STR_Cope["Now_Boot"] += 1
###					wHitPatt.append( wKind )
#					break	# 1つの実行で止めておく
#		
#		return
#
#

#####################################################
# HTL取得
#####################################################
	def Get_HTL(self):
		self.ARR_NewTL = []
		wNext_Id = None
		wMax_Toots = gVal.DEF_STR_TLNUM["getHTLnum"]
		while (len(self.ARR_NewTL) < wMax_Toots ):
			#############################
			# TL取得
			wRes = self.Obj_Parent.OBJ_MyDon.GetHomeTL( limit=40, max_id=wNext_Id )
			if wRes['Result']!=True :
				return wRes	#失敗
			
			wGet_Toots = wRes['Responce']	#toot list(json形式)
			
			#############################
			# 新しいトゥートが取得できなかったらループ終了
			if len( wGet_Toots ) > 0:
				self.ARR_NewTL += wGet_Toots
			else:
				break
			
			#############################
			# configの最大取得数を超えていたらループ終了
			if len( self.ARR_NewTL ) >= wMax_Toots :
				break
			
			#############################
			# ページネーション(次の40件を取得する設定)
			try:
				wNext_Id = wGet_Toots[-1]['id']
			except:
				###ありえない
				wRes['Reason'] = "CLS_LookHTL: Get_HTL: Page nation error"
				wRes['Result'] = False
				return wRes
		
		return wRes



#####################################################
# 過去HTL取得・保存
#####################################################
	def Get_RateHTL(self):
		#############################
		# 読み出し先初期化
		self.ARR_RateTL = []
		
		#############################
		# ファイル読み込み
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['Rate_HTLFile']
		if CLS_File.sReadFile( wFile_path, outLine=self.ARR_RateTL )!=True :
			return False	#失敗
		
		return True			#成功

	#####################################################
	def Set_RateHTL(self):
		#############################
		# ファイル書き込み (改行つき)
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['Rate_HTLFile']
		if CLS_File.sWriteFile( wFile_path, self.ARR_UpdateTL, inRT=True )!=True :
			return False	#失敗
		
		return True			#成功

	#####################################################
	def Init_RateHTL(self):
		#############################
		# IDを詰め込む
		self.ARR_UpdateTL = []
		for wROW in self.ARR_NewTL :
			self.ARR_UpdateTL.append( wROW['id'] )
		
		#############################
		# ファイル書き込み (改行つき)
		self.Set_RateHTL()
		return



#####################################################
# TL解析パターン読み込み
#####################################################
	def Get_Anap(self):
		#############################
		# 読み出し先初期化
		self.ARR_AnapTL = {}
		wAnapList = []	#解析パターンファイル
		
		#############################
		# ファイル読み込み
		wFile_path = gVal.DEF_STR_FILE['HTLBoostFile']
		if CLS_File.sReadFile( wFile_path, outLine=wAnapList )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookHTL: Get_Anap: HTLBoostFile read failed: " + wFile_path )
			return False	#失敗
		
		#############################
		# データ枠の作成
		wIndex = 0
		for wLine in wAnapList :
			wLine = wLine.split( gVal.DEF_DATA_BOUNDARY )
			if len(wLine)!=3 :
				continue	#フォーマットになってない
			if wLine[0].find("#")==0 :
				continue	#コメントアウト
			
			self.ARR_AnapTL.update({ wIndex : "" })
			self.ARR_AnapTL[wIndex] = {}
			self.ARR_AnapTL[wIndex].update({ "Kind"     : wLine[0] })
			self.ARR_AnapTL[wIndex].update({ "Tag"      : wLine[1] })
			self.ARR_AnapTL[wIndex].update({ "Fulluser" : wLine[2] })
			wIndex += 1
		
		if len(self.ARR_AnapTL)==0 :
			self.Obj_Parent.OBJ_Mylog.Log( 'c', "CLS_LookHTL: Get_Anap: HTLBoostFile in none pattern: " + wFile_path )
			return False	#パターンなし
		
		return True



#####################################################
# ブースト
#####################################################
	def Boost( self, inID ) :
		#############################
		#ブースト
		wRes = self.Obj_Parent.OBJ_MyDon.Boost( id=inID )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookHTL: Boost: Mastodon error: " + wRes['Reason'] )
			return False
		
		return True



#####################################################
# ついったー転送
#####################################################
	def TwitterBoost( self, inID ) :
		#############################
		# ユーザ名の変換
		wFulluser = CLS_UserData.sUserCheck( self.Obj_Parent.CHR_Account )
		if wFulluser['Result']!=True :
			###今のところ通らないルート
			return False
		wDomain = wFulluser['Domain']
		
		#############################
		# ファボられたトゥートURL
		wToot_Url = "https://" + wDomain + gVal.DEF_TOOT_SUBURL + str(inID)
		wCHR_Tweet = "mastodonから転送:" + '\n' + wToot_Url
		
		#############################
		# Twitterへ投稿
		wRes = self.Obj_Parent.OBJ_Twitter.Tweet( wCHR_Tweet )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookHTL: TwitterBoost: Mastodon error: " + wRes['Reason'] )
			return False
		
		return True



