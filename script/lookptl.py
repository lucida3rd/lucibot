# coding: UTF-8
#####################################################
# 十八試るしぼっと
#   Class   ：連合TL監視処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/1/19
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
class CLS_LookPTL:

	ARR_PPTL     = []	#PTL解析パターン
	ARR_RateTL   = []	#過去LTL
	ARR_UpdateTL = []	#新・過去LTL
	ARR_NewTL    = []	#新LTL
	
	CopePTL = {
		"Now_Word"  : 0,							#今ワード監視した数
		"Now_Cope"  : 0,							#処理した新トゥート数
		"Now_Favo"  : 0,							#今ニコった数
		"Now_Boot"  : 0,							#今ブーストした数
		"Now_ARip"  : 0,							#今エアリプした数
		"dummy"     : 0								#(未使用)
	}



#####################################################
# Init
#####################################################
	def __init__(self):
		return



#####################################################
# メイン処理
#####################################################
	def cMain(self):
		global_val.gCLS_Mylog.cLog('c', "連合TL監視処理")
		
		#############################
		#TL解析パターン読み込み
		self.cGet_PPTL()
		
		#############################
		#TL読み込み
		self.cGet_PTL()
		
		#############################
		#過去TL読み込み
		self.cGet_RatePTL()
		self.ARR_UpdateTL = []	#新過去TLは初期化
		
		#############################
		#TLチェック
		res = False
		for row in self.ARR_NewTL:
			#############################
			#チェックするので新過去TLに保管
			self.ARR_UpdateTL.append(row['id'])
			
			#############################
			#過去チェックしたトゥートか
			#  であればスキップする
			flg_rate = False
			for row_rate in self.ARR_RateTL:
				if str(row_rate) == str(row['id']) :
					flg_rate = True
					break
			if flg_rate == True :
				continue
			
			#############################
			#新トゥートへの対応
			res = self.cCopePTL(row)
			self.CopePTL["Now_Cope"] += 1
			

		#############################
		#新過去TL保存
		self.cSet_RatePTL()
		
		#############################
		#トラヒックをトゥートして保存
		flg_traffic = global_val.gCLS_Traffic.cToot_Traffic()
		
		if flg_traffic == True or self.CopePTL["Now_Word"] > 0 :
			msg = "Traffic=" + str(flg_traffic) + " Word=" + str(self.CopePTL["Now_Word"])
			global_val.gCLS_Mylog.cLog('b', "連合TL処理完了：" + msg )
		
		return True



#####################################################
# 対応
#####################################################
	def cCopePTL(self,row):
		hit_patt = []
		
		#############################
		#トラヒックに記録
		global_val.gCLS_Traffic.cCnt_Traffic(row)
		
		#############################
		#ユーザ収集ファイルに記録：フォロー候補
		#  ※既にリストにあれば追加されない
		global_val.gCLS_UserInfo.cAdd_UserCorrect( row )
		
		#############################
		#単語学習
		global_val.gCLS_TootCorrect.cWordStudy( row )
		
		#############################
		#フォロワー状態
		flg_follower = global_val.gCLS_UserInfo.cChk_UserFollower(row['account']['id'])
		
		#############################
		#トゥートからHTMLタグを除去
		cont = global_val.gCLS_MainProc.cDel_HTML( row['content'], tag=True )
		
		#############################
		#解析種類の判定
		for patt in self.ARR_PPTL:
