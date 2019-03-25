#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ユーザ登録
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/25
#####################################################
# Private Function:
#   __registUser( self, inFulluser, inMail, inPass ):
#   __prn( self, inMsg ):
#
# Instance Function:
#   __init__(self):
#   GetMastodon( self, inFulluser ):
#   CreateMastodon( self, inFulluser ):
#   Test( self, inFulluser ):
#   Regist( self, inFulluser ):
#   Update( self, inFulluser ):
#   Delete( self, inFulluser ):
#
# Class Function(static):
#   sRegistMastodon( cls, inFulluser, inMail, inPass ):
#
#####################################################

from osif import CLS_OSIF
from filectrl import CLS_File
from userdata import CLS_UserData
from botjob import CLS_Botjob
from mastodon_use import CLS_Mastodon_Use
from gval import gVal
#####################################################
class CLS_Regist() :
#####################################################
	STR_Mastodon = {}	#CreateMastodonの生成物

#####################################################
# Init
#####################################################
	def __init__(self):
		self.STR_Mastodon = {}
		return



#####################################################
# mastodonクラス生成
#####################################################
	def GetMastodon( self, inFulluser ):
		#############################
		# 応答形式の取得(mastodon形式)
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_Mastodon_Use.sGet_API_Resp()
		
		#############################
		# 出力先領域のチェック
			#辞書型か？
		if isinstance( self.STR_Mastodon, dict )!=True :
			wRes['Reason'] = "CLS_Regist: GetMastodon: STR_Mastodon is not dict: type= " + type(self.STR_Mastodon)
			return wRes
		
			#重複してるか？
		if inFulluser not in self.STR_Mastodon :
			wRes['Reason'] = "CLS_Regist: GetMastodon: Can't find mastodon: " + inFulluser
			return wRes
		
		wRes['Responce'] = self.STR_Mastodon[inFulluser]
		wRes['Result'] = True
		return wRes



#####################################################
# mastodonクラス生成
#####################################################
	def CreateMastodon( self, inFulluser ):
		#############################
		# 応答形式の取得(mastodon形式)
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_Mastodon_Use.sGet_API_Resp()
		
		#############################
		# 出力先領域のチェック
			#辞書型か？
		if isinstance( self.STR_Mastodon, dict )!=True :
			wRes['Reason'] = "CLS_Regist: CreateMastodon: STR_Mastodon is not dict: type= " + type(self.STR_Mastodon)
			return wRes
		
			#重複してるか？
		if inFulluser in self.STR_Mastodon :
			wRes['Reason'] = "CLS_Regist: CreateMastodon: Overlap user: " + inFulluser
			return wRes
		
		#############################
		# ドメイン抽出
		wSTR_user = CLS_UserData.sUserCheck( inFulluser )
		if wSTR_user['Result']!=True :
			wRes['Reason'] = "CLS_Regist: CreateMastodon: Domain check error: " + inFulluser
			return wRes
		
		#############################
		# ping疎通チェック
		if CLS_OSIF.sPing( wSTR_user['Domain'] )!=True :
			wRes['Reason'] = "CLS_Regist: CreateMastodon: Ping check error: " + wSTR_user['Domain']
			return wRes	#失敗
		
		#############################
		# レジストファイルの存在チェック
		wGetPath = CLS_UserData.sGetUserPath( inFulluser )
##		if wGetPath['Result']!=True :
##			wRes['Reason'] = "CLS_Regist: CreateMastodon: User path ng: " + wGetPath['Reason']
##			return wRes
		
		wRegFile = wGetPath['Responce'] + gVal.STR_File['Reg_RegFile']
		if CLS_File.sExist( wRegFile )!=True :
			wRes['Reason'] = "CLS_Regist: CreateMastodon: Regist File not is found: " + wRegFile
			return wRes		#ファイルがない
		
		wUserFile = wGetPath['Responce'] + gVal.STR_File['Reg_UserFile']
		if CLS_File.sExist( wUserFile )!=True :
			wRes['Reason'] = "CLS_Regist: CreateMastodon: Userreg File not is found: " + wUserFile
			return wRes		#ファイルがない
		
		#############################
		# mastodon APIオブジェクトを生成する
		self.STR_Mastodon.update({ inFulluser : CLS_Mastodon_Use(
			api_base_url = "https://" + wSTR_user['Domain'],
			client_id    = wRegFile,
			access_token = wUserFile ) })
