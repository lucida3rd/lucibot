# coding: UTF-8
#####################################################
# 十八試るしぼっと
#   Class   ：ログ処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2018/11/17
#####################################################
from datetime import datetime
import codecs
import string
#import re
import global_val
#####################################################
class CLS_Mylog:
	GetTD = ''			#取得日時
	NowTimeDate  = ''	#現在日時

#####################################################
# Init
#####################################################
	def __init__(self):
		self.pGetTime()
		return



#####################################################
# 時間を取得する
#####################################################
	def pGetTime(self):
		#############################
		# 時間を取得
		try:
##			self.NowTimeDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			self.GetTD       = datetime.now()
			self.NowTimeDate = self.GetTD.strftime("%Y-%m-%d %H:%M:%S")
		except ValueError as err :
			self.GetTD = ''
			NowTimeDate  = 'xxxx-xx-xx xx:xx:xx'
			return False
		
		#############################
		# 取得成功
		return True



#####################################################
# ログデータのセット
#####################################################
	def cLog(self,level,msg,view=False,tag=""):
		
		#############################
		# 設定されたログレベルが適当でなければ
		# 'a'を設定しなおす
		if level != 'a' and level != 'b' and level != 'c' :
			level = 'a'
		
		#############################
		# ログレベルで出力が有効か
		if global_val.gConfig['LogLevel'] == 'c' and ( level == 'b' or level == 'c' ) :
			return
		
		if global_val.gConfig['LogLevel'] == 'b' and level == 'c' :
			return
		
		###※以下ログ出力
		#############################
		# 余白・改行を取る
		msg  = msg.strip()
		
		#############################
		# 時間を取得
		self.pGetTime()
		
		#############################
		# ファイルへ書き出す
		self.pWrite(msg,tag)
		return



#####################################################
# ファイルへの書き出し
#####################################################
	def pWrite(self,msg,tag=""):
		#############################
		# ファイル名の作成
		log_file = ''
		if self.GetTD == '' :
			log_file = global_val.gMyLog_path + tag + '_error.log'
		else :
			log_date = self.GetTD.strftime("%Y%m%d")
			log_file = global_val.gMyLog_path + tag + log_date + '.log'
		
		#############################
		# 追記モードで開く
		file = codecs.open( log_file, 'a', 'utf-8')
		
		#############################
		# データを作成
		setline = []
		line = self.NowTimeDate + ' ' + msg + '\n'
		setline.append( line )
		
		#############################
		# 書き込んで閉じる
##		file.write( string.join(setline,'') )
		file.writelines( setline )
		file.close()
		
		return



