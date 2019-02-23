# coding: UTF-8
#####################################################
# 十八試るしぼっと
#   Class   ：トゥート収集処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2018/11/24
#####################################################
from datetime import datetime
import codecs
import os
import random
import linecache
import re
import sys
import MeCab
import global_val
#####################################################
class CLS_TootCorrect:

	InitCorrect = False					#読み込んだか
	
	WordStudyNum = 0					#単語学習トゥート数
	
	BrDict = {}							#単語(辞書)
	ClazList = []						#品詞パターン
	
	WordList = {}						#単語一覧
	WordListREM = {}					#禁止ワード
	FLG_WordUpdate = False
	
	OBJ_MeCab = ""

	CopeCorr = {
		"Now_Word"  : 0,				#今学習した単語数
		"dummy"     : 0					#(未使用)
	}



#####################################################
# Init
#####################################################
	def __init__(self):
		if global_val.gConfig["WordStudy"] != "on" :
			return	#機能無効
		
		self.pCreate_MeCab()
		return



#####################################################
# MeCab処理
#####################################################
	def pCreate_MeCab(self):
		self.OBJ_MeCab = MeCab.Tagger( "-Ochasen" )
		return



#####################################################
# 文章解読
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
#	[7]	ウチ		読み
#	[8]	ウチ		発音
#####################################################
	def pAnalize_MeCab( self, words ):
		#############################
		# MeCabで文章解読
		word_ex = words.encode("utf-8")
		annalize = self.OBJ_MeCab.parseToNode( word_ex )
		
		#############################
		# 解読結果の辞書化
		get_words = {}
		index = 0
		while annalize :
			#############################
			# 解読結果を配列化
			annalize_line = annalize.feature.split(',')
			
			#############################
			# 辞書に詰め込む
			#   念のためutf-8でデコードする
			get_words.update({ index : "" })
			get_words[index] = {}
			get_words[index].update({ "word" : annalize.surface.decode("utf-8", "ignore") })
			get_words[index].update({ "claz" : annalize_line[0].decode("utf-8", "ignore") })
			
			get_words[index].update({ "cla1" : annalize_line[1].decode("utf-8", "ignore") })
			get_words[index].update({ "cla2" : annalize_line[2].decode("utf-8", "ignore") })
			get_words[index].update({ "cla3" : annalize_line[3].decode("utf-8", "ignore") })
			get_words[index].update({ "ktyp" : annalize_line[4].decode("utf-8", "ignore") })
			get_words[index].update({ "kkat" : annalize_line[5].decode("utf-8", "ignore") })
			
			#############################
			# 英文に読みが付かない対応(MeCabのせい)
			if len(annalize_line) > 7 :
				get_words[index].update({ "yomi" : annalize_line[7].decode("utf-8", "ignore") })
			else :	#index0-6
				get_words[index].update({ "yomi" : "*" })
			
			index += 1
			
			#############################
			# 次の単語へ
			annalize = annalize.next
		
		return get_words



#####################################################
# 辞書読み込み
#   辞書型で登録する
#####################################################
	def cGet_Words(self):
		if global_val.gConfig["WordStudy"] != "on" :
			return	#機能無効
		
		if os.path.exists(global_val.gUserDic_file)==False :
			global_val.gCLS_Mylog.cLog('a', "CLS_TootCorrect：cGet_Words：ファイルがない：" + global_val.gUserDic_file )
			return
		
		#初期化
		self.BrDict = {}
		
		self.WordList = {}
		for line in codecs.open( global_val.gUserDic_file, 'r', 'utf-8'):	#ファイルを開く
			line = line.strip()
			lines = line.split(global_val.gCHR_Border)
			
			index = lines[0]
			self.WordList.update({ index : "" })
			self.WordList[index] = {}
			self.WordList[index].update({ "word" : lines[0] })
			self.WordList[index].update({ "claz" : lines[1] })
			self.WordList[index].update({ "yomi" : lines[2] })
			
			self.WordList[index].update({ "cla1" : lines[3] })
			self.WordList[index].update({ "cla2" : lines[4] })
			self.WordList[index].update({ "cla3" : lines[5] })
			self.WordList[index].update({ "ktyp" : lines[6] })
			self.WordList[index].update({ "kkat" : lines[7] })
			
			self.WordList[index].update({ "date" : lines[8] })
			self.WordList[index].update({ "def"  : lines[9] })
			#使用辞書に登録
			self.pSet_BrDict( lines[1], lines[0] )
		
		res = self.pGet_WordsRem()	#禁止ワードも読み込む
		if res!=True :
			return
		
		res = self.pGet_ClazList()	#品詞リストも読み込む
		if res!=True :
			return
		
		self.InitCorrect = True		#有効
		return