###			flg_orginit=True ) })
		
		wIniStatus = self.STR_Mastodon[inFulluser].GetIniStatus()
		if wIniStatus['Result']!=True :
			wRes['Reason'] = "CLS_Regist: CreateMastodon: Create Mastodon object failuer: " + wIniStatus['Reason']
			return wRes		#mastodon error
		
		#############################
		# 通信テスト(トークンチェック)
		if self.STR_Mastodon[inFulluser].TokenCheck()!=True :
			wRes['Reason'] = "CLS_Regist: CreateMastodon: Mastodon Token is None (mastodon error): " + inFulluser
			return wRes		#ファイルがない
		
		wRes['Result'] = True
		return wRes


#####################################################
# mastodonレジスト
#####################################################
	@classmethod
	def sRegistMastodon( cls, inFulluser, inMail, inPass ):
		#############################
		# 応答形式の取得(mastodon形式)
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_Mastodon_Use.sGet_API_Resp()
		
		#############################
		# ドメイン抽出
		wSTR_user = CLS_UserData.sUserCheck( inFulluser )
		if wSTR_user['Result']!=True :
			wRes['Reason'] = wSTR_user['Reason']
			return wRes
		
		#############################
		# レジスト処理
		wGetPath = CLS_UserData.sGetUserPath( inFulluser )
		if wGetPath['Result']!=True :
			wRes['Reason'] = "CLS_Regist: sRegistMastodon: User path ng: " + wGetPath['Reason']
			return wRes
		
		wRes = CLS_Mastodon_Use.create_app(
			client_name  = gVal.STR_SystemInfo['Client_Name'],
			api_base_url = "https://" + wSTR_user['Domain'],
			to_file = wGetPath['Responce'] + gVal.STR_File['Reg_RegFile'] )
		
		if wRes['Result']!=True :
			return wRes
		
		wMastodon = CLS_Mastodon_Use(
			client_id = wGetPath['Responce'] + gVal.STR_File['Reg_RegFile'],
			api_base_url = "https://" + wSTR_user['Domain'] )
		
		wIniStatus = wMastodon.GetIniStatus()
		if wIniStatus['Result']!=True :
			wRes['Reason'] = "CLS_Regist: sRegistMastodon: Create Mastodon object failuer: " + wIniStatus['Reason']
			return wRes		#mastodon error
		
		wRes = wMastodon.log_in(
			username = inMail,
			password = inPass,
			to_file = wGetPath['Responce'] + gVal.STR_File['Reg_UserFile'] )
		
		return wRes		#応答形式(mastodon形式)



#####################################################
# 通信テスト
#####################################################
	def Test( self, inFulluser=None ):
		#############################
		# ユーザ名がない場合、名前を入力する
		if inFulluser==None :
			wStr = "通信テストをおこないます。" + '\n'
			wStr = wStr + "テストするユーザ名をドメインを含めて入力してください。 例= " + gVal.DEF_EXAMPLE_ACCOUNT
			CLS_OSIF.sPrn( wStr )
			inFulluser = CLS_OSIF.sInp( "User？=> " )
		
		#############################
		# 応答形式の取得(mastodon形式)
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_Mastodon_Use.sGet_API_Resp()
		
		#############################
		# ユーザ名の妥当性チェック
		wSTR_user = CLS_UserData.sUserCheck( inFulluser )
		if wSTR_user['Result']!=True :
			wRes['Reason'] = wSTR_user['Reason']
			return wRes
		elif wSTR_user['Registed']==False :
			wRes['Reason'] = "登録されていないユーザです。: " + inFulluser
			return wRes
		
		self.__prn( "通信テスト中..." )
		#############################
		# 通信テスト
		wRes = self.CreateMastodon( inFulluser )
		if wRes['Result']!=True :
			wStr = "mastodonとの通信テストに失敗しました" + '\n'
			wStr = wStr + "メールアドレス、パスワード、mastodonが運用中か確認してください。" + '\n'
			wStr = wStr + wRes['Reason'] + '\n'
			self.__prn( wStr )
			return wRes
		
		self.__prn( "テスト完了。通信は正常です。" + '\n' )
		return wRes



