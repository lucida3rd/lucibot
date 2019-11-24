#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：Twitterリーダ処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/11/24
#####################################################
# Private Function:
#   __checkTwitterPatt( self, inROW ):
#   __getTwitterPatt(self):
#
# Instance Function:
#   __init__( self, parentObj=None ):
#   __run(self):
#   Send_Toot(self):
#   Send_Trend(self):
#   Set_DBctrl_Twitter(self):
#   Get_DBctrl_Twitter(self):
#   Sended_DBctrl_Twitter(self):
#   Delete_DBctrl_Twitter(self):
#   Get_TwitterTL(self):
#   Get_RateTwitterTL(self):
#
# Class Function(static):
#   (none)
#
#####################################################
from postgresql_use import CLS_PostgreSQL_Use

from osif import CLS_OSIF
from filectrl import CLS_File
from userdata import CLS_UserData
from gval import gVal
#####################################################
class CLS_TwitterReader():
#####################################################
	CHR_LogName  = "Twitterリーダ処理"
	Obj_Parent = ""				#親クラス実体
	
	ARR_NewTL    = []			#Twitter TL(API)
	ARR_AnapTL   = {}			#TL解析パターン
	ARR_RateTL   = []			#過去TL(id)
	ARR_UpdateTL = []			#新・過去TL(id)

	ARR_Twitter = {}			#今回処理するトゥート

	STR_Cope = {				#処理カウンタ
		"Now_Cope"		: 0,	#処理したトレンド数
		
		"Twitter"		: 0,	#取得ツイート数
		"Sended"		: 0,	#トゥート送信数
		"TrendSended"	: 0,	#Trendトゥート送信数
		
		"Insert"		: 0,	#DB挿入
		"Update"		: 0,	#DB更新
		"Delete"		: 0,	#DB削除
		
		"dummy"			: 0		#(未使用)
	}

	DEF_SENDRANGE = [
		'unlisted',
		'private'
	]
	
	DEF_SENDRANGE_TREND = "private"
	DEF_MAX_TREND       = 10
	
##	CHR_SendRange   = "unlisted"
	DEF_SENDRANGE   = "unlisted"
	CHR_TrendSender = ""

