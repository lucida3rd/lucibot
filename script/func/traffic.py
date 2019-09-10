#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：トラヒック処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/9/9
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
# トラヒック設計仕様
#・計測対象アカウントの制御は、ユーザクラスでおこなう。
#・MasterUserのドメインはデフォルトで計測対象となる。
#  その他は、toot/traffic.txtでドメインを指定する。
#・計測用のアカウントは、ユーザ登録時に
#  data/_traffic.txtに登録される。
#  既に同じドメインのものが登録されている場合はおこなわない。
#  ユーザ削除されると、同じドメインの別のアカウントを登録する。
#  ない場合はそのドメインは計測対象から外れる。
#・MasterUserのドメインで他のアカウントが登録されたときは、
#  そのアカウントが計測対象となる。
#・計測対象はLocalTLからおこなう。この際、言語は問わないこと。
#
#####################################################
from postgresql_use import CLS_PostgreSQL_Use

from osif import CLS_OSIF
from filectrl import CLS_File
from userdata import CLS_UserData
from gval import gVal
#####################################################
class CLS_Traffic():
#####################################################
	Obj_Parent = ""				#親クラス実体
	
	FLG_Valid  = False			#カウント対象
	VAL_NowCount = 0			#カウント値

								#**パターン解析からロードする
	CHR_SendRange  = ""			#トラヒック送信範囲
	ARR_SendDomain = []			#トラヒック送信対象ドメイン
	DEF_SENDRANGE  = "unlisted"
	DEF_ARR_CHECKRANGE = [
		"public",
		"unlisted",
		"private" ]

#####################################################
# Init
#####################################################
	def __init__( self, parentObj=None ):
		if parentObj==None :
			###親クラス実体の未設定
			CLS_OSIF.sPrn( "CLS_Traffic: __init__: You have not set the parent class entity for parentObj" )
			return
		
		self.Obj_Parent = parentObj
		self.FLG_Valid    = CLS_UserData.sCheckTrafficUser( self.Obj_Parent.CHR_Account )
		self.VAL_NowCount = 0
		return



#####################################################
# カウントアップ
#   カウントしたらTrueを返す
#####################################################
	def Countup(self):
		#############################
		# カウント対象か
		if self.FLG_Valid!=True :
			return False
		
		#############################
		# カウントアップする
		self.VAL_NowCount += 1
		return True



#####################################################
# カウンタを更新
#####################################################
	def Update(self):
		#############################
		# カウント対象か
		if self.FLG_Valid!=True :
			##更新なし
			return True
		
		#############################
		# ドメインの抽出
		wDomain = self.Obj_Parent.CHR_Account.split("@")
		if len(wDomain)!=2 :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Update: Illigal admin_id: " + self.Obj_Parent.CHR_Account )
			return False
		wDomain = wDomain[1]
		
		#############################
		# DB接続
		wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Update: DB Connect test is failed: " + wRes['Reason'] + " domain=" + wDomain )
			wOBJ_DB.Close()
			return False
		
		#############################
		# ドメイン存在チェック
		wQuery = "select * from TBL_TRAFFIC_DATA where " + \
					" domain = '" + wDomain + "' " + \
					";"
		wRes = wOBJ_DB.RunQuery( wQuery )
		wRes = wOBJ_DB.GetQueryStat()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Update: Run Query is failed: " + wRes['Reason'] + " query=" + wRes['Query'] )
			wOBJ_DB.Close()
			return False
		
		if len(wRes['Responce']['Data'])!=1 :
			##存在しない
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Update: select Domain is failed: " + " domain=" + wDomain + " nums=" + str(len(wRes['Responce']['Data'])) )
			wOBJ_DB.Close()
			return False
		
		#############################
		# カウント値の取り出し
		for wLineTap in wRes['Responce']['Data'] :
			wGetTap = []
			for wCel in wLineTap :
				wGetTap.append( wCel )
				## [0] ..domain
				## [1] ..count
				## [2] ..rat_count
				## [3] ..now_count
				## [4] ..rat_days
				## [5] ..now_days
		
		wCount    = int( wGetTap[1] )
		
		#############################
		# カウントアップ
		wCount += self.VAL_NowCount
		
		#############################
		# テーブルの更新
		wQuery = "update TBL_TRAFFIC_DATA set " + \
					"count = " + str(wCount) + " " + \
					"where domain = '" + wDomain + "' ;"
		
		wRes = wOBJ_DB.RunQuery( wQuery )
		wRes = wOBJ_DB.GetQueryStat()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Update: Update Count is failed: " + wRes['Reason'] + " domain=" + wDomain )
			wOBJ_DB.Close()
			return False
		
		#############################
		# DB切断
		wOBJ_DB.Close()
		return True			#成功



