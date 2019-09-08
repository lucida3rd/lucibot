#!/usr/bin/python
# coding: UTF-8
#####################################################
# public
#   Class   ：SSL証明書情報
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/9/6
#####################################################
# Private Function:
#   __exgCertTD( cls, inSSL_TD ) :
#   __exgDecode( cls, inObjData ) :
#
# Instance Function:
#   (none)
#
# Class Function(static):
#   sGetCertInfo( cls, inDomain ):
#
#####################################################
# 前提：
#   OpenSSLモジュールが必要
# # php3 install pyOpenSSL
#####################################################
import codecs
import ssl
import OpenSSL

#####################################################
class CLS_SSLCtrl() :

	DEF_MOJI_ENCODE = 'utf-8'		#文字エンコード

#####################################################
# SSL証明書情報取得
#####################################################
	@classmethod
	def sGetCertInfo( cls, inDomain ):
		#############################
		# 応答情報の作成
		wResult = {
			"Result"	: False,
			"Reason"	: "",
			
			"Befour"	: "",		#更新日
			"After"		: "",		#期限日
			"Other"		: {}
		}
		
		#############################
		# Cert情報を取得する
		wCert = ssl.get_server_certificate(( inDomain, 443 ) )
		wOSSL = OpenSSL.crypto.load_certificate( OpenSSL.crypto.FILETYPE_PEM, wCert )
		
		#############################
		# 更新日の取得
		wSSL_Befour = wOSSL.get_notBefore()
		wRes = cls.__exgCertTD( wSSL_Befour )
		if wRes['Result']!=True :
			wResult['Reason'] = wRes['Reason']
			return wResult
		wResult['Befour'] = wRes['TimeDate']
		
		#############################
		# 期限日の取得
		wSSL_After = wOSSL.get_notAfter()
		wRes = cls.__exgCertTD( wSSL_After )
		if wRes['Result']!=True :
			wResult['Reason'] = wRes['Reason']
			return wResult
		wResult['After'] = wRes['TimeDate']
		
		#############################
		# その他の情報
		wSSL_Others = wOSSL.get_subject().get_components()
		wDecode_Others = []
		wFlg = False
		### デコードしながら辞書に戻す
		for wLine in wSSL_Others :
			wGetLine = []
			for wCel in wLine :
				wCel = cls.__exgDecode( wCel )
				if wCel==None :
					wFlg = True	#デコード失敗
					break
				wGetLine.append( wCel )
			if wFlg==True :
				break	##デコード失敗したら抜ける
			wDecode_Others.append( wGetLine )
		
		if wFlg==True :
			##デコード失敗
			wResult['Reason'] = "CLS_SSLCtrl: __exgCertTD: decode error"
			return wResult
		
		wResult['Other'] = wDecode_Others
		
		#############################
		# 正常
		wResult['Result'] = True
		return wResult

	#####################################################
	@classmethod
	def __exgCertTD( cls, inSSL_TD ) :
		#############################
		# 応答情報の作成
		wResult = {
			"Result"	: False,
			"Reason"	: "",
			"TimeDate"	: ""
		}
		
		#############################
		# 書式: 20190822190124Z
		#############################
		#############################
		# テキストにデコード
		wSSL_TD = cls.__exgDecode( inSSL_TD )
		if wSSL_TD==None :
			wResult['Reason'] = "CLS_SSLCtrl: __exgCertTD: decode error"
			return wResult
		
		#############################
		# 日の取り出し
		try :
			wDate = []
			wDate.append( wSSL_TD[0:4] )
			wDate.append( wSSL_TD[4:6] )
			wDate.append( wSSL_TD[6:8] )
			wDate = '-'.join( wDate )
		except ValueError as err :
			wResult['Reason'] = "CLS_SSLCtrl: __exgCertTD: Date exchange error: " + err
			return wResult
		
		#############################
		# 時間の取り出し
		try :
			wTime = []
			wTime.append( wSSL_TD[8:10] )
			wTime.append( wSSL_TD[10:12] )
			wTime.append( wSSL_TD[12:14] )
			wTime = ':'.join( wTime )
		except ValueError as err :
			wResult['Reason'] = "CLS_SSLCtrl: __exgCertTD: Date exchange error: " + err
			return wResult
		
		#############################
		# 合成して結果に詰める
		wResult['TimeDate'] = wDate + " " + wTime
		wResult['Result']   = True
		return wResult

	#####################################################
	@classmethod
	def __exgDecode( cls, inObjData ) :
		try :
			wSTR_Decode = inObjData.decode( encoding=cls.DEF_MOJI_ENCODE )
		except ValueError as err :
			return None
		
		return wSTR_Decode