#####################################################
# Init
#####################################################
	def __init__( self, parentObj=None ):
		if parentObj==None :
			###親クラス実体の未設定
			CLS_OSIF.sPrn( "CLS_TwitterReader: __init__: You have not set the parent class entity for parentObj" )
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
		# Twitterリーダ パターン読み込み
		if self.__getTwitterPatt()!=True :
			return
		
		#############################
		# トレンドの送信
		if gVal.FLG_Test_Mode==False :
			# 1時間経ってる周回か
			if gVal.STR_TimeInfo['OneHour']==True and \
			   self.CHR_TrendSender==self.Obj_Parent.CHR_Account :
				self.Send_Trend()
		else :
			###テストモード時
			if self.CHR_TrendSender==self.Obj_Parent.CHR_Account :
				self.Send_Trend()
		
		#############################
		# Twitterから取得
		#   ハード監視ユーザ 1つのみで実行
		if CLS_UserData.sCheckHardUser( self.Obj_Parent.CHR_Account )==True :
			#############################
			# 送信済レコードを削除
			# ・1時間経ってる周回か
			if gVal.STR_TimeInfo['OneHour']==True :
				self.Delete_DBctrl_Twitter()
			
			#############################
			# Twitterタイムライン取得
			if self.Get_TwitterTL()!=True :
				return
			
			#############################
			# 過去TLの読み込み
			wRes = self.Get_RateTwitterTL()
			if wRes!=True :
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: __run: Get_RateTwitterTL failed" )
				return
			if len(self.ARR_RateTL)==0 :
				self.Init_RateTwitterTL()
				if gVal.FLG_Test_Mode==False :
					self.Obj_Parent.OBJ_Mylog.Log( 'b', self.CHR_LogName + " Twitter過去TL初期化" )
				else :
					self.Obj_Parent.OBJ_Mylog.Log( 'b', self.CHR_LogName + " Twitter過去TL初期化", inView=True )
				return
			
			#############################
			# 新規ツイートを辞書に収める
			self.ARR_Twitter = {}
			wIndex = 0
			
			self.ARR_UpdateTL = []
			for wROW in self.ARR_NewTL :
				#############################
				# チェックするので新過去TLに保管
				self.ARR_UpdateTL.append( wROW['id'] )
				
				#############################
				# 過去チェックしたトゥートはスキップ
				wFlg_Rate = False
				for wRow_Rate in self.ARR_RateTL :
					if str(wRow_Rate) == str(wROW['id']) :
						wFlg_Rate = True
						break
				
				if wFlg_Rate == True :
					continue
				
				#############################
				# パターンチェック
				wRes_check = self.__checkTwitterPatt( wROW )
				if wRes_check['result']!=True :
					continue
				
				#############################
				# 格納
				self.ARR_Twitter.update({ wIndex : "" })
				self.ARR_Twitter[wIndex] = {}
				self.ARR_Twitter[wIndex].update({ "id"   : str(wROW['id']) })
				self.ARR_Twitter[wIndex].update({ "text" : str(wROW['text']) })
				self.ARR_Twitter[wIndex].update({ "screen_name" : str(wROW['user']['screen_name']) })
				self.ARR_Twitter[wIndex].update({ "send_user"   : wRes_check['send_user'] })
				self.ARR_Twitter[wIndex].update({ "tags"        : wRes_check['tags'] })
				self.ARR_Twitter[wIndex].update({ "lupdate" : "" })
				self.ARR_Twitter[wIndex].update({ "sended" : False })
				#更新時間 (twitter時間)
				wTime = CLS_OSIF.sGetTimeformat_Twitter( wROW['created_at'] )
				if wTime['Result']!=True :
					self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: __run: sGetTimeformat_Twitter is failed" )
					continue
				self.ARR_Twitter[wIndex]['lupdate'] = wTime['TimeDate']
				
				wIndex += 1
				self.STR_Cope["Now_Cope"] += 1
			
			#############################
			# 新・過去LTL保存
			wRes = self.Set_RateTwitterTL()
			if wRes!=True :
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: __run: Set_RateTwitterTL failed" )
				return
			
			#############################
			# DBに格納
			self.Set_DBctrl_Twitter()
		
		#############################
		# トゥート送信
		self.Send_Toot()
		
		#############################
		# 処理結果ログ
		wStr = self.CHR_LogName + " 結果: Cope=" + str(self.STR_Cope['Now_Cope'])
		wStr = wStr + " Twitter=" + str(self.STR_Cope['Twitter'])
		wStr = wStr + " Sended=" + str(self.STR_Cope['Sended'])
		wStr = wStr + " DB=[Insert:" + str(self.STR_Cope['Insert']) + " Update:" + str(self.STR_Cope['Update']) + " Delete:" + str(self.STR_Cope['Delete']) + "]"
		if self.STR_Cope['TrendSended']>0 :
			wStr = wStr + " Trend Sended"
		
		if gVal.FLG_Test_Mode==False :
			self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr )
		else:
			self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr, inView=True )
		
		return



#####################################################
# トゥート送信
#####################################################
	def Send_Toot(self):
		#############################
		# DB制御  取出
		self.Get_DBctrl_Twitter()
		
		#############################
		# 送信データなし
		wKeylist = self.ARR_Twitter.keys()
		if len(	wKeylist )==0 :
			return
		
		#############################
		# 送信
		for wKey in wKeylist :
			#############################
			# トゥートの組み立て
			wCHR_Title = "Transfer from Twitter:" + '\n'
			
			wCHR_Body = ""
			### Body
			wText = self.ARR_Twitter[wKey]['text'].replace( '\n', '' )
			wText = CLS_OSIF.sDel_URL( wText )	#URLを除去
			wCHR_Body = wCHR_Body + wText + '\n'
			
			### Source: User / Timedate / URL
			wCHR_Body = wCHR_Body + "--[Source: " + str(self.ARR_Twitter[wKey]['lupdate']) + "]--" + '\n'
			wCHR_Body = wCHR_Body + "User: " + self.ARR_Twitter[wKey]['screen_name'] + " "
			wCHR_Body = wCHR_Body + "https://twitter.com/" + self.ARR_Twitter[wKey]['screen_name'] + "/status/" + str(self.ARR_Twitter[wKey]['id']) + '\n'
			
			### add Tags
			wCHR_Tags = ""
			if self.ARR_Twitter[wKey]['tags']!="" :
				wARR_Tags = self.ARR_Twitter[wKey]['tags'].split(",")
				for wTag in wARR_Tags :
					wCHR_Tags = wCHR_Tags + " #" + wTag
			