#####################################################
# 禁止ワードの読み込み
#   辞書型で登録する
#####################################################
	def pGet_WordsRem(self):
		if os.path.exists(global_val.gUserDicRem_file)==False :
			global_val.gCLS_Mylog.cLog('a', "CLS_TootCorrect：pGet_WordsRem：ファイルがない：" + global_val.gUserDicRem_file )
			return False
		
		self.WordListREM = {}
		for line in codecs.open( global_val.gUserDicRem_file, 'r', 'utf-8'):	#ファイルを開く
			line = line.strip()
			self.WordListREM.update({ line : 0 })
		
		return True



#####################################################
# 禁止ワードチェック
#####################################################
	def pCheck_WordsRem(self,word):
		if len(self.WordListREM)<=0 :
			return True	#禁止なしorロード失敗だったら
		
		keylist = self.WordListREM.keys()
		if word in keylist :
			return False	#禁止あり
			
		return True



#####################################################
# 辞書書き出し
#####################################################
	def cSet_Words(self):
		if self.FLG_WordUpdate == False or self.InitCorrect == False :
			return	#更新なし or 機能無効
		
		if os.path.exists(global_val.gUserDic_file)==False :
			global_val.gCLS_Mylog.cLog('a', "CLS_TootCorrect：cSet_Words：ファイルがない：" + global_val.gUserDic_file )
			return
		
		#############################
		# ユーザ収集ファイルのオープン
		file = codecs.open( global_val.gUserDic_file, 'w', 'utf-8')
		file.close()
		file = codecs.open( global_val.gUserDic_file, 'w', 'utf-8')
		
		#############################
		# 追加データを作成
		setline = []
		keylist = self.WordList.keys()
		for ikey in keylist :
			line = self.WordList[ikey]['word'] + global_val.gCHR_Border
			line = line + self.WordList[ikey]['claz'] + global_val.gCHR_Border
			line = line + self.WordList[ikey]['yomi'] + global_val.gCHR_Border
			
			line = line + self.WordList[ikey]['cla1'] + global_val.gCHR_Border
			line = line + self.WordList[ikey]['cla2'] + global_val.gCHR_Border
			line = line + self.WordList[ikey]['cla3'] + global_val.gCHR_Border
			line = line + self.WordList[ikey]['ktyp'] + global_val.gCHR_Border
			line = line + self.WordList[ikey]['kkat'] + global_val.gCHR_Border
			
			line = line + str(self.WordList[ikey]['date']) + global_val.gCHR_Border
			line = line + self.WordList[ikey]['def'] + '\n'
			setline.append(line)

		
		#############################
		# 書き込んで閉じる
		file.writelines( setline )
		file.close()
		
		self.pSet_ClazList()	#品詞リストも書きだす
		
		#############################
		# 単語学習数のログ書きだし
		if self.CopeCorr["Now_Word"] > 0 :
			msg = "Word=" + str(self.CopeCorr["Now_Word"])
			global_val.gCLS_Mylog.cLog('b', "単語学習完了：" + msg )
		
		return



#####################################################
# 品詞リスト読み込み
#   リスト型で登録する
#####################################################
	def pGet_ClazList(self):
		if os.path.exists(global_val.gClazList_file)==False :
			global_val.gCLS_Mylog.cLog('a', "CLS_TootCorrect：cGet_ClazList：ファイルがない：" + global_val.gClazList_file )
			return False
		
		#初期化
		self.ClazList = []
		
		for line in codecs.open( global_val.gClazList_file, 'r', 'utf-8'):	#ファイルを開く
			line = line.strip()
			lines = line.split(",")
			
			#1行リストに変換
			clist = []
			for claz in lines :
				clist.append(claz)
			
			#品詞リストに登録
			self.ClazList.append( clist )
		
		return True



