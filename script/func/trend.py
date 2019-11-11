#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：トレンド処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/11/11
#####################################################
# Private Function:
#   __getTrafficPatt(self):
#
# Instance Function:
#   __init__( self, inPath ):
#   Countup(self):
#   Update(self):
#   SendTraffic(self):
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
class CLS_Trend():
#####################################################
	CHR_LogName  = "トレンド処理"
	Obj_Parent = ""				#親クラス実体
	
	FLG_Valid  = False			#トレンド対象
	ARR_Trend  = {}

								#**パターン解析からロードする
	ARR_SendDomain = []			#トレンド通知対象ドメイン
	DEF_SENDRANGE  = "private"

#####################################################
# Init
#####################################################
	def __init__( self, parentObj=None ):
		if parentObj==None :
			###親クラス実体の未設定
			CLS_OSIF.sPrn( "CLS_Trend: __init__: You have not set the parent class entity for parentObj" )
			return
		
		self.Obj_Parent = parentObj
		self.FLG_Valid  = CLS_UserData.sCheckTrafficUser( self.Obj_Parent.CHR_Account )
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
		# 1時間経ってる周回か
#		if gVal.STR_TimeInfo['OneHour']==False :
#			return	#周回ではない
		
		#############################
		# トレンドパターン読み込み
		if self.__getTrendPatt()!=True :
			return
		
		#############################
		# 取得処理対象か
		if self.FLG_Valid==True :
			#############################
			# 取得
			self.Get_Trend()
		
		#############################
		# トレンド送信
		### MasterUserか
		if gVal.STR_MasterConfig['MasterUser']==self.Obj_Parent.CHR_Account :
			#############################
			# 送信
			self.Send_Trend()
		
		return




#####################################################
# トレンド取得
#####################################################
	def Get_Trend(self):
		#############################
		# ドメインの抽出
		wDomain = self.Obj_Parent.CHR_Account.split("@")
		if len(wDomain)!=2 :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Trend: Get_Trend: Illigal admin_id: " + self.Obj_Parent.CHR_Account )
			return
		wDomain = wDomain[1]
		
		#############################
		# トレンド取得対象のドメインか
		if wDomain not in self.ARR_SendDomain :
			self.Obj_Parent.OBJ_Mylog.Log( 'c', "トレンド取得対象外のドメイン" )
			return
		
		#############################
		# mastodonからトレンド取得
		wRes = self.__getTrends()
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Trend: Get_Trend: Trend read failed: " + wRes['Reason'] )
			return
		
		#############################
		# DB接続
		wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Trend: Get_Trend: DB Connect test is failed: " + wRes['Reason'] )
			wOBJ_DB.Close()
			return
		
		#############################
		# 自ドメインのトレンド情報を一旦削除
		wQuery = "delete from TBL_TREND where domain = '" + wDomain + "'" + \
				";"
		wDBRes = wOBJ_DB.RunQuery( wQuery )
		wDBRes = wOBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Trend: Get_Trend: Run Query is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
			wOBJ_DB.Close()
			return
		
		#############################
		# 最新のトレンド情報を追加
		wKeyList = self.ARR_Trend.keys()
		wRank = 1
		for wKey in self.ARR_Trend :
			wQuery = "insert into TBL_TREND values (" + \
						str(wRank) + "," + \
						"'" + self.ARR_Trend[wKey]['name'] + "'," + \
						"'" + wDomain + "'," + \
						str(self.ARR_Trend[wKey]['uses']) + "," + \
						str(self.ARR_Trend[wKey]['accs']) + " " + \
						") ;"
			
			wDBRes = wOBJ_DB.RunQuery( wQuery )
			wDBRes = wOBJ_DB.GetQueryStat()
			if wDBRes['Result']!=True :
				##失敗
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Trend: Get_Trend: Run Query is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
				wOBJ_DB.Close()
				return
			wRank += 1
		
		#############################
		# 正常終了
		wOBJ_DB.Close()
		return

	def __getTrends(self):
		self.ARR_Trend = {}
		wARR_Trend = []
		wARR_SetTrend = {}
		#############################
		# TL取得
		wRes = self.Obj_Parent.OBJ_MyDon.GetTrends()
		if wRes['Result']!=True :
			return wRes	#失敗
		
		wARR_Trend = wRes['Responce']	#toot list(json形式)
		
		###sample
		# {'name': 'introduction',
		#  'url': 'https://fedibird.com/tags/introduction',
		#  'history': [
		#    {'day': '1573430400', 'uses': '1', 'accounts': '1'},
		#    {'day': '1573344000', 'uses': '8', 'accounts': '8'},
		#    {'day': '1573257600', 'uses': '4', 'accounts': '3'},
		#    {'day': '1573171200', 'uses': '37', 'accounts': '31'},
		#    {'day': '1573084800', 'uses': '19', 'accounts': '17'},
		#    {'day': '1572998400', 'uses': '1', 'accounts': '1'},
		#    {'day': '1572912000', 'uses': '0', 'accounts': '0'}]}

		#############################
		# 情報を丸めこむ
		wIndex = 0
		wRank = 1
		for wLine in wARR_Trend :
			#############################
			# トレンド値を計算
			#   2時間以内のタグ利用数、使用ユーザ数？
			wUses = 0
			wAccs = 0
			if len(wLine['history'])>=2 :
				wUses = int(wLine['history'][0]['uses']) + int(wLine['history'][1]['uses'])
				wAccs = int(wLine['history'][0]['accounts']) + int(wLine['history'][1]['accounts'])
			
			#############################
			# 辞書に詰める
			self.ARR_Trend.update({ wIndex : "" })
			self.ARR_Trend[wIndex] = {}
			self.ARR_Trend[wIndex].update({ "rank" : wRank })
			self.ARR_Trend[wIndex].update({ "name" : wLine['name'] })
