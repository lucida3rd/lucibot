#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ワード収集
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/11/21
#####################################################
# Private Function:
#   __selectMeCabDic(self):
#   __analizeMeCab( self, inWords ):
#
# Instance Function:
#   __init__( self, inPath ):
#   GetWordCorrectStat(self):
#   GetWordREM(self) :
#   GetRandToot(self) :
#   WordStudy( self, inCont ):
#
# Class Function(static):
#   (none)
#
#####################################################
import MeCab
from postgresql_use import CLS_PostgreSQL_Use

from osif import CLS_OSIF
from filectrl import CLS_File
from userdata import CLS_UserData
from gval import gVal
#####################################################
class CLS_WordCorr():
#####################################################
	Obj_Parent = ""		#親クラス実体
	OBJ_MeCab  = ""		#MeCAB実体
	
##	STR_WordDic  = {}	#単語辞書
##	STR_ClazList = []	#品詞リスト
	
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
		wFile_path = gVal.DEF_STR_FILE['WordREMFile']
		if CLS_File.sReadFile( wFile_path, outLine=gVal.STR_WordREM )!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: GetWordREM: WordREM file read failed: " + wFile_path )
			return False	#失敗
		
		return True			#成功



#####################################################
# ランダムトゥート取得
#####################################################
	def GetRandToot(self) :
		wToot = ""
		#############################
		# ワード収集が有効か
		if gVal.STR_MasterConfig['WordStudy']!="on" :
			return wToot	#無効
		
		#############################
		# DB接続
		wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: GetRandToot: DB Connect test is failed: " + wRes['Reason'] )
			wOBJ_DB.Close()
			return wToot
		
		#############################
		# 品詞パターンを取得
		wQuery = "select claz from TBL_CLAZ_LIST order by random() limit 1" + \
					";"
		wDBRes = wOBJ_DB.RunQuery( wQuery )
		wDBRes = wOBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: GetRandToot: Run Query is failed (get TBL_CLAZ_LIST): " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
			wOBJ_DB.Close()
			return wToot
		if len(wDBRes['Responce']['Data'])!=1 :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: GetRandToot: Run Query is failed (get TBL_CLAZ_LIST is not 1): " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
			wOBJ_DB.Close()
			return wToot
		wSelClazList = wDBRes['Responce']['Data'][0][0]
		wClazList    = wSelClazList.split(",")
		
		#############################
		# 最適化用にパターンにある品詞をまとめこむ。
		# ついで収集用にまとめ領域を作る。
		wRandDic = {}
		wClazDic = {}
		wIndex   = 0
		for wClaz in wClazList :
			wKeyList = list(wClazDic.keys())
			if wClaz not in wKeyList :
				wClazDic.update({ wClaz : 1 })
			else :
				wClazDic[wClaz] += 1
			
			wRandDic.update({ wIndex : "" })
			wRandDic[wIndex] = {}
			wRandDic[wIndex].update({ "claz" : wClaz })
			wRandDic[wIndex].update({ "word" : "" })
			wIndex += 1
		
		#############################
		# 品詞ごとにワードを収集する
		wKeyList = list(wClazDic.keys())
		for wKey in wKeyList :
			wQuery = "select word from TBL_WORD_CORRECT where " + \
						"claz = '" + wKey + "' order by random() limit " + str(wClazDic[wKey]) + \
						";"
			wDBRes = wOBJ_DB.RunQuery( wQuery )
			wDBRes = wOBJ_DB.GetQueryStat()
			if wDBRes['Result']!=True :
				##失敗
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: GetRandToot: Run Query is failed (get TBL_WORD_CORRECT is random select): " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
				wOBJ_DB.Close()
				return wToot
			
			for wWord in wDBRes['Responce']['Data'] :
				wRandList = wRandDic.keys()
				wFLG_Hit  = False
				for wRandKey in wRandList :
					if wRandDic[wRandKey]['claz']==wKey :
						wFLG_Hit = True
						break
				
				if wFLG_Hit==True :
					wRandDic[wRandKey]['word'] = wWord[0]
		
		#############################
		# 使った品詞パターンを削除する
		wQuery = "delete from TBL_CLAZ_LIST where " + \
					"claz = '" + wSelClazList + "'" + \
					";"
		wDBRes = wOBJ_DB.RunQuery( wQuery )
		wDBRes = wOBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: GetRandToot: Run Query is failed (delete TBL_CLAZ_LIST): " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
			wOBJ_DB.Close()
			return wToot
		
		#############################
		# DB切断
		wOBJ_DB.Close()
		
		#############################
		# 文字列に組み立てる
		wToot = ""
		wRandList = wRandDic.keys()
		for wRandKey in wRandList :
			wToot = wToot + wRandDic[wRandKey]['word']
		
		return wToot	#成功



