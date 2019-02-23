# coding: UTF-8
#####################################################
# 十八試るしぼっと
#   Class   ：ユーザ情報管理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/1/19
#####################################################
from datetime import datetime
import time
import os
import codecs
import random
import global_val
#####################################################
class CLS_UserInfo:
	CheckNum = 0						#今周回のチェック数
	
	CorrUserList  = {}					#収集ユーザ一覧
	CorrUserListREM = {}				#収集除外
	FLG_UserCorrUpdate = False



#####################################################
# Init
#####################################################
	def __init__(self):
		return



#####################################################
# ユーザをフォローしているか
# useridnum=row['account']['id']
#####################################################
	def cChk_UserFollow(self, useridnum ):
		
		#############################
		# 整数変換
		useridnum = int(useridnum)
		
		#############################
		# ユーザが収集されていなければ除外
		if useridnum not in self.CorrUserList :
			return False
		
		if self.CorrUserList[useridnum]['follow'] != "FFF" :
			return False
		
		return True



#####################################################
# ユーザがフォロワーか
# useridnum=row['account']['id']
#####################################################
	def cChk_UserFollower(self, useridnum ):
		
		#############################
		# 整数変換
		useridnum = int(useridnum)
		
		#############################
		# ユーザが収集されていなければ除外
		if useridnum not in self.CorrUserList :
			return False
		
		if self.CorrUserList[useridnum]['follower'] != "FFF" :
			return False
		
		return True



#####################################################
# ユーザ収集への追加
#   辞書型で登録する
#####################################################
	def cAdd_UserCorrect(self, row ):
		#############################
		# 既に存在していれば、情報を更新する
		if int(row['account']['id']) in self.CorrUserList :
			self.cUpdate_UserCorrect(row)
			return False
		
		userinfo = row['account']
		userinfo['id'] = int(userinfo['id'])
		stat = "@@@"	#チェック候補
		#############################
		#自分か
		fulluser = self.cGet_FullUser( userinfo['username'], userinfo['url'] )
		index = userinfo['id']
		if fulluser['fulluser'] == global_val.gConfig["UserBot"] :
			return True		#スルーする
		
		#############################
		#日本人か(*1)
		if row['language']!="ja" and global_val.gConfig["JPonly"]=='on' :
			return True		#スルーする
		
		#############################
		# 除外リスト対象
		if fulluser['domain'] in self.CorrUserListREM :
			return True		#スルーする
		
		#############################
		# 鍵の有無
		if row['account']['locked']==True :
			flg_locked = "KKK"
		else :
			flg_locked = "---"
		
		#############################
		#プロフURL
		prof_url = global_val.gConfig["BaseUrl"] + global_val.gProfSuburl + str(userinfo['id'])
		
		self.CorrUserList.update({ index : "" })
		self.CorrUserList[index] = {}
		self.CorrUserList[index].update({ "id"       : userinfo['id'] })
		self.CorrUserList[index].update({ "username" : userinfo['username'] })
		self.CorrUserList[index].update({ "domain"   : fulluser['domain'] })
		self.CorrUserList[index].update({ "prof_url" : prof_url })
		
		self.CorrUserList[index].update({ "stat"      : stat })
			## @@@ フォローチェック予約(まだ未フォロー)
			## --- フォローチェック済
			## DDD ドメインブロックユーザ
			## RRR リムーブ予約
			## xxx チェックもしくはフォロー失敗
			## *** リストから消す
		
		self.CorrUserList[index].update({ "followed" : "---" })			#フォローしたことがある
		self.CorrUserList[index].update({ "follow"   : "---" })			#現在フォロー状態
		self.CorrUserList[index].update({ "follower" : "---" })			#現在フォロワーか
		self.CorrUserList[index].update({ "locked"   : flg_locked })	#鍵
		self.CorrUserList[index].update({ "score"  : 0 })
		self.CorrUserList[index].update({ "lastupdate" : global_val.gFull_TimeDate })
		self.CorrUserList[index].update({ "lastcheck"  : global_val.gFull_TimeDate })
		
		self.FLG_UserCorrUpdate = True
		return True



#####################################################
# ユーザ収集情報更新
#####################################################
	def cUpdate_UserCorrect(self, row ):
		
		useridnum = int(row['account']['id'])
		#############################
		# ユーザが収集されていなければ除外
		if useridnum not in self.CorrUserList :
			return
		
		#############################
		# 最終更新日の更新
		self.CorrUserList[useridnum]['lastupdate'] = global_val.gFull_TimeDate
		
		#############################
		# 鍵垢か
		if row['account']['locked']==True :
			flg_locked = "KKK"
		else :
			flg_locked = "---"
		
		self.CorrUserList[useridnum]['locked'] = flg_locked
		
		#############################
		# 候補かDBだったら処理そこまで
		if self.CorrUserList[useridnum]['stat'] == "DDD" or \
		   self.CorrUserList[useridnum]['stat'] == "@@@" :
			return
		
		#############################
		# 最終チェック日から1日経過してる
		rate_date = datetime.strptime( str(self.CorrUserList[useridnum]['lastcheck']), "%Y-%m-%d %H:%M:%S" )
		ratday = global_val.gFull_TimeDate - rate_date
		ratday = ratday.days
		if ratday>= 1 :
			self.CorrUserList[useridnum]['stat'] = "@@@"
		
		return



