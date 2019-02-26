#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ファイル制御
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/2/24
#####################################################
import os
import shutil
import codecs
import global_val
#####################################################
class CLS_File:
	

#####################################################
# Init
#####################################################
	def __init__(self):
		return



#####################################################
# 存在チェック
#####################################################
	def cExist( self, path ):
		### memo: ファイルだけ
		### os.path.isfile
		
		wRes = os.path.exists(path)
		if wRes==False :
			return False
		
		return True



#####################################################
# フォルダ存在チェック
#####################################################
	def cFolderExist( self, path, name ):
		#############################
		# データフォルダの取得
		wList = self.cGetFolderList( path )
		
		#############################
		# 重複チェック
		for f in wList :
			if f==name :
				return True
		
		return False



#####################################################
# フォルダ一覧取得
#####################################################
	def cGetFolderList( self, path ):
		filelist = []
		for f in os.listdir( path ) :
			if os.path.isdir( os.path.join( path, f ) ) :
				filelist.append(f)
		
		return filelist

##	def cGetFolderList( self, path, topdown=True, onerror=None, followlinks=False ):
##		wList = ""
##		for d, s, f in os.walk( top=path, topdown=topdown, onerror=onerror, followlinks=followlinks ) :
##			wList = wList + d + '\n'
##
##	## dirpath	：ディレクトリパス
##	## dirname	：dirpathで指定したディレクトリ内のサブディレクトリ名のリスト
##	## filename	：dirpath内のファイル名（ディレクトリでない）のリスト
##		return wList



#####################################################
# フォルダ作成
#####################################################
	def cMakeFolder( self, path ):
		try:
			os.mkdir( path )
		except ValueError as err :
			return False
		
		return True



#####################################################
# フォルダコピー
#####################################################
	def cCopyFolder( self, src_path, dst_path ):
		try:
			shutil.copytree( src_path, dst_path )
		except ValueError as err :
			return False
		
		return True



#####################################################
# フォルダ削除
#####################################################
	def cDelFolder( self, path ):
		try:
			shutil.rmtree( path )
		except ValueError as err :
			return False
		
		return True








#####################################################
# ファイル中身だけクリア
#####################################################
	def cClearFile( self, path ):
		if self.cExist( path )!=True :
			return False
		
		try:
			file = codecs.open( path, 'w', 'utf-8')
			file.close()
		except ValueError as err :
			return False
		
		return True














