#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：PTL監視処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/11/19
#####################################################
# Private Function:
#   __run(self):
#   __cope( self, inROW ) :
#   __get_Rip( self, inFilename ):
#
# Instance Function:
#   __init__( self, parentObj=None ):	※親クラス実体を設定すること
#   Get_PTL(self):
#   Get_RatePTL(self):
#   Set_RatePTL(self):
#   Get_Anap(self):
#   Nicoru( self, inID ) :
#   Boost( self, inID ) :
#   HimoRipry( self, inFilename, inRepID ):
#   AirRipry( self, inFilename ):
#   IndWordOpe( self, inFulluser, inPatt, inUri ) :
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
class CLS_LookPTL():
#####################################################
	CHR_LogName  = "PTL監視"
	Obj_Parent   = ""		#親クラス実体

	ARR_NewTL    = []		#mastodon TL(mastodon API)
	ARR_AnapTL   = {}		#TL解析パターン
	ARR_RateTL   = []		#過去TL(id)
	ARR_UpdateTL = []		#新・過去TL(id)
	ARR_NoWPaccount = []	#監視除外アカウント
	ARR_NoWPdomain  = []	#監視除外ドメイン

	STR_Cope = {			#処理カウンタ
		"Now_Cope"  : 0,		#処理した新トゥート数
		
		"Now_Favo"  : 0,		#今ニコった数
		"Now_Boot"  : 0,		#今ブーストした数
		"Now_ARip"  : 0,		#今エアリプした数
		"Now_Word"  : 0,		#今ワード監視した数
##		"UserCorr"	: 0,		#ユーザ収集
		"dummy"     : 0	#(未使用)
	}



#####################################################
# Init
#####################################################
	def __init__( self, parentObj=None ):
		if parentObj==None :
			###親クラス実体の未設定
			CLS_OSIF.sPrn( "CLS_LookPTL: __init__: You have not set the parent class entity for parentObj" )
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
		if gVal.FLG_Test_Mode==False :
			self.Obj_Parent.OBJ_Mylog.Log( 'b', self.CHR_LogName + " 開始" )
		else:
			self.Obj_Parent.OBJ_Mylog.Log( 'b', self.CHR_LogName + " 開始", inView=True )
		
		#############################
		# TL解析パターン読み込み
		if self.Get_Anap()!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookPTL: __run: Pattern PTL read failed" )
			return
		
		#############################
		# PTL読み込み(mastodon)
		wRes = self.Get_PTL()
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookPTL: __run: PTL read failed: " + wRes['Reason'] )
			return
		
		#############################
		# 過去PTLの読み込み
		wRes = self.Get_RatePTL()
		if wRes!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookPTL: __run: Get_RatePTL failed" )
			return
		if len(self.ARR_RateTL)==0 :
			self.Init_RatePTL()
			if gVal.FLG_Test_Mode==False :
				self.Obj_Parent.OBJ_Mylog.Log( 'b', self.CHR_LogName + " PTL過去TL初期化" )
			else :
				self.Obj_Parent.OBJ_Mylog.Log( 'b', self.CHR_LogName + " PTL過去TL初期化", inView=True )
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
		# 新・過去LTL保存
		wRes = self.Set_RatePTL()
		if wRes!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookPTL: __run: Set_RatePTL failed" )
			return
		
		#############################
		# 処理結果ログ
		wSTR_User = self.Obj_Parent.OBJ_UserCorr.GetUserCorrectStat()	#収集状況の取得
		
		wStr = self.CHR_LogName + " 結果: 新Toot=" + str(self.STR_Cope['Now_Cope']) + " "
		wStr = wStr + "Favo=" + str(self.STR_Cope['Now_Favo']) + " "
		wStr = wStr + "Boot=" + str(self.STR_Cope['Now_Boot']) + " "
		wStr = wStr + "AirRip=" + str(self.STR_Cope['Now_ARip']) + " "
		wStr = wStr + "WordOp=" + str(self.STR_Cope['Now_Word']) + '\n'