##			wCHR_Toot = wCHR_Title + wCHR_Body + "#" + gVal.STR_MasterConfig['TwitterReaderTag']
			wCHR_Toot = wCHR_Title + wCHR_Body + "#" + gVal.STR_MasterConfig['TwitterReaderTag'] + wCHR_Tags
			
			#############################
			# トゥートの送信
##			wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, visibility=self.CHR_SendRange )
			wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, visibility=self.DEF_SENDRANGE )
			if wRes['Result']!=True :
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: Send_Trend: Mastodon error: " + wRes['Reason'] )
				return
			
			self.ARR_Twitter[wKey]['sended'] = True
			#############################
			# カウント
			self.STR_Cope['Sended'] += 1
		
		#############################
		# DB制御  送信済にチェック
		self.Sended_DBctrl_Twitter()
		return



#####################################################
# トレンド送信
#####################################################
	def Send_Trend(self):
		#############################
		# Twitterトレンド取得
		wRes = self.Obj_Parent.OBJ_Twitter.GetTrends()
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: Send_Trend: Twitter API Error: " + wRes['Reason'] )
			return False
		
		if len(wRes['Responce'])==0 :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: Send_Trend: Twitter Trends get is Zero" )
			return False
		
		if 'trends' not in wRes['Responce'][0] :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: Send_Trend: Twitter Trends data is not exist" )
			return False
		
		#############################
		# 時刻の取り出し
		wTime = CLS_OSIF.sGetTimeformat_Twitter( wRes['Responce'][0]['created_at'] )
		wGetTimeDate = None
		if wTime['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: Send_Trend: sGetTimeformat_Twitter is failed" )
			return False
		wGetTimeDate = wTime['TimeDate']
		
		#############################
		# トレンドの取り出し
		wARR_Trends = wRes['Responce'][0]['trends']
		
		#############################
		# トゥートの組み立て
		wCHR_Title = "Twitter Trend"
		
		wCHR_Body = ""
		wIndex    = 0
		for wLine in wARR_Trends :
			#############################
			# 最大数
			if self.DEF_MAX_TREND<=wIndex :
				break
			
			wInd = wLine['name'].find("#")
			if wInd<0 :
				wLine['name'] = "#" + wLine['name']
			
			### Body
			wCHR_Body = wCHR_Body + wLine['name']
			### Point
			if wLine['tweet_volume']!=None :
				wCHR_Body = wCHR_Body + " (" + str(wLine['tweet_volume']) + ")"
			wCHR_Body = wCHR_Body + '\n' + '\n'
			
			wIndex += 1
		
		if wIndex==0 :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: Send_Trend: Trend Body size is zero" )
			return
		
		wCHR_Body = wCHR_Body + "[" + wGetTimeDate + "] "
		wCHR_Body = wCHR_Body + "#" + gVal.STR_MasterConfig['TwitterReaderTag'] + '\n'
		
		wCHR_Toot = wCHR_Body + "**上から最新順 (Top " + str(self.DEF_MAX_TREND) + " Tag)" + '\n' + "**() タグ使用数"
		#############################
		# トゥートの送信
		wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, spoiler_text=wCHR_Title, visibility=self.DEF_SENDRANGE_TREND )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: Send_Trend: Mastodon error: " + wRes['Reason'] )
			return
		
		#############################
		# カウント
		self.STR_Cope['TrendSended'] += 1
		
		return