#####################################################
# ユーザ収集ファイルの読み込み
#   辞書型で登録する
#####################################################
	def cGet_UserCorrect(self):
		if os.path.exists(global_val.gUserCorr_file)==False :
			global_val.gCLS_Mylog.cLog('a', "CLS_AutoFollow：cGet_UserCorrect：ファイルがない：" + global_val.gUserCorr_file )
			return
		
		self.pGet_UserCorrectRem()	#除外ファイルも読み込み
		
		self.CorrUserList = {}
		for line in open( global_val.gUserCorr_file, 'r'):	#ファイルを開く
			line = line.strip()
			lines = line.split(global_val.gCHR_Border)
			
			index = int(lines[0])
			self.CorrUserList.update({ index : "" })
			self.CorrUserList[index] = {}
			self.CorrUserList[index].update({ "id"       : lines[0] })
			self.CorrUserList[index].update({ "username" : lines[1] })
			self.CorrUserList[index].update({ "domain"   : lines[2] })
			self.CorrUserList[index].update({ "prof_url" : lines[3] })
			
			self.CorrUserList[index].update({ "stat"     : lines[4] })
			self.CorrUserList[index].update({ "followed" : lines[5] })
			self.CorrUserList[index].update({ "follow"   : lines[6] })
			self.CorrUserList[index].update({ "follower" : lines[7] })
			self.CorrUserList[index].update({ "locked"   : lines[8] })
			self.CorrUserList[index].update({ "score"    : lines[9] })
			self.CorrUserList[index].update({ "lastupdate" : lines[10] })
			self.CorrUserList[index].update({ "lastcheck"  : lines[11] })
				#整数化
			self.CorrUserList[index]['id']    = int( self.CorrUserList[index]['id'] )
			self.CorrUserList[index]['score'] = int( self.CorrUserList[index]['score'] )
		
			#############################
			# 除外リストに入っている
			if self.CorrUserList[index]['domain'] in self.CorrUserListREM :
				self.CorrUserList[index]['stat'] = "DDD"
			
		
		return



#####################################################
# ユーザ収集除外ファイルの読み込み
#   辞書型で登録する
#####################################################
	def pGet_UserCorrectRem(self):
		if os.path.exists(global_val.gUserCorrRem_file)==False :
			global_val.gCLS_Mylog.cLog('a', "CLS_AutoFollow：cGet_UserCorrectRem：ファイルがない：" + global_val.gUserCorrRem_file )
			return False
		
		self.CorrUserListREM = {}
		for line in open( global_val.gUserCorrRem_file, 'r'):	#ファイルを開く
			line = line.strip()
			self.CorrUserListREM.update({ line : 0 })
		
		return True



#####################################################
# ユーザ収集ファイルの書き出し
# ユーザ収集出力ファイルの書き出し
#####################################################
	def cSet_UserCorrect(self):
		if self.FLG_UserCorrUpdate == False :
			return	#更新なし
		
		if os.path.exists(global_val.gUserCorr_file)==False :
			global_val.gCLS_Mylog.cLog('a', "CLS_AutoFollow：cSet_UserCorrect：ファイルがない：" + global_val.gUserCorr_file )
			return
		
		#############################
		# ユーザ収集ファイルのオープン
		file = codecs.open( global_val.gUserCorr_file, 'w', 'utf-8')
		file.close()
		file = codecs.open( global_val.gUserCorr_file, 'w', 'utf-8')
		
		#############################
		# 追加データを作成
		setline = []
		keylist = self.CorrUserList.keys()
		for ikey in keylist :
			if self.CorrUserList[ikey]['stat'] == "***" :
				continue
			
			line = str(self.CorrUserList[ikey]['id']) + global_val.gCHR_Border
			line = line + self.CorrUserList[ikey]['username'] + global_val.gCHR_Border
			line = line + self.CorrUserList[ikey]['domain']   + global_val.gCHR_Border
			line = line + self.CorrUserList[ikey]['prof_url'] + global_val.gCHR_Border
			line = line + self.CorrUserList[ikey]['stat']     + global_val.gCHR_Border
			line = line + self.CorrUserList[ikey]['followed'] + global_val.gCHR_Border
			line = line + self.CorrUserList[ikey]['follow']   + global_val.gCHR_Border
			line = line + self.CorrUserList[ikey]['follower'] + global_val.gCHR_Border
			line = line + str(self.CorrUserList[ikey]['locked']) + global_val.gCHR_Border
			line = line + str(self.CorrUserList[ikey]['score']) + global_val.gCHR_Border
			line = line + str(self.CorrUserList[ikey]['lastupdate']) + global_val.gCHR_Border
			line = line + str(self.CorrUserList[ikey]['lastcheck']) + '\n'
			setline.append(line)
		
		#############################
		# 書き込んで閉じる
		file.writelines( setline )
		file.close()
		
		return