#####################################################
# 品詞リスト書き出し
#####################################################
	def pSet_ClazList(self):
		if self.FLG_WordUpdate == False :
			return	#更新なし
		
		if os.path.exists(global_val.gClazList_file)==False :
			global_val.gCLS_Mylog.cLog('a', "CLS_TootCorrect：cSet_ClazList：ファイルがない：" + global_val.gClazList_file )
			return
		
		#############################
		# 品詞リストファイルのオープン
		file = codecs.open( global_val.gClazList_file, 'w', 'utf-8')
		file.close()
		file = codecs.open( global_val.gClazList_file, 'w', 'utf-8')
		
		#############################
		# 追加データを作成
		setline = []
		for lines in self.ClazList :
			line = ""
			for claz in lines :
				line = line + claz + ","
			
			line = line + '\n'
			setline.append(line)
		
		#############################
		# 書き込んで閉じる
		file.writelines( setline )
		file.close()
		
		return



#####################################################
# 辞書が使えるかどうか
#   文字登録数60以上かつ、各品詞が1以上の時、有効とする
#####################################################
	def cIs_Words(self):
		words = 0
		flg = True
		keylist = self.WordList.keys()
		#############################
		# 各品詞の数を判定
		for ikey in keylist :
			reng = len(self.WordList[ikey])
			if reng<1 :
				flg = False
				break
			#総数加算
			words += reng
		
		#############################
		# 辞書の登録総数を判断
		if words<60 :
			flg = False
		
		return flg



#####################################################
# 単語学習
#####################################################
	def cWordStudy( self, row ):
		if self.InitCorrect != True :
			return False	#機能無効
		
		#############################
		# 学習数が上限か
		if global_val.gConfig['studyNum'] <= self.WordStudyNum :
			return False
		
			#自分は登録しない
		userinfo = row['account']
		fulluser = global_val.gCLS_UserInfo.cGet_FullUser( userinfo['username'], userinfo['url'] )
		if fulluser['fulluser'] == global_val.gConfig["UserBot"] :
			return False
		
		cont = global_val.gCLS_MainProc.cDel_HTML( row['content'] )
		#############################
		# ユーザ収集
		idnum = int(userinfo['id'])
		global_val.gCLS_UserInfo.cAdd_UserCorrect(row)		#未収集なら追加・フォロー候補
		
		#############################
		# ここまで来たら学習を試みたことにする
		self.WordStudyNum += 1
		
		#############################
		# 辞書のうち古い単語は忘れる
		keylist = self.WordList.keys()
		for ikey in list(keylist) :	#RuntimeError対策
			if self.WordList[ikey]['def'] != "-" :
				continue	#消したくない単語はスキップ
			rate_date = datetime.strptime( str(self.WordList[ikey]['date']), "%Y-%m-%d %H:%M:%S" )
			ratday = global_val.gFull_TimeDate - rate_date
			ratday = ratday.days
			if global_val.gConfig["studyDay"] < ratday :
				self.WordList.pop(ikey)
				self.FLG_WordUpdate = True
		
		#############################
		# 文章の解読＆エンコード
		get_words = self.pAnalize_MeCab( cont )
		get_words_len = len( get_words )
		if get_words_len == 0 :
			return False
		
		keylist = get_words.keys()
		clazlist = []
		for ikey in keylist :
			word = get_words[ikey]['word']
			#############################
			# 登録済みの単語か
			if word in self.WordList :
				self.WordList[word]['date'] = global_val.gFull_TimeDate	#触れたので再記憶
				self.FLG_WordUpdate = True
				continue
			
			#############################
			# BOS/EOS
			if get_words[ikey]['claz'] == "BOS/EOS" :
				continue
			
			#############################
			# 意識不明な単語、パターンとして使えない単語
			if (get_words[ikey]['claz'] == "名詞" and get_words[ikey]['yomi'] == "*" and get_words[ikey]['cla1'] == "サ変接続" ) or \
			   (get_words[ikey]['claz'] == "名詞" and get_words[ikey]['cla1'] == "数" ) or \
			   get_words[ikey]['claz'] == "記号" :
				continue
			
			#############################
			# 名詞かつ 3文字以内の半角英字
			if (get_words[ikey]['claz'] == "名詞" and get_words[ikey]['cla1'] == "一般" ) or \
			   (get_words[ikey]['claz'] == "名詞" and get_words[ikey]['cla1'] == "固有名詞" and get_words[ikey]['cla2'] == "組織" ) :
				res = re.search( r'^[a-zA-Z]+$', word )
				if res:
					if len(word)<=3 :
						continue
			
			#############################
			# 禁止ワードか
			if self.pCheck_WordsRem(word)==False :
				break
			
			#############################
			# 辞書の登録数が最大か
			#   最大なら一番上の1個を削除する
			#   削除できなければ、登録せず終わる
			leng = len( self.WordList )
			if leng >= global_val.gConfig['studyMax'] :
				del_keylist = self.WordList.keys()
				flg_del = False
				for d_ikey in del_keylist :
					if self.WordList[d_ikey]['def'] == "-" :
						self.WordList.pop(d_ikey)
						flg_del = True
						break
				
				if flg_del == False :
					global_val.gCLS_Mylog.cLog('b', "これ以上学習不可" )
					return False
			
			#############################
			# 単語の登録
			word = get_words[ikey]['word']	#念のため
			self.WordList.update({ word : "" })
			self.WordList[word] = {}
			self.WordList[word].update({ "word" : word })
			self.WordList[word].update({ "claz" : get_words[ikey]['claz'] })
			self.WordList[word].update({ "yomi" : get_words[ikey]['yomi'] })
			
			self.WordList[word].update({ "cla1" : get_words[ikey]['cla1'] })
			self.WordList[word].update({ "cla2" : get_words[ikey]['cla2'] })
			self.WordList[word].update({ "cla3" : get_words[ikey]['cla3'] })
			self.WordList[word].update({ "ktyp" : get_words[ikey]['ktyp'] })
			self.WordList[word].update({ "kkat" : get_words[ikey]['kkat'] })
			
			self.WordList[word].update({ "date" : global_val.gFull_TimeDate })
			self.WordList[word].update({ "def"  : "-" })
			