#####################################################
# DB制御  Twitter格納
#####################################################
	def Set_DBctrl_Twitter(self):
		#############################
		# DB接続
		wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: Set_DBctrl_Twitter: DB Connect test is failed: " + wRes['Reason'] )
			wOBJ_DB.Close()
			return
		
		wKeyList = self.ARR_Twitter.keys()
		#############################
		# ダブりがないかチェック
		# ・なければ追加
		# ・あれば更新
		for wKey in wKeyList :
			wQuery = "select * from TBL_TWITTER_READER where id = '" + self.ARR_Twitter[wKey]['id'] + "' ;"
			wDBRes = wOBJ_DB.RunQuery( wQuery )
			wDBRes = wOBJ_DB.GetQueryStat()
			if wDBRes['Result']!=True :
				##失敗
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: Set_DBctrl_Twitter: Run Query is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
				wOBJ_DB.Close()
				return False
			
			wFLG_Update = False
			wText = str(self.ARR_Twitter[wKey]['text']).replace( "'", "''" )
			#############################
			# クエリの作成
			if self.ARR_Twitter[wKey]['tags']=="" :
				self.ARR_Twitter[wKey]['tags'] = "(none)"	# SQL用補完
			
			###なければ追加
			if len(wDBRes['Responce']['Data'])==0 :
				wQuery = "insert into TBL_TWITTER_READER values (" + \
							str( self.ARR_Twitter[wKey]['id'] ) + "," + \
							"'" + wText + "'," + \
							"'" + self.ARR_Twitter[wKey]['screen_name'] + "'," + \
							"'" + self.ARR_Twitter[wKey]['send_user'] + "'," + \
							"'" + self.ARR_Twitter[wKey]['tags'] + "'," + \
							"'" + self.ARR_Twitter[wKey]['lupdate'] + "'," + \
							str( self.ARR_Twitter[wKey]['sended'] ) + " " + \
							") ;"
			
			###あれば更新
			else :
				wChgList = []
				if wOBJ_DB.ChgList( wDBRes['Responce']['Data'], outList=wChgList )!=True :
					##ないケースかも
					self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: AddUser: Select data is Zero" )
					wOBJ_DB.Close()
					return False
				wChgList = wChgList[0]	#1行しかないし切る
				
				wQuery = "update TBL_TWITTER_READER set " + \
						"text = '" + wText + "', " + \
						"screen_name = '" + str(self.ARR_Twitter[wKey]['screen_name']) + "', " + \
						"send_user = '"   + str(self.ARR_Twitter[wKey]['send_user']) + "', " + \
						"tags = '"    + str(self.ARR_Twitter[wKey]['tags']) + "', " + \
						"lupdate = '" + str(self.ARR_Twitter[wKey]['lupdate']) + "', " + \
						"sended = "   + str(self.ARR_Twitter[wKey]['sended']) + " " + \
						"where id = '" + wChgList[0] + "' ;"
				
				wFLG_Update = True
			
			#############################
			# クエリ実行
			wDBRes = wOBJ_DB.RunQuery( wQuery )
			wDBRes = wOBJ_DB.GetQueryStat()
			if wDBRes['Result']!=True :
				##失敗
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: AddUser: DB insert is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
				wOBJ_DB.Close()
				return False
			
			#############################
			# カウント
			if wFLG_Update==True :
				self.STR_Cope['Update'] += 1
			else :
				self.STR_Cope['Insert'] += 1
		
		#############################
		# 正常終了
		wOBJ_DB.Close()
		return



