#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ユーザ登録
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/2/24
#####################################################
from mastodon_use import CLS_Mastodon_Use
from getpass import getpass
import global_val
#####################################################
class CLS_Regist:
	

#####################################################
# Init
#####################################################
	def __init__(self):
		return



#####################################################
# 一覧表示
#####################################################
	def cViewList(self):
		
		global_val.gCLS_Init.cPrint( "--------------------" )
		global_val.gCLS_Init.cPrint( " 登録ユーザ一覧" )
		global_val.gCLS_Init.cPrint( "--------------------" )
		
		#############################
		# データフォルダの一覧(トップだけ)取得
		wList = global_val.gCLS_File.cGetFolderList( global_val.gUserData_Path )
		
		if len(wList)==0 :
			global_val.gCLS_Init.cPrint( "ユーザ登録がありません" )
			return
		
		#############################
		# 表示
		for f in wList :
			global_val.gCLS_Init.cPrint( f )
		
		#見やすくするため意味ないけど
		global_val.gCLS_Init.cPrint( "" )
		return



#####################################################
# ユーザ登録
#####################################################
	def cRegist( self, fulluser ):
		
		#############################
		# ユーザ名の妥当性チェック
		wSTR_user = self.pUserCheck( fulluser )
		if wSTR_user['Result']!=True :
			return
		
		#############################
		# 重複チェック
		if global_val.gCLS_File.cFolderExist( global_val.gUserData_Path, fulluser )==True :
			global_val.gCLS_Init.cPrint( "既に登録されているユーザです" )
			return
		
		#############################
		# メールアドレス、パスワードの入力
		global_val.gCLS_Init.cPrint( '\n' + fulluser + " を登録します。" )
		global_val.gCLS_Init.cPrint( "mastodonに登録したメールアドレスとパスワードを入力してください。" )
		
		###入力受け付け
		wMail = input("Mailaddr: ").strip()
		wPass = getpass("Password: ").strip()	#pass表示されない
		
		global_val.gCLS_Init.cPrint( '\n' + "mastodon ID: " + fulluser )
		global_val.gCLS_Init.cPrint( "Mailaddress: " + wMail )
		wRes = input("以上の内容で登録します(y/N): ").strip()
		if wRes!="y" :
			global_val.gCLS_Init.cPrint( "登録を中止しました" + '\n' )
			return
		
		#############################
		# mastodonアクセス前 ping疎通チェック
		if global_val.gCLS_Init.cPing( wSTR_user['Domain'] )!=True :
			global_val.gCLS_Init.cPrint( "mastodonサーバ " + wSTR_user['Domain'] + " が応答しません。登録を中止します" )
			return
		
		global_val.gCLS_Init.cPrint( '\n' + "データ登録中......" )
		#############################
		# テンプレートデータのコピー(データ作成)
		if global_val.gCLS_File.cCopyFolder(
			global_val.gSTR_File['defUserdata'],
			global_val.gUserData_Path + fulluser )!=True :
			###ありえない
			global_val.gCLS_Init.cPrint( "CLS_Regist: cViewList: defaultデータコピー失敗" )
			return
		
		if global_val.gCLS_File.cFolderExist( global_val.gUserData_Path, fulluser )!=True :
			global_val.gCLS_Init.cPrint( "CLS_Regist: cViewList: ユーザデータの登録に失敗しました" )
			return
		
		wCHR_ApiBaseURL = "https://" + wSTR_user['Domain']
		#############################
		# mastodonアカウントへの関連付け(本レジスト)
		CLS_Mastodon_Use.create_app(
			client_name  = global_val.gSTR_SystemInfo['Client_Name'],
			api_base_url = wCHR_ApiBaseURL,
			to_file = global_val.gUserData_Path + fulluser + global_val.gSTR_File['RegFile'] )
		
		mastodon = CLS_Mastodon_Use(
			client_id = global_val.gUserData_Path + fulluser + global_val.gSTR_File['RegFile'],
			api_base_url = wCHR_ApiBaseURL )
		
		mastodon.log_in(
			username = wMail,
			password = wPass,
			to_file = global_val.gUserData_Path + fulluser + global_val.gSTR_File['UserFile'] )
		
		#############################
		# レジストできたかテスト
		wRes = global_val.gCLS_Init.cCreateMastodon(
				wCHR_ApiBaseURL,
				global_val.gUserData_Path + fulluser + global_val.gSTR_File['RegFile'],
				global_val.gUserData_Path + fulluser + global_val.gSTR_File['UserFile'] )
		if wRes!=True :
			global_val.gCLS_Init.cPrint( "mastodonへの関連付けに失敗しました" )
			global_val.gCLS_Init.cPrint( "メールアドレス、パスワード、mastodonが運用中か確認してください。" + '\n' )
			# データ削除
			global_val.gCLS_File.cDelFolder( global_val.gUserData_Path + fulluser )
			return
		
		#############################
		# 完了
		global_val.gCLS_Init.cPrint( fulluser + " の登録が完了しました" + '\n' )
		return



