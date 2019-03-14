#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ワード収集
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/14
#####################################################
# Private Function:
#   __selectMeCabDic(self):
#   __deleteOldWord(self) :
#   __getClazList(self) :
#   __setClazList(self) :
#   __getWordDic_Fmt(self) :
#   __chgWordDic_Line( self, inKey ) :
#
# Instance Function:
#   __init__( self, inPath ):
#   GetWordCorrectStat(self):
#   GetWordREM(self) :
#   CheckWordREM( self, inWord ):
#   GetWorddic(self) :
#   SetWorddic(self) :
#   Analize_MeCab( self, inWords ):
#   WordStudy( self, inROW ):
#
# Class Function(static):
#   (none)
#
#####################################################
import MeCab

from osif import CLS_OSIF
from filectrl import CLS_File
from userdata import CLS_UserData
from gval import gVal
#####################################################
class CLS_WordCorr():
#####################################################
	Obj_Parent = ""		#親クラス実体
	OBJ_MeCab  = ""		#MeCAB実体
	
	STR_WordDic  = {}	#単語辞書
	STR_ClazList = []	#品詞リスト
	
	STR_Stat = {
		"Cope"		: 0,		#今回の処理単語数
		"Regist"	: 0,		#今回の登録単語数
		"Delete"	: 0,		#今回の削除単語数
		"ClazList"	: 0,		#品詞リスト数
		
		"StudyNum"	: 0,		#今回の学習回数
		"WordLimit"	: False		#単語学習上限超えか
	}

#####################################################
# Init
#####################################################
	def GetWordCorrectStat(self):
		return self.STR_Stat



#####################################################
# Init
#####################################################
	def __init__( self, parentObj=None ):
		if parentObj==None :
			###親クラス実体の未設定
			CLS_OSIF.sPrn( "CLS_WordCorr: __init__: You have not set the parent class entity for parentObj" )
			return
		
		self.Obj_Parent = parentObj
		self.__selectMeCabDic()
		return



#####################################################
# MeCab辞書の設定
#####################################################
	def __selectMeCabDic(self):
##		### 標準辞書？
##		self.OBJ_MeCab  = MeCab.Tagger( "-Ochasen" )
		
		### MeCabシステム辞書
		self.OBJ_MeCab  = MeCab.Tagger('-d /usr/local/lib/mecab/dic/ipadic')
		return



#####################################################
# 禁止ワード読み込み
#####################################################
	def GetWordREM(self) :
		#############################
		# 初期化
		gVal.STR_WordREM = []
		
		#############################
		# ファイル読み込み
		wFile_path = gVal.STR_File['WordREMFile']
		if CLS_File.sReadFile( wFile_path, outLine=gVal.STR_WordREM )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_UserCorr: GetWordREM: WordREM file read failed: " + wFile_path )
			return False	#失敗
		
		return True			#成功



#####################################################
# 禁止ワードチェック
#####################################################
	def CheckWordREM( self, inWord ):
		#############################
		# 禁止ワードチェック
		if len( gVal.STR_WordREM )<=0 :
			return True		#禁止ワード未設定 orロード失敗だったら
		
		for wWordREM in gVal.STR_WordREM :
			if inWord.find( wWordREM )>=0 :
				return False	#禁止あり
		
		return True		#禁止なし



