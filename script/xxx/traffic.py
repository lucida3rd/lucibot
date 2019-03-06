# coding: UTF-8
#####################################################
# 十八試るしぼっと
#   Class   ：トラヒック処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2018/11/24
#####################################################
from datetime import datetime
from datetime import timedelta
import codecs
import os
import random
import linecache
import re
import global_val
#####################################################
class CLS_Traffic:
	
	Init = False
	
	Now_Traffic = {}	#トラヒック記録
	Rat_Traffic = {}
	FLG_UserCorr = False



#####################################################
# Init
#####################################################
	def __init__(self):
		if global_val.gConfig["Traffic"] != "on" :
			return
		
		#############################
		# トラヒックの初期化
		self.pInitTraffic()
		return



#####################################################
# トラヒックのカウント
#####################################################
	def cCnt_Traffic(self,row):
		#############################
		# 初期化済みか
		if self.Init != True:
			return
		
		#############################
		# ドメインを抜き取る
		index = row['account']['url'].find('/@')
		udomain = row['account']['url']
		udomain = udomain[8:index]
		
		#############################
		# ドメインが記録対象か
		keylist = self.Now_Traffic.keys()
		cflg = False
		for ckey in keylist :
			if udomain == ckey :
				cflg = True
				break
		
		if cflg == True :
			self.Now_Traffic[udomain] += 1
		else :
			self.Now_Traffic['--Others--'] += 1
		
		return



#####################################################
# トラヒックのトゥート
#####################################################
	def cToot_Traffic(self):
		#############################
		# 初期化済みか
		if self.Init != True:
			return False
		
		#############################
		# 退避トラヒックのセーブ
		self.pSet_WorkTraffic()
		
		#############################
		# 1時間経ってないか
		if global_val.gFlg_1HourTime == False :
			return False
		
		#############################
		# 最初の1時間はスキップする
		#   データは破棄
		if global_val.gTraffic_1HourSkip == True :
			global_val.gCLS_Mylog.cLog('c', "トラヒック 1時間スキップ")
			global_val.gTraffic_1HourSkip = False
			self.pAllClearTraffic()
			self.pSet_WorkTraffic()	##セーブ
			return False
		
		#############################
		#トラヒック対象を取得
		keylist = self.Now_Traffic.keys()
		
		#############################
		#過去との比較をするか
		flg_rate = False
		for ckey in keylist :
			if self.Rat_Traffic[ckey]>0 :
				flg_rate = True
				break
		
		#############################
		#時間の組み立て
		#  1時間前の時間をセット
##		ntime = global_val.gOBJ_TimeDate.strftime("%Y-%m-%d %H")
		ntime = global_val.gOBJ_TimeDate - timedelta(hours=1)
		ntime = ntime.strftime("%Y-%m-%d %H")
		
		#############################
		#トゥートを作成
		cw_text = "mastodon：" + ntime + "時の連合トゥート数（本鯖上観測）"
		toot_text = ''
		if flg_rate==True :
			for ckey in keylist :
				rate_val = self.Now_Traffic[ckey] - self.Rat_Traffic[ckey]
				if rate_val>0:
					plus_text = "+"
				else :
					plus_text = ""
				toot_text = toot_text + ckey + '=' + str(self.Now_Traffic[ckey]) + "(" + plus_text + str(rate_val) + ")" + '\n'
		else :
			for ckey in keylist :
				toot_text = toot_text + ckey + '=' + str(self.Now_Traffic[ckey]) + '\n'
		
		#############################
		#トゥート
		res = global_val.gCLS_Mastodon.cCwToot( spoiler_text=cw_text, status=toot_text, visibility=global_val.gVisi_Range )
		
		#############################
		#Twitterへも投稿
		if res['result']==True:
			tweet_text = cw_text + '\n' + res['responce']['url']
			global_val.gCLS_Twitter.cTweet( tweet_text )
		
		#############################
		# トラヒック記録を初期化する
		self.pClearTraffic()
		self.pSet_WorkTraffic()
		
		return True



#####################################################
# トラヒックをクリア
#   現在は過去に退避する
#####################################################
	def pClearTraffic(self):
		keylist = self.Now_Traffic.keys()
		for ckey in keylist :
			self.Rat_Traffic[ckey] = self.Now_Traffic[ckey]
			self.Now_Traffic[ckey] = 0
		
		return