#####################################################
# 文章解読 (単語に分解)
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
	def __analizeMeCab( self, inWords ):
##		#############################
##		# HTMLタグの除去
##		wWord = CLS_OSIF.sDel_HTML( inWords )
##		
		#############################
		# MeCabで文章解読
##		wAnnalize = self.OBJ_MeCab.parse( wWord )
		wAnnalize = self.OBJ_MeCab.parse( inWords )
		
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
			wGetWords[wIndex].update({ "word" : wWord })
			wGetWords[wIndex].update({ "claz" : wYouso[0] })
			
			wGetWords[wIndex].update({ "cla1" : wYouso[1] })
			wGetWords[wIndex].update({ "cla2" : wYouso[2] })
			wGetWords[wIndex].update({ "cla3" : wYouso[3] })
			wGetWords[wIndex].update({ "ktyp" : wYouso[4] })
			wGetWords[wIndex].update({ "kkat" : wYouso[5] })
			
			#############################
			# 英文に読み、発音が付かない対応
			if len(wYouso) > 7 :
				wGetWords[wIndex].update({ "yomi" : wYouso[7] })
			else :	#index0-6
				wGetWords[wIndex].update({ "yomi" : "*" })
			
			wIndex += 1
		
		#############################
		# 異常ありか？
		if wFlg_Error==True :
			wGetWords = {}	# 0を返す
		
		return wGetWords



#####################################################
# 単語学習
#####################################################
###	def WordStudy( self, inCont, inCreateAt ):
	def WordStudy( self, inCont ):
		#############################
		# 単語なし
		if inCont=="" :
			return False
		
		#############################
		# ' 文字が含まれていたら除外する
##		wRes = CLS_OSIF.sRe_Search( "'", inCont )
##		if wRes :
		if inCont.find("'")>=0 :
			return False
		
		#############################
		# ワード収集が有効か
		if gVal.STR_MasterConfig['WordStudy']!="on" :
			return False	#無効
		
		#############################
		# 今回の学習数が上限か
		if self.STR_Stat['StudyNum'] >= gVal.DEF_STR_TLNUM['studyNum'] :
			return False	#今回は学習しない
		
		#############################
		# DB接続
		wOBJ_DB = CLS_PostgreSQL_Use( gVal.DEF_STR_FILE['DBinfo_File'] )
		wRes = wOBJ_DB.GetIniStatus()
		if wRes['Result']!=True :
			##失敗
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: WordStudy: DB Connect test is failed: " + wRes['Reason'] )
			wOBJ_DB.Close()
			return False
		
		wVAL_Rate_WordNum = -1
		#############################
		# 1日1回、古いレコードを削除する
		if gVal.STR_TimeInfo['OneDay']==True :
			###現在のレコード数
			wDBRes = wOBJ_DB.RunCount( "TBL_WORD_CORRECT" )
			wDBRes = wOBJ_DB.GetQueryStat()
			if wDBRes['Result']!=True :
				##失敗
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: WordStudy: Run Query is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
				wOBJ_DB.Close()
				return False
			wVAL_Rate_WordNum = wDBRes['Responce']
			
			###指定日付の抽出
			wLag = gVal.DEF_STR_TLNUM['studyDay'] * 24 * 60 * 60
