#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ハード監視処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/9/13
#####################################################
# Private Function:
#   __run(self):
#   __get_CPU_Info(self):
#   __get_Memory_Info(self):
#   __get_Swap_Info(self):
#   __get_SSD_Info(self):
#   __get_Runtime_Info(self):
#
# Instance Function:
#   __init__( self, parentObj=None ):
#   SSL_Info(self):
#   Hard_Info(self):
#
# Class Function(static):
#   sRun(cls):
#
#####################################################
import psutil

from osif import CLS_OSIF
from filectrl import CLS_File
from userdata import CLS_UserData
from sslctrl import CLS_SSLCtrl
from gval import gVal
#####################################################
class CLS_LookHard:
#####################################################
	CHR_LogName  = "ハード監視"
	Obj_Parent   = ""		#親クラス実体
	
	STR_Info = {}

#####################################################
# Init
#####################################################
	def __init__( self, parentObj=None ):
		if parentObj==None :
			###親クラス実体の未設定
			CLS_OSIF.sPrn( "CLS_LookHard: __init__: You have not set the parent class entity for parentObj" )
			return
		
		self.Obj_Parent = parentObj
		self.__run()	#処理開始
		
		self.STR_Info = {
			"Result"	: False,
			"Reason"	: ""
		}
		return



#####################################################
# 処理実行
#####################################################
	def __run(self):
		#############################
		# 監視ユーザ設定済か
		if gVal.STR_MasterConfig['AdminUser']=="" :
			return
		
		#############################
		# 日付変更時間か
		if gVal.STR_TimeInfo['OneDay']==False :
			return
		
		#############################
		# ハード監視ユーザか
		#   ・トラヒック監視ユーザの1番目か
		#   ・1番目がMasuerUserの場合は2番目か
		if CLS_UserData.sCheckHardUser( self.Obj_Parent.CHR_Account )!=True :
			return
		
		# 監視確定
		#############################
		# 開始ログ
		self.Obj_Parent.OBJ_Mylog.Log( 'b', self.CHR_LogName + " 開始" )
		
		#############################
		# SSL証明書情報
		self.SSL_Info()
		
		#############################
		# ハード情報
		self.Hard_Info()
		
		self.STR_Info['Result'] = True
		#############################
		# 処理結果ログ
		wStr = self.CHR_LogName + " 結果: 結果=" + str(self.STR_Info['Result'])

		if gVal.FLG_Test_Mode==False :
			self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr )
		else:
			self.Obj_Parent.OBJ_Mylog.Log( 'b', wStr, True )
		
		return



