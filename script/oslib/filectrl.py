#!/usr/bin/python
# coding: UTF-8
#####################################################
# public
#   Class   ：ファイル制御
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/12/17
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   (none)
#
# Class Function(static):
#   sExist( cls, inPath ):
#   sFolderExist( cls, inPath, inName ):
#   sLs( cls, inPath ):
#   sMkdir( cls, inPath ):
#   sCopytree( cls, inSrcPath, inDstPath ):
#   sRmtree( cls, inPath ):
#   sCopy( cls, inSrcPath, inDstPath ):
#   sRename( cls, inSrcPath, inDstPath ):
#   sClrFile( cls, inPath ):
#   sWriteFile( cls, inPath, inSetLine ):
#   sAddFile( cls, inPath, inSetLine ):
#   sReadFile( cls, inPath, outLine ):
#   sChmod( cls, inPath, inMod ):
#   sGetTimedate( cls, inPath ) :
#
#####################################################
from datetime import datetime
import os
import shutil
import codecs
import glob
import zipfile

#####################################################
class CLS_File() :

	DEF_MOJI_ENCODE = 'utf-8'								#文字エンコード

#####################################################
# 存在チェック
#####################################################
	@classmethod
	def sExist( cls, inPath ):
		### memo: ファイルだけ
		### os.path.isfile
		wRes = os.path.exists( inPath )
		if wRes==False :
			return False
		
		return True



#####################################################
# フォルダ存在チェック
#####################################################
	@classmethod
	def sFolderExist( cls, inPath, inName ):
		#############################
		# 存在チェック
		if cls().sExist( inPath )!=True :
			return False
		
		#############################
		# データフォルダの取得
		wList = cls().sLs( inPath )
		
		#############################
		# 重複チェック
		for wFile in wList :
			if wFile==inName :
				return True
		
		return False



#####################################################
# フォルダ一覧取得
#####################################################
	@classmethod
	def sLs( cls, inPath ):
		#############################
		# 存在チェック
		if cls().sExist( inPath )!=True :
##			return False
			return []
		
		#############################
		# フォルダリストの取得
		wARR_Filelist = []
		for wFile in os.listdir( inPath ) :
			if os.path.isdir( os.path.join( inPath, wFile ) ) :
				wARR_Filelist.append( wFile )
		
		return wARR_Filelist



#####################################################
# フォルダ作成
#####################################################
	@classmethod
	def sMkdir( cls, inPath ):
		try:
			os.mkdir( inPath )
		except ValueError as err :
			return False
		
		return True



#####################################################
# フォルダコピー
#####################################################
	@classmethod
	def sCopytree( cls, inSrcPath, inDstPath ):
		#############################
		# 存在チェック
		if cls().sExist( inSrcPath )!=True :
			return False
		
		###inDstPathはそもそも存在しない前提
		
		#############################
		# コピー
		try:
			shutil.copytree( inSrcPath, inDstPath )
		except ValueError as err :
			return False
		
		return True



#####################################################
# ファイル一覧取得
#####################################################
	@classmethod
	def sFs( cls, inPath ):
		#############################
		# 存在チェック
		if cls().sExist( inPath )!=True :
			return []
		
		#############################
		# ファイルリストの取得
		try:
			wARR_Filelist = glob.glob( inPath + "*" )
		except ValueError as err :
			return []
		
		return wARR_Filelist



#####################################################
# フォルダ削除
#####################################################
	@classmethod
	def sRmtree( cls, inPath ):
		try:
			shutil.rmtree( inPath )
		except ValueError as err :
			return False
		
		return True



#####################################################
# ファイルコピー
#####################################################
	@classmethod
	def sCopy( cls, inSrcPath, inDstPath ):
		#############################
		# 存在チェック
		if cls().sExist( inSrcPath )!=True :
			return False
		
		###inDstPathはそもそも存在しない前提
		
		#############################
		# コピー
		try:
			shutil.copyfile( inSrcPath, inDstPath )
		except ValueError as err :
			return False
		
		return True



#####################################################
# ファイルリネーム
#####################################################
	@classmethod
	def sRename( cls, inSrcPath, inDstPath ):
		#############################
		# 存在チェック
		if cls().sExist( inSrcPath )!=True :
			return False
		
		###inDstPathはそもそも存在しない前提
		
		#############################
		# リネーム
		try:
			os.rename( inSrcPath, inDstPath )
		except ValueError as err :
			return False
		
		return True