##			wLagTime = CLS_OSIF.sTimeLag( gVal.STR_TimeInfo['TimeDate'], inThreshold=wLag, inTimezone=-1 )
			wLagTime = CLS_OSIF.sTimeLag( inThreshold=wLag, inTimezone=-1 )
			if wLagTime['Result']!=True :
				##失敗
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: WordStudy: sTimeLag is failed" )
				wOBJ_DB.Close()
				return False
			
			###単語テーブル
			wQuery = "delete from TBL_WORD_CORRECT where lupdate < " + \
					"timestamp '" + str(wLagTime['RateTime']) + "' " + \
					";"
			wDBRes = wOBJ_DB.RunQuery( wQuery )
			wDBRes = wOBJ_DB.GetQueryStat()
			if wDBRes['Result']!=True :
				##失敗
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: WordStudy: Run Query is failed (Old TBL_WORD_CORRECT delete): " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
				wOBJ_DB.Close()
				return False
			
			###品詞パターン テーブル
			wQuery = "delete from TBL_CLAZ_LIST where lupdate < " + \
					"timestamp '" + str(wLagTime['RateTime']) + "' " + \
					";"
			wDBRes = wOBJ_DB.RunQuery( wQuery )
			wDBRes = wOBJ_DB.GetQueryStat()
			if wDBRes['Result']!=True :
				##失敗
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: WordStudy: Run Query is failed (Old TBL_CLAZ_LIST delete): " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
				wOBJ_DB.Close()
				return False
			
			###削除後レコード数
			wDBRes = wOBJ_DB.RunCount( "TBL_WORD_CORRECT" )
			wDBRes = wOBJ_DB.GetQueryStat()
			if wDBRes['Result']!=True :
				##失敗
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: WordStudy: Run Query is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
				wOBJ_DB.Close()
				return False
			wVAL_WordNum = wDBRes['Responce']
			
			###削除数
			wVAL_Delete_WordNum = wVAL_Rate_WordNum - wVAL_WordNum
			self.STR_Stat["Delete"] += wVAL_Delete_WordNum
			self.Obj_Parent.OBJ_Mylog.Log( 'b', "古い単語・品詞パターン削除: 対象=" + str(wLagTime['RateTime']) + " 以前" )
		
		#############################
		# レコード数の抽出
		if wVAL_Rate_WordNum==-1 :
			###削除で結果出してない場合に処理する
			wDBRes = wOBJ_DB.RunCount( "TBL_WORD_CORRECT" )
			wDBRes = wOBJ_DB.GetQueryStat()
			if wDBRes['Result']!=True :
				##失敗
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: WordStudy: Run Query is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
				wOBJ_DB.Close()
				return False
			
			wVAL_WordNum = wDBRes['Responce']
		
		#############################
		# 学習数が上限か
		if gVal.DEF_STR_TLNUM['studyMax'] <= wVAL_WordNum :
			if self.STR_Stat['WordLimit']==False :
				self.Obj_Parent.OBJ_Mylog.Log( 'b', "学習不能(単語登録数上限: " + str(gVal.DEF_STR_TLNUM['studyMax']) + "件)" )
				self.STR_Stat['WordLimit'] = True
			wOBJ_DB.Close()
			return False	#上限
		
		#############################
		# デコーダで解読 (出力は辞書型)
		wGetWords = self.__analizeMeCab( inCont )
		if len(wGetWords) == 0 :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: WordStudy: MeCab analize result is zero, or failed" )
			wOBJ_DB.Close()
			return False	#失敗
		
		# ここまでで登録処理確定
		#############################
		self.STR_Stat['Cope'] += len( wGetWords )	#単語数を記録
		
##		#############################
##		# トゥートから時間を取得
##		wTime = CLS_OSIF.sGetTimeformat( inCreateAt )
##		if wTime['Result']==True :
##			wTime = wTime['TimeDate']
##		else:
##			wTime = None
##		
		#############################
		# 解読した結果(単語)を判定しながら詰めていく
		wKeylist  = wGetWords.keys()	#キーはIndex整数
		wClazList = ""					#文書パターン
		for wKey in wKeylist :
			#############################
			# 登録済みの単語か
			wQuery = "word = '" + wGetWords[wKey]['word'] + "'"
			wDBRes = wOBJ_DB.RunExist( "TBL_WORD_CORRECT", wQuery )
			wDBRes = wOBJ_DB.GetQueryStat()
			if wDBRes['Result']!=True :
				##失敗
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: WordStudy: Run Query is failed (Word check): " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
				wOBJ_DB.Close()
				return False
			
			if wDBRes['Responce']==True :
				###登録済み
				###  触れたので時刻を更新
				wQuery = "update TBL_WORD_CORRECT set " + \
						"lupdate = '"   + str(gVal.STR_TimeInfo['TimeDate']) + "' " + \
						"where word = '" + wGetWords[wKey]['word'] + "' ;"
				
				wDBRes = wOBJ_DB.RunQuery( wQuery )
				wDBRes = wOBJ_DB.GetQueryStat()
				if wDBRes['Result']!=True :
					##失敗
					self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: WordStudy: Run Query is failed (Word check, time update): " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
					wOBJ_DB.Close()
					return False
				
				###品詞パターンは記録する
				wClazList = wClazList + wGetWords[wKey]['claz'] + ","
				continue	#登録済なのでスキップ
			
			#############################
			# 除外する品詞か
			#### BOS/EOS
			if wGetWords[wKey]['claz'] == "BOS/EOS" :
				continue
			
			#### 意識不明な単語、パターンとして使えない単語
			if (wGetWords[wKey]['claz'] == "名詞" and wGetWords[wKey]['yomi'] == "*" and wGetWords[wKey]['cla1'] == "サ変接続" ) or \
			   (wGetWords[wKey]['claz'] == "名詞" and wGetWords[wKey]['cla1'] == "数" ) or \
			   wGetWords[wKey]['claz'] == "記号" :
				continue
			
			#### 名詞かつ 3文字以内の半角英字
			if (wGetWords[wKey]['claz'] == "名詞" and wGetWords[wKey]['cla1'] == "一般" ) or \
			   (wGetWords[wKey]['claz'] == "名詞" and wGetWords[wKey]['cla1'] == "固有名詞" and wGetWords[wKey]['cla2'] == "組織" ) :
				wRes = CLS_OSIF.sRe_Search( r'^[a-zA-Z]+$', wGetWords[wKey]['word'] )
				if wRes:
					if len(wGetWords[wKey]['word'])<=3 :
						continue
			
			#### 禁止ワードを含むか