#####################################################
# トラヒック送信
#   送信済ならTrueを返す
#####################################################
	def SendTraffic(self):
		#############################
		# トラヒックが有効か
		if gVal.STR_MasterConfig['Traffic']!="on" :
			return False
		
		#############################
		# MasterUserか
		if gVal.STR_MasterConfig['MasterUser']!=self.Obj_Parent.CHR_Account :
			return False	#SubUserは抜ける
		
		#############################
		# 1時間経ってる周回か
		if gVal.STR_TimeInfo['OneHour']==False :
			return False	#Traffic送信周回ではない
		
		#############################
		# トゥート送信対象のトラヒックドメイン読み込み
		###読み出し先初期化
		if self.__getTrafficPatt()!=True :
			return False	#失敗
		if len(self.ARR_SendDomain)==0 :
			###デフォルトだと指定あるのでいちお入れる
			self.Obj_Parent.OBJ_Mylog.Log( 'c', "CLS_Traffic: トラヒック送信の指定先=なし" )
			return False	###対象なし
		
		#############################
		# ドメインの抽出
		wDomain = self.Obj_Parent.CHR_Account.split("@")
		if len(wDomain)!=2 :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: Update: Illigal admin_id: " + self.Obj_Parent.CHR_Account )
			return False
		wDomain = wDomain[1]
		
		#############################
		# 送信処理開始
		
		#############################
		# DB接続
		wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: SendTraffic: DB Connect test is failed: " + wRes['Reason'] + " domain=" + wDomain )
			wOBJ_DB.Close()
			return False
		
		#############################
		# 全トラヒックのロード
		wQuery = "select * from TBL_TRAFFIC_DATA ;"
		
		wRes = wOBJ_DB.RunQuery( wQuery )
		wRes = wOBJ_DB.GetQueryStat()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: SendTraffic: Run Query is failed: " + wRes['Reason'] + " query=" + wRes['Query'] )
			wOBJ_DB.Close()
			return False
		
		if len(wRes['Responce']['Data'])==0 :
			##トラヒック情報なし
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: SendTraffic: TBL_TRAFFIC_DATA record is 0" )
			wOBJ_DB.Close()
			return False
		
		#############################
		# カウント値の取り出しと、リセット
		wTraffic  = {}
		wIndex    = 0
		for wLineTap in wRes['Responce']['Data'] :
			##領域の準備
			wTraffic.update({ wIndex : "" })
			wTraffic[wIndex] = {}
			wTraffic[wIndex].update({ "domain"    : "" })
			wTraffic[wIndex].update({ "count"     : 0 })
			wTraffic[wIndex].update({ "rat_count" : 0 })
			wTraffic[wIndex].update({ "now_count" : 0 })
			wTraffic[wIndex].update({ "rat_days"  : 0 })
			wTraffic[wIndex].update({ "now_days"  : 0 })
			wTraffic[wIndex].update({ "rat_wday"  : 0 })
			wTraffic[wIndex].update({ "now_wday"  : 0 })
			
			##カウンタの取り出し
			wGetTap = []
			for wCel in wLineTap :
				wGetTap.append( wCel )
				## [0] ..domain
				## [1] ..count
				## [2] ..rat_count
				## [3] ..now_count
				## [4] ..rat_days
				## [5] ..now_days
			
			##領域へロード
			wTraffic[wIndex].update({ "domain"    : wGetTap[0].strip() })
			wTraffic[wIndex].update({ "count"     : int( wGetTap[1] ) })
			wTraffic[wIndex].update({ "rat_count" : int( wGetTap[2] ) })
			wTraffic[wIndex].update({ "now_count" : int( wGetTap[3] ) })
			wTraffic[wIndex].update({ "rat_days"  : int( wGetTap[4] ) })
			wTraffic[wIndex].update({ "now_days"  : int( wGetTap[5] ) })
			
			##カウンタのリセットと、過去カウンタの記録（入れ替え）
			wTraffic[wIndex]['rat_count'] = wTraffic[wIndex]['now_count']	# 1時間前
			wTraffic[wIndex]['now_count'] = wTraffic[wIndex]['count']		# 現在(後ろで送信)
			wTraffic[wIndex]['now_days'] += wTraffic[wIndex]['count']		# 1日に加算
			wTraffic[wIndex]['count']     = 0
			
			### 1日経った =twitterに送信する
			if gVal.STR_TimeInfo['OneDay']==True :
				wTraffic[wIndex]['rat_wday'] = wTraffic[wIndex]['rat_days']
				wTraffic[wIndex]['now_wday'] = wTraffic[wIndex]['now_days']
				wTraffic[wIndex]['rat_days'] = wTraffic[wIndex]['now_days']
				wTraffic[wIndex]['now_days'] = 0
			
			##DBを更新
			wQuery = "update TBL_TRAFFIC_DATA set " + \
					"count = " + str(wTraffic[wIndex]['count']) + ", " + \
					"rat_count = " + str(wTraffic[wIndex]['rat_count']) + ", " + \
					"now_count = " + str(wTraffic[wIndex]['now_count']) + ", " + \
					"rat_days = " + str(wTraffic[wIndex]['rat_days']) + ", " + \
					"now_days = " + str(wTraffic[wIndex]['now_days']) + " " + \
					"where domain = '" + wTraffic[wIndex]['domain'] + "' ;"
			
			wRes = wOBJ_DB.RunQuery( wQuery )
			wRes = wOBJ_DB.GetQueryStat()
			if wRes['Result']!=True :
				##失敗
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: SendTraffic: Standby reset is failed: " + wRes['Reason'] + " domain=" + wTraffic[wIndex]['domain'] )
				wOBJ_DB.Close()
				return False
			
			##インデックス更新
			wIndex += 1
		
		#############################
		# DB切断
		wOBJ_DB.Close()
		
		#############################
		# 送信するトラヒックの作成
		
		#############################
		# トラヒック送信対象の順番に入れ替える
		wARR_SendTraffic = {}
		wIndex = 0
		wKeyList = wTraffic.keys()
		for wSendDomain in self.ARR_SendDomain :
			##対象のトラヒックを探す
			for wKey in wKeyList :
				if wTraffic[wKey]['domain']!=wSendDomain :
					continue
				##ヒット
				wARR_SendTraffic.update({ wIndex : wTraffic[wKey] })
				wIndex += 1
		
		#############################
		# トゥートの組み立て
		wCHR_TimeDate = gVal.STR_TimeInfo['TimeDate'].split(" ")
