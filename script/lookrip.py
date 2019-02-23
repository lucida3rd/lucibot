# coding: UTF-8
#####################################################
# 十八試るしぼっと
#   Class   ：リプライ監視処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/1/22
#####################################################
import codecs
import os
import random
import linecache
import re
import global_val
#####################################################
class CLS_LookRIP:

	ARR_RRTL     = []	#リプライ解析パターン
	ARR_RateTL   = []	#過去LTL
	ARR_UpdateTL = []	#新・過去LTL
	ARR_NewTL    = []	#新LTL
	
	CopeRTL = {
	"Now_Ripry" : 0,							#処理した通常リプライ
	"Now_Cope"  : 0,							#処理した新トゥート数
	"dummy"     : 0								#(未使用)
	}

	ARR_RateFav   = []	#過去ファボ
	ARR_UpdateFav = []	#新・過去ファボ
	ARR_Fav = []		#新ファボ
	
	CopeFav = {
	"Now_Cope"  : 0,							#処理した新ファボ数
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
		global_val.gCLS_Mylog.cLog('c', "リプライ監視処理")

		#############################
		#リプライ解析パターン読み込み
		self.cGet_RRTL()
		
		#############################
		#リプライ読み込み
		self.cGet_Reply()
		
		#############################
		#過去リプライ読み込み
		self.cGet_RateRTL()
		self.ARR_UpdateTL = []	#新過去LTLは初期化
		
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
			res = self.cCopeRTL(row)
			self.CopeRTL["Now_Cope"] += 1
		
		#############################
		#新過去リプライ保存
		self.cSet_RateRTL()
		
		if self.CopeRTL["Now_Ripry"] > 0 :
			msg = "Repry=" + str(self.CopeRTL["Now_Ripry"])
			global_val.gCLS_Mylog.cLog('b', "リプライ処理完了：" + msg )
		
		return True



#####################################################
# 対応
#####################################################
	def cCopeRTL(self,row):
		hit_patt = []
		
		#############################
		#リプをニコるか
		if global_val.gConfig["RIP_Favo"] == "on" :
			global_val.gCLS_Mastodon.cFavourite(row['id'])
##			hit_patt.append("fav")
		
		#############################
		#解析種類の判定
		for patt in self.ARR_RRTL:
			
			#############################
			#解析：ID教えて
			if patt[0] == 'howid' :
				#############################
				#既に同じ処理した
				flg_hit = False
				for chk_patt in hit_patt:
					if chk_patt == patt[0]:
						flg_hit = True
						break
				if flg_hit == True:
					continue
				
				#############################
				#パターンマッチ
				cont = global_val.gCLS_MainProc.cDel_HTML( row['content'] )
				res = re.search( patt[1], cont )
				if res:
					index = row['account']['url'].find('/@')
					fulluser = row['account']['url']
					fulluser = fulluser[8:index]
					fulluser = row['account']['username'] + '@' + fulluser
					
					toot_char = '@' +fulluser + ' あなたのIDは ' + row['account']['id'] + ' です'
					global_val.gCLS_Mastodon.cToot(status=toot_char, visibility='direct' )
					hit_patt.append(patt[0])

			#############################
			#解析：通常リプライ
			if patt[0] == 'r' :
				#############################
				#既に同じ処理した
				flg_hit = False
				for chk_patt in hit_patt:
					if chk_patt == patt[0]:
						flg_hit = True
						break
				if flg_hit == True:
					continue
				
				#############################
				#パターンマッチ
				cont = global_val.gCLS_MainProc.cDel_HTML( row['content'] )
				res = re.search( patt[1], cont )
				if res:
					index = row['account']['url'].find('/@')
					fulluser = row['account']['url']
					fulluser = fulluser[8:index]
					fulluser = row['account']['username'] + '@' + fulluser
					
					self.CopeRTL["Now_Ripry"] += 1
					self.cRipry(patt[2],fulluser)
					hit_patt.append(patt[0])

			#############################
			#解析：学習
			if patt[0] == 'study' :
				#############################
				#既に同じ処理した
				flg_hit = False
				for chk_patt in hit_patt:
					if chk_patt == patt[0]:
						flg_hit = True
						break
				if flg_hit == True:
					continue
				
				#############################
				#パターンマッチ
				cont = global_val.gCLS_MainProc.cDel_HTML( row['content'] )
				res = re.search( patt[1], cont )
				if res:
					index = row['account']['url'].find('/@')
					fulluser = row['account']['url']
					fulluser = fulluser[8:index]
					fulluser = row['account']['username'] + '@' + fulluser
					
					#学習
					index = cont.find('::') + 2
					cont  = cont[index:]
					global_val.gCLS_TootCorrect.cWordStudy( row )
					
					toot_char = '@' +fulluser + ' リプライから単語を学習しました。協力ありがと☆彡 (*´ω｀*)'
					global_val.gCLS_Mastodon.cToot(status=toot_char, visibility='unlisted' )
					hit_patt.append(patt[0])

		#############################
		#ヒット有無により戻り値を変化
		if len(hit_patt)==0 :
			#############################
			# ランダムリプライを返信
			index = row['account']['url'].find('/@')
			fulluser = row['account']['url']
			fulluser = fulluser[8:index]
			fulluser = row['account']['username'] + '@' + fulluser
			
			word = global_val.gCLS_TootCorrect.cGet_RandSentence()
			if word!="":
				toot_char = '@' + fulluser + " " + word
				global_val.gCLS_Mastodon.cToot(status=toot_char, visibility='unlisted' )
			
			return False	#ヒットしてない
		
		return True			#ヒットした



#####################################################
# リプライ取得
#####################################################
	def cGet_Reply(self):
		#############################
		# とりあえず通知一覧を取り込む
		self.ARR_NewTL = []
		wARR_NewTL = []
		next_id = 0
		max_toots = global_val.gConfig["getRIPnum"]
		while (len(wARR_NewTL) < max_toots):
			get_toots = global_val.gCLS_Mastodon.cGetNotificationList( max_id=next_id )
			
			# 新しいトゥートが取得できなかったらループ終了
			if len( get_toots ) > 0:
				wARR_NewTL += get_toots
			else:
				break
			
			# 80件以上のページネーションするための値取得
			toots_last = len(wARR_NewTL)-1
			if '_pagination_next' in wARR_NewTL[toots_last] :
				if 'max_id' in wARR_NewTL[toots_last]['_pagination_next']:
					next_id = wARR_NewTL[toots_last]['_pagination_next']['max_id']
				else:
					break
			else:
				break
		
		#############################
		# 取得がなければ中止
		if len(wARR_NewTL)<=0 :
			return
		
		#############################
		# 取り込んだ中から自垢へのリプライを絞り込む
		username = global_val.gConfig["UserBot"].split('@')
		username = '@' + username[0]
		for row in wARR_NewTL :
			#############################
			# ファボは別保存する
			if 'favourite' == row['type'] :
				self.ARR_Fav.append(row)
				continue
			
			#############################
			# リプライトゥートを絞る
			if 'mention' != row['type'] :
				continue
			if 'status' not in row :
				continue
			if 'content' not in row['status'] :
				continue
			
			if global_val.gCLS_MainProc.cTimeLag( creaate_at=row['created_at'] )==False :
				continue
			
### type:
### favourite	ファボ
### reblog		ブースト
### follow		フォロー
### mention		リプライ

			
			toot_char = row['status']['content']
			
			#############################
			# HTMLタグを除去
			toot_char = global_val.gCLS_MainProc.cDel_HTML( toot_char )
			
			#############################
			# 自垢へのリプライか
			if toot_char.find(username) >= 0 :
				self.ARR_NewTL.append(row['status'])
		
		return



#####################################################
# 過去リプライ取得
#####################################################
	def cGet_RateRTL(self):
		self.ARR_RateTL = []
		for line in open( global_val.gRateRTL_file, 'r'):	#ファイルを開く
			line = line.strip()
			self.ARR_RateTL.append(line)
		
		return



#####################################################
# 過去リプライ保存
#####################################################
	def cSet_RateRTL(self):
		#############################
		# 書き込みモードで開く
		file = open( global_val.gRateRTL_file, 'w')
		
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
# リプライ解析パターン読み出し
#####################################################
	def cGet_RRTL(self):
		if os.path.exists(global_val.gLookRTL_file)==False :
			global_val.gCLS_Mylog.cLog('a', "CLS_LookRIP：cGet_RRTL：ファイルがない：" + global_val.gLookRTL_file )
			return
		
		self.ARR_RRTL = []
		for line in codecs.open( global_val.gLookRTL_file, 'r', 'utf-8'):	#ファイルを開く
			line = line.strip()
			lines = line.split(global_val.gCHR_Border)
			self.ARR_RRTL.append(lines)
		
		return



#####################################################
# リプライ
#####################################################
	def cRipry(self,filename,fulluser):
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
		toot_char = '@' + fulluser + ' ' + lines[1]
		global_val.gCLS_Mastodon.cToot(status=toot_char, visibility=range )
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
			global_val.gCLS_Mylog.cLog('a', "CLS_LookRIP：cGet_Rip：ファイルがない：" + filepath )
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
# ファボ監視 - メイン処理
#####################################################
	def cFavoInd(self):
		global_val.gCLS_Mylog.cLog('c', "ファボ監視処理")

		#############################
		#過去ファボ読み込み
		self.cGet_RateFav()
		self.ARR_UpdateFav = []	#新過去ファボは初期化
		
		#############################
		#ファボチェック
		res = False
		for row in self.ARR_Fav:
			#############################
			#チェックするので新過去TLに保管
			self.ARR_UpdateFav.append(row['status']['id'])
			
			#############################
			#過去チェックしたトゥートか
			#  であればスキップする
			flg_rate = False
			for row_rate in self.ARR_RateFav:
				
				if str(row_rate) == str(row['status']['id']) :
					flg_rate = True
					break
			if flg_rate == True :
				continue
			
			#############################
			#新ファボへの対応
			res = self.cCopeFav( row['account'], row['status'] )
		
		#############################
		#新過去ファボ保存
		self.cSet_RateFav()
		
		if self.CopeFav["Now_Cope"] > 0 :
			msg = "Repry=" + str(self.CopeFav["Now_Cope"])
			global_val.gCLS_Mylog.cLog('b', "ファボ監視処理完了：" + msg )
		
		return True



#####################################################
# 対応 - ファボ監視
#####################################################
	def cCopeFav( self, row_account, row_status ):
		
		#############################
		# ファボ監視のファボか？
###		if row_status['content'].find(global_val.gConfig["IND_FavoTag"])>=0 :
		if self._CopeFav_Objection( row_status )==False :
			return False
		
		#############################
		# ファボったユーザ
		index = row_account['url'].find('/@')
		fulluser = row_account['url']
		fulluser = fulluser[8:index]
		fulluser = row_account['username'] + '@' + fulluser
		
		dispname = row_account['display_name'] + 'さん'
		
		#############################
		# ファボられたトゥートURL
		toot_url = global_val.gConfig["BaseUrl"] + '/web/statuses/' + row_status['id']
		
		#############################
		# トゥートする (public)
		toot_char = dispname + '( @' + fulluser + ' )'
		toot_char = toot_char + 'にファボられました #' + global_val.gConfig["IND_FavoTag"] + '\n'
		toot_char = toot_char + toot_url
		
		global_val.gCLS_Mastodon.cToot(status=toot_char, visibility='public' )
		
		self.CopeFav["Now_Cope"] += 1
		return True




#####################################################
# 対応 - ファボ監視
#####################################################
	def _CopeFav_Objection( self, row_status ):
		
		#############################
		# ファボ通知のファボか？
		if row_status['content'].find(global_val.gConfig["IND_FavoTag"])>=0 :
			return False	#ファボ通知：監視外
		
		#############################
		# ファボ監視のファボか？
		if row_status['visibility']=='public' :
			return True	#範囲：公開
		
		if row_status['visibility']=='unlisted' and global_val.gConfig["IND_Favo_Unl"]=='on' :
			return True	#範囲：未収載かつフラグ有効
		
		return False	#範囲外



#####################################################
# 過去ファボ取得
#####################################################
	def cGet_RateFav(self):
		self.ARR_RateFav = []
		for line in open( global_val.gRateFav_file, 'r'):	#ファイルを開く
			line = line.strip()
			self.ARR_RateFav.append(line)
		
		return



#####################################################
# 過去ファボ保存
#####################################################
	def cSet_RateFav(self):
		#############################
		# 書き込みモードで開く
		file = open( global_val.gRateFav_file, 'w')
		
		#############################
		# データを作成
		setline = []
		for getline in self.ARR_UpdateFav :
			line = str( getline )
			line = line.strip()
			line = line + '\n'
			setline.append(line)
		
		#############################
		# 書き込んで閉じる
		file.writelines( setline )
		file.close()
		
		return