##			if self.CheckWordREM( wGetWords[wKey]['word'] )==False :
			if wGetWords[wKey]['word'] in gVal.STR_WordREM :
				continue	#禁止あり
			
			###**ループ中に辞書の登録上限を超えても何もしない仕様(DBだしええかと)
			
			#############################
			# 単語の登録
			wWord = str(wGetWords[wKey]['word']).replace( "'", "''" )
			wClaz = str(wGetWords[wKey]['claz']).replace( "'", "''" )
			wYomi = str(wGetWords[wKey]['yomi']).replace( "'", "''" )
			wQuery = "insert into TBL_WORD_CORRECT values (" + \
						"'" + wWord + "'," + \
						"'" + wClaz + "'," + \
						"'" + wYomi + "'," + \
						"'" + wGetWords[wKey]['cla1'] + "'," + \
						"'" + wGetWords[wKey]['cla2'] + "'," + \
						"'" + wGetWords[wKey]['cla3'] + "'," + \
						"'" + wGetWords[wKey]['ktyp'] + "'," + \
						"'" + wGetWords[wKey]['kkat'] + "'," + \
						"'" + str(gVal.STR_TimeInfo['TimeDate']) + "'," + \
						"False " + \
						") ;"
			
			wDBRes = wOBJ_DB.RunQuery( wQuery )
			wDBRes = wOBJ_DB.GetQueryStat()
			if wDBRes['Result']!=True :
				##失敗
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: WordStudy: Run Query is failed (Word regist): " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
				wOBJ_DB.Close()
				return False
			
			self.STR_Stat['Regist'] += 1
			
			###品詞パターンは記録する
			wClazList = wClazList + wGetWords[wKey]['claz'] + ","
		
		#############################
		# 今回の学習回数更新
		self.STR_Stat['StudyNum'] += 1
		
		#############################
		# 品詞パターン学習
		if wClazList!="" :
			wClazList = wClazList[0:len(wClazList)-1]	#末尾の','を抜く
			
			###同じ品詞パターンがあるか
			wQuery = "claz = '" + wClazList + "'"
			wDBRes = wOBJ_DB.RunExist( "TBL_CLAZ_LIST", wQuery )
			wDBRes = wOBJ_DB.GetQueryStat()
			if wDBRes['Result']!=True :
				##失敗
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: WordStudy: Run Query is failed (Claz check): " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
				wOBJ_DB.Close()
				return False
			
			if wDBRes['Responce']==True :
				###登録済みならここで終わる(正常)
				wOBJ_DB.Close()
				return True
			
			###登録なしなら、登録する
			###  **ここで品詞パターンの登録上限を超えても何もしない仕様(DBだしええかと)
			wQuery = "insert into TBL_CLAZ_LIST values (" + \
						"'" + wClazList + "'," + \
						"'" + str(gVal.STR_TimeInfo['TimeDate']) + "'," + \
						"False " + \
						") ;"
			
			wDBRes = wOBJ_DB.RunQuery( wQuery )
			wDBRes = wOBJ_DB.GetQueryStat()
			if wDBRes['Result']!=True :
				##失敗
				self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_WordCorr: WordStudy: Run Query is failed (Claz regist): " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
				wOBJ_DB.Close()
				return False
			
			self.STR_Stat['ClazList'] += 1
		
		#############################
		# 正常終了
		wOBJ_DB.Close()
		return True