#####################################################
# DB制御  取出
#####################################################
	def Get_DBctrl_Twitter(self):
		#############################
		# DB接続
		wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: Get_DBctrl_Twitter: DB Connect test is failed: " + wRes['Reason'] )
			wOBJ_DB.Close()
			return
		
		#############################
		# 取り出し
		wQuery = "select * from TBL_TWITTER_READER ;"
		
		wRes = wOBJ_DB.RunQuery( wQuery )
		wRes = wOBJ_DB.GetQueryStat()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: Get_DBctrl_Twitter: Run Query is failed: " + wRes['Reason'] + " query=" + wRes['Query'] )
			wOBJ_DB.Close()
			return
		
		if len(wRes['Responce']['Data'])==0 :
			##トレンド情報なし
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: Get_DBctrl_Twitter: TBL_TWITTER_READER record is 0" )
			wOBJ_DB.Close()
			return
		
		#############################
		# 一回ローカルに読み出す
		wARR_Twitter = {}
		wIndex       = 0
		for wLineTap in wRes['Responce']['Data'] :
			##領域の準備
			wARR_Twitter.update({ wIndex : "" })
			wARR_Twitter[wIndex] = {}
			wARR_Twitter[wIndex].update({ "id"   : 0 })
			wARR_Twitter[wIndex].update({ "text"   : "" })
			wARR_Twitter[wIndex].update({ "screen_name" : "" })
			wARR_Twitter[wIndex].update({ "send_user"   : "" })
			wARR_Twitter[wIndex].update({ "tags"        : "" })
			wARR_Twitter[wIndex].update({ "lupdate" : "" })
			wARR_Twitter[wIndex].update({ "sended"  : False })
			
			##取り出し
			wGetTap = []
			for wCel in wLineTap :
				wGetTap.append( wCel )
				## [0] ..id
				## [1] ..text
				## [2] ..screen_name
				## [3] ..send_user
				## [4] ..tags
				## [5] ..lupdate
				## [6] ..sended
			
			##領域へロード
			wARR_Twitter[wIndex]['id']   = int( wGetTap[0] )
			wARR_Twitter[wIndex]['text'] = wGetTap[1].strip()
			wARR_Twitter[wIndex]['screen_name'] = wGetTap[2].strip()
			wARR_Twitter[wIndex]['send_user']   = wGetTap[3].strip()
			wARR_Twitter[wIndex]['lupdate']     = wGetTap[5]
			wARR_Twitter[wIndex]['sended']      = wGetTap[6]
			
			wGetTap[4] = wGetTap[4].strip()
			if wGetTap[4]=="(none)" :
				wGetTap[4] = ""			# null設定
			wARR_Twitter[wIndex]['tags'] = wGetTap[4]
			
			wIndex += 1
		
		#############################
		# DB切断
		wOBJ_DB.Close()
		
		#############################
		# 未送信のものを読みだす
		self.ARR_Twitter = {}
		
		wKeylist = wARR_Twitter.keys()
		wIndex   = 0
		for wKey in wKeylist :
			if wARR_Twitter[wKey]['sended']==True :
				continue	#送信済
			if wARR_Twitter[wKey]['send_user']!=self.Obj_Parent.CHR_Account :
				continue	#送信者ではない
			
			#############################
			# 格納
			self.ARR_Twitter.update({ wIndex : "" })
			self.ARR_Twitter[wIndex] = {}
			self.ARR_Twitter[wIndex].update({ "id"   : wARR_Twitter[wKey]['id'] })
			self.ARR_Twitter[wIndex].update({ "text" : wARR_Twitter[wKey]['text'] })
			self.ARR_Twitter[wIndex].update({ "screen_name" : wARR_Twitter[wKey]['screen_name'] })
			self.ARR_Twitter[wIndex].update({ "send_user"   : wARR_Twitter[wKey]['send_user'] })
			self.ARR_Twitter[wIndex].update({ "tags"        : wARR_Twitter[wKey]['tags'] })
			self.ARR_Twitter[wIndex].update({ "lupdate"     : wARR_Twitter[wKey]['lupdate'] })
			self.ARR_Twitter[wIndex].update({ "sended"      : False })
			wIndex += 1
		
		return