#####################################################
# 単語辞書データの読み込み(Master/Sub用)
#####################################################
	def GetWorddic(self) :
		#############################
		# 初期化
		self.STR_WordDic = {}
		wWork_WordDic    = []
		
		#############################
		# ファイル読み込み
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.STR_File['WorddicFile']
		if CLS_File.sReadFile( wFile_path, outLine=wWork_WordDic )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: GetWorddic: Worddic file read failed: " + wFile_path )
			return False	#失敗
		
		#############################
		# データをユーザ情報に読み出す
		try:
			for wLine in wWork_WordDic :
				wLine = wLine.split( gVal.DEF_DATA_BOUNDARY )	#分解
				
				wGet_WordDic = self.__getWordDic_Fmt()
				wGet_WordDic['Word'] = wLine[0]
				wGet_WordDic['Claz'] = wLine[1]
				wGet_WordDic['Yomi'] = wLine[2]
				
				wGet_WordDic['Cla1'] = wLine[3]
				wGet_WordDic['Cla2'] = wLine[4]
				wGet_WordDic['Cla3'] = wLine[5]
				wGet_WordDic['Ktyp'] = wLine[6]
				wGet_WordDic['Kkat'] = wLine[7]
				
				wGet_WordDic['Lastupdate'] = wLine[8]
				wGet_WordDic['Def']  = wLine[9]
				
				self.STR_WordDic.update({ wLine[0] : wGet_WordDic })
		except ValueError as err :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: GetWorddic: Worddic exception: " + str(err) )
			return False	#失敗
		
		#############################
		# 品詞リストの読み込み
		self.__getClazList()
		
		#############################
		# 辞書のうち古い単語は忘れる
		self.__deleteOldWord()
		return True

	#####################################################
	def __deleteOldWord(self) :
		#############################
		# 現在時刻を取得する
		wTime = CLS_OSIF.sGetTime()
		if wTime['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: __deleteOldWord: sGetTime failed" )
			return
		
		wStudyDay = gVal.STR_MasterConfig['studyDay']	#覚えておく日数
		#############################
		# 辞書のうち古い単語を検索して消す
		wKeylist = self.STR_WordDic.keys()
		for wKey in list(wKeylist) :
			if self.STR_WordDic[wKey]['Def'] != "-" :
				continue	#消したくない単語はスキップ
			
##			wRateDate = datetime.strptime( str(self.STR_WordDic[wKey]['Lastupdate']), "%Y-%m-%d %H:%M:%S" )
##			wRatDay = wTime['TimeDate'] - wRateDate
##			wRatDay = wRatDay.days	#日に変換
##			if wStudyDay < ratday :
###				self.Obj_Parent.OBJ_Mylog.Log( 'c', "期限切れ単語削除: " + self.STR_WordDic[wKey]['Word'] )
##				self.STR_WordDic.pop( wKey )	#単語を削除
##				self.STR_Stat['Delete'] += 1
		
			wThreshold = wStudyDay * (60 * 60 * 24)	#日数を秒に直す
			wLag = CLS_OSIF.sTimeLag( str(self.STR_WordDic[wKey]['Lastupdate']), inThreshold=wThreshold )
			if wLag['Result']!=True :
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: __deleteOldWord: sGetTime failed" )
			
			if wLag['Beyond']==True :
				###期限切れ
###				self.Obj_Parent.OBJ_Mylog.Log( 'c', "期限切れ単語削除: " + self.STR_WordDic[wKey]['Word'] )
				self.STR_WordDic.pop( wKey )	#単語を削除
				self.STR_Stat['Delete'] += 1
		
		return

	#####################################################
	def __getClazList(self) :
		#############################
		# 初期化
		self.STR_ClazList = []
		
		#############################
		# ファイル読み込み
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.STR_File['ClazListFile']
		if CLS_File.sReadFile( wFile_path, outLine=self.STR_ClazList )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: __getClazList: ClazList file read failed: " + wFile_path )
			return False	#失敗
		
		return True			#成功



#####################################################
# 単語辞書データの書き込み(Master/Sub用)
#####################################################
	def SetWorddic(self) :
		#############################
		# 初期化
		wWork_WordDic = []
		
		#############################
		# データをユーザ情報に読み出す
		wKeyList = self.STR_WordDic.keys()
		for wKey in list(wKeyList) :
			wLine = self.__chgWordDic_Line( wKey )
			wWork_WordDic.append( wLine )
		
		#############################
		# ファイル書き込み
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.STR_File['WorddicFile']
		if CLS_File.sWriteFile( wFile_path, wWork_WordDic, inRT=True )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: GetWorddic: Worddic file write failed: " + wFile_path )
			return False	#失敗
		
		#############################
		# 品詞リストの書き込み
		self.__setClazList()
		
		return True

	#####################################################
	def __setClazList(self) :
		#############################
		# ファイル書き込み
		wFile_path = self.Obj_Parent.CHR_User_path + gVal.STR_File['ClazListFile']
		if CLS_File.sWriteFile( wFile_path, self.STR_ClazList, inRT=True )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: __setClazList: Userinfo file write failed: " + wFile_path )
			return False	#失敗
		
		return True



#####################################################
# 単語辞書型の取得
#####################################################
# 例：
#		表形式
#	[0]	名詞		品詞
#	[1]	非自立		品詞細分類1
#	[2]	副詞可能	品詞細分類2
#	[3]	*			品詞細分類3
#	[4]	*			活用型
#	[5]	*			活用形
#	[6]	うち		原型
#	[7]	ウチ		読み  *英語文字には要素が含まれない
#	[8]	ウチ		発音  *英語文字には要素が含まれない
#####################################################
	def __getWordDic_Fmt(self) :
		wWordDic = {}
		wWordDic.update({ "Word"       : "" })
		wWordDic.update({ "Claz"       : "" })
		wWordDic.update({ "Yomi"       : "" })
		
		wWordDic.update({ "Cla1"       : "" })
		wWordDic.update({ "Cla2"       : "" })
		wWordDic.update({ "Cla3"       : "" })
		wWordDic.update({ "Ktyp"       : "" })
		wWordDic.update({ "Kkat"       : "" })
		
		wWordDic.update({ "Lastupdate" : "" })
		wWordDic.update({ "Def"        : "" })
		return wWordDic



#####################################################
# 単語辞書書き出し型への変換
#####################################################
	def __chgWordDic_Line( self, inKey ) :
		wWordDic = ""
		wWordDic = wWordDic + str(self.STR_WordDic[inKey]['Word']) + gVal.DEF_DATA_BOUNDARY
		wWordDic = wWordDic + self.STR_WordDic[inKey]['Claz'] + gVal.DEF_DATA_BOUNDARY
		wWordDic = wWordDic + self.STR_WordDic[inKey]['Yomi'] + gVal.DEF_DATA_BOUNDARY
		
		wWordDic = wWordDic + self.STR_WordDic[inKey]['Cla1'] + gVal.DEF_DATA_BOUNDARY
		wWordDic = wWordDic + self.STR_WordDic[inKey]['Cla2'] + gVal.DEF_DATA_BOUNDARY
		wWordDic = wWordDic + self.STR_WordDic[inKey]['Cla3'] + gVal.DEF_DATA_BOUNDARY
		wWordDic = wWordDic + self.STR_WordDic[inKey]['Ktyp'] + gVal.DEF_DATA_BOUNDARY
		wWordDic = wWordDic + self.STR_WordDic[inKey]['Kkat'] + gVal.DEF_DATA_BOUNDARY
		
		wWordDic = wWordDic + str(self.STR_WordDic[inKey]['Lastupdate']) + gVal.DEF_DATA_BOUNDARY
		wWordDic = wWordDic + self.STR_WordDic[inKey]['Def']
		return wWordDic



#####################################################
# 文章解読 (単語に分解)
#####################################################
	def Analize_MeCab( self, inWords ):
		#############################
		# HTMLタグの除去
		wWord = CLS_OSIF.sDel_HTML( inWords )
		
		#############################
		# MeCabで文章解読
		wAnnalize = self.OBJ_MeCab.parse( wWord )
		
		#############################
		# まず単語別の解析毎に分ける
		wAnnalize = wAnnalize.split('\n')
		
		wGetWords = {}	#結果用
		wIndex    = 0	#辞書Index
		wFlg_Error = False
		for wAnalize_line in wAnnalize :
			if wAnalize_line=="EOS" :
				break	#終了
			
			#############################
			# 単語と解析要素を分ける
			wAnalize_line = wAnalize_line.split('\t')
			
			if not isinstance( wAnalize_line, list ) :
				wFlg_Error = True	#異常
			
			if len(wAnalize_line)!=2 :
				wFlg_Error = True	#異常
			
			wWord = wAnalize_line[0]	#単語を取り出す
			
			#############################
			# 解析要素を分ける
			wYouso = wAnalize_line[1].split(',')
			
			#############################
			# 結果を辞書に詰め込む
			wGetWords.update({ wIndex : "" })
			wGetWords[wIndex] = {}
			wGetWords[wIndex].update({ "Word" : wWord })
			wGetWords[wIndex].update({ "Claz" : wYouso[0] })
			
			wGetWords[wIndex].update({ "Cla1" : wYouso[1] })
			wGetWords[wIndex].update({ "Cla2" : wYouso[2] })
			wGetWords[wIndex].update({ "Cla3" : wYouso[3] })
			wGetWords[wIndex].update({ "Ktyp" : wYouso[4] })
			wGetWords[wIndex].update({ "Kkat" : wYouso[5] })
			
			#############################
			# 英文に読み、発音が付かない対応
			if len(wYouso) > 7 :
				wGetWords[wIndex].update({ "Yomi" : wYouso[7] })
			else :	#index0-6
				wGetWords[wIndex].update({ "Yomi" : "*" })
			
			wIndex += 1
		
		#############################
		# 異常ありか？
		if wFlg_Error==True :
			wGetWords = {}	# 0を返す
		
		return wGetWords



#####################################################
# 単語学習
#####################################################
	def WordStudy( self, inROW ):
		#############################
		# ワード収集が有効か
		if gVal.STR_Config['WordCorrect']!="on" :
			return False	#無効
		
		#############################
		# 今回の学習数が上限か
		if self.STR_Stat['StudyNum'] >= gVal.STR_MasterConfig['studyNum'] :
			return False	#今回は学習しない
		
		#############################
		# 自分のトゥートか
		wAccount  = inROW['account']
		wFulluser = CLS_UserData.sGetFulluser( wAccount['username'], wAccount['url'] )
		if wFulluser['Result']!=True :
			###今のところ通らないルート
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: WordStudy: sGetFulluser failed: " + wFulluser['Reason'] )
			return False	#失敗
		
		if wFulluser['Fulluser'] == self.Obj_Parent.CHR_Account :
			return False	#自分は学習しない
		
		#############################
		# 学習数が上限か
		wStudyMax = gVal.STR_MasterConfig['studyMax']
		if wStudyMax <= len(self.STR_WordDic) :
			if self.STR_Stat['WordLimit']==False :
				self.Obj_Parent.OBJ_Mylog.Log( 'b', "学習不能(単語登録数上限: " + str(wStudyMax) + "件)" )
				self.STR_Stat['WordLimit'] = True
			
			return False	#上限
		
		#############################
		# デコーダで解読 (出力は辞書型)
		wGetWords = self.Analize_MeCab( inROW['content'] )
		if len(wGetWords) == 0 :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: WordStudy: MeCab analize failed" )
			return False	#失敗
		
		# ここまでで登録処理確定
		#############################
		self.STR_Stat['Cope'] += len(wGetWords)	#単語数を記録
		
		#############################
		# トゥートから時間を取得
		wTime = CLS_OSIF.sGetTimeformat( inROW['created_at'] )
		if wTime['Result']==True :
			wTime = wTime['TimeDate']
		else:
			wTime = None
		
		wKeylist  = wGetWords.keys()	#キーはIndex整数
		wClazList = ""
		for wKey in wKeylist :
			#############################
			# 登録済みの単語か
			if wGetWords[wKey]['Word'] in self.STR_WordDic :
				if wTime != None :	#触れたので時刻を更新
					self.STR_WordDic[ wGetWords[wKey]['Word'] ]['Lastupdate'] = wTime
				
				wClazList = wClazList + wGetWords[wKey]['Claz'] + ","
				continue	#登録済なのでスキップ
			
			#############################
			# BOS/EOS
			if wGetWords[wKey]['Claz'] == "BOS/EOS" :
				continue
			
			#############################
			# 意識不明な単語、パターンとして使えない単語
			if (wGetWords[wKey]['Claz'] == "名詞" and wGetWords[wKey]['Yomi'] == "*" and wGetWords[wKey]['Cla1'] == "サ変接続" ) or \
			   (wGetWords[wKey]['Claz'] == "名詞" and wGetWords[wKey]['Cla1'] == "数" ) or \
			   wGetWords[wKey]['Claz'] == "記号" :
				continue
			
			#############################
			# 名詞かつ 3文字以内の半角英字
			if (wGetWords[wKey]['Claz'] == "名詞" and wGetWords[wKey]['Cla1'] == "一般" ) or \
			   (wGetWords[wKey]['Claz'] == "名詞" and wGetWords[wKey]['Cla1'] == "固有名詞" and wGetWords[wKey]['Cla2'] == "組織" ) :
				wRes = CLS_OSIF.sRe_Search( r'^[a-zA-Z]+$', wGetWords[wKey]['Word'] )
				if wRes:
					if len(wGetWords[wKey]['Word'])<=3 :
						continue
			
			#############################
			# 禁止ワードを含むか
			if self.CheckWordREM( wGetWords[wKey]['Word'] )==False :
				continue	#禁止あり
			
			#############################
			# ループ中に辞書の登録数が最大か
			#   最大なら一番上の1個を削除する
			#   削除できなければ、登録せず終わる
			if wStudyMax <= len( self.STR_WordDic ) :
				wDel_Keylist = self.STR_WordDic.keys()
				wFlg_Del = False
				for wD_Key in list(wDel_Keylist) :
					if self.STR_WordDic[wD_Key]['Def'] == "-" :
						self.STR_WordDic.pop(wD_Key)
						self.STR_Stat['Delete'] += 1
						wFlg_Del = True
						break
				
				if wFlg_Del == False :
					if self.STR_Stat['WordLimit']==False :
						self.Obj_Parent.OBJ_Mylog.Log( 'b', "学習不能(登録中上限超え: " + str(wStudyMax) + "件)" )
						self.STR_Stat['WordLimit'] = True
					
					return False
			
			#############################
			# 単語の登録
			wWordKey = wGetWords[wKey]['Word']
			self.STR_WordDic.update({ wWordKey : "" })
			self.STR_WordDic[wWordKey] = {}
			self.STR_WordDic[wWordKey].update({ "Word" : wWordKey })
			self.STR_WordDic[wWordKey].update({ "Claz" : wGetWords[wKey]['Claz'] })
			self.STR_WordDic[wWordKey].update({ "Yomi" : wGetWords[wKey]['Yomi'] })
			
			self.STR_WordDic[wWordKey].update({ "Cla1" : wGetWords[wKey]['Cla1'] })
			self.STR_WordDic[wWordKey].update({ "Cla2" : wGetWords[wKey]['Cla2'] })
			self.STR_WordDic[wWordKey].update({ "Cla3" : wGetWords[wKey]['Cla3'] })
			self.STR_WordDic[wWordKey].update({ "Ktyp" : wGetWords[wKey]['Ktyp'] })
			self.STR_WordDic[wWordKey].update({ "Kkat" : wGetWords[wKey]['Kkat'] })
			
			self.STR_WordDic[wWordKey].update({ "Lastupdate" : wTime })
			self.STR_WordDic[wWordKey].update({ "Def"  : "-" })
			
			self.STR_Stat['Regist'] += 1
			
			wClazList = wClazList + wGetWords[wKey]['Claz'] + ","
		
		#############################
		# 今回の学習回数更新
		self.STR_Stat['StudyNum'] += 1
		
		#############################
		# 品詞パターン学習
		if wClazList!="" :
			wClazList = wClazList[0:len(wClazList)-1]	#末尾の','を抜く
			
			# 同じパターンがなければ
			if wClazList not in self.STR_ClazList :
				#品詞リストの最大超えならランダムで1個減らす
				if len(self.STR_ClazList) >= gVal.STR_MasterConfig['clazListNum']:
					wVal = CLS_OSIF.sGetRand( len(self.STR_ClazList) )
					if wVal>=0 :
						self.STR_ClazList.pop(wVal)
				
				#パターン追加
				self.STR_ClazList.append( wClazList )
				self.STR_Stat['ClazList'] += 1
		
		return True