##		wCHR_Title = "Mastodon Traffic: " + wCHR_TimeDate[0] + " " + str(gVal.STR_TimeInfo['Hour']) + "時台"
		wCHR_Title = "Mastodon Traffic: " + wCHR_TimeDate[0] + " " + str(gVal.STR_TimeInfo['Hour']) + "時"
		
		wCHR_Body = ""
		wKeyList  = wARR_SendTraffic.keys()
		for wIndex in wKeyList :
			wCHR_Body = wCHR_Body + wARR_SendTraffic[wIndex]['domain'] + ": " + str(wARR_SendTraffic[wIndex]['now_count'])
			
			if wARR_SendTraffic[wIndex]['rat_count']>=0 :
				##bot起動の最初の1時間は差を出さない
				wRateCount = wARR_SendTraffic[wIndex]['now_count'] - wARR_SendTraffic[wIndex]['rat_count']
				wCHR_Body = wCHR_Body + "("
				if wRateCount>0 :
					wCHR_Body = wCHR_Body + "+"
				wCHR_Body = wCHR_Body + str(wRateCount) + ")" + '\n'
			else :
				wCHR_Body = wCHR_Body + '\n'
		
		wCHR_Toot = wCHR_Body + "#" + gVal.STR_MasterConfig['TrafficTag']
		
		#############################
		# トゥートの送信
		wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, spoiler_text=wCHR_Title, visibility=self.CHR_SendRange )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: SendTraffic: Mastodon error: " + wRes['Reason'] )
			return False
		
		#############################
		# Twitterが有効か
		if gVal.STR_MasterConfig['Twitter']!="on" :
			return True	#トラヒックは送信済
		
		#############################
		# 1日経ってる周回か
		if gVal.STR_TimeInfo['OneDay']==False :
			return True	#トラヒックは送信済
		
		#############################
		# ツイートの組み立て
		wCHR_TimeDate = gVal.STR_TimeInfo['TimeDate'].split(" ")
