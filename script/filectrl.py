#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ファイル制御
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/3
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
#   sClrFile( cls, inPath ):
#   sWriteFile( cls, inPath, inSetLine ):
#   sAddFile( cls, inPath, inSetLine ):
#
#####################################################
import os
import shutil
import codecs
from gval import gVal
#####################################################
class CLS_File() :
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
			return False
		
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
			wFile = codecs.open( inPath, 'w', gVal.DEF_MOJI_ENCODE )
			wFile.close()
		except ValueError as err :
			return False
		
		return True



#####################################################
# ファイル上書き書き込み
#####################################################
	@classmethod
	def sWriteFile( cls, inPath, inSetLine ):
		#############################
		# 中身クリア
		if cls().sClrFile( inPath )!=True :
			return False
		
		#############################
		# 書き込み
		try:
			wFile = codecs.open( inPath, 'w', gVal.DEF_MOJI_ENCODE )
			wFile.writelines( inSetLine )
			wFile.close()
		except ValueError as err :
			return False
		
		return True



#####################################################
# ファイル追加書き込み
#####################################################
	@classmethod
	def sAddFile( cls, inPath, inSetLine ):
		#############################
		# 存在チェック
		if cls().sExist( inPath )!=True :
			return False
		
		#############################
		# 書き込み
		try:
			wFile = codecs.open( inPath, 'a', gVal.DEF_MOJI_ENCODE )
			wFile.writelines( inSetLine )
			wFile.close()
		except ValueError as err :
			return False
		
		return True