##			self.ARR_Trend[wIndex].update({ "url"  : wLine['url'] })
			self.ARR_Trend[wIndex].update({ "uses" : wUses })
			self.ARR_Trend[wIndex].update({ "accs" : wAccs })
			wRank  += 1
			wIndex += 1

###
#			wARR_SetTrend.update({ wIndex : "" })
#			wARR_SetTrend[wIndex] = {}
#			wARR_SetTrend[wIndex].update({ "name" : wLine['name'] })
##			wARR_SetTrend[wIndex].update({ "url"  : wLine['url'] })
#			wARR_SetTrend[wIndex].update({ "uses" : wUses })
#			wARR_SetTrend[wIndex].update({ "accs" : wAccs })
#			wIndex += 1
#		
#		#############################
#		# ソート
#		wKeyList = wARR_SetTrend.keys()
#		### 1以下はソートしない
#		if len(wKeyList)==0 :
#			return wRes
#		if len(wKeyList)==1 :
#			self.ARR_Trend.update({ wIndex : wARR_SetTrend[0] })
#			return wRes	# 1以下はソートしない
#		
#		wTrendLen = len(wARR_SetTrend)	#取得トレンド数
#		wSetKeylist = []
#		wKey = 0
#		wB_Index = -1
#		wCount = 0
#		while True :
#			wKey = -1
#			for wChooseKey in wKeyList :
#				if wChooseKey in wSetKeylist :
#					continue	#既に決定してる要素
#				wKey = wChooseKey
#				break
#			if wKey==-1 :
#				break	#全て決定済
#			
#			wB_Index = wKey
#			for wKey2 in wKeyList :
#				if wKey==wKey2 :
#					continue	#自分は除外
#				if wKey2 in wSetKeylist :
#					continue	#既に決定してる要素
#				
#				if wARR_SetTrend[wKey]['uses']<wARR_SetTrend[wKey2]['uses'] :
#					wB_Index = wKey2	#今より大きい要素が見つかった
#			
#			wSetKeylist.append( wB_Index )	#一番大きい要素を記録
#			wCount += 1
#		
#		#############################
#		# ソート結果順に辞書に詰める
#		wIndex = 0
#		for wKey in wSetKeylist :
#			self.ARR_Trend.update({ wIndex : "" })
#			self.ARR_Trend[wIndex] = {}
#			self.ARR_Trend[wIndex].update({ "name" : wARR_SetTrend[wKey]['name'] })
##			self.ARR_Trend[wIndex].update({ "url"  : wARR_SetTrend[wKey]['url'] })
#			self.ARR_Trend[wIndex].update({ "uses" : wARR_SetTrend[wKey]['uses'] })
#			self.ARR_Trend[wIndex].update({ "accs" : wARR_SetTrend[wKey]['accs'] })
#			wIndex += 1
		
