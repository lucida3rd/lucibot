#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：ユーザ登録
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/2/27
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
# mastodonクラス生成
#####################################################
	def cCreateMastodon( self, base_url, reg_file, user_file ):
		#############################
		# ping疎通チェック
		wDomain = base_url.split("//")
		if global_val.gCLS_Init.cPing(wDomain[1])!=True :
			return False	#失敗
		
		#############################
		# レジストファイルの存在チェック
		if global_val.gCLS_File.cExist( reg_file )!=True :
			global_val.gCLS_Init.cPrint( "CLS_Regist: cCreateMastodon: File not is found: " + reg_file )
			return False	#ファイルがない
		
		if global_val.gCLS_File.cExist( user_file )!=True :
			global_val.gCLS_Init.cPrint( "CLS_Regist: cCreateMastodon: File not is found: " + user_file )
			return False	#ファイルがない
		
		#############################
		# mastodon APIオブジェクトを生成する
		global_val.gCLS_Mastodon = CLS_Mastodon_Use(
			api_base_url = base_url,
			client_id    = reg_file,
			access_token = user_file,
			flg_orginit=True )
		
		#############################
		# 通信テスト
		if global_val.gCLS_Mastodon.cTest()!=True :
			return False	#失敗
		
		return True


#####################################################
# mastodonレジスト
#####################################################
	def cRegistMastodon( self, in_Base_url, in_Fulluser, in_Mail, in_Pass ):
		CLS_Mastodon_Use.create_app(
			client_name  = global_val.gSTR_SystemInfo['Client_Name'],
			api_base_url = in_Base_url,
			to_file = global_val.gUserData_Path + in_Fulluser + global_val.gSTR_File['RegFile'] )
		
		mastodon = CLS_Mastodon_Use(
			client_id = global_val.gUserData_Path + in_Fulluser + global_val.gSTR_File['RegFile'],
			api_base_url = in_Base_url )
		
		wToken = mastodon.log_in(
			username = in_Mail,
			password = in_Pass,
			to_file = global_val.gUserData_Path + in_Fulluser + global_val.gSTR_File['UserFile'] )
		
		#############################
		# mastodonが生成されたか確認
		if wToken=="" :
			return False	#失敗
		
		return True



#####################################################
# 通信テスト
#####################################################
	def cTest( self, fulluser ):
		
		#############################
		# ユーザ名の妥当性チェック
		wSTR_user = self.cUserCheck( fulluser )
		if wSTR_user['Result']!=True :
			global_val.gCLS_Init.cPrint( "ユーザ名が誤ってます。" )
			return False
		
		#############################
		# 重複チェック
		if global_val.gCLS_File.cFolderExist( global_val.gUserData_Path, fulluser )!=True :
			global_val.gCLS_Init.cPrint( "登録されていないユーザです。" )
			return False
		
		global_val.gCLS_Init.cPrint( "通信テスト中..." )
		wCHR_ApiBaseURL = "https://" + wSTR_user['Domain']
		#############################
		# 通信テスト
		wRes = self.cCreateMastodon(
				wCHR_ApiBaseURL,
				global_val.gUserData_Path + fulluser + global_val.gSTR_File['RegFile'],
				global_val.gUserData_Path + fulluser + global_val.gSTR_File['UserFile'] )
		
		if wRes!=True :
			wStr = "mastodonとの通信テストに失敗しました" + '\n'
			wStr = wStr + "メールアドレス、パスワード、mastodonが運用中か確認してください。" + '\n'
			global_val.gCLS_Init.cPrint( wStr )
			return False
		
		#############################
		# 通信テスト
		global_val.gCLS_Init.cPrint( "テスト完了。通信は正常です。" + '\n' )
		return True



#####################################################
# ユーザ一覧取得
#####################################################
	def cGetUserList(self):
		wList = global_val.gCLS_File.cGetFolderList( global_val.gUserData_Path )
		
		#############################
		# masterConfigを抜く
		wList.remove( global_val.gCHR_masterConfig )
		
		return wList



#####################################################
# 同報配信ユーザ一覧の作成
#####################################################
	def cGetMulticastUserList(self):
		
		wMulticastList = []
		
		#############################
		# データフォルダの一覧(トップだけ)取得
		wList = self.cGetUserList()
		
		if len(wList)==0 :
			###イレギュラー...
			global_val.gCLS_Init.cPrint( "CLS_Regist: cGetMulticastUserList: No user registration" )
			return wMulticastList
		
		###同報配信元には配信しないので抜く
		wList.remove( global_val.gSTR_masterConfig['MasterUser'] )
		
		#############################
		# 登録ユーザのconfigから Multicast値 を読み込む
		for ikey in wList :
			wRes = global_val.gCLS_Config.cGetMulticast( global_val.gUserData_Path + ikey + global_val.gSTR_File['Config_file'] )
			if wRes['Result']==False :
				continue
			
			if wRes['Flg']=="on" :
				wMulticastList.append( ikey )
		
		return wMulticastList