#####################################################
# DB制御  送信済
#####################################################
	def Sended_DBctrl_Twitter(self):
		#############################
		# DB接続
		wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: Sended_DBctrl_Twitter: DB Connect test is failed: " + wRes['Reason'] )
			wOBJ_DB.Close()
			return
		
		#############################
		# 更新
		wQuery = "update TBL_TWITTER_READER set " + \
					"sended = True " + \
					"where "
		
		wKeylist = self.ARR_Twitter.keys()
		wLen = len( wKeylist )
		wIndex = 0
		for wKey in wKeylist :
			if self.ARR_Twitter[wKey]['sended']==True :
				wQuery = wQuery + "id = '" + str(self.ARR_Twitter[wKey]['id']) + "'"
			
			self.STR_Cope['Update'] += 1
			wIndex += 1
			if wLen>wIndex :
				wQuery = wQuery + " or "
		
		wQuery = wQuery + " ;"
		
		#############################
		# クエリ実行
		wDBRes = wOBJ_DB.RunQuery( wQuery )
		wDBRes = wOBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: Sended_DBctrl_Twitter: DB insert is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
			wOBJ_DB.Close()
			return
		
		#############################
		# DB切断
		wOBJ_DB.Close()
		
		return



#####################################################
# DB制御  削除
#####################################################
	def Delete_DBctrl_Twitter(self):
		#############################
		# DB接続
		wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: Delete_DBctrl_Twitter: DB Connect test is failed: " + wRes['Reason'] )
			wOBJ_DB.Close()
			return
		
		#############################
		# 削除対象レコード数
		wQuery = "select * from TBL_TWITTER_READER where sended = True ;"
		wDBRes = wOBJ_DB.RunQuery( wQuery )
		wDBRes = wOBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: Delete_DBctrl_Twitter: Run Query is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
			wOBJ_DB.Close()
			return False
		
		wDeleteNum = len(wDBRes['Responce']['Data'])
		
		#############################
		# 削除
		wQuery = "delete from TBL_TWITTER_READER where " + \
					"sended = True " + \
					";"
		
		#############################
		# クエリ実行
		wDBRes = wOBJ_DB.RunQuery( wQuery )
		wDBRes = wOBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: Delete_DBctrl_Twitter: DB insert is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
			wOBJ_DB.Close()
			return
		
		self.STR_Cope['Delete'] += wDeleteNum
		#############################
		# DB切断
		wOBJ_DB.Close()
		
		return



#####################################################
# Twitterリーダ パターンチェック
#####################################################
	def __checkTwitterPatt( self, inROW ):
		wRes = {
			"result"    : False,
			"send_user" : "",
			"tags"      : "" }
		
		wKeylist = self.ARR_AnapTL.keys()
		wFlg_Hit = False
		for wKey in wKeylist :
##			if self.ARR_AnapTL[wKey]['user']==str(inROW['user']['screen_name']) :
##				wFlg_Hit = True
##				break		#対象ツイートユーザ
			if self.ARR_AnapTL[wKey]['user']!=str(inROW['user']['screen_name']) :
				#対象ツイートユーザではない
				continue
			
			if self.ARR_AnapTL[wKey]['patt']=="" :
##				continue
				#対象ツイートユーザ かつ パターン設定なし：Hitあり
				wFlg_Hit = True
				break
			
			wRes_Search = CLS_OSIF.sRe_Search( self.ARR_AnapTL[wKey]['patt'], str(inROW['text']) )
			if wRes_Search :
				#対象ツイートユーザ かつ パターンヒット：Hitあり
				wFlg_Hit = True
				break
		
		### Hitあり
		if wFlg_Hit==True :
			wRes['send_user'] = self.ARR_AnapTL[wKey]['send']
			wRes['tags']      = self.ARR_AnapTL[wKey]['tags']
			wRes['result']    = True
		
		return wRes



#####################################################
# Twitterタイムライン取得
#####################################################
	def Get_TwitterTL(self):
		self.ARR_NewTL = []
		
		#############################
		# 取得
		wRes = self.Obj_Parent.OBJ_Twitter.GetTL()
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: Get_TwitterTL: Twitter API Error: " + wRes['Reason'] )
			return False
		
		#############################
		# ローカルに取得
		for wROW in wRes['Responce'] :
