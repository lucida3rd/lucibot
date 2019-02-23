# coding: UTF-8
#####################################################
# 十八試るしぼっと
#   Class   ：マスター初期化処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/2/3
#####################################################
import os
import sys
gPath = os.path.dirname(os.path.abspath(__file__)) + "/../script"
sys.path.append(gPath)

import time
import global_val
from config import CLS_Config
from mylog import CLS_Mylog
from mainproc import CLS_MainProc

from mastodon_use import CLS_Mastodon_Use
from twitter_use import CLS_Twitter_Use
from randtoot import CLS_RandToot
from lookptl import CLS_LookPTL
from lookrip import CLS_LookRIP
from circletoot import CLS_CircleToot
from userinfo import CLS_UserInfo
from tootcorr import CLS_TootCorrect
from traffic import CLS_Traffic
from lookhard import CLS_LookHard


#####################################################
class CLS_Init:
	FLG_MyLock    = False
	VAL_PythonVer = 0

#####################################################
# Init
#####################################################
	def __init__(self):
		
		#############################
		# Python version取得
		_getPythonVer()
		return



#####################################################
# 初期処理
#####################################################
	def cInit(self):
		#############################
		# 環境設定のロード
		global_val.gCLS_Config = CLS_Config()
		global_val.gCLS_Config.cGet()
		
		#############################
		# 排他制御
		#   True =排他中
		#   False=なし/ここで排他する
		if self.cLocked() == True:
			return False
		
		#############################
		# botを起動するか
		if global_val.gConfig["BotStart"] != "on" :
			return False	#起動しない
		
		#############################
		# クラスの生成
		global_val.gCLS_Mylog = CLS_Mylog()
		global_val.gCLS_MainProc = CLS_MainProc()
		global_val.gCLS_RandToot = CLS_RandToot()
		global_val.gCLS_LookPTL = CLS_LookPTL()
		global_val.gCLS_LookRIP = CLS_LookRIP()
		global_val.gCLS_CircleToot = CLS_CircleToot()
		global_val.gCLS_UserInfo = CLS_UserInfo()
		global_val.gCLS_TootCorrect = CLS_TootCorrect()
		global_val.gCLS_Traffic = CLS_Traffic()
		global_val.gCLS_LookHard = CLS_LookHard()
		global_val.gCLS_Twitter = CLS_Twitter_Use()
		
		#############################
		# mastodonクラスの生成
		global_val.gCLS_Mastodon = CLS_Mastodon_Use(
				api_base_url = global_val.gConfig["BaseUrl"],
				client_id = global_val.gMastodonParam['RegFilePath'],
				access_token = global_val.gMastodonParam['UserFilePath'],
				flg_orginit=True )
		
		#############################
		# mastodonが生成されたか確認
		if global_val.gCLS_Mastodon.Flg_Init != True :
			return False	#失敗
		
		return True



#####################################################
# 初期処理：ハード監視用
#####################################################
	def cInit_Hard(self):
		#############################
		# 環境設定のロード
		global_val.gCLS_Config = CLS_Config()
		global_val.gCLS_Config.cGet()
		
		#############################
		# botを起動するか
		if global_val.gConfig["LookHard"] != "on" :
			return False	#起動しない
		
		#############################
		# クラスの生成
		global_val.gCLS_LookHard = CLS_LookHard()
		global_val.gCLS_Mylog = CLS_Mylog()
		
		global_val.gCLS_Mastodon = CLS_Mastodon_Use(
				api_base_url = global_val.gConfig["BaseUrl"],
				client_id = global_val.gMastodonParam['RegFilePath'],
				access_token = global_val.gMastodonParam['UserFilePath'],
				flg_orginit=True )
		
		#############################
		# mastodonが生成されたか確認
		if global_val.gCLS_Mastodon.Flg_Init != True :
			return False	#失敗
		
		return True



#####################################################
# 排他制御
#   True =排他中
#   False=なし
#####################################################
	def cLocked(self):
		#############################
		# 排他処理をしなければ なし
		if global_val.gConfig["Lock"] == "off" :
			return False
		
		#############################
		# 排他ファイルオープン
		for line in open( global_val.gLock_file, 'r'):	#ファイルを開く
			lockstat = line.strip()
		
		#############################
		# 排他=なし
		#   排他ONする
		if lockstat == '0':
			file = open( global_val.gLock_file, 'w')
			file.close()
			file = open( global_val.gLock_file, 'w')
			
			line = "1"
			setline = []
			setline.append(line)
			file.writelines( setline )
			file.close()
			
			self.FLG_MyLock = True
			return False	#排他なし
		
		#############################
		# 排他=排他中
		#   待つ
		if line == "1":
			self.cLockwait()
		
		return True	#排他あり



#####################################################
# 排他解除
#####################################################
	def cUnlock(self):
		file = open( global_val.gLock_file, 'w')
		file.close()
		file = open( global_val.gLock_file, 'w')
		
		line = "0"
		setline = []
		setline.append(line)
		file.writelines( setline )
		file.close()
		return



#####################################################
# 排他待ち
#####################################################
	def cLockwait(self):
		
		#############################
		# ループ回数に達するまでLockを監視する
		wLoop = 0
		while True:
			#############################
			# 5秒wait
			time.sleep(5)
			
			#############################
			# 排他を確認する
			#   排他が解除されていたらwaitを終わる
			for line in open( global_val.gLock_file, 'r'):	#ファイルを開く
				lockstat = line.strip()
			
			if lockstat == '0':
				return
			
			#############################
			# ループ回数に達したらwaitを終わる
			wLoop += 1
			if wLoop >= global_val.gLockWait_Num :
				break
		
		#############################
		# 排他を解除する
		self.cUnlock()
		
		return



#####################################################
# Python version取得
#####################################################
	def _getPythonVer(self):
		
		#############################
		# メジャーバージョンをセット
		self.VAL_PythonVer = sys.version_info.major
		
		## 参考：
		## sys.version_info(major=2, minor=7, micro=5, releaselevel='final', serial=0)
		return



