#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：マスター実行処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/2/24
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
	wFlg = False
	
	#############################
	# 初期化クラスの生成
	global_val.gCLS_Init = CLS_Init()
	
	#############################
	# データフォルダのチェック
	if global_val.gCLS_File.cExist( global_val.gUserData_Path )!=True :
		###通常ありえない
		global_val.gCLS_Init.cPrint("データフォルダがありません: 設定パス: " + global_val.gUserData_Path )
		return
	
	#####################################################
	# 引数=2のコマンド群
	if len(wARRargs)==2 :
	#############################
	# システム情報の表示
		if wARRargs[1]=='-v' :
			global_val.gCLS_Init.cViewSysinfo()
			wFlg = True
	
	#############################
	# ユーザ登録 一覧表示
		elif wARRargs[1]=='-ul' :
			global_val.gCLS_Regist.cViewList()
			wFlg = True
	
	#############################
	# ハード監視 メイン処理
#		elif wARRargs[1]=='-h' :
#			self.hard_main()
#			wFlg = True
	

	#####################################################
	# 引数=3のコマンド群
	if len(wARRargs)==3 :
	#############################
	# ユーザ登録 登録
		if wARRargs[1]=='-ur' :
			global_val.gCLS_Regist.cRegist( wARRargs[2] )
			wFlg = True
	
	#############################
	# ユーザ登録 再登録
		elif wARRargs[1]=='-uu' :
			global_val.gCLS_Regist.cUpdate( wARRargs[2] )
			wFlg = True
	
	#############################
	# ユーザ登録 削除
		elif wARRargs[1]=='-ud' :
			global_val.gCLS_Regist.cDelete( wARRargs[2] )
			wFlg = True
	
#	#############################
#	# RUN メイン処理
#		elif wARRargs[1]=='-m' :
#			self.run_main()
#			wFlg = True
	

	#####################################################
	# コマンド未実行
	if wFlg != True :
		global_val.gCLS_Init.cPrint("コマンドが無効です")
	
	return



#####################################################
# RUN メイン処理
#####################################################
def run_main():
	#############################
	# 初期化処理
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