##		print( "GetTrends: " + str(len(wARR_Trend)) )
##		wKeylist = self.ARR_Trend.keys()
##		for wKey in wKeylist :
##			print( self.ARR_Trend[wKey]['name'] + ": " + str(self.ARR_Trend[wKey]['uses']) )
		return wRes



#####################################################
# トレンド送信
#####################################################
	def Send_Trend(self):
		#############################
		# トレンド取得対象ドメインがなければ未処理
		if len(self.ARR_SendDomain)==0 :
			self.Obj_Parent.OBJ_Mylog.Log( 'c', "トレンド対象ドメインなし" )
			return
		
		#############################
		# DB接続
		wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Trend: Send_Trend: DB Connect test is failed: " + wRes['Reason'] )
			wOBJ_DB.Close()
			return
		
		#############################
		# トレンド情報のロード
		wQuery = "select * from TBL_TREND ;"
		
		wRes = wOBJ_DB.RunQuery( wQuery )
		wRes = wOBJ_DB.GetQueryStat()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Trend: Send_Trend: Run Query is failed: " + wRes['Reason'] + " query=" + wRes['Query'] )
			wOBJ_DB.Close()
			return
		
		if len(wRes['Responce']['Data'])==0 :
			##トレンド情報なし
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Trend: Send_Trend: TBL_TREND record is 0" )
			wOBJ_DB.Close()
			return
		
		#############################
		# 一回ローカルに読み出す
		wARR_Trend  = {}
		wIndex    = 0
		for wLineTap in wRes['Responce']['Data'] :
			##領域の準備
			wARR_Trend.update({ wIndex : "" })
			wARR_Trend[wIndex] = {}
			wARR_Trend[wIndex].update({ "rank"   : 0 })
			wARR_Trend[wIndex].update({ "name"   : "" })
			wARR_Trend[wIndex].update({ "domain" : "" })
			wARR_Trend[wIndex].update({ "uses"   : 0 })
			wARR_Trend[wIndex].update({ "accs"   : 0 })
			
			##トレンド情報の取り出し
			wGetTap = []
			for wCel in wLineTap :
				wGetTap.append( wCel )
				## [0] ..name
				## [1] ..domain
				## [2] ..uses
				## [3] ..accs
			
			##領域へロード
			wARR_Trend[wIndex].update({ "rank"   : int( wGetTap[0] ) })
			wARR_Trend[wIndex].update({ "name"   : wGetTap[1].strip() })
			wARR_Trend[wIndex].update({ "domain" : wGetTap[2].strip() })
			wARR_Trend[wIndex].update({ "uses"   : int( wGetTap[3] ) })
			wARR_Trend[wIndex].update({ "accs  " : int( wGetTap[4] ) })
			wIndex += 1
		
		#############################
		# DB切断
		wOBJ_DB.Close()
		
		#############################
		# トレンド取得対象ドメインごとに処理する
		for wDomain in self.ARR_SendDomain :
			wARR_MatomeKeys = []
			
			#############################
			# 現ドメインのインデックスをまとめる(まとめキー)
			wKeyList = wARR_Trend.keys()
			for wKey in wKeyList :
				if wARR_Trend[wKey]['domain']==wDomain :
					wARR_MatomeKeys.append(wKey)
			
			if len(wARR_MatomeKeys)==0 :
				self.Obj_Parent.OBJ_Mylog.Log( 'c', "トレンド情報なし: " + wDomain )
				continue	#トレンドがないドメイン
			
			#############################
			# ランクの昇順にソートする
			wTrendLen = len(wARR_MatomeKeys)	#ドメインのトレンド数
			wSetKeylist = []
			wKey = 0
			wB_Index = -1
			wRank = 1
