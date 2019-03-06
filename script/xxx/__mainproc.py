# coding: UTF-8
#####################################################
# 十八試るしぼっと
#   Class   ：メイン処理処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/1/19
#####################################################
from datetime import datetime
from datetime import timedelta
import os
import re
import global_val
#####################################################
class CLS_MainProc:
##	VAL_TootNum = 0

#####################################################
# Init
#####################################################
	def __init__(self):
		return



#####################################################
# 処理本体
#####################################################
	def cMain(self):
		#############################
		# 1時間監視処理
		self.pChk1HourTime()
		
		#############################
		#ユーザ収集ファイル読み込み
		global_val.gCLS_UserInfo.cGet_UserCorrect()
		#辞書ファイル読み込み
		global_val.gCLS_TootCorrect.cGet_Words()
		
		#############################
		#モード：PTL監視
		ret = global_val.gCLS_LookPTL.cMain()
		
		#############################
		#モード：ユーザチェック
		ret = global_val.gCLS_UserInfo.cUserCheck()
		
		#############################
		#モード：周期トゥート
		if global_val.gConfig["CircleToot"] == "on" :
			ret = global_val.gCLS_CircleToot.cMain()
		
		#############################
		#モード：ランダムトゥート
		if global_val.gConfig["RandToot"] == "on" :
			ret = global_val.gCLS_RandToot.cMain()
		
		#############################
		#モード：リプライ監視
##		if global_val.gConfig["LookRIP"] == "on" :
##			ret = global_val.gCLS_LookRIP.cMain()
		ret = global_val.gCLS_LookRIP.cMain()
		
		#############################
		#モード：ファボ監視
		if global_val.gConfig["IND_Favo"] == "on" :
			ret = global_val.gCLS_LookRIP.cFavoInd()
		
		#############################
		#ユーザ収集ファイル書き込み
		global_val.gCLS_UserInfo.cSet_UserCorrect()
		#辞書ファイル書き込み
		global_val.gCLS_TootCorrect.cSet_Words()
		
		return



#####################################################
# 1時間監視
#####################################################
	def pChk1HourTime(self):
		#############################
		# 記録ファイルをロード
		file = open( global_val.g1HourTimeCheck_file, 'r')
		for row in file:
			rtime = row.strip()
		file.close()
		
		rtime = rtime.split(',')
		rhour = rtime[1]
		
		#############################
		# PC時間を取得
###		nhour = datetime.now().strftime("%H")
###		ntime = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
										## 2018-03-04 12:10:45
		now_td = datetime.now()
		global_val.gOBJ_TimeDate = now_td
		nhour = now_td.strftime("%H")	#時間だけ
		nweek = str( now_td.weekday() )	#曜日 0=月,1=火,2=水,3=木,4=金,5=土,6=日
		ntime = now_td.strftime("%Y-%m-%d") + ',' + nhour + ',' + nweek
		
		#############################
		# フル日時の作成
		now_date = str(now_td)
		ifind = now_date.find('+')
		now_date = now_date[0:ifind]
		ifind = now_date.find('.')
		if ifind>=0 :
			now_date = now_date[0:ifind]
		global_val.gFull_TimeDate = datetime.strptime(now_date, "%Y-%m-%d %H:%M:%S")
		
		#############################
		# 時間が同じ＝少なくとも1時間経ってないか？
		if rhour == nhour :
			global_val.gFlg_1HourTime = False
			return
		else :
			global_val.gFlg_1HourTime = True
		
		#############################
		# 時間をセーブ
		file = open( global_val.g1HourTimeCheck_file, 'w')
		file.writelines( ntime )
		file.close()
		return



#####################################################
# ファイルの日時取得
#####################################################
	def cGet_File_TimeDate(self,path):
		if os.path.exists( path )==False :
			global_val.gCLS_Mylog.cLog('a', "CLS_MainProc：pGet_File_TimeDate：ファイルがない：" + path )
			return ""
		
		#############################
		# 周期トゥートパターンファイルの日時取得
		wdt = datetime.fromtimestamp(os.stat( path ).st_mtime)
		wdt = wdt.strftime("%Y-%m-%d %H:%M:%S")
		
		return wdt



#####################################################
# 公開範囲の取得
#####################################################
	def cGet_Visi(self,comm):
		if comm == 'p' :
			chr_range = 'public'
		elif comm == 'l' :
			chr_range = 'private'
		else :
			chr_range = 'unlisted'
		
		return chr_range



#####################################################
# row['content']からHTMLタグを除去
#####################################################
	def cDel_HTML(self,cont,tag=False):
		patt = re.compile(r"<[^>]*?>")
		d_cont = patt.sub("", cont)
		
		return d_cont



#####################################################
# 時間差
#    threshold = 300	# 60(s) * 5(m)
#####################################################
	def cTimeLag(self, creaate_at, threshold=300 ):
		#############################
		# 最終トゥートの作成日
		toot_td = str( creaate_at )
			##形式合わせ +、.を省く（鯖によって違う？
		ifind = toot_td.find('+')
		toot_td = toot_td[0:ifind]
		ifind = toot_td.find('.')
		if ifind>=0 :
			toot_td = toot_td[0:ifind]
		
		try:
			toot_td = datetime.strptime(toot_td, "%Y-%m-%d %H:%M:%S") + timedelta(hours=global_val.gTimeZone)
			toot_day = toot_td.strftime( "%Y-%m-%d %H:%M:%S" )
		except ValueError as err :
			global_val.gCLS_Mylog.cLog('a', "CLS_MainProc：cTime_Lag：日時の書式エラー" )
			return False
		
		#############################
		# 差を求める
		rattime = global_val.gOBJ_TimeDate - toot_td
###		rattime = rattime.seconds
		rattime = rattime.total_seconds()
		
		if rattime > threshold :
			return False
		
		return True



##td = dt_now - dt
##print(td)
### 1 day, 18:31:13.271231
##
##print(type(td))
### <class 'datetime.timedelta'>
##
##print(td.days)
### 1
##
##print(td.seconds)
### 66673
##
##print(td.microseconds)
### 271231
##
##print(td.total_seconds())
### 153073.271231