##		wStr = wStr + " UserCorr=" + str(self.STR_Cope['UserCorr']) + '\n'
		wStr = wStr + "UserCorr=[Cope:" + str(wSTR_User['Cope']) + " Add:" + str(wSTR_User['UserAdd']) + " Update:" + str(wSTR_User['UserUpdate']) + "]"
		
		###ワード収集有効時はログを出す
		if gVal.STR_MasterConfig['WordStudy']=="on" :
			wSTR_Word = self.Obj_Parent.OBJ_WordCorr.GetWordCorrectStat()	#収集状況の取得
			wStr = wStr + '\n' + "WordCorr=[Cope:" + str(wSTR_Word['Cope']) + " Regist:" + str(wSTR_Word['Regist']) + " Delete:" + str(wSTR_Word['Delete'])
			wStr = wStr + " ClazList:" + str(wSTR_Word['ClazList']) + "]"
		
		if gVal.FLG_Test_Mode==False :
			self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr )
		else:
			self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr, inView=True )
		
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
		if self.__copeCorr( wFulluser, inROW['language'], wCont )!=True :
			return	### 除外
		
		#############################
		#ユーザ収集ファイルに記録
		#  ・新規  ：追加
		#  ・追加済：更新
##		if self.Obj_Parent.OBJ_UserCorr.AddUser( inROW )==True :
##			self.STR_Cope['UserCorr'] += 1
##		self.Obj_Parent.OBJ_UserCorr.AddUser( inROW )
		self.Obj_Parent.OBJ_UserCorr.AddUser( inROW, wFulluser )
		
		#############################
		#単語学習
##		if gVal.STR_MasterConfig['WordStudy'] == "on" :
##			self.Obj_Parent.OBJ_WordCorr.WordStudy( inROW )
##		self.Obj_Parent.OBJ_WordCorr.WordStudy( wCont, inROW['created_at'] )
		self.Obj_Parent.OBJ_WordCorr.WordStudy( wCont )
		
##		#############################
##		#パターン反応
##		###トゥートからHTMLタグを除去
##		wCont = CLS_OSIF.sDel_HTML( inROW['content'] )
##		
##		###ユーザ名の変換
##		wFulluser = CLS_UserData.sGetFulluser( inROW['account']['username'], inROW['account']['url'] )
##		if wFulluser['Result']!=True :
##			###今のところ通らないルート
##			return False
##		
##		#############################
##		#除外トゥート
##		###リプライ（先頭に@付きトゥート）
##		if wCont.find('@') == 0 :
##			return
##		
##		###自分(このbot)のトゥート
##		if wFulluser['Fulluser'] == self.Obj_Parent.CHR_Account :
##			return
		
		#############################
		# フォロワー状態
		#   True =フォロワー
		#   False=フォロワーじゃない
		wFLG_Follower = self.Obj_Parent.OBJ_Follow.Check_Follower( wFulluser['Fulluser'] )
		
		#############################
		#解析種類の判定
		wKeyList = self.ARR_AnapTL.keys()
		for wKey in wKeyList :
			#############################
			#解析：ニコる
			if self.ARR_AnapTL[wKey]['Kind']=="f" and gVal.STR_MasterConfig['PTL_Favo']=="on" and \
			   wFLG_Follower==True :
				###マッチチェック
				wRes = CLS_OSIF.sRe_Search( self.ARR_AnapTL[wKey]['Pattern'], wCont )
				if not wRes :
					##アンマッチ
					continue
				###実行
				if self.Nicoru( inROW['id'] )!=True :
					break
				self.STR_Cope["Now_Favo"] += 1
				break
			
			#############################
			#解析：ブースト
			if self.ARR_AnapTL[wKey]['Kind']=="b" and gVal.STR_MasterConfig['PTL_Boot']=="on" and \
			   wFLG_Follower==True :
				###マッチチェック
				wRes = CLS_OSIF.sRe_Search( self.ARR_AnapTL[wKey]['Pattern'], wCont )
				if not wRes :
					##アンマッチ
					continue
				###実行
				if self.Boost( inROW['id'] )!=True :
					break
				self.STR_Cope["Now_Boot"] += 1
				break
			
			#############################
			#解析：紐エアリプ
			if self.ARR_AnapTL[wKey]['Kind']=="h" and gVal.STR_MasterConfig['PTL_HRip']=="on" and \
			   wFLG_Follower==True :
				###マッチチェック
				wRes = CLS_OSIF.sRe_Search( self.ARR_AnapTL[wKey]['Pattern'], wCont )
				if not wRes :
					##アンマッチ
					continue
				###実行
				if self.HimoRipry( self.ARR_AnapTL[wKey]['File'], inROW['id'] )!=True :
					break
				self.STR_Cope["Now_ARip"] += 1
				break
			
			#############################
			#解析：エアリプ
