#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：マスター実行処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/2/27
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
		global_val.gCLS_Init.cPrint("main(): Datafolder not found: " + global_val.gUserData_Path )
		return
	
	#############################
	# master環境情報の読み込み
	if global_val.gCLS_Config.cGetMasterConfig()!=True :
		#############################
		# 環境のセットアップ
		global_val.gCLS_Config.cMasterSetup()
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
	# master環境情報の表示
		elif wARRargs[1]=='-vm' :
			global_val.gCLS_Config.cCnfMasterConfig_Disp()
			wFlg = True
	
	#############################
	# master運用操作
		elif wARRargs[1]=='-mrun' :
			global_val.gCLS_Config.cCnfMasterRun()
			wFlg = True
	
	#############################
	# masterメンテ操作
		elif wARRargs[1]=='-mman' :
			global_val.gCLS_Config.cCnfMasterMainte()
			wFlg = True
	
	#############################
	# ユーザ登録 一覧表示
		elif wARRargs[1]=='-vl' :
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
	# master環境情報の表示・操作
		if wARRargs[1]=='-c' and wARRargs[2]=='mconf' :
			global_val.gCLS_Config.cCnfMasterConfig()
			wFlg = True
	
	#############################
	# AdminUserの変更
		elif wARRargs[1]=='-c' and wARRargs[2]=='admin' :
			global_val.gCLS_Config.cCnfAdminUser()
			wFlg = True
	
	#############################
	# MasterUserの変更
		elif wARRargs[1]=='-c' and wARRargs[2]=='master' :
			global_val.gCLS_Config.cCnfMasterUser()
			wFlg = True
	
	#############################
	# ユーザ登録 登録
		elif wARRargs[1]=='-ur' :
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
	
	#############################
	# 通信テスト
		elif wARRargs[1]=='-utest' :
			global_val.gCLS_Regist.cTest( wARRargs[2] )
			wFlg = True
	
#	#############################
#	# RUN メイン処理
#		elif wARRargs[1]=='-m' :
#			self.run_main()
#			wFlg = True
	

	#####################################################
	# コマンド未実行
	#   Help表示
	if wFlg != True :
		global_val.gCLS_Init.cViewHelp()
	
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