#			wCount = 0
#			while True :
#				wKey = -1
#				for wChooseKey in wARR_MatomeKeys :
#					if wChooseKey in wSetKeylist :
#						continue	#既に決定してる要素
#					wKey = wChooseKey
#					break
#				if wKey==-1 :
#					break	#全て決定済
#				
#				wB_Index = wKey
#				for wKey2 in wARR_MatomeKeys :
#					if wKey==wKey2 :
#						continue	#自分は除外
#					if wKey2 in wSetKeylist :
#						continue	#既に決定してる要素
#					
#					if wARR_Trend[wKey]['uses']<wARR_Trend[wKey2]['uses'] :
#						wB_Index = wKey2	#今より大きい要素が見つかった
#				
#				wSetKeylist.append( wB_Index )	#一番大きい要素を記録
#				wCount += 1
			while True :
				wKey = -1
				for wChooseKey in wARR_MatomeKeys :
					if wChooseKey in wSetKeylist :
						continue	#既に決定してる要素
					wKey = wChooseKey
					break
				if wKey==-1 :
					break	#全て決定済
				
				wB_Index = wKey
				if wARR_Trend[wKey]['rank']!=wRank :
					###ランクがずれてる場合、トレンド値で並べる
					for wKey2 in wARR_MatomeKeys :
						if wKey==wKey2 :
							continue	#自分は除外
						if wKey2 in wSetKeylist :
							continue	#既に決定してる要素
						
						if wARR_Trend[wKey]['uses']<wARR_Trend[wKey2]['uses'] :
							wB_Index = wKey2	#今より大きい要素が見つかった
				wRank += 1
				
				wSetKeylist.append( wB_Index )	#ランク順か、トレンド値の一番大きい要素を記録
			
			#############################
			# トゥートの組み立て
			wCHR_TimeDate = gVal.STR_TimeInfo['TimeDate'].split(" ")
			wCHR_Title = "Mastodon " + wDomain + " TrendTag: " + wCHR_TimeDate[0] + " " + str(gVal.STR_TimeInfo['Hour']) + "時"
			
			wCHR_Body = ""
			for wKey in wSetKeylist :
				if wARR_Trend[wKey]['domain']!=wDomain :
					continue	#違うドメインのトレンド
				
				###とりあえずソートなしで
				wCHR_Body = wCHR_Body + "#" + wARR_Trend[wKey]['name'] + " (" + str(wARR_Trend[wKey]['uses']) + ")" + '\n'
				
				wCHR_Toot = wCHR_Body + "***上から最新順"
		
			#############################
			# トゥートの送信
			wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, spoiler_text=wCHR_Title, visibility=self.DEF_SENDRANGE )
			if wRes['Result']!=True :
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Trend: Send_Trend: Mastodon error: " + wRes['Reason'] )
				return
		
		return



#####################################################
# トレンド パターン読み込み
#####################################################
	def __getTrendPatt(self):
		#############################
		# 読み出し先初期化
		self.ARR_SendDomain = []
		wSendDomain = []	#解析パターンファイル
		
		#############################
		# ファイル読み込み
		wFile_path = gVal.DEF_STR_FILE['TrendTootFile']
		if CLS_File.sReadFile( wFile_path, outLine=wSendDomain )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Trend: __getTrendPatt: TrendTootFile read failed: " + wFile_path )
			return False	#失敗
		
		#############################
		# パターンの詰め込み
		for wLine in wSendDomain :
			wLine = wLine.split( gVal.DEF_DATA_BOUNDARY )
			if len(wLine)!=2 :
				continue	#フォーマットになってない
			if wLine[0].find("#")==0 :
				continue	#コメントアウト
			
			#############################
			# ドメイン
			if wLine[0]=="d" :
				self.ARR_SendDomain.append( wLine[1] )
		
		return True