##			#############################
##			#トゥートからHTMLタグを除去
##			cont = global_val.gCLS_MainProc.cDel_HTML( row['content'] )
			
			#############################
			#リプライは除外（先頭に@付きトゥート）
			if cont.find('@') == 0 :
				continue
			
			#############################
			#自分(このbot)のトゥートならスキップ
			if str(row['account']['username']) == global_val.gMyID :
				continue
			
			#############################
			#解析：ニコる
			if patt[0] == 'f' and global_val.gConfig["PTL_Favo"] == "on" and flg_follower==True :
				#############################
				#既にニコったか
				if self.pCheck_HitPatt(hit_patt,patt[0]) == True :
					continue	#既に同じ処理した
				
				#############################
				#パターンマッチ
				res = re.search( patt[1], cont )
				if res:
					self.CopePTL["Now_Favo"] += 1
					global_val.gCLS_Mastodon.cFavourite(row['id'])
					hit_patt.append(patt[0])
			
			#############################
			#解析：ブースト
			if patt[0] == 'b' and global_val.gConfig["PTL_Boot"] == "on" and flg_follower==True :
				#############################
				#既にブスったか
				if self.pCheck_HitPatt(hit_patt,patt[0]) == True :
					continue	#既に同じ処理した
				
				#############################
				#パターンマッチ
				res = re.search( patt[1], cont )
				if res:
					self.CopePTL["Now_Boot"] += 1
					global_val.gCLS_Mastodon.cBoost(row['id'])
					hit_patt.append(patt[0])
			
			#############################
			#解析：紐エアリプ
			if patt[0] == 'h' and global_val.gConfig["PTL_HRip"] == "on" and flg_follower==True :
				#############################
				#既にエアリプしたか
				if self.pCheck_HitPatt(hit_patt,patt[0]) == True :
					continue	#既に同じ処理した
				
				#############################
				#パターンマッチ
				res = re.search( patt[1], cont )
				if res:
					self.CopePTL["Now_ARip"] += 1
					self.cHimoRipry( patt[2], row['id'] )
					hit_patt.append(patt[0])
			
			#############################
			#解析：エアリプ
			if patt[0] == 'a' and global_val.gConfig["PTL_ARip"] == "on" and flg_follower==True :
				#############################
				#既にエアリプしたか
				if self.pCheck_HitPatt(hit_patt,patt[0]) == True :
					continue	#既に同じ処理した
				
				#############################
				#パターンマッチ
				res = re.search( patt[1], cont )
				if res:
					self.CopePTL["Now_ARip"] += 1
					self.cAirRipry( patt[2] )
					hit_patt.append(patt[0])
			
			#############################
			#解析：ワード監視
			if patt[0] == 'w' and global_val.gConfig["PTL_WordOpe"] == "on" and global_val.gConfig["UserMaster"] != "" :
				#############################
				#既に監視したか
				if self.pCheck_HitPatt(hit_patt,patt[0]) == True :
					continue	#既に同じ処理した
				
				#############################
				#パターンマッチ
				res = re.search( patt[1], cont )
				if res:
					self.CopePTL["Now_Word"] += 1
					self.cIndLookWordOpe( row['account']['username'], patt[1], row['uri'], patt[2] )
					hit_patt.append(patt[0])
			

		#############################
		#ヒット有無により戻り値を変化
		if len(hit_patt)==0 :
			return False	#ヒットしてない
		
		return True			#ヒットした



#####################################################
	def pCheck_HitPatt(self,hit_patt,patt):
		flg_hit = False
		for chk_patt in hit_patt:
			if chk_patt == patt:
				flg_hit = True
				break
		
		return flg_hit



#####################################################
# PTL取得
#####################################################
	def cGet_PTL(self):
		self.ARR_NewTL = []
		next_id = 0
		max_toots = global_val.gConfig["getPTLnum"]
		while (len(self.ARR_NewTL) < max_toots):
			get_toots = global_val.gCLS_Mastodon.cGetTimeline_Public( limit=40, max_id=next_id )
			
			# 新しいトゥートが取得できなかったらループ終了
			if len( get_toots ) > 0:
				self.ARR_NewTL += get_toots
			else:
				break
			
			# 80件以上のページネーションするための値取得
			toots_last = len(self.ARR_NewTL)-1
			if '_pagination_next' in self.ARR_NewTL[toots_last] :
				if 'max_id' in self.ARR_NewTL[toots_last]['_pagination_next']:
					next_id = self.ARR_NewTL[toots_last]['_pagination_next']['max_id']
				else:
					break
			else:
				break
		
		return



#####################################################
# 過去PTL取得
#####################################################
	def cGet_RatePTL(self):
		self.ARR_RateTL = []
		for line in open( global_val.gRatePTL_file, 'r'):	#ファイルを開く
			line = line.strip()
			self.ARR_RateTL.append(line)
		
		return



