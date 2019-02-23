# coding: UTF-8
#####################################################
# 十八試るしぼっと
#   Class   ：マスター実行処理
#   Site URL：https://lucida-memo.info/
#   Update  ：2019/2/3
#####################################################
import sys
from datetime import datetime
sys.path.append('script')

from grobal_init import CLS_Init
import global_val

#####################################################
# メイン処理
#####################################################
def main():
	#############################
	# 引数を取得
	wARRargs = sys.argv
	
	if len(wARRargs)==2 :
	#############################
	# ハード監視 メイン処理
		if wARRargs[1]=='-h' :
			self.hard_main()
	
	if len(wARRargs)==3 :
	#############################
	# RUN メイン処理
		if wARRargs[1]=='-m' :
#		elif wARRargs[1]=='-m' :
			self.run_main()
	
	return



#####################################################
# RUN メイン処理
#####################################################
def run_main():
	#############################
	# 初期化処理
	global_val.gCLS_Init = CLS_Init()
	if global_val.gCLS_Init.cInit() != True :
		return	#初期化失敗
	
	#############################
	# 処理開始
	global_val.gCLS_Mylog.cLog('a', "bot処理開始")
	
	#############################
	# 処理本体
	global_val.gCLS_MainProc.cMain()
	
	#############################
	# 排他解除
	global_val.gCLS_Init.cUnlock()
	
	#############################
	# 処理おわり
	global_val.gCLS_Mylog.cLog('c', "bot処理終了")
	
	return



#####################################################
# ハード監視 メイン処理
#####################################################
def hard_main():
	#############################
	# 初期化処理
	global_val.gCLS_Init = CLS_Init()
	if global_val.gCLS_Init.cInit_Hard() != True :
		return	#初期化失敗
	
	#############################
	# 処理開始
	global_val.gCLS_Mylog.cLog('a', "bot処理開始", global_val.gMyLog_Hard )
	
	#############################
	# 処理本体
	global_val.gCLS_LookHard.cMain()
	
	#############################
	# 処理おわり
	global_val.gCLS_Mylog.cLog('c', "bot処理終了", global_val.gMyLog_Hard )
	
	return



#############################
# メイン処理起動
main()