#####################################################
# スコア加算
# useridnum=row['account']['id']
#####################################################
	def cAdd_GetScore(self, useridnum, score ):
		#############################
		# ユーザが収集されていなければ除外
		if useridnum not in self.CorrUserList :
			return
		
		#############################
		# フォロー者ではない
		if self.cChk_UserFollow(useridnum) != True :
			return
		
		#############################
		# スコアを抽出
		if score in global_val.gScore :
			point = global_val.gScore[score]
		else :
			point = 1	#無いスコアは1点固定
		
		self.CorrUserList[useridnum]['score'] += point
		return



#####################################################
# ユーザ情報取得変換
#   usernameとurlからドメインとフルuser名を作成する
#####################################################
	def cGet_FullUser( self, username, url ):
		userinfo = {}
		userinfo.update({ "fulluser" : "" })
		userinfo.update({ "domain"   : "" })
		
		index = url.find('/@')
		domain = url
		domain = domain[8:index]
		# https://
		index = domain.find('/')
		if index>=0 :
			domain = domain[0:index]
		userinfo['domain'] = domain
		userinfo['fulluser'] = username + '@' + userinfo['domain']
		return userinfo



#####################################################
# ユーザチェック処理
#####################################################
	def cUserCheck(self):
		
		global_val.gCLS_Mylog.cLog('a', "フォローチェック処理")
		
		self.CheckNum = 0	#チェックユーザ数
		userlist = self.CorrUserList.keys()
		flg_reverse = False	#チェックユーザを実施したか
		flg_failure = False	#ユーザ情報取得失敗か
		for ukey in userlist :
			#############################
			# ユーザ情報取得失敗していたら
			# もう止める
			if flg_failure==True :
				break
			
			no_follow = False
			#############################
			# チェックユーザ数チェック
			#   規定数処理したら、やめる
			if global_val.gConfig["getFollowMnum"] <= self.CheckNum :
				break
			
			#############################
			# 予約中か
			#   予約でなければ次へ
			if self.CorrUserList[ukey]['stat'] != "@@@" :
				continue
			
			flg_reverse = True
			#ここでカウントとする(負荷はかける)
			self.CheckNum += 1
			#############################
			# フォローなどの情報を取得する
			userstat = global_val.gCLS_Mastodon.cGetAccountStat( self.CorrUserList[ukey]['id'] )
			if len(userstat)!=1 :
				self.CorrUserList[ukey]['stat'] = "xxx"	#失敗
				no_follow = True
				flg_failure = True
				time.sleep(1)
				break
			
			#############################
			# フォロワーか
			if userstat[0]['followed_by']==True :
				self.CorrUserList[ukey]['follower'] = "FFF"
			else :
				self.CorrUserList[ukey]['follower'] = "---"
			
			#############################
			# フォローか
			if userstat[0]['following']==True :
				self.CorrUserList[ukey]['follow'] = "FFF"	#手動フォロー
				no_follow = True
			elif userstat[0]['requested']==True :					#鍵垢・リクエスト中
				res = global_val.gCLS_Mastodon.cIDRemove( self.CorrUserList[ukey]['id'] )
				if res==False :
					self.CorrUserList[ukey]['follow'] = "RRR"	#解除失敗・フォロリク中
				no_follow = True
			else :
				self.CorrUserList[ukey]['follow'] = "---"
			
			#############################
			# フォローしたことがあるか
			if self.CorrUserList[ukey]['followed'] == "FFF" :
				no_follow = True
			
			#############################
			# 鍵垢か
			if self.CorrUserList[ukey]['locked'] == "KKK" :
				no_follow = True
			
			#############################
			# チェックはここで終了確定
			self.CorrUserList[ukey]['stat'] = "---"
			
			#############################
			# 最終チェック日をセット
			self.CorrUserList[ukey]['lastcheck'] = global_val.gFull_TimeDate
			
			#############################
			# フォローしないか
			if no_follow==True :
				continue
			
			#############################
			# 自動フォロー処理
			if global_val.gConfig["AutoFollow"] == "on" :
				if global_val.gConfig["Mainte"] == "on" :
					global_val.gCLS_Mylog.cLog('a', "フォロー(仮想): "+ self.CorrUserList[ukey]['username'] + "@" + self.CorrUserList[ukey]['domain'] )
					self.CorrUserList[ukey]['stat'] = "---"
					self.CorrUserList[ukey]['follow'] = "FFF"
					res = False
				else :
					res = global_val.gCLS_Mastodon.cIDFollow( self.CorrUserList[ukey]['id'] )
				
				if res == True :
					self.CorrUserList[ukey]['stat'] = "---"
					self.CorrUserList[ukey]['follow'] = "FFF"
					self.CorrUserList[ukey]['followed'] = "FFF"
		
		#############################
		# 予約を処理していない、もしくはAutoFollow=OFF
		if flg_reverse == False and flg_failure==False :
			userlist = list(self.CorrUserList.keys())
			for ukey in userlist :
				#############################
				# チェックユーザ数チェック
				#   規定数処理したら、やめる
				if global_val.gConfig["getFollowMnum"] <= self.CheckNum :
					break
				
				#############################
				# ドメインブロック者でフォロワー
				#  =ブロック→ブロック解除する
				if self.CorrUserList[ukey]['stat'] == "DDD" and \
				   self.CorrUserList[ukey]['follower'] == "FFF" :
					self.CheckNum += 1	#成否に関わらずカウント
					res = global_val.gCLS_Mastodon.cBlock( self.CorrUserList[ukey]['id'] )
					if res!=True :
						time.sleep(1)
						continue
					res = global_val.gCLS_Mastodon.cUnblock( self.CorrUserList[ukey]['id'] )
					if res!=True :
						time.sleep(1)
						continue
					self.CorrUserList[ukey]['follow'] = "---"	#フォーリムーブ成功
					self.CorrUserList[ukey]['follower'] = "---"
					self.CorrUserList[ukey]['stat'] = "***"
					global_val.gCLS_Mylog.cLog('c', "ドメインブロック:フォロワーリムーブ: "+ self.CorrUserList[ukey]['username'] + "@" + self.CorrUserList[ukey]['domain'] )
					continue
				
				#############################
				# ドメインブロック者でフォロー者
				#  =リムーブする
				if self.CorrUserList[ukey]['stat'] == "DDD" and \
				   self.CorrUserList[ukey]['follow'] == "FFF" :
					self.CheckNum += 1	#成否に関わらずカウント
					res = global_val.gCLS_Mastodon.cIDRemove( self.CorrUserList[ukey]['id'] )
					if res!=True :
						time.sleep(1)
						continue
					self.CorrUserList[ukey]['follow'] = "---"	#リムーブ成功
					self.CorrUserList[ukey]['stat'] = "***"
					global_val.gCLS_Mylog.cLog('c', "ドメインブロック:リムーブ: "+ self.CorrUserList[ukey]['username'] + "@" + self.CorrUserList[ukey]['domain'] )
					continue
				
				#############################
				# リムーブ予約者
				#  =リムーブする
				if self.CorrUserList[ukey]['stat'] == "RRR" :
					self.CheckNum += 1	#成否に関わらずカウント
					res = global_val.gCLS_Mastodon.cIDRemove( self.CorrUserList[ukey]['id'] )
					if res!=True :
						time.sleep(1)
						continue
					self.CorrUserList[ukey]['follow'] = "---"	#リムーブ成功
					self.CorrUserList[ukey]['stat'] = "***"
					global_val.gCLS_Mylog.cLog('c', "リムーブ予約: "+ self.CorrUserList[ukey]['username'] + "@" + self.CorrUserList[ukey]['domain'] )
					continue
				
				#############################
				# 更新日が30日超のユーザをマークする
				rate_date = datetime.strptime( str(self.CorrUserList[ukey]['lastupdate']), "%Y-%m-%d %H:%M:%S" )
				ratday = global_val.gFull_TimeDate - rate_date
				ratday = ratday.days
				if ratday>30 :
					self.CheckNum += 1	#成否に関わらずカウント
					res = global_val.gCLS_Mastodon.cIDRemove( self.CorrUserList[ukey]['id'] )
					if res!=True :
						time.sleep(1)
						continue
					self.CorrUserList[ukey]['follow'] = "---"	#リムーブ成功
					self.CorrUserList[ukey]['stat'] = "***"
					global_val.gCLS_Mylog.cLog('c', "未更新ユーザのリムーブ: "+ self.CorrUserList[ukey]['username'] + "@" + self.CorrUserList[ukey]['domain'] )

#					continue
		
		#############################
		# ユーザ収集更新
		self.FLG_UserCorrUpdate = True
		return



