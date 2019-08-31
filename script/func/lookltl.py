#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：LTL監視処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/8/30
#####################################################
# Private Function:
#   __run(self):
#   __cope( self, inROW ) :
#
# Instance Function:
#   __init__( self, parentObj=None ):	※親クラス実体を設定すること
#   Get_LTL(self):
#   Get_RateLTL(self):
#   Set_RateLTL(self):
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
from filectrl import CLS_File
from gval import gVal
#####################################################
class CLS_LookLTL():
#####################################################
	CHR_LogName  = "LTL監視"
	Obj_Parent   = ""		#親クラス実体

	ARR_NewTL    = []		#mastodon TL(mastodon API)
	ARR_AnapTL   = []		#TL解析パターン
	ARR_RateTL   = []		#過去TL(id)
	ARR_UpdateTL = []		#新・過去TL(id)

	STR_Cope = {			#処理カウンタ
		"Now_Cope"  : 0,		#処理した新トゥート数
		
		"Traffic"	: 0,		#トラヒック数
##		"UserCorr"	: 0,		#ユーザ収集
##		"Now_Word"  : 0,		#今ワード監視した数
##		"Now_Favo"  : 0,		#今ニコった数
##		"Now_Boot"  : 0,		#今ブーストした数
##		"Now_ARip"  : 0,		#今エアリプした数
		
		"dummy"     : 0	#(未使用)
	}



#####################################################
# Init
#####################################################
	def __init__( self, parentObj=None ):
		if parentObj==None :
			###親クラス実体の未設定
			CLS_OSIF.sPrn( "CLS_LookLTL: __init__: You have not set the parent class entity for parentObj" )
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
		# LTL読み込み(mastodon)
		wRes = self.Get_LTL()
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookLTL: __run: LTL read failed: " + wRes['Reason'] )
			return
		
		#############################
		# TL解析パターン読み込み
		### LTL監視にはない
		
		#############################
		# 過去LTLの読み込み
		wRes = self.Get_RateLTL()
		if wRes!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookLTL: __run: Get_RateLTL failed" )
			return
		if len(self.ARR_RateTL)==0 :
			self.Init_RateLTL()
			if gVal.FLG_Test_Mode==False :
				self.Obj_Parent.OBJ_Mylog.Log( 'b', self.CHR_LogName + " LTL過去TL初期化" )
			else :
				self.Obj_Parent.OBJ_Mylog.Log( 'b', self.CHR_LogName + " LTL過去TL初期化", inView=True )
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
		wRes = self.Set_RateLTL()
		if wRes!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookLTL: __run: Set_RateLTL failed" )
			return
		
		#############################
		# カウンタを更新する
		self.Obj_Parent.OBJ_Traffic.Update()
		
		#############################
		# トラヒックを送信する(Masterのみ)
		wTrafficSended = ""
		if self.Obj_Parent.OBJ_Traffic.SendTraffic()==True :
			wTrafficSended = " [1時間トラヒック済]"
		
		#############################
		# 処理結果ログ
##		wSTR_Word = self.Obj_Parent.OBJ_WordCorr.GetWordCorrectStat()	#収集状況の取得
##		
		wStr = self.CHR_LogName + " 結果: 新Toot=" + str(self.STR_Cope['Now_Cope'])
		wStr = wStr + " Traffic=" + str(self.STR_Cope['Traffic']) + wTrafficSended
##		wStr = wStr + " UserCorr=" + str(self.STR_Cope['UserCorr']) + '\n'
##		wStr = wStr + "WordCorr=[Cope:" + str(wSTR_Word['Cope']) + " Regist:" + str(wSTR_Word['Regist']) + " Delete:" + str(wSTR_Word['Delete'])
##		wStr = wStr + " ClazList:" + str(wSTR_Word['ClazList']) + "]"

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
		#トラヒックに記録
##		if gVal.STR_Config['TrafficCnt'] == "on" :
##			if self.Obj_Parent.OBJ_Traffic.Countup()==True :
##				self.STR_Cope['Traffic'] += 1
##			else:
##				###ありえなくない？
##				self.Obj_Parent.OBJ_Traffic.CountReset()
##				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookLTL: __cope: Traffic counter failer (and Reset)" )
##		self.Obj_Parent.OBJ_Traffic.Countup()
##		self.STR_Cope['Traffic'] += 1
		if self.Obj_Parent.OBJ_Traffic.Countup()==True :
			##カウント入った
			self.STR_Cope['Traffic'] += 1
		
##		#############################
##		#ユーザ収集ファイルに記録
##		#  ・新規  ：追加
##		#  ・追加済：更新
##		if self.Obj_Parent.OBJ_UserCorr.AddUser( inROW )==True :
##			self.STR_Cope['UserCorr'] += 1
		
##		#############################
##		#単語学習
##		if gVal.STR_Config['WordCorrect'] == "on" :
##			self.Obj_Parent.OBJ_WordCorr.WordStudy( inROW )
		
		#############################
		#トゥートからHTMLタグを除去
		#### LTLでは実装しない
		
		#############################
		#解析種類の判定
		#### LTLでは実装しない
		
		return



#####################################################
# LTL取得
#####################################################
	def Get_LTL(self):
		self.ARR_NewTL = []
		wNext_Id = None
		wMax_Toots = gVal.DEF_STR_TLNUM["getLTLnum"]
		while (len(self.ARR_NewTL) < wMax_Toots ):
			#############################
			# TL取得
			wRes = self.Obj_Parent.OBJ_MyDon.GetLocalTL( limit=40, max_id=wNext_Id )
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
				wRes['Reason'] = "CLS_LookLTL: Get_LTL: Page nation error"
				wRes['Result'] = False
				return wRes
		
		return wRes



#####################################################
# 過去LTL取得・保存・初期化
#####################################################
	def Get_RateLTL(self):
		#############################
		# 読み出し先初期化
		self.ARR_RateTL = []
		
		#############################
		# ファイル読み込み
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['Rate_LTLFile']
		if CLS_File.sReadFile( wFile_path, outLine=self.ARR_RateTL )!=True :
			return False	#失敗
		
		return True			#成功

	#####################################################
	def Set_RateLTL(self):
		#############################
		# ファイル書き込み (改行つき)
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.DEF_STR_FILE['Rate_LTLFile']
		if CLS_File.sWriteFile( wFile_path, self.ARR_UpdateTL, inRT=True )!=True :
			return False	#失敗
		
		return True			#成功

	#####################################################
	def Init_RateLTL(self):
		#############################
		# IDを詰め込む
		self.ARR_UpdateTL = []
		for wROW in self.ARR_NewTL :
			self.ARR_UpdateTL.append( wROW['id'] )
		
		#############################
		# ファイル書き込み (改行つき)
		self.Set_RateLTL()
		return