###			global_val.gCLS_Mylog.cLog('c', "単語登録：" + word )
			
			self.CopeCorr['Now_Word'] += 1
			self.FLG_WordUpdate = True
			
			clazlist.append(get_words[ikey]['claz'])
		
		#############################
		# 品詞パターン学習
		#   品詞数が1以上 かつ
		#   品詞リストが上限でない
		if len( clazlist ) > 0 and len(self.ClazList) < global_val.gClazList_Num:
			self.ClazList.append( clazlist )
		
		return True


#####################################################
# 文章取得
#####################################################
	def cGet_RandSentence( self ):
		#############################
		# 品詞パターンの決定
		reng = len( self.ClazList )
		if reng==0 :
			return ""	#パターンなし
		
		index = random.randrange( reng )
		
		#############################
		# 文章を組み立てる
		sentence = ""
		clazline = self.ClazList[index]
		rat_claz = ""
		rat_num = 0
		for claz in clazline :
			if claz=="":
				continue	#可変リストの空欄対応
			
			#############################
			# 同じ品詞の計測
			if claz==rat_claz:
				rat_num += 1
#				if rat_num>3:	#4回以上の場合スキップ
				if rat_num>2:	#3回以上の場合スキップ
					continue
			else :
				rat_claz = claz	#違う品詞=クリア
				rat_num = 1		#違う品詞 1回目
			
			word = self.pGet_RandWord( claz )
			if word=="":
				sentence = ""
				break
			
			sentence = sentence + word
		
		if sentence=="":
			return ""	#無効
		
		#############################
		# 使った品詞パターンは捨てる
		self.ClazList.pop(index)
		
		return sentence



#####################################################
# 使用単語辞書
#####################################################
	def pSet_BrDict( self, claz, word ):
		#############################
		# 品詞の登録があるか
		keylist = self.BrDict.keys()
		flg = False
		for key in keylist :
			if claz==key :
				flg = True
				break
		
		#############################
		# 品詞の登録がなければ作成
		if flg==False :
			self.BrDict.update({ claz : "" })
			key = claz
			self.BrDict[key] = {}
		
		#############################
		# 登録
		index = len( self.BrDict[key] )
		self.BrDict[key].update({ index : word })
		return



#####################################################
# 単語取得
#####################################################
	def pGet_RandWord( self, claz ):
		#############################
		# 品詞の登録があるか
		sel_claz = claz
		if claz not in self.BrDict :
			return ""
		
		#############################
		# 単語を決める
		reng = len( self.BrDict[sel_claz] )
		if reng==0 :
			return ""
		ran = random.randrange( reng )
		word = self.BrDict[sel_claz][ran]
		
		#############################
		# 延命する
		self.WordList[word]['date'] = global_val.gFull_TimeDate
		self.FLG_WordUpdate = True
		
		return word



