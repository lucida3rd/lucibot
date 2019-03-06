# coding: UTF-8
#####################################################
# 十八試るしぼっと
#   Class   ：ランダムトゥート処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2018/11/17
#####################################################
import codecs
import os
import random
import linecache
import global_val
#####################################################
class CLS_RandToot:
	VAL_TootNum = 0

#####################################################
# Init
#####################################################
	def __init__(self):
		return



#####################################################
# メイン処理
#####################################################
	def cMain(self):
		global_val.gCLS_Mylog.cLog('c', "ランダムトゥート処理")
		
		#############################
		# 辞書が使えるかどうか
		if global_val.gCLS_TootCorrect.cIs_Words() != True :
			return False
		
		#############################
		# トゥート頻度
		ran = random.randrange(global_val.gConfig["getRandRange"])
		if ran >= global_val.gConfig["getRandVal"] :
			return False
		
		#############################
		# ランダムトゥートを作成する
		word = global_val.gCLS_TootCorrect.cGet_RandSentence()
		if word=="":
			return False
		
		#############################
		#トゥート
		global_val.gCLS_Mastodon.cToot(status=word, visibility='unlisted' )
			#visibility='public'
			#visibility='private'
			#visibility='unlisted'
		
		return True