#####################################################
# 過去PTL保存
#####################################################
	def cSet_RatePTL(self):
		#############################
		# 書き込みモードで開く
		file = open( global_val.gRatePTL_file, 'w')
		
		#############################
		# データを作成
		setline = []
		for getline in self.ARR_UpdateTL :
			line = str( getline )
			line = line.strip()
			line = line + '\n'
			setline.append(line)
		
		#############################
		# 書き込んで閉じる
		file.writelines( setline )
		file.close()
		
		return



#####################################################
# PTL解析パターン読み出し
#####################################################
	def cGet_PPTL(self):
		if os.path.exists(global_val.gLookPTL_file)==False :
			global_val.gCLS_Mylog.cLog('a', "CLS_LookPTL：cGet_PPTL：ファイルがない：" + global_val.gLookPTL_file )
			return
		
		self.ARR_PPTL = []
		for line in codecs.open( global_val.gLookPTL_file, 'r', 'utf-8'):	#ファイルを開く
			line = line.strip()
			lines = line.split(global_val.gCHR_Border)
			self.ARR_PPTL.append(lines)
		
		return



#####################################################
# 紐エアリプ
#####################################################
	def cHimoRipry(self,filename,repid):
		#############################
		# 候補を取得
		lines = self.cGet_Rip(filename)
		
		#############################
		# 候補がみつからない場合は処理しない
		if len(lines) == 0:
			return False
		
		#############################
		#公開範囲の設定
		range = global_val.gCLS_MainProc.cGet_Visi(lines[0])
		
		#############################
		#トゥート
		global_val.gCLS_Mastodon.cToot(status=lines[1], visibility=range, in_reply_to_id=repid )
		return True



#####################################################
# エアリプ
#####################################################
	def cAirRipry(self,filename):
		#############################
		# 候補を取得
		lines = self.cGet_Rip(filename)
		
		#############################
		# 候補がみつからない場合は処理しない
		if len(lines) == 0:
			return False
		
		#############################
		#公開範囲の設定
		range = global_val.gCLS_MainProc.cGet_Visi(lines[0])
		
		#############################
		#トゥート
		global_val.gCLS_Mastodon.cToot(status=lines[1], visibility=range )
		return True



#####################################################
# リプ候補選択
#####################################################
	def cGet_Rip(self,filename):
		#############################
		#登録数の取得
		tootNum = 0
		filepath = global_val.gReplyFile_dir + filename
		
		if os.path.exists(filepath)==False :
			global_val.gCLS_Mylog.cLog('a', "CLS_LookPTL：cGet_Rip：ファイルがない：" + filepath )
			return []
		
		for line in codecs.open( filepath, 'r', 'utf-8'):	#ファイルを開く
			tootNum += 1
		
		#############################
		#乱数の取得
		rand = random.randint( 1, tootNum )
		
		#############################
		# コメントアウトとかなら+1して最後尾で前に戻って見つける
		#   （ので候補はたくさん登録したほうがいい）
		indx = 1
		lines = []
		while tootNum >= indx:
			#############################
			# 登録トゥートキャッシュ
			target_line = linecache.getline( filepath, rand )
			target_line = target_line.strip()
			
			if target_line.find("#") != 0:
				#############################
				# 分解
				lines = target_line.split(global_val.gCHR_Border)
				if len(lines)==2 :
					break
			
			#############################
			# 次の候補シーク
			rand += 1
			if rand >= tootNum:
				rand = 1
			
			indx += 1
		
		linecache.clearcache()
		
		return lines



#####################################################
# 指定のユーザに監視結果を通知する
#####################################################
	def cIndLookWordOpe(self,user_name,patt,uri,ind_user):
		toot_char = '@' + ind_user + ' ワード通知：' + '\n'
		toot_char = toot_char + '対象者：' + user_name + '\n'
		toot_char = toot_char + 'パターン：' + patt + '\n'
		toot_char = toot_char + 'トゥート：' + uri + '\n'
		
		#############################
		#トゥート
		global_val.gCLS_Mastodon.cToot(status=toot_char, visibility='direct' )
		return True