##			if self.ARR_AnapTL[wKey]['Kind']=="a" and gVal.STR_MasterConfig['PTL_ARip']=="on" and \
##			   wFLG_Follower==True :
			if self.ARR_AnapTL[wKey]['Kind']=="a" and gVal.STR_MasterConfig['PTL_ARip']=="on" :
				###マッチチェック
				wRes = CLS_OSIF.sRe_Search( self.ARR_AnapTL[wKey]['Pattern'], wCont )
				if not wRes :
					##アンマッチ
					continue
				###実行
				if self.AirRipry( self.ARR_AnapTL[wKey]['File'] )!=True :
					break
				self.STR_Cope["Now_ARip"] += 1
				break
			
			#############################
			#解析：ワード監視
			if self.ARR_AnapTL[wKey]['Kind']=="w" and gVal.STR_MasterConfig['PTL_WordOpe']=="on" and \
			   gVal.STR_MasterConfig['AdminUser']!="" :
				
				# 監視除外アカウントか
				if wFulluser['Fulluser'] in self.ARR_NoWPaccount :
					self.Obj_Parent.OBJ_Mylog.Log( 'c', "ワード監視除外アカウント: " + wFulluser['Fulluser'] )
					continue
				# 監視除外ドメインか
				if wFulluser['Domain'] in self.ARR_NoWPdomain :
					self.Obj_Parent.OBJ_Mylog.Log( 'c', "ワード監視除外ドメイン: " + wFulluser['Domain'] )
					continue
				
				###マッチチェック
				wRes = CLS_OSIF.sRe_Search( self.ARR_AnapTL[wKey]['Pattern'], wCont )
				if not wRes :
					##アンマッチ
					continue
				###実行
				if self.IndWordOpe( wFulluser['Fulluser'], self.ARR_AnapTL[wKey]['Pattern'], inROW['uri'] )!=True :
					break
				self.STR_Cope["Now_Word"] += 1
				break
		
		return

##	#####################################################
##	def __copeCheck( self, inMode, inPatt, inCont ):
##		#############################
##		# パターンチェック
##		wRes = CLS_OSIF.sRe_Search( inPatt, inCont )
##		if wRes :
##			wARRpat.appent( inMode )	#次は同じモードのチェックはやらない
##			return True		#パターンマッチ
##		
##		return False		#アンマッチ
##
	#####################################################
	def __copeCorr( self, inUser, inLang, inCont ):
		#############################
		# 除外トゥート
		###自分
		if inUser['Fulluser'] == self.Obj_Parent.CHR_Account :
			return False
		
		###外人 (日本人限定=ON時)
		if inLang!="ja" and gVal.STR_MasterConfig["JPonly"]=="on" :
			return False
		
		###除外ドメイン
		if inUser['Domain'] in gVal.STR_DomainREM :
			return False
		
		###リプライ（先頭に@付きトゥート）
		if inCont.find('@') == 0 :
			return False
		
		###タグ付き
		### PRタグは自分しか使わないので上の条件で弾ける
		wRes_1 = inCont.find( gVal.STR_MasterConfig['iActionTag'] )
		wRes_2 = inCont.find( gVal.STR_MasterConfig['mTootTag'] )
		wRes_4 = inCont.find( gVal.STR_MasterConfig['TrafficTag'] )
		wRes_5 = inCont.find( gVal.STR_MasterConfig['SystemTag'] )
		if wRes_1>=0 or wRes_2>=0 or wRes_4>=0 or wRes_5>=0 :
			return False
		
		return True



#####################################################
# PTL取得
#####################################################
	def Get_PTL(self):
		self.ARR_NewTL = []
		wNext_Id = None
		wMax_Toots = gVal.DEF_STR_TLNUM["getPTLnum"]
		while (len(self.ARR_NewTL) < wMax_Toots ):
			#############################
			# TL取得
			wRes = self.Obj_Parent.OBJ_MyDon.GetPublicTL( limit=40, max_id=wNext_Id )
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
				wRes['Reason'] = "CLS_LookPTL: Get_PTL: Page nation error"
				wRes['Result'] = False
				return wRes
		
		return wRes



