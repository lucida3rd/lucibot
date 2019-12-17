#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ログアーカイブ
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/12/17
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   __init__(self):
#   Run(self):
#
# Class Function(static):
#   (none)
#
#####################################################
# 制限：
#   ・MasterConfigのログは自動削除しない
#   ・作成されたzipはWindows標準のアーカイバでは解凍できない。
#     7zipなど専用のアーカイバで解凍可能。
#####################################################

from osif import CLS_OSIF
from filectrl import CLS_File
from userdata import CLS_UserData

from gval import gVal
#####################################################
class CLS_LogArcive():
#####################################################

#####################################################
# 初期化
#####################################################
	def __init__(self):
		return



#####################################################
# 処理実行
#####################################################
	def Run(self):
		#############################
		# 処理開始の確認
		wStr = "ログのアーカイブを開始します。" + '\n'
		wStr = wStr + "よろしいですか？(y/N)=> "
		wRes = CLS_OSIF.sInp( wStr )
		if wRes!="y" :
			CLS_OSIF.sPrn( "処理を中止しました。" )
			return
		
		#############################
		# ユーザフォルダのアーカイブリスト 作成
		wARR_UserList = CLS_UserData.sGetUserList()
		wARR_ArciveList = []
		wARR_DeleteList = {}
		wIndex = 0
		for wLine in wARR_UserList :
			#############################
			# パス生成
			wPath = gVal.DEF_USERDATA_PATH + wLine + "/log/"
			wARR_ArciveList.append( wPath )
			
			#############################
			# ファイル一覧生成
			wFileList = CLS_File.sFs( wPath )
			wDelList = []
			for wFilePath in wFileList :
##				wFilePath = wPath + wFilePath
				wARR_ArciveList.append( wFilePath )
				wDelList.append( wFilePath )
			
			wARR_DeleteList.update({ wIndex : wDelList })
			wIndex += 1
		
		#############################
		# masterConfigフォルダ 追加
		wPath = gVal.DEF_USERDATA_PATH + gVal.DEF_MASTERCONFIG_NAME + "/log/"
		wARR_ArciveList.append( wPath )
		
		wFileList = CLS_File.sFs( wPath )
		wDelList = []
		for wFilePath in wFileList :
##			wFilePath = wPath + wFilePath
			wARR_ArciveList.append( wFilePath )
			wDelList.append( wFilePath )
		
##		wARR_DeleteList.update({ wIndex : wDelList })
##		wIndex += 1
		
		#############################
		# 各カレントの削除一覧から最後尾を抜く
		wKeyList = wARR_DeleteList.keys()
		for wKey in wKeyList :
			if len(wARR_DeleteList[wKey])>=2 :
				del wARR_DeleteList[wKey][-1]
		
		#############################
		# アーカイブ名の作成
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			CLS_OSIF.sPrn( "時間取得失敗。処理を中止しました。" )
			return
		wDate = wTD['TimeDate'].split(" ")
		
		#############################
		# ファイルパスを作成する
##		wLogFile = gVal.DEF_STR_FILE['MasterLog_path'] + "logs" + wDate[0] + wDate[1] + ".zip"
		wNDate = wDate[0].replace( "-", "" )
		wNTime = wDate[1].replace( ":", "" )
		wFileName = "logs_" + wNDate + "_" + wNTime + ".zip"
		wLogFile = gVal.DEF_STR_FILE['MasterConfig_path'] + wFileName
		
		CLS_OSIF.sPrn( '\n' + "アーカイブ実行中..." )
		#############################
		# アーカイブ実行
###		print( "xx1: " + wLogFile )
###		print( "xx2: " + str(wARR_ArciveList) )
		if CLS_File.sFolderArcive( wLogFile, wARR_ArciveList )!=True :
			CLS_OSIF.sPrn( "アーカイブ失敗。処理を中止しました。" )
			return
		
		CLS_OSIF.sPrn( '\n' + "古いログを削除中..." )
		#############################
		# 古いログを削除
		wKeyList = wARR_DeleteList.keys()
		for wKey in wKeyList :
			for wPath in wARR_DeleteList[wKey] :
###				print( wPath )
				if CLS_File.sRemove( wPath )!=True :
					CLS_OSIF.sPrn( "削除失敗。処理を中止しました。" )
					break
		
		CLS_OSIF.sPrn( "処理が完了しました。" )
		return