##			print( "id: " + str(wROW['id']) )
##			print( "text: " + str(wROW['text']) )
##			print( "user: " + str(wROW['user']['name']) + "(@" + str(wROW['user']['screen_name']) + ")" )
##			print( "country: " + wROW['lang'] )
#############################
# ツイート除外(mastodon健全化)
# ・いかがわしいツイート
# ・鍵垢
##			if "possibly_sensitive" not in wROW :
##				continue
			if wROW['user']['protected']==True :
				continue
			
#############################
			self.ARR_NewTL.append( wROW )
			self.STR_Cope["Twitter"] += 1
		
		return True



#####################################################
# 過去TL取得・保存・初期化
#####################################################
	def Get_RateTwitterTL(self):
		#############################
		# 読み出し先初期化
		self.ARR_RateTL = []
		
		#############################
		# ファイル読み込み
		wFile_path = gVal.DEF_MASTERCONFIG + gVal.DEF_STR_FILE['TweetFile']
		if CLS_File.sReadFile( wFile_path, outLine=self.ARR_RateTL )!=True :
			return False	#失敗
		
		return True			#成功

	#####################################################
	def Set_RateTwitterTL(self):
		#############################
		# ファイル書き込み (改行つき)
		wFile_path = gVal.DEF_MASTERCONFIG + gVal.DEF_STR_FILE['TweetFile']
		if CLS_File.sWriteFile( wFile_path, self.ARR_UpdateTL, inRT=True )!=True :
			return False	#失敗
		
		return True			#成功

	#####################################################
	def Init_RateTwitterTL(self):
		#############################
		# IDを詰め込む
		self.ARR_UpdateTL = []
		for wROW in self.ARR_NewTL :
			self.ARR_UpdateTL.append( wROW['id'] )
		
		#############################
		# ファイル書き込み (改行つき)
		self.Set_RateTwitterTL()
		return



#####################################################
# Twitterリーダ パターン読み込み
#####################################################
	def __getTwitterPatt(self):
		#############################
		# 読み出し先初期化
		self.ARR_AnapTL = {}
		wARR_TwitterReader = []	#解析パターンファイル
		
		#############################
		# ファイル読み込み
		wFile_path = gVal.DEF_STR_FILE['TwetterReaderFile']
		if CLS_File.sReadFile( wFile_path, outLine=wARR_TwitterReader )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_TwitterReader: __getTwitterPatt: TwetterReaderFile read failed: " + wFile_path )
			return False	#失敗
		
		#############################
		# パターンの詰め込み
		wIndex = 0
		for wLine in wARR_TwitterReader :
			wLine = wLine.split( gVal.DEF_DATA_BOUNDARY )
			if len(wLine)==2 :
##				#############################
##				# 範囲
##				if wLine[0]=="r" :
##					if wLine[1] in self.DEF_SENDRANGE :
##						self.CHR_SendRange = wLine[1]
##				
##				elif wLine[0]=="T" and self.CHR_TrendSender=="" :
				#############################
				# トレンド送信ユーザ
				if wLine[0]=="T" and self.CHR_TrendSender=="" :
					self.CHR_TrendSender = wLine[1]
				
				continue
			
##			if len(wLine)!=4 :
			if len(wLine)!=5 :
				continue	#フォーマットになってない
			if wLine[0].find("#")==0 :
				continue	#コメントアウト
			
			#############################
			# アカウント
			if wLine[0]=="P" :
				self.ARR_AnapTL.update({ wIndex : "" })
				self.ARR_AnapTL[wIndex] = {}
				self.ARR_AnapTL[wIndex].update({ "user" : wLine[1] })
				self.ARR_AnapTL[wIndex].update({ "patt" : wLine[2] })
				self.ARR_AnapTL[wIndex].update({ "send" : wLine[3] })
				self.ARR_AnapTL[wIndex].update({ "tags" : wLine[4] })
				wIndex += 1
		
		return True