#####################################################
# ファイル削除
#####################################################
	@classmethod
	def sRemove( cls, inSrcPath ):
		#############################
		# 存在チェック
		if cls().sExist( inSrcPath )!=True :
			return False
		
		#############################
		# 削除
		try:
			os.remove( inSrcPath )
		except ValueError as err :
			return False
		
		return True



#####################################################
# ファイル中身だけクリア
#####################################################
	@classmethod
	def sClrFile( cls, inPath ):
		#############################
		# 存在チェック
		if cls().sExist( inPath )!=True :
			return False
		
		#############################
		# 中身クリア
		try:
			wFile = codecs.open( inPath, 'w', cls.DEF_MOJI_ENCODE )
			wFile.close()
		except ValueError as err :
			return False
		
		return True



#####################################################
# ファイル上書き書き込み
#####################################################
	@classmethod
	def sWriteFile( cls, inPath, inSetLine, inExist=True, inRT=False ):
		#############################
		# 存在チェック
		if inExist==True :
			if cls().sExist( inPath )!=True :
				return False
		
		#############################
		# 改行を付加
		wSetLine = []
		if inRT==True :
			for wLine in inSetLine :
				wLine = str(wLine) + '\n'
				wSetLine.append( wLine )
		else:
			wSetLine = inSetLine
		
		#############################
		# 書き込み
		try:
			wFile = codecs.open( inPath, 'w', cls.DEF_MOJI_ENCODE )
			wFile.writelines( wSetLine )
			wFile.close()
		except ValueError as err :
			return False
		
		return True



#####################################################
# ファイル追加書き込み
#####################################################
	@classmethod
	def sAddFile( cls, inPath, inSetLine, inExist=True, inRT=False ):
		#############################
		# 存在チェック
		if inExist==True :
			if cls().sExist( inPath )!=True :
				return False
		
		#############################
		# 改行を付加
		wSetLine = []
		if inRT==True :
			for wLine in inSetLine :
				wLine = str(wLine) + '\n'
				wSetLine.append( wLine )
		else:
			wSetLine = inSetLine
		
		#############################
		# 書き込み
		try:
			wFile = codecs.open( inPath, 'a', cls.DEF_MOJI_ENCODE )
			wFile.writelines( wSetLine )
			wFile.close()
		except ValueError as err :
			return False
		
		return True



#####################################################
# ファイル読み込み
#####################################################
	@classmethod
	def sReadFile( cls, inPath, outLine ):
		
		pList = outLine		#アドレス渡し
		#############################
		# 読み出し先がリスト型か
		if isinstance( pList, list )!=True :
			return False
		
###		if len(pList)!=0 :
###			return False
		
		#############################
		# 存在チェック
		if cls().sExist( inPath )!=True :
			return False
		
		#############################
		# 読み出し先に読み出す
		try:
			for wLine in open( inPath, 'r'):	#ファイルを開く
				wLine = wLine.strip()
				pList.append( wLine )
		except ValueError as err :
			return False
		
		return True



#####################################################
# ファイル権限変更
#####################################################
	@classmethod
	def sChmod( cls, inPath, inMod ):
		#############################
		# 存在チェック
		if cls().sExist( inPath )!=True :
			return False
		
		try:
			os.chmod( inPath, inMod )
		except ValueError as err :
			return False
		
		return True



#####################################################
# フォルダアーカイブ
#####################################################
	@classmethod
	def sFolderArcive( cls, inDstPath, inFolderList ):
		#############################
		# パラメータチェック
		if len(inFolderList)==0 :
			return False
		
		wFLG_Err = False
		try:
			#############################
			# アーカイブ
##			with zipfile.ZipFile(inDstPath,'w') as wMyzip:
			with zipfile.ZipFile( inDstPath, 'w', compression=zipfile.ZIP_DEFLATED ) as wMyzip:
				for wLine in inFolderList :
					wMyzip.write( wLine )
		
		except ValueError as err :
			wFLG_Err = True
		
		#############################
		# エラーの場合
		if wFLG_Err==True :
			### ***消す
			return False
		
		#############################
		# OK
		return True



#####################################################
# ファイルの日時取得
#####################################################
	@classmethod
	def sGetTimedate( cls, inPath ) :
		#############################
		# 存在チェック
		if cls().sExist( inPath )!=True :
			return ""
		
		#############################
		# 周期トゥートパターンファイルの日時取得
		wTD = datetime.fromtimestamp( os.stat( inPath ).st_mtime )
		wTD = wdt.strftime("%Y-%m-%d %H:%M:%S")
		
		return wTD