#####################################################
# 過去PTL取得・保存・初期化
#####################################################
	def Get_RatePTL(self):
		#############################
		# 読み出し先初期化
		self.ARR_RateTL = []
		
		#############################
		# ファイル読み込み
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['Rate_PTLFile']
		if CLS_File.sReadFile( wFile_path, outLine=self.ARR_RateTL )!=True :
			return False	#失敗
		
		return True			#成功

	#####################################################
	def Set_RatePTL(self):
		#############################
		# ファイル書き込み (改行つき)
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['Rate_PTLFile']
		if CLS_File.sWriteFile( wFile_path, self.ARR_UpdateTL, inRT=True )!=True :
			return False	#失敗
		
		return True			#成功

	#####################################################
	def Init_RatePTL(self):
		#############################
		# IDを詰め込む
		self.ARR_UpdateTL = []
		for wROW in self.ARR_NewTL :
			self.ARR_UpdateTL.append( wROW['id'] )
		
		#############################
		# ファイル書き込み (改行つき)
		self.Set_RatePTL()
		return



#####################################################
# TL解析パターン読み出し
#####################################################
	def Get_Anap(self):
		#############################
		# 読み出し先初期化
		self.ARR_AnapTL = {}
		self.ARR_NoWPaccount = []
		self.ARR_NoWPdomain = []
		wAnapList = []	#解析パターンファイル
		
		#############################
		# ファイル読み込み
		wFile_path = gVal.DEF_STR_FILE['PatternPTLFile']
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
			
			if wLine[0]=="wa" :	#監視除外アカウント
				self.ARR_NoWPaccount.append( wLine[1] )
				continue
			if wLine[0]=="wd" :	#監視除外ドメイン
				self.ARR_NoWPdomain.append( wLine[1] )
				continue
			
			self.ARR_AnapTL.update({ wIndex : "" })
			self.ARR_AnapTL[wIndex] = {}
			self.ARR_AnapTL[wIndex].update({ "Kind"    : wLine[0] })
			self.ARR_AnapTL[wIndex].update({ "Pattern" : wLine[1] })
			self.ARR_AnapTL[wIndex].update({ "File"    : wLine[2] })
			wIndex += 1
		
		###なしでもOKとする
		return True			#成功



#####################################################
# ニコる
#####################################################
	def Nicoru( self, inID ) :
		#############################
		#ニコる
		wRes = self.Obj_Parent.OBJ_MyDon.Favo( id=inID )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookPTL: Nicoru: Mastodon error: " + wRes['Reason'] )
			return False
		
		return True



#####################################################
# ブースト
#####################################################
	def Boost( self, inID ) :
		#############################
		#ブースト
		wRes = self.Obj_Parent.OBJ_MyDon.Boost( id=inID )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookPTL: Boost: Mastodon error: " + wRes['Reason'] )
			return False
		
		return True



#####################################################
# 紐エアリプ
#####################################################
	def HimoRipry( self, inFilename, inRepID ):
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
		#トゥート
		wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wARR_Line[1], visibility="public", in_reply_to_id=inRepID )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookPTL: HimoRipry: Mastodon error: " + wRes['Reason'] )
			return False
		
		return True



#####################################################
# エアリプ
#####################################################
	def AirRipry( self, inFilename ):
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
		#トゥート
		wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wARR_Line[1], visibility="public" )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookPTL: AirRipry: Mastodon error: " + wRes['Reason'] )
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
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookPTL: __get_Rip: File read is failure: " + wFile_path )
			return []
		if len(wARR_Load)==0 :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookPTL: __get_Rip: The file is empty: " + wFile_path )
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
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookPTL: __get_Rip: Riply kouho is zero" )
			return []
		
		#############################
		# 乱数の取得
		wRand = CLS_OSIF.sGetRand( len(wARR_RipKouho) )
		if wRand<0 :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookPTL: __get_Rip: sGetRand error: " + str(wRand) )
			return []
		
		#############################
		# リプを出力
		wLine = wARR_RipKouho[wRand]
		return wLine



#####################################################
# ワード監視
#####################################################
	def IndWordOpe( self, inFulluser, inPatt, inUri ) :
		#############################
		#トゥートの組み立て
		wCHR_Toot = "@" + gVal.STR_MasterConfig['AdminUser'] + " [ワード監視通知]" + '\n'
		wCHR_Toot = wCHR_Toot + "対象者："   + '\n' + inFulluser + '\n'
		wCHR_Toot = wCHR_Toot + "パターン：" + '\n' + inPatt + '\n'
##		wCHR_Toot = wCHR_Toot + "トゥートURI：" + '\n' + inUri
		wCHR_Toot = wCHR_Toot + "トゥートURI：" + '\n' + inUri + '\n' + "#" + gVal.STR_MasterConfig['SystemTag']
		
		#############################
		#トゥート
		wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, visibility="direct" )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookPTL: IndWordOpe: Mastodon error: " + wRes['Reason'] )
			return False
		
		return True