#####################################################
# ユーザ登録
#   コンソールからの操作
#####################################################
	def Regist( self, inFulluser=None ):
		#############################
		# ユーザ名がない場合、名前を入力する
		if inFulluser==None :
			wStr = gVal.STR_SystemInfo['Client_Name'] + " に新しいユーザ名を入力します。" + '\n'
			wStr = wStr + "登録するユーザ名をドメインを含めて入力してください。 例= " + gVal.DEF_EXAMPLE_ACCOUNT
			CLS_OSIF.sPrn( wStr )
			inFulluser = CLS_OSIF.sInp( "User？=> " )
		
		#############################
		# ユーザ名の妥当性チェック
		wSTR_user = CLS_UserData.sUserCheck( inFulluser )
		if wSTR_user['Result']!=True :
			CLS_OSIF.sPrn( wSTR_user['Reason'] )
			return False
		elif wSTR_user['Registed']==True :
			CLS_OSIF.sPrn( "既に登録されているユーザです。: " + inFulluser )
			return False
		
		#############################
		# メールアドレス、パスワードの入力
		wStr = '\n' + inFulluser + " を登録します。"
		wStr = wStr + "mastodonに登録したメールアドレスとパスワードを入力してください。"
		CLS_OSIF.sPrn( wStr )
		
		###入力受け付け
		wMail = CLS_OSIF.sInp( "Mailaddr: " )
		wPass = CLS_OSIF.sGpp( "Password: " )
		
		wStr = '\n' + "mastodon ID: " + inFulluser + '\n'
		wStr = wStr + "Mailaddress: " + wMail
		CLS_OSIF.sPrn( wStr )
		wRes = CLS_OSIF.sInp( "以上の内容で登録します(y/N): " )
		if wRes!="y" :
			CLS_OSIF.sPrn( "登録を中止しました" + '\n' )
			return False
		
		#############################
		# 入力チェック
		wRes = self.__registUser( inFulluser, wMail, wPass )
		if wRes['Result']!=True :
			CLS_OSIF.sPrn( wRes['Reason'] )
			return False
		
		CLS_OSIF.sPrn( '\n' + "通信テスト中..." )
		#############################
		# mastodonアクセス前 ping疎通チェック
		if CLS_OSIF.sPing( wSTR_user['Domain'] )!=True :
			CLS_OSIF.sPrn( "mastodonサーバ " + wSTR_user['Domain'] + " が応答しません。登録を中止します。" )
			return False
		
		CLS_OSIF.sPrn( "通信OK" + '\n' + "データ登録中......" )
		#############################
		# テンプレートデータのコピー(データ作成)
		wGetPath = CLS_UserData.sGetUserPath( inFulluser )
##		if wGetPath['Result']!=True :
##			CLS_OSIF.sPrn( "CLS_Regist: Regist: User path ng: " + wGetPath['Reason'] )
##			return False
		
		if CLS_File.sCopytree(
			gVal.STR_File['defUserdata_path'],
			wGetPath['Responce'] )!=True :
			###ありえない
			CLS_OSIF.sPrn( "CLS_Regist: Regist: defaultデータコピー失敗" )
			return False
		
		if CLS_File.sFolderExist( gVal.DEF_USERDATA_PATH, inFulluser )!=True :
			CLS_OSIF.sPrn( "CLS_Regist: Regist: ユーザデータの登録に失敗しました" )
			return False
		
		#############################
		# mastodonアカウントへの関連付け(本レジスト)
		wRes = self.sRegistMastodon( inFulluser, wMail, wPass )
		if wRes['Result']!=True :
			wStr = "mastodonへの関連付けに失敗しました" + '\n'
			wStr = wStr + "メールアドレス、パスワード、mastodonが運用中か確認してください。" + '\n'
			wStr = wStr + wRes['Reason']
			CLS_OSIF.sPrn( wStr )
			# データ削除
			CLS_File.sRmtree( wGetPath['Responce'] )
			return False
		
		CLS_OSIF.sPrn( "登録OK" + '\n' + "mastodon登録テスト中......" )
		#############################
		# 通信テスト
		wRes = self.CreateMastodon( inFulluser )
		if wRes['Result']!=True :
			wStr = "mastodonへの関連付けに失敗しました" + '\n'
			wStr = wStr + "メールアドレス、パスワード、mastodonが運用中か確認してください。" + '\n'
			wStr = wStr + wRes['Reason']
			CLS_OSIF.sPrn( wStr )
			# データ削除
			CLS_File.sRmtree( wGetPath['Responce'] )
			return False
		
		CLS_OSIF.sPrn( "mastodon登録OK" + '\n' )
		
		#############################
		# cron作成
		if inFulluser == gVal.STR_MasterConfig['MasterUser'] :
			wKind = gVal.DEF_CRON_MASTER
		else:
			wKind = gVal.DEF_CRON_SUB
		
		wCLS_botjib = CLS_Botjob()
		wPutRes = wCLS_botjib.Put( wKind, inFulluser )
		if wPutRes['Result']!=True :
			CLS_OSIF.sPrn( "CLS_Regist: Regist: cron create failed: " + wPutRes['Reason'] )
			return False
		
		CLS_OSIF.sPrn( '\n' + "cronを起動しました" )
		
		#############################
		# 完了
		CLS_OSIF.sPrn( inFulluser + " の登録が完了しました" + '\n' )
		return True