##		wCHR_Title = "Mastodon Traffic: " + wCHR_TimeDate[0] + " " + str(gVal.STR_TimeInfo['Hour']) + "時"
		wCHR_Title = "Mastodon Traffic: " + wCHR_TimeDate[0]
		
		wCHR_Body = ""
		wKeyList  = wARR_SendTraffic.keys()
		for wIndex in wKeyList :
			wCHR_Body = wCHR_Body + wARR_SendTraffic[wIndex]['domain'] + ": " + str(wARR_SendTraffic[wIndex]['now_wday'])
			
			if wARR_SendTraffic[wIndex]['rat_wday']>=0 :
				##bot起動の最初の1日は差を出さない
				wRateCount = wARR_SendTraffic[wIndex]['now_wday'] - wARR_SendTraffic[wIndex]['rat_wday']
				wCHR_Body = wCHR_Body + "("
				if wRateCount>0 :
					wCHR_Body = wCHR_Body + "+"
				wCHR_Body = wCHR_Body + str(wRateCount) + ")" + '\n'
			else :
				wCHR_Body = wCHR_Body + '\n'
		
##		wCHR_Tweet = wCHR_Title + '\n' + wCHR_Body + "#" + gVal.STR_MasterConfig['TwitterTag']
##		if gVal.STR_MasterConfig['TwitterTag']!="" :
##			wCHR_Tweet = wCHR_Tweet + "#" + gVal.STR_MasterConfig['TwitterTag']
		
		wCHR_Tweet = wCHR_Title + '\n' + wCHR_Body
		wARR_Tweet = wCHR_Tweet.split('\n')	#チェック用の行にバラす
		
		#############################
		# タグを抜いた文字数を計算する
		wTwitterTag = ""
		if gVal.STR_MasterConfig['TwitterTag']=="" :
			wMAX_Tweet = 140
		else :
			wTwitterTag = '\n' + "#" + gVal.STR_MasterConfig['TwitterTag']
			wMAX_Tweet = 140 - len( wTwitterTag )
		
		#############################
		# 文字数を140字に収める
		#   最後尾のトラヒック情報(ドメイン別)を1つずつ削って収める
		for wI in list( range(len(wARR_Tweet)) ) :
##			if len(wCHR_Tweet)<=140 :
			if len(wCHR_Tweet)<=wMAX_Tweet :
				break	#140字に収まっている
			
			##最後尾を削って文字列に直す
			del wARR_Tweet[-1]
			wCHR_Tweet = '\n'.join(wARR_Tweet)
		
		#############################
		# 1番目のドメインを最後尾に移動(Twitter上で目立たせる)
		wARR_Tweet = wCHR_Tweet.split('\n')
		if len(wARR_Tweet)>=2 :
			wARR_Tweet.append( wARR_Tweet[1] )
			del wARR_Tweet[1]
		wCHR_Tweet = '\n'.join(wARR_Tweet)
		wCHR_Tweet = wCHR_Tweet + wTwitterTag	#タグを付ける
		
		#############################
		# ツイートの送信
		if gVal.FLG_Test_Mode==False :
			wRes = self.Obj_Parent.OBJ_Twitter.Tweet( wCHR_Tweet )
			if wRes['Result']!=True :
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: SendTraffic: Twitter API Error: " + wRes['Reason'] )
				##失敗しても処理は継続
		
		else:
			wStr = "Twitter(TestMode): ツイート内容= " + '\n' + wCHR_Tweet
			self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr, inView=True )
		
		return True	#トラヒックは送信済



#####################################################
# トラヒック パターン読み込み
#####################################################
	def __getTrafficPatt(self):
		#############################
		# 読み出し先初期化
		self.CHR_SendRange  = self.DEF_SENDRANGE
		self.ARR_SendDomain = []
		wSendDomain = []	#解析パターンファイル
		wFLG_Range  = False
		
		#############################
		# ファイル読み込み
		wFile_path = gVal.DEF_STR_FILE['TrafficTootFile']
		if CLS_File.sReadFile( wFile_path, outLine=wSendDomain )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_Traffic: __getTrafficPatt: TrafficTootFile read failed: " + wFile_path )
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
			# 公開範囲
			if wLine[0]=="r" :
				if CLS_UserData.sCheckRange(wLine[1])==True :
					self.CHR_SendRange = wLine[1]
					wFLG_Range = True
					continue
			
			#############################
			# ドメイン
			if wLine[0]=="d" :
				self.ARR_SendDomain.append( wLine[1] )
		
		if wFLG_Range==False :
			###デフォルトだと指定あるのでいちお入れる
			self.Obj_Parent.OBJ_Mylog.Log( 'c', "__getTrafficPatt: トラヒック送信の公開範囲なし(内部設定=" + self.DEF_SENDRANGE + ")" )
		
		return True



