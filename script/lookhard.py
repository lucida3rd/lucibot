# coding: UTF-8
#####################################################
# 十八試るしぼっと
#   Class   ：ハード監視処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2018/11/24
#####################################################
from datetime import datetime
import codecs
import string
import psutil
import global_val
#####################################################
class CLS_LookHard:
	# ハード情報：CPU
	hardInfo_CPU = {
		"iowait"		: 0,			#I/Oの完了待ち時間
		"irq"			: 0,			#ハードウェア割り込みに費やした時間
		"softirq"		: 0,			#ソフトウェア割り込みに費やした時間
		"steal"			: 0,			#仮想化環境で実行している他のOSで費やした時間
		"dummy"			: ""
	}

	# ハード情報：メモリ
	hardInfo_MEM = {
		"total"			: 0,			#物理メモリの合計
		"used"			: 0,			#使用中の物理メモリの合計
		"free"			: 0,			#空き物理メモリの合計
		"percent"		: 0,			#使用中の物理メモリの割り合い
		"dummy"			: ""
	}

	# ハード情報：スワップ
	hardInfo_Swap = {
		"total"			: 0,			#スワップメモリの合計
		"used"			: 0,			#使用中のスワップメモリの合計
		"free"			: 0,			#空きスワップメモリの合計
		"percent"		: 0,			#使用中のスワップメモリの割り合い
		"dummy"			: ""
	}

	# ハード情報：HDD / SSD
	hardInfo_Disk = {
		"total"			: 0,			#ディスクの合計
		"used"			: 0,			#使用中のディスクの合計
		"free"			: 0,			#空きディスクの合計
		"percent"		: 0,			#使用中のディスクの割り合い
		"dummy"			: ""
	}

	# ハード情報：稼働時間
	hardInfo_SysTime = {
		"boottime"		: 0,			#ブート日時
		"nowtime"		: 0,			#現日時
		"syshour"		: 0,			#稼働時間
		"sysday"		: 0,			#稼働日数
		"dummy"			: ""
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
##		global_val.gCLS_Mylog.cLog('c', "ハード監視処理")
		
		#############################
		# PC時間を取得
###		ntime = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
										## 2018-03-04 12:10:45
		global_val.gOBJ_TimeDate = datetime.now()
		
		#############################
		#ハード情報の収集
		self.cGetHardInfo()
		
		#############################
		#ファイルへ記録
		self.pWrite()
		
		#############################
		#時間の組み立て
		ntime = global_val.gOBJ_TimeDate.strftime("%Y-%m-%d")
		
		#############################
		#トゥートの作成
		toot_head = 'ハード監視通知：' + ntime
		
		toot_char = '@' + global_val.gConfig["UserMaster"] + '\n'
		toot_char = toot_char + '＜メモリ＞' + '\n'
		toot_char = toot_char + '全体：' + str( self.hardInfo_MEM['total'] ) + '.MB' + '\n'
		toot_char = toot_char + '使用：' + str( self.hardInfo_MEM['used'] ) + '.MB' + '\n'
		toot_char = toot_char + '使％：' + str( self.hardInfo_MEM['percent'] ) + '%' + '\n'
		toot_char = toot_char + '\n'
		
		toot_char = toot_char + '＜スワップ＞' + '\n'
		toot_char = toot_char + '全体：' + str( self.hardInfo_Swap['total'] ) + '.MB' + '\n'
		toot_char = toot_char + '使用：' + str( self.hardInfo_Swap['used'] ) + '.MB' + '\n'
		toot_char = toot_char + '使％：' + str( self.hardInfo_Swap['percent'] ) + '%' + '\n'
		toot_char = toot_char + '\n'
		
		toot_char = toot_char + '＜ディスク＞' + '\n'
		toot_char = toot_char + '全体：' + str( self.hardInfo_Disk['total'] ) + '.MB' + '\n'
		toot_char = toot_char + '使用：' + str( self.hardInfo_Disk['used'] ) + '.MB' + '\n'
		toot_char = toot_char + '使％：' + str( self.hardInfo_Disk['percent'] ) + '%' + '\n'
		toot_char = toot_char + '\n'
		
		toot_char = toot_char + '＜稼働日数＞' + '\n'
		toot_char = toot_char + 'ブート日：' + str( self.hardInfo_SysTime['boottime'] ) + '\n'
		toot_char = toot_char + '稼働日数：' + str( self.hardInfo_SysTime['sysday'] ) + '日' + str( self.hardInfo_SysTime['syshour'] ) + '時間'+ '\n'
		toot_char = toot_char + '\n'
		
		#############################
		#トゥート
###		global_val.gCLS_Mastodon.cToot(status=toot_char, visibility='direct' )
		global_val.gCLS_Mastodon.cCwToot(spoiler_text=toot_head, status=toot_char, visibility='direct' )
		
		return True



#####################################################
# csvファイルへの書き出し
#####################################################
	def pWrite(self):
		#############################
		# ファイル名の作成
		filename = "hard" + global_val.gOBJ_TimeDate.strftime("%Y")
		log_file = global_val.gMyLog_path + filename + '.csv'
		
		#############################
		# 追記モードで開く
		file = codecs.open( log_file, 'a', 'utf-8')
		
		#############################
		# データを作成
		dataline = global_val.gOBJ_TimeDate.strftime("%Y-%m-%d") + ','
		dataline = dataline + str( self.hardInfo_MEM['total'] ) + ','
		dataline = dataline + str( self.hardInfo_MEM['used'] ) + ','
		dataline = dataline + str( self.hardInfo_MEM['percent'] ) + ','
		
		dataline = dataline + str( self.hardInfo_Swap['total'] ) + ','
		dataline = dataline + str( self.hardInfo_Swap['used'] ) + ','
		dataline = dataline + str( self.hardInfo_Swap['percent'] ) + ','
		
		dataline = dataline + str( self.hardInfo_Disk['total'] ) + ','
		dataline = dataline + str( self.hardInfo_Disk['used'] ) + ','
		dataline = dataline + str( self.hardInfo_Disk['percent'] ) + ','
		
		dataline = dataline + str( self.hardInfo_SysTime['boottime'] ) + ','
		dataline = dataline + str( self.hardInfo_SysTime['nowtime'] ) + ','
		dataline = dataline + str( self.hardInfo_SysTime['syshour'] ) + ','
		dataline = dataline + str( self.hardInfo_SysTime['sysday'] ) + ','
		
		dataline = dataline + '\n'
		
		setline = []
		setline.append( dataline )
		
		#############################
		# 書き込んで閉じる
		file.write( string.join(setline,'') )
		file.close()
		
		return



#####################################################
# ハード情報取得
#####################################################
	def cGetHardInfo(self):
		self.pGetHardInfo_CPU()
		self.pGetHardInfo_MEM()
		self.pGetHardInfo_Swap()
		self.pGetHardInfo_Disk()
		self.pGetHardInfo_SysTime()
		return

#####################################################
# ハード情報：CPU
	def pGetHardInfo_CPU(self):
		ginf = psutil.cpu_times()
		self.hardInfo_CPU['iowait']  = float(ginf.iowait)
		self.hardInfo_CPU['irq']     = float(ginf.irq)
		self.hardInfo_CPU['softirq'] = float(ginf.softirq)
		self.hardInfo_CPU['steal']   = float(ginf.steal)
		return

#####################################################
# ハード情報：メモリ
	def pGetHardInfo_MEM(self):
		ginf = psutil.virtual_memory()
		self.hardInfo_MEM['total'] = int(ginf.total) / 1024 / 1024
		self.hardInfo_MEM['used']  = int(ginf.used) / 1024 / 1024
		self.hardInfo_MEM['free']  = int(ginf.free) / 1024 / 1024
		self.hardInfo_MEM['percent'] = float(ginf.percent)
		percent = float(self.hardInfo_MEM['used']) / float(self.hardInfo_MEM['total'])
##		percent = float(self.hardInfo_MEM['free']) / float(self.hardInfo_MEM['total'])
##		self.hardInfo_MEM['percent'] = round(percent,4) * 100
##		percent = float(100) - float(ginf.percent)
##		self.hardInfo_MEM['percent'] = round(percent,4)
		return

#####################################################
# ハード情報：スワップ
	def pGetHardInfo_Swap(self):
		ginf = psutil.swap_memory()
		self.hardInfo_Swap['total'] = int(ginf.total) / 1024 / 1024
		self.hardInfo_Swap['used']  = int(ginf.used) / 1024 / 1024
		self.hardInfo_Swap['free']  = int(ginf.free) / 1024 / 1024
		self.hardInfo_Swap['percent'] = float(ginf.percent)
		
##		percent = float(hardInfo_Swap['used']) / float(hardInfo_Swap['total'])
##		hardInfo_Swap['percent'] = round(percent,2)
		return

#####################################################
# ハード情報：HDD / SSD
	def pGetHardInfo_Disk(self):
		ginf = psutil.disk_usage('/')
		self.hardInfo_Disk['total'] = int(ginf.total) / 1024 / 1024
		self.hardInfo_Disk['used']  = int(ginf.used) / 1024 / 1024
		self.hardInfo_Disk['free']  = int(ginf.free) / 1024 / 1024
		self.hardInfo_Disk['percent'] = float(ginf.percent)
		return

#####################################################
# ハード情報：稼働時間
	def pGetHardInfo_SysTime(self):
		gnowtime = global_val.gOBJ_TimeDate
		self.hardInfo_SysTime['nowtime'] = gnowtime.strftime("%Y/%m/%d %H:%M:%S")
		
		gboottime = datetime.fromtimestamp(psutil.boot_time())
		self.hardInfo_SysTime['boottime'] = gboottime.strftime("%Y/%m/%d %H:%M:%S")
		
		systime = gnowtime - gboottime
		systime = systime.total_seconds()
		systime = int( systime / float(3600) )
		self.hardInfo_SysTime['syshour'] = systime		#稼働時間
		self.hardInfo_SysTime['sysday'] = systime / 24	#稼働日数
		
		return



#####################################################
#参考情報
# https://psutil.readthedocs.io/en/latest/
#
# psutil.cpu_times()
# scputimes(user=2647.52, nice=26.74, system=497.66, idle=204426.26,
#           iowait=31.94, irq=0.0, softirq=91.41,
#           steal=53.55, guest=0.0, guest_nice=0.0)
#
# mem = psutil.virtual_memory()
# mem
# svmem(total=2096582656, available=357773312, percent=82.9,
#       used=1352089600, free=144453632, active=1396162560, inactive=377090048,
#       buffers=0, cached=600039424, shared=222015488, slab=75333632)
#
# pspsutil.swap_memory()
# sswap(total=4294963200, used=532480, free=4294430720, percent=0.0, sin=0, sout=2011136)
#
# psutil.disk_usage('/')
# sdiskusage(total=48855232512, used=8248000512, free=40607232000, percent=16.9)
#
# psutil.net_io_counters()
# snetio(bytes_sent=2742803614, bytes_recv=2883713232, packets_sent=6677043, packets_recv=8484344, errin=0, errout=0, dropin=0, dropout=0)
#
# datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
#
# psutil.users()
# [suser(name='root', terminal='pts/0', host='xxxxxxxxxx', started=1542348032.0, pid=xxxxx)]
#
#####################################################