#####################################################
# ユーザ再登録
#####################################################
	def Update( self, inFulluser=None ):
		#############################
		# ユーザ名がない場合、名前を入力する
		if inFulluser==None :
			wStr = gVal.STR_SystemInfo['Client_Name'] + " に再登録するユーザ名を入力します。" + '\n'
			wStr = wStr + "再登録するユーザ名をドメインを含めて入力してください。 例= " + gVal.DEF_EXAMPLE_ACCOUNT
			CLS_OSIF.sPrn( wStr )
			inFulluser = CLS_OSIF.sInp( "User？=> " )
		
		#############################
		# ユーザ名の妥当性チェック
		wSTR_user = CLS_UserData.sUserCheck( inFulluser )
		if wSTR_user['Result']!=True :
			CLS_OSIF.sPrn( wSTR_user['Reason'] )
			return False
		elif wSTR_user['Registed']==False :
			CLS_OSIF.sPrn( "そのユーザは登録されていません。: " + inFulluser )
			return False
		
		#############################
		# メールアドレス、パスワードの入力
		wStr = '\n' + inFulluser + " を登録します。"
		wStr = wStr + "mastodonに登録したメールアドレスとパスワードを入力してください。"
		CLS_OSIF.sPrn( wStr )
		
		###入力受け付け
		wMail = CLS_OSIF.sInp( "Mailaddr: " )
		wPass = CLS_OSIF.sGpp( "Password: " )
		
		wStr = '\n' + "mastodon ID: " + inFulluser + '\n'
		wStr = wStr + "Mailaddress: " + wMail
		CLS_OSIF.sPrn( wStr )
		wRes = CLS_OSIF.sInp( "以上の内容で登録します(y/N): " )
		if wRes!="y" :
			CLS_OSIF.sPrn( "登録を中止しました" + '\n' )
			return False
		
		#############################
		# 入力チェック
		wRes = self.__registUser( inFulluser, wMail, wPass )
		if wRes['Result']!=True :
			CLS_OSIF.sPrn( wRes['Reason'] )
			return False
		
		CLS_OSIF.sPrn( '\n' + "通信テスト中..." )
		#############################
		# mastodonアクセス前 ping疎通チェック
		if CLS_OSIF.sPing( wSTR_user['Domain'] )!=True :
			CLS_OSIF.sPrn( "mastodonサーバ " + wSTR_user['Domain'] + " が応答しません。登録を中止します。" )
			return False
		
		CLS_OSIF.sPrn( "通信OK" + '\n' + "データ登録中......" )
		#############################
		# レジストファイルの作りなおし
		wGetPath = CLS_UserData.sGetUserPath( inFulluser )
		if wGetPath['Result']!=True :
			CLS_OSIF.sPrn( "CLS_Regist: Update: User path ng: " + wGetPath['Reason'] )
			return False
		
		if CLS_File.sClrFile( wGetPath['Responce'] + gVal.STR_File['Reg_RegFile'] )!=True :
			CLS_OSIF.sPrn( "CLS_Regist: Update: Reg File is not found: " + wGetPath['Responce'] + gVal.STR_File['Reg_RegFile'] )
			return False
		
		if CLS_File.sClrFile( wGetPath['Responce'] + gVal.STR_File['Reg_UserFile'] )!=True :
			CLS_OSIF.sPrn( "CLS_Regist: Update: User File is not found: " + wGetPath['Responce'] + gVal.STR_File['Reg_UserFile'] )
			return False
		
		#############################
		# mastodonアカウントへの関連付け(本レジスト)
		wRes = CLS_Regist.sRegistMastodon( inFulluser, wMail, wPass )
		if wRes['Result']!=True :
			wStr = "mastodonへの関連付けに失敗しました" + '\n'
			wStr = wStr + "メールアドレス、パスワード、mastodonが運用中か確認してください。" + '\n'
			wStr = wStr + wRes['Reason']
			CLS_OSIF.sPrn( wStr )
			# データ削除
			CLS_File.sRmtree( wGetPath['Responce'] )
			return False
		
		CLS_OSIF.sPrn( "登録OK" + '\n' + "mastodon登録テスト中......" )
		#############################
		# 通信テスト
		wRes = self.CreateMastodon( inFulluser )
		if wRes['Result']!=True :
			wStr = "mastodonへの関連付けに失敗しました" + '\n'
			wStr = wStr + "メールアドレス、パスワード、mastodonが運用中か確認してください。" + '\n'
			wStr = wStr + wRes['Reason']
			CLS_OSIF.sPrn( wStr )
			# データ削除
			CLS_File.sRmtree( wGetPath['Responce'] )
			return False
		
		CLS_OSIF.sPrn( "mastodon登録OK" + '\n' )
		
		#############################
		# 完了
		CLS_OSIF.sPrn( inFulluser + " の再登録が完了しました" + '\n' )
		return True