#####################################################
# トラヒック全クリア
#####################################################
	def pAllClearTraffic(self):
		keylist = self.Now_Traffic.keys()
		for ckey in keylist :
			self.Rat_Traffic[ckey] = 0
			self.Now_Traffic[ckey] = 0
		
		return



#####################################################
# トラヒックの初期化
#####################################################
	def pInitTraffic(self):
		#############################
		# 記録領域の初期化
		self.Now_Traffic = {}
		self.Rat_Traffic = {}
		
		#############################
		# 記録領域の作成
		file = open( global_val.gTraffic_file, 'r')
		for row in file:
			str_inst = row.strip()
			self.Now_Traffic.update({ str_inst : 0 })
			self.Rat_Traffic.update({ str_inst : 0 })
		file.close()
		
		self.Now_Traffic.update({ "--Others--" : 0 })
		self.Rat_Traffic.update({ "--Others--" : 0 })
		
		#############################
		# 退避トラヒックのロード
		self.pGet_WorkTraffic()
		
		#############################
		# 初期化済み
		self.Init = True
		return



#####################################################
# 退避トラヒックファイルの読み込み
#####################################################
	def pGet_WorkTraffic(self):
		#############################
		# 現在トラヒック
		for line in open( global_val.gNowTraffic_file, 'r'):	#ファイルを開く
			#############################
			# 分解+要素数の確認
			line = line.strip()
			get_line = line.split("=")
			if len(get_line) != 2 :
				continue
			
			#############################
			# キーがあるか確認
			if get_line[0] not in self.Now_Traffic :
				continue
			
			get_line[1] = int( get_line[1] )
			#############################
			# 更新する
			self.Now_Traffic.update({ get_line[0] : get_line[1] })
		
		global_val.gTraffic_1HourSkip = False
		#############################
		# 過去トラヒック
		for line in open( global_val.gRatTraffic_file, 'r'):	#ファイルを開く
			#############################
			# 分解+要素数の確認
			line = line.strip()
			get_line = line.split("=")
			if len(get_line) != 2 :
				continue
			
			#############################
			# 1時間スキップか
			if get_line[0] == '_1HourSkip_' and get_line[1] == 'on' :
				global_val.gTraffic_1HourSkip = True
				continue
			
			#############################
			# キーがあるか確認
			if get_line[0] not in self.Rat_Traffic :
				continue
			
			get_line[1] = int( get_line[1] )
			#############################
			# 更新する
			self.Rat_Traffic.update({ get_line[0] : get_line[1] })
		
		return



#####################################################
# 退避トラヒックファイルへの書き出し
#####################################################
	def pSet_WorkTraffic(self):
		#############################
		# 現在トラヒック
		file = open( global_val.gNowTraffic_file, 'w')
		file.close()
		file = open( global_val.gNowTraffic_file, 'w')
		
		#############################
		# キー一覧を取得
		keylist = self.Now_Traffic.keys()
		
		#############################
		# データを作成
		setline = []
		for setkey in keylist :
			line = setkey + '='
			line = line + str( self.Now_Traffic[setkey] )
			line = line.strip()
			line = line + '\n'
			setline.append(line)
		
		#############################
		# 書き込んで閉じる
		file.writelines( setline )
		file.close()
		
		
		#############################
		# 過去トラヒック
		file = open( global_val.gRatTraffic_file, 'w')
		file.close()
		file = open( global_val.gRatTraffic_file, 'w')
		
		#############################
		# キー一覧を取得
		keylist = self.Rat_Traffic.keys()
		
		#############################
		# データを作成
		setline = []
		
		# 1時間スキップの退避
		if global_val.gTraffic_1HourSkip == True :
			line = '_1HourSkip_=on' + '\n'
			setline.append(line)
			global_val.gCLS_Mylog.cLog('c', "トラヒック 1時間スキップ設定")
		
		for setkey in keylist :
			line = setkey + '='
			line = line + str( self.Rat_Traffic[setkey] )
			line = line.strip()
			line = line + '\n'
			setline.append(line)
		
		#############################
		# 書き込んで閉じる
		file.writelines( setline )
		file.close()
		
		return