#####################################################
# 一覧表示
#####################################################
	def cViewList(self):
		
		###画面クリアして一覧表示する
		global_val.gCLS_Init.cDispClear()
		wStr = "--------------------" + '\n'
		wStr = wStr + " 登録ユーザ一覧" + '\n'
		wStr = wStr + "--------------------"
		global_val.gCLS_Init.cPrint( wStr )
		
		#############################
		# データフォルダの一覧(トップだけ)取得
		wList = self.cGetUserList()
		if len(wList)==0 :
			global_val.gCLS_Init.cPrint( "ユーザ登録がありません" )
			return
		
		#############################
		# 同報配信設定ユーザ一覧の取得
		wMulticastList = self.cGetMulticastUserList()
		
		#############################
		# 表示
		wStr = ""
		for f in wList :
			#############################
			# MasterUserフラグ
			if global_val.gSTR_masterConfig['MasterUser']==f :
				wStr = wStr + "*"
			else:
				wStr = wStr + " "
			
			#############################
			# 同報配信ユーザフラグ
			if f in wMulticastList :
				wStr = wStr + "m"
			else:
				wStr = wStr + " "
			
			#############################
			# ユーザ名
			wStr = wStr + " " + f + '\n'
		
		global_val.gCLS_Init.cPrint( wStr )
		return



#####################################################
# ユーザ登録
#####################################################
	def cRegist( self, fulluser ):
		
		#############################
		# ユーザ名の妥当性チェック
		wSTR_user = self.cUserCheck( fulluser )
		if wSTR_user['Result']!=True :
			return False
		
		#############################
		# 重複チェック
		if global_val.gCLS_File.cFolderExist( global_val.gUserData_Path, fulluser )==True :
			global_val.gCLS_Init.cPrint( "既に登録されているユーザです" )
			return False
		
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
			return False
		
		#############################
		# mastodonアクセス前 ping疎通チェック
		if global_val.gCLS_Init.cPing( wSTR_user['Domain'] )!=True :
			global_val.gCLS_Init.cPrint( "mastodonサーバ " + wSTR_user['Domain'] + " が応答しません。登録を中止します" )
			return False
		
		global_val.gCLS_Init.cPrint( '\n' + "データ登録中......" )
		#############################
		# テンプレートデータのコピー(データ作成)
		if global_val.gCLS_File.cCopyFolder(
			global_val.gSTR_File['defUserdata'],
			global_val.gUserData_Path + fulluser )!=True :
			###ありえない
			global_val.gCLS_Init.cPrint( "CLS_Regist: cViewList: defaultデータコピー失敗" )
			return False
		
		if global_val.gCLS_File.cFolderExist( global_val.gUserData_Path, fulluser )!=True :
			global_val.gCLS_Init.cPrint( "CLS_Regist: cViewList: ユーザデータの登録に失敗しました" )
			return False
		
		wCHR_ApiBaseURL = "https://" + wSTR_user['Domain']
		#############################
		# mastodonアカウントへの関連付け(本レジスト)
		wRes = self.cRegistMastodon(
				wCHR_ApiBaseURL, fulluser, wMail, wPass )
		if wRes!=True :
			wStr = "mastodonへの関連付けに失敗しました" + '\n'
			wStr = wStr + "メールアドレス、パスワード、mastodonが運用中か確認してください。"
			global_val.gCLS_Init.cPrint( wStr )
			# データ削除
			global_val.gCLS_File.cDelFolder( global_val.gUserData_Path + fulluser )
			return False
		
		#############################
		# 通信テスト
		wRes = self.cCreateMastodon(
				wCHR_ApiBaseURL,
				global_val.gUserData_Path + fulluser + global_val.gSTR_File['RegFile'],
				global_val.gUserData_Path + fulluser + global_val.gSTR_File['UserFile'] )
		
		if wRes!=True :
			wStr = "mastodonとの通信テストに失敗しました" + '\n'
			wStr = wStr + "メールアドレス、パスワード、mastodonが運用中か確認してください。"
			global_val.gCLS_Init.cPrint( wStr )
			# データ削除
			global_val.gCLS_File.cDelFolder( global_val.gUserData_Path + fulluser )
			return False
		
		#############################
		# 1件目だったらMasterUserとして登録する
		# master環境情報にも反映する
		wList = global_val.gCLS_Regist.cGetUserList()
		if len(wList)==1 :
			global_val.gCLS_Config.cCnfMasterUser( fulluser )
			global_val.gCLS_Config.cSetMasterConfig()
		
		#############################
		# 完了
		global_val.gCLS_Init.cPrint( fulluser + " の登録が完了しました" + '\n' )
		return True