#####################################################
# SSL証明書情報
#####################################################
	def SSL_Info(self):
		#############################
		# 監視ユーザのドメインを抜く
		wFulluser = CLS_UserData.sUserCheck( gVal.STR_MasterConfig['AdminUser'] )
		if wFulluser['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookHard: SSL_Info: AdminUser domain is invalid: " + gVal.STR_MasterConfig['AdminUser'] )
			return False
		
		#############################
		# 情報取得
		wCertInfo = CLS_SSLCtrl.sGetCertInfo( wFulluser['Domain'] )
		##	"Result"	: False,
		##	"Reason"	: "",
		##	"Befour"	: "",		#更新日
		##	"After"		: "",		#期限日
		##	"Other"		: {}
		if wCertInfo['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookHard: SSL_Info: sGetCertInfo is failed: " + wCertInfo['Reason'] )
			return False
		
		#############################
		# 期日までの時間差を求める
		wThreshold = 7 * (24 * 60 * 60)	# 7日..意味ないけど
		wLag = CLS_OSIF.sTimeLag( wCertInfo['After'], inThreshold=wThreshold, inTimezone=-1 )
		##	"Result"	: False,
		##	"Beyond"	: False,
		##	"Future"	: False,
		##	"InputTime"	: "",
		##	"NowTime"	: "",
		##	"RateTime"	: "",
		##	"RateSec"	: 0
		if wLag['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookHard: SSL_Info: sTimeLag is failed" )
			return False
		
		#############################
		# 期限切れ通知判定
		wCHR_Body = None
##		if wLag['Future']==True and gVal.DEF_STR_TLNUM['indSSLday']>=wLag['RateTime'].days :
		if wLag['Future']==True and gVal.DEF_STR_TLNUM['indSSLday']>=wLag['RateDay'] :
			##まだ余裕がある
##			wCHR_Body = "サーバ[" + wFulluser['Domain'] + "] のSSL証明書期限切れまであと " + str(wLag['RateTime'].days) + "日です。"
			wCHR_Body = "サーバ[" + wFulluser['Domain'] + "] のSSL証明書期限切れまであと " + str(wLag['RateDay']) + "日です。"
##		else :
##			##期限切れ(てか送信すらできないと思う)
##			wCHR_Body = "サーバ[" + wFulluser['Domain'] + "] のSSL証明書の期限が切れました。"
##		
		if wCHR_Body==None :
			return True	#通知日ではない
		
		#############################
		#トゥートの組み立て
		wCHR_Toot = "@" + gVal.STR_MasterConfig['AdminUser'] + " [SSL証明書期限通知]" + '\n'
		wCHR_Toot = wCHR_Toot + wCHR_Body + '\n'
##		wCHR_Toot = wCHR_Toot + "期限日：" + '\n' + wCertInfo['After']
		wCHR_Toot = wCHR_Toot + "期限日：" + '\n' + wCertInfo['After'] + '\n' + gVal.STR_MasterConfig['SystemTag']
		
		#############################
		#トゥート
		wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, visibility="direct" )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookHard: SSL_Info: Mastodon error: " + wRes['Reason'] )
			return False
		
		#############################
		# メモ
		self.STR_Info.update({ "SSL_Info" : {} })
		self.STR_Info['SSL_Info'].update({ "UpdateTD"	: wCertInfo['Befour'] })
		self.STR_Info['SSL_Info'].update({ "RateTD"		: wCertInfo['After'] })
##		self.STR_Info['SSL_Info'].update({ "RateDay"	: str(wLag['RateTime'].days) })
		self.STR_Info['SSL_Info'].update({ "RateDay"	: str(wLag['RateDay']) })
		
		return True



#####################################################
# ハード情報
#####################################################
	def Hard_Info(self):
		#############################
		# 取得する
		wCPU = self.__get_CPU_Info()
		if wCPU['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookHard: Hard_Info: CPU Info get is failed" )
			return False
		
		wMemory = self.__get_Memory_Info()
		if wMemory['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookHard: Hard_Info: Memory Info get is failed" )
			return False
		
		wSwap = self.__get_Swap_Info()
		if wSwap['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookHard: Hard_Info: Swap Info get is failed" )
			return False
		
		wSSD = self.__get_SSD_Info()
		if wSSD['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookHard: Hard_Info: SSD Info get is failed" )
			return False
		
		wRuntime = self.__get_CPU_Info()
		if wRuntime['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookHard: Hard_Info: Runtime Info get is failed" )
			return False
		
		#############################
		#トゥートの組み立て
##		wCHR_Toot = "@" + gVal.STR_MasterConfig['AdminUser'] + " [ハード情報]" + '\n'
		wCHR_Title = "ハード情報通知"
		wCHR_Toot  = "@" + gVal.STR_MasterConfig['AdminUser'] + "[ハード情報通知]" + '\n'
		
		### 稼働時間
		wNowDate = wRuntime['NowTD'].split(" ")
		wRunDate = wRuntime['BootTD'].split(" ")
		
		wCHR_Toot = wCHR_Toot + "現在日付：" + wNowDate[0] + '\n'
		wCHR_Toot = wCHR_Toot + "起動日付：" + wRunDate[0] + '\n'
		wCHR_Toot = wCHR_Toot + "稼働時間：" + str(wRuntime['Runtime']) + " .h" + '\n'
		wCHR_Toot = wCHR_Toot + "稼働日数：" + str(wRuntime['RunDays']) + " .h" + '\n'
		
		### HHD/SSD
		wCHR_Toot = wCHR_Toot + "*--------------------*" + '\n'
		wCHR_Toot = wCHR_Toot + "HHD/SSD：" + '\n'
		wCHR_Toot = wCHR_Toot + "総容量：" + str(wSSD['total']) + " .MB" + '\n'
		wCHR_Toot = wCHR_Toot + "使用中：" + str(wSSD['used']) + " .MB" + '\n'
		wCHR_Toot = wCHR_Toot + "未使用：" + str(wSSD['free']) + " .MB" + '\n'
		wCHR_Toot = wCHR_Toot + "使用率：" + str(wSSD['percent']) + " %" + '\n'
		
		### メモリ
		wCHR_Toot = wCHR_Toot + "*--------------------*" + '\n'
		wCHR_Toot = wCHR_Toot + "メモリ：" + '\n'
		wCHR_Toot = wCHR_Toot + "総容量：" + str(wMemory['total']) + " .MB" + '\n'
		wCHR_Toot = wCHR_Toot + "使用中：" + str(wMemory['used']) + " .MB" + '\n'
		wCHR_Toot = wCHR_Toot + "未使用：" + str(wMemory['free']) + " .MB" + '\n'
		wCHR_Toot = wCHR_Toot + "使用率：" + str(wMemory['percent']) + " %" + '\n'
		
		### スワップ
		wCHR_Toot = wCHR_Toot + "*--------------------*" + '\n'
		wCHR_Toot = wCHR_Toot + "メモリ：" + '\n'
		wCHR_Toot = wCHR_Toot + "総容量：" + str(wSwap['total']) + " .MB" + '\n'
		wCHR_Toot = wCHR_Toot + "使用中：" + str(wSwap['used']) + " .MB" + '\n'
		wCHR_Toot = wCHR_Toot + "未使用：" + str(wSwap['free']) + " .MB" + '\n'
##		wCHR_Toot = wCHR_Toot + "使用率：" + str(wSwap['percent']) + " %"
		wCHR_Toot = wCHR_Toot + "使用率：" + str(wSwap['percent']) + " %" + '\n'
		
		wCHR_Toot = wCHR_Toot + gVal.STR_MasterConfig['SystemTag']
		
		#############################
		#トゥート
		wRes = self.Obj_Parent.OBJ_MyDon.Toot( status=wCHR_Toot, spoiler_text=wCHR_Title, visibility="direct" )
		if wRes['Result']!=True :
			self.Obj_Parent.OBJ_Mylog.Log( 'a', "CLS_LookHard: Hard_Info: Mastodon error: " + wRes['Reason'] )
			return False
		
		return True

	#####################################################
	# CPU
	def __get_CPU_Info(self):
		#############################
		# 枠作成
		wHardInfo = {
			"Result"	: False,
			
			"iowait"	: 0,
			"irq"		: 0,
			"softirq"	: 0,
			"steal"		: 0,
			"(dummy)"	: ""
		}
		
		try :
			#############################
			# 取得
			wARR_Info = psutil.cpu_times()
			
			wHardInfo['iowait']  = float(wARR_Info.iowait)
			wHardInfo['irq']     = float(wARR_Info.irq)
			wHardInfo['softirq'] = float(wARR_Info.softirq)
			wHardInfo['steal']   = float(wARR_Info.steal)
		except ValueError as err :
			return wHardInfo
		
		#############################
		# メモ
		self.STR_Info.update({ "CPU_Info" : {} })
		self.STR_Info['CPU_Info'].update({ "iowait"		: wHardInfo['iowait'] })
		self.STR_Info['CPU_Info'].update({ "irq"		: wHardInfo['irq'] })
		self.STR_Info['CPU_Info'].update({ "softirq"	: wHardInfo['softirq'] })
		self.STR_Info['CPU_Info'].update({ "steal"		: wHardInfo['steal'] })
		
		wHardInfo['Result'] = True
		return wHardInfo

	#####################################################
	# メモリ
	def __get_Memory_Info(self):
		#############################
		# 枠作成
		wHardInfo = {
			"Result"	: False,
			
			"total"		: 0,
			"used"		: 0,
			"free"		: 0,
			"percent"	: 0,
			"(dummy)"	: ""
		}
		
		try :
			#############################
			# 取得
			wARR_Info = psutil.virtual_memory()
			
			wHardInfo['total']   = int(wARR_Info.total) / 1024 / 1024
			wHardInfo['used']    = int(wARR_Info.used) / 1024 / 1024
			wHardInfo['free']    = int(wARR_Info.free) / 1024 / 1024
			wHardInfo['percent'] = float(wARR_Info.percent)
		except ValueError as err :
			return wHardInfo
		
		#############################
		# メモ
		self.STR_Info.update({ "Memory_Info" : {} })
		self.STR_Info['Memory_Info'].update({ "total"	: wHardInfo['total'] })
		self.STR_Info['Memory_Info'].update({ "used"	: wHardInfo['used'] })
		self.STR_Info['Memory_Info'].update({ "free"	: wHardInfo['free'] })
		self.STR_Info['Memory_Info'].update({ "percent"	: wHardInfo['percent'] })
		
		wHardInfo['Result'] = True
		return wHardInfo

	#####################################################
	# スワップ
	def __get_Swap_Info(self):
		#############################
		# 枠作成
		wHardInfo = {
			"Result"	: False,
			
			"total"		: 0,
			"used"		: 0,
			"free"		: 0,
			"percent"	: 0,
			"(dummy)"	: ""
		}
		
		try :
			#############################
			# 取得
			wARR_Info = psutil.swap_memory()
			
			wHardInfo['total']   = int(wARR_Info.total) / 1024 / 1024
			wHardInfo['used']    = int(wARR_Info.used) / 1024 / 1024
			wHardInfo['free']    = int(wARR_Info.free) / 1024 / 1024
			wHardInfo['percent'] = float(wARR_Info.percent)
		except ValueError as err :
			return wHardInfo
		
		#############################
		# メモ
		self.STR_Info.update({ "Swap_Info" : {} })
		self.STR_Info['Swap_Info'].update({ "total"		: wHardInfo['total'] })
		self.STR_Info['Swap_Info'].update({ "used"		: wHardInfo['used'] })
		self.STR_Info['Swap_Info'].update({ "free"		: wHardInfo['free'] })
		self.STR_Info['Swap_Info'].update({ "percent"	: wHardInfo['percent'] })
		
		wHardInfo['Result'] = True
		return wHardInfo

	#####################################################
	# HHD/SSD
	def __get_SSD_Info(self):
		#############################
		# 枠作成
		wHardInfo = {
			"Result"	: False,
			
			"total"		: 0,
			"used"		: 0,
			"free"		: 0,
			"percent"	: 0,
			"(dummy)"	: ""
		}
		
		try :
			#############################
			# 取得
			wARR_Info = psutil.disk_usage('/')
			
			wHardInfo['total']   = int(wARR_Info.total) / 1024 / 1024
			wHardInfo['used']    = int(wARR_Info.used) / 1024 / 1024
			wHardInfo['free']    = int(wARR_Info.free) / 1024 / 1024
			wHardInfo['percent'] = float(wARR_Info.percent)
		except ValueError as err :
			return wHardInfo
		
		#############################
		# メモ
		self.STR_Info.update({ "SSD_Info" : {} })
		self.STR_Info['SSD_Info'].update({ "total"		: wHardInfo['total'] })
		self.STR_Info['SSD_Info'].update({ "used"		: wHardInfo['used'] })
		self.STR_Info['SSD_Info'].update({ "free"		: wHardInfo['free'] })
		self.STR_Info['SSD_Info'].update({ "percent"	: wHardInfo['percent'] })
		
		wHardInfo['Result'] = True
		return wHardInfo

	#####################################################
	# 稼働時間
	def __get_Runtime_Info(self):
		#############################
		# 枠作成
		wHardInfo = {
			"Result"	: False,
			
			"NowTD"		: "",
			"BootTD"	: "",
			"Runtime"	: 0,
			"RunDays"	: 0,
			"(dummy)"	: ""
		}
		
		try :
			#############################
			# 取得
			wHardInfo['NowTD'] = gVal.STR_TimeInfo['TimeDate']
			
			###稼働日
			wBootTime = datetime.fromtimestamp(psutil.boot_time())
			wHardInfo['BootTD'] = wBootTime.strftime("%Y/%m/%d %H:%M:%S")
			
			###稼働時間
			wRuntime = wHardInfo['NowTD'] - wHardInfo['BootTD']
			wRuntime = wRuntime.total_seconds()
			wRuntime = int( wRuntime / float(3600) )
			wHardInfo['Runtime'] = wRuntime			#稼働時間
			wHardInfo['RunDays'] = wRuntime / 24	#稼働日数
		except ValueError as err :
			return wHardInfo
		
		#############################
		# メモ
		self.STR_Info.update({ "Runtime_Info" : {} })
		self.STR_Info['Runtime_Info'].update({ "NowTD"		: wHardInfo['NowTD'] })
		self.STR_Info['Runtime_Info'].update({ "BootTD"		: wHardInfo['BootTD'] })
		self.STR_Info['Runtime_Info'].update({ "Runtime"	: wHardInfo['Runtime'] })
		self.STR_Info['Runtime_Info'].update({ "RunDays"	: wHardInfo['RunDays'] })
		
		wHardInfo['Result'] = True
		return wHardInfo


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

