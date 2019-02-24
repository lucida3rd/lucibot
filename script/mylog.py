#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ログ処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/2/24
#####################################################
import codecs
import string
import global_val
#####################################################
class CLS_Mylog:
	NowTimeDate  = ''	#現在日時

#####################################################
# Init
#####################################################
	def __init__(self):
		return



#####################################################
# 時間を取得する
#####################################################
	def pGetTime(self):
		wRes = global_val.gCLS_Init.cGetTime()
		if wRes['Result']!=True :
			return False
		
		self.NowTimeDate = wRes['TimeDate']
		return True



#####################################################
# ログデータのセット
#####################################################
##	def cLog( self, level, msg, view=False, tag="" ):
	def cLog( self, level, log_file, msg, view=False ):
		
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
		# パスが無設定ならregに出力する
		if log_file=="" :
			wDate = NowTimeDate.split(" ")
			if wDate[0]=="" :
				###ありえないor時計ぶっ壊れてる？
				global_val.gCLS_Init.cPrint( 'unknown Time = ' + msg )
				return
			
			log_file = global_val.gSTR_File['RegLog'] + wDate[0] + '.log'
		
		#############################
		# コンソールに表示する
		# = システムログに出る
		if view==True :
			global_val.gCLS_Init.cPrint( self.NowTimeDate + ' ' + msg )
		
		#############################
		# ファイルへ書き出す
		self.pWrite( msg=msg, tag=tag )
		return



#####################################################
# ファイルへの書き出し
#####################################################
##	def pWrite( self, msg, tag="" ):
	def pWrite( self, log_file, msg ):
##		#############################
##		# ファイル名の作成
##		log_file = ''
##		if self.GetTD == '' :
##			log_file = global_val.gMyLog_path + tag + '_error.log'
##		else :
##			log_date = self.GetTD.strftime("%Y%m%d")
##			log_file = global_val.gMyLog_path + tag + log_date + '.log'
		
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
		file.writelines( setline )
		file.close()
		
		return