#####################################################
# ユーザ削除
#####################################################
	def Delete( self, inFulluser=None ):
		#############################
		# 1件しかない場合か、MasterUserは削除できない
		#   ※1件しかない場合はそれがMasterUserなので
		wList = CLS_UserData.sGetUserList()
		if len(wList)==1 :
			CLS_OSIF.sPrn( "残り1件しかないので、そのユーザは削除できません。" )
			return False
		
		if gVal.STR_MasterConfig['MasterUser']==inFulluser :
			CLS_OSIF.sPrn( "MasterUserは削除できません。" )
			return False
		
		#############################
		# ユーザ名がない場合、名前を入力する
		if inFulluser==None :
			wStr = gVal.STR_SystemInfo['Client_Name'] + " から削除するユーザ名を入力します。" + '\n'
			wStr = wStr + "削除するユーザ名をドメインを含めて入力してください。 例= " + gVal.DEF_EXAMPLE_ACCOUNT
			CLS_OSIF.sPrn( wStr )
			inFulluser = CLS_OSIF.sInp( "User？=> " )
		
		#############################
		# ユーザ名の妥当性チェック
		wSTR_user = CLS_UserData.sUserCheck( inFulluser )
		if wSTR_user['Result']!=True :
			CLS_OSIF.sPrn( wSTR_user['Reason'] )
			return False
		elif wSTR_user['Registed']==False :
			CLS_OSIF.sPrn( "そのユーザは登録されていません。: " + inFulluser )
			return False
		
		#############################
		# 削除の確認
		CLS_OSIF.sPrn( "ユーザデータの削除をおこないます。データの復旧はできません。" )
		wRes = CLS_OSIF.sInp("本当に削除してよろしいでしょうか(y/N)=> " )
		if wRes!="y" :
			CLS_OSIF.sPrn( "削除を中止しました" + '\n' )
			return False
		
		CLS_OSIF.sPrn( '\n' + "データ削除中......(2分かかります)" )
		#############################
		# cron削除
		wCLS_botjib = CLS_Botjob()
		wDelRes = wCLS_botjib.Del( gVal.DEF_CRON_SUB, inFulluser )
		if wDelRes['Result']==True :
			#############################
			# 実行中のcronが処理が終わるまで待機
			CLS_OSIF.sSleep( 120 )
		
		#############################
		# データ削除
		wGetPath = CLS_UserData.sGetUserPath( inFulluser )
		if wGetPath['Result']!=True :
			CLS_OSIF.sPrn( "CLS_Regist: Delete: User path ng: " + wGetPath['Reason'] )
			return False
		
		if CLS_File.sRmtree( wGetPath['Responce'] )!=True :
			CLS_OSIF.sPrn( "CLS_Regist: Delete: Data is not found: " + wGetPath['Responce'] )
			return False
		
		#############################
		# 完了
		wStr = inFulluser + " のデータは全て削除されました" + '\n'
		wStr = wStr + "mastodon側の認証済みアプリ情報は手で消してください。" + '\n'
		CLS_OSIF.sPrn( wStr )
		return True



#####################################################
# ユーザ登録内容の妥当性チェック
#####################################################
	def __registUser( self, inFulluser, inMail, inPass ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# ユーザ名の妥当性チェック(いちお再チェック)
		wSTR_user = CLS_UserData.sUserCheck( inFulluser )
		if wSTR_user['Result']!=True :
			wRes['Reason'] = wSTR_user['Reason']
			return wRes
		
		#############################
		# 入力間違いのチェック
		wFlg = True
		if inFulluser==inMail :
			wFlg = False
		elif inFulluser==inPass :
			wFlg = False
		elif inMail==inPass :
			wFlg = False
		
		if wFlg!=True :
			wRes['Reason'] = "ユーザ名、メールアドレス、パスワードの入力が誤ってます。(重複検出)"
			return wRes
		
		wRes['Result'] = True
		return wRes



#####################################################
# 画面出力
#   コンソール時にのみ画面出力する
#####################################################
	def __prn( self, inMsg ):
		if gVal.FLG_Console_Mode==False :
			return
		
		CLS_OSIF.sPrn( inMsg )
		return