#####################################################
# ユーザ再登録
#####################################################
	def cUpdate( self, fulluser ):
		
		#############################
		# ユーザ名の妥当性チェック
		wSTR_user = self.pUserCheck( fulluser )
		if wSTR_user['Result']!=True :
			return
		
		#############################
		# 重複チェック
		if global_val.gCLS_File.cFolderExist( global_val.gUserData_Path, fulluser )!=True :
			global_val.gCLS_Init.cPrint( "そのユーザは登録されていません" )
			return
		
		#############################
		# メールアドレス、パスワードの入力
		global_val.gCLS_Init.cPrint( '\n' + fulluser + " を再登録します。" )
		global_val.gCLS_Init.cPrint( "mastodonに登録したメールアドレスとパスワードを入力してください。" )
		
		###入力受け付け
		wMail = input("Mailaddr: ").strip()
		wPass = getpass("Password: ").strip()	#pass表示されない
		
		global_val.gCLS_Init.cPrint( '\n' + "mastodon ID: " + fulluser )
		global_val.gCLS_Init.cPrint( "Mailaddress: " + wMail )
		wRes = input("以上の内容で登録します(y/N): ").strip()
		if wRes!="y" :
			global_val.gCLS_Init.cPrint( "登録を中止しました" + '\n' )
			return
		
		#############################
		# mastodonアクセス前 ping疎通チェック
		if global_val.gCLS_Init.cPing( wSTR_user['Domain'] )!=True :
			global_val.gCLS_Init.cPrint( "mastodonサーバ " + wSTR_user['Domain'] + " が応答しません。登録を中止します" )
			return
		
		global_val.gCLS_Init.cPrint( '\n' + "データ登録中......" )
		
		#############################
		# レジストファイルの作りなおし
		if global_val.gCLS_File.cClearFile( global_val.gUserData_Path + fulluser + global_val.gSTR_File['RegFile'] )!=True :
			global_val.gCLS_Init.cPrint( "CLS_Regist: cUpdate: File not found: " + global_val.gUserData_Path + fulluser + global_val.gSTR_File['RegFile'] )
			return
		
		if global_val.gCLS_File.cClearFile( global_val.gUserData_Path + fulluser + global_val.gSTR_File['UserFile'] )!=True :
			global_val.gCLS_Init.cPrint( "CLS_Regist: cUpdate: File not found: " + global_val.gUserData_Path + fulluser + global_val.gSTR_File['UserFile'] )
			return
		
		wCHR_ApiBaseURL = "https://" + wSTR_user['Domain']
		#############################
		# mastodonアカウントへの関連付け(本レジスト)
		CLS_Mastodon_Use.create_app(
			client_name  = global_val.gSTR_SystemInfo['Client_Name'],
			api_base_url = wCHR_ApiBaseURL,
			to_file = global_val.gUserData_Path + fulluser + global_val.gSTR_File['RegFile'] )
		
		mastodon = CLS_Mastodon_Use(
			client_id = global_val.gUserData_Path + fulluser + global_val.gSTR_File['RegFile'],
			api_base_url = wCHR_ApiBaseURL )
		
		mastodon.log_in(
			username = wMail,
			password = wPass,
			to_file = global_val.gUserData_Path + fulluser + global_val.gSTR_File['UserFile'] )
		
		#############################
		# レジストできたかテスト
		wRes = global_val.gCLS_Init.cCreateMastodon(
				wCHR_ApiBaseURL,
				global_val.gUserData_Path + fulluser + global_val.gSTR_File['RegFile'],
				global_val.gUserData_Path + fulluser + global_val.gSTR_File['UserFile'] )
		if wRes!=True :
			global_val.gCLS_Init.cPrint( "mastodonへの関連付けに失敗しました" )
			global_val.gCLS_Init.cPrint( "メールアドレス、パスワード、mastodonが運用中か確認してください。" + '\n' )
			return
		
		#############################
		# 完了
		global_val.gCLS_Init.cPrint( fulluser + " の再登録が完了しました" + '\n' )
		return



#####################################################
# ユーザ削除
#####################################################
	def cDelete( self, fulluser ):
		
		#############################
		# ユーザ名の妥当性チェック
		wSTR_user = self.pUserCheck( fulluser )
		if wSTR_user['Result']!=True :
			return
		
		#############################
		# 重複チェック
		if global_val.gCLS_File.cFolderExist( global_val.gUserData_Path, fulluser )!=True :
			global_val.gCLS_Init.cPrint( "そのユーザは登録されていません" )
			return
		
		#############################
		# 削除の確認
		global_val.gCLS_Init.cPrint( "ユーザデータの削除をおこないます。データの復旧はできません。" )
		wRes = input("本当に削除してよろしいでしょうか(y/N): ").strip()
		if wRes!="y" :
			global_val.gCLS_Init.cPrint( "削除を中止しました" + '\n' )
			return
		
		global_val.gCLS_Init.cPrint( '\n' + "データ削除中......" )
		#############################
		# データ削除
		if global_val.gCLS_File.cDelFolder( global_val.gUserData_Path + fulluser )!=True :
			global_val.gCLS_Init.cPrint( "CLS_Regist: cDelete: Data not found: " + global_val.gUserData_Path + fulluser )
			return
		
		#############################
		# 完了
		global_val.gCLS_Init.cPrint( fulluser + " のデータは全て削除されました" + '\n' + "mastodon側の認証済みアプリ情報は手で消してください。" )
		return










#####################################################
# ユーザ名の妥当性チェック
#####################################################
	def pUserCheck( self, fulluser ):
		
		wRes = {
			"Result"	: False,
			"User"		: "",
			"Domain"	: ""
		}
		
		wUser = fulluser.split("@")
		if len(wUser)!=2 :
			global_val.gCLS_Init.cPrint( "ドメインを含む形で入力してください: 例: user@domain" )
			return wRes
		
		wRes['User']   = wUser[0]
		wRes['Domain'] = wUser[1]
		wRes['Result'] = True
		return wRes