#####################################################
# ユーザ再登録
#####################################################
	def cUpdate( self, fulluser ):
		
		#############################
		# ユーザ名の妥当性チェック
		wSTR_user = self.cUserCheck( fulluser )
		if wSTR_user['Result']!=True :
			return False
		
		#############################
		# 重複チェック
		if global_val.gCLS_File.cFolderExist( global_val.gUserData_Path, fulluser )!=True :
			global_val.gCLS_Init.cPrint( "そのユーザは登録されていません" )
			return False
		
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
			return False
		
		#############################
		# mastodonアクセス前 ping疎通チェック
		if global_val.gCLS_Init.cPing( wSTR_user['Domain'] )!=True :
			global_val.gCLS_Init.cPrint( "mastodonサーバ " + wSTR_user['Domain'] + " が応答しません。登録を中止します" )
			return False
		
		global_val.gCLS_Init.cPrint( '\n' + "データ登録中......" )
		
		#############################
		# レジストファイルの作りなおし
		if global_val.gCLS_File.cClearFile( global_val.gUserData_Path + fulluser + global_val.gSTR_File['RegFile'] )!=True :
			global_val.gCLS_Init.cPrint( "CLS_Regist: cUpdate: File not found: " + global_val.gUserData_Path + fulluser + global_val.gSTR_File['RegFile'] )
			return False
		
		if global_val.gCLS_File.cClearFile( global_val.gUserData_Path + fulluser + global_val.gSTR_File['UserFile'] )!=True :
			global_val.gCLS_Init.cPrint( "CLS_Regist: cUpdate: File not found: " + global_val.gUserData_Path + fulluser + global_val.gSTR_File['UserFile'] )
			return False
		
		wCHR_ApiBaseURL = "https://" + wSTR_user['Domain']
		#############################
		# mastodonアカウントへの関連付け(本レジスト)
		wRes = self.cRegistMastodon(
				wCHR_ApiBaseURL, fulluser, wMail, wPass )
		if wRes!=True :
			wStr = "mastodonへの関連付けに失敗しました" + '\n'
			wStr = wStr + "メールアドレス、パスワード、mastodonが運用中か確認してください。"
			global_val.gCLS_Init.cPrint( wStr )
			# データ削除
			global_val.gCLS_File.cDelFolder( global_val.gUserData_Path + fulluser )
			return False
		
		#############################
		# 通信テスト
		wRes = self.cCreateMastodon(
				wCHR_ApiBaseURL,
				global_val.gUserData_Path + fulluser + global_val.gSTR_File['RegFile'],
				global_val.gUserData_Path + fulluser + global_val.gSTR_File['UserFile'] )
		
		if wRes!=True :
			wStr = "mastodonとの通信テストに失敗しました" + '\n'
			wStr = wStr + "メールアドレス、パスワード、mastodonが運用中か確認してください。"
			global_val.gCLS_Init.cPrint( wStr )
			# データ削除
			global_val.gCLS_File.cDelFolder( global_val.gUserData_Path + fulluser )
			return False
		
		#############################
		# 完了
		global_val.gCLS_Init.cPrint( fulluser + " の再登録が完了しました" + '\n' )
		return True



#####################################################
# ユーザ削除
#####################################################
	def cDelete( self, fulluser ):
		
		#############################
		# 1件しかない場合か、MasterUserは削除できない
		#   ※1件しかない場合はそれがMasterUserなので
		wList = global_val.gCLS_Regist.cGetUserList()
		if len(wList)==1 :
			global_val.gCLS_Init.cPrint( "残り1件しかないので、そのユーザは削除できません。" )
			return False
		
		if global_val.gSTR_masterConfig['MasterUser']==fulluser :
			global_val.gCLS_Init.cPrint( "MasterUserは削除できません。" )
			return False
		
		#############################
		# ユーザ名の妥当性チェック
		wSTR_user = self.cUserCheck( fulluser )
		if wSTR_user['Result']!=True :
			return False
		
		#############################
		# 重複チェック
		if global_val.gCLS_File.cFolderExist( global_val.gUserData_Path, fulluser )!=True :
			global_val.gCLS_Init.cPrint( "そのユーザは登録されていません" )
			return False
		
		#############################
		# 削除の確認
		global_val.gCLS_Init.cPrint( "ユーザデータの削除をおこないます。データの復旧はできません。" )
		wRes = input("本当に削除してよろしいでしょうか(y/N): ").strip()
		if wRes!="y" :
			global_val.gCLS_Init.cPrint( "削除を中止しました" + '\n' )
			return False
		
		global_val.gCLS_Init.cPrint( '\n' + "データ削除中......" )
		#############################
		# データ削除
		if global_val.gCLS_File.cDelFolder( global_val.gUserData_Path + fulluser )!=True :
			global_val.gCLS_Init.cPrint( "CLS_Regist: cDelete: Data not found: " + global_val.gUserData_Path + fulluser )
			return False
		
		#############################
		# 完了
		global_val.gCLS_Init.cPrint( fulluser + " のデータは全て削除されました" + '\n' + "mastodon側の認証済みアプリ情報は手で消してください。" )
		return True



#####################################################
# ユーザ名の妥当性チェック
#####################################################
	def cUserCheck( self, fulluser ):
		
		wRes = {
			"Result"	: False,
			"User"		: "",
			"Domain"	: ""
		}
		
		wUser = fulluser.split("@")
		if len(wUser)!=2 :
			global_val.gCLS_Init.cPrint( "ドメインを含めて入力してください: 例= " + global_val.gCHR_ExampleAccount )
			return wRes
		
		wRes['User']   = wUser[0]
		wRes['Domain'] = wUser[1]
		wRes['Result'] = True
		return wRes



