#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：環境設定処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/2/27
#####################################################
import codecs
import global_val
#####################################################
class CLS_Config:
	
	FLG_Init_Master = False		#master環境情報OK
	FLG_Init_Config = False		#環境情報OK
	
	STR_cnfMasterConf = [
		'MasterUser',
		'AdminUser',
		'Twitter',
		'Traffic',
		'LookHard',
		'WordStudy',
		'mRun',
		'mMainte'
	]

#####################################################
# Init
#####################################################
	def __init__(self):
		return



#####################################################
# master環境情報の読み込み
#####################################################
	def cGetMasterConfig(self):
		#############################
		# ファイルの存在チェック
		if global_val.gCLS_File.cExist( global_val.gSTR_File['masterConfig_file'] )!=True :
			return False	#ない
		
		#############################
		# 読み込み
		for line in open( global_val.gSTR_File['masterConfig_file'], 'r'):
			#############################
			# 分解+要素数の確認
			line = line.strip()
			get_line = line.split("=")
			if len(get_line) != 2 :
				continue
			
			#############################
			# キーがあるか確認
			if get_line[0] not in global_val.gSTR_masterConfig :
				continue
			
			#############################
			# 更新する
			global_val.gSTR_masterConfig[get_line[0]] = get_line[1]
		
		#############################
		# 文字→数値へ変換
		global_val.gSTR_masterConfig["studyNum"] = int( global_val.gSTR_masterConfig["studyNum"] )
		global_val.gSTR_masterConfig["studyMax"] = int( global_val.gSTR_masterConfig["studyMax"] )
		global_val.gSTR_masterConfig["studyDay"] = int( global_val.gSTR_masterConfig["studyDay"] )
		
		FLG_Init_Master = True
		return True



#####################################################
# master環境情報の書き込み
#####################################################
	def cSetMasterConfig(self):
		#############################
		# ファイルの存在チェック
		if global_val.gCLS_File.cExist( global_val.gSTR_File['masterConfig_file'] )!=True :
			return False	#ない
		
		#############################
		# ファイルオープン
		file = codecs.open( global_val.gSTR_File['masterConfig_file'], 'w', 'utf-8')
		file.close()
		file = codecs.open( global_val.gSTR_File['masterConfig_file'], 'w', 'utf-8')
		
		#############################
		# 追加データを作成
		setline = []
		keylist = global_val.gSTR_masterConfig.keys()
		for ikey in keylist :
			line = ikey + "=" + str(global_val.gSTR_masterConfig[ikey]) + '\n'
			setline.append(line)
		
		#############################
		# 書き込んで閉じる
		file.writelines( setline )
		file.close()
		return True



#####################################################
# master環境情報セットアップ
#####################################################
	def cMasterSetup(self):
		#############################
		# フォルダの存在チェック
		if global_val.gCLS_File.cExist( global_val.gSTR_File['masterConfig'] )==True :
			return False	#既にある
		
		global_val.gCLS_Init.cPrint( '\n' + "master環境情報が存在しないため、セットアップを行います。" )
		global_val.gCLS_Init.cPrint( "master環境のテンプレートをコピーします....." )
		#############################
		# テンプレートデータのコピー(データ作成)
		if global_val.gCLS_File.cCopyFolder(
			global_val.gSTR_File['defMasterdata'],
			global_val.gSTR_File['masterConfig'] )!=True :
			###ありえない
			global_val.gCLS_Init.cPrint( "CLS_Config: cSetMasterSetup: defaultデータコピー失敗" )
			return False
		
		#############################
		# フォルダの存在チェック
		if global_val.gCLS_File.cExist( global_val.gSTR_File['masterConfig'] )!=True :
			global_val.gCLS_Init.cPrint( "CLS_Config: cSetMasterSetup: データコピー失敗" )
			return False	#失敗
		
		#############################
		# コピー完了
		wRes = input("master環境情報のコピーが完了しました。リターンキーでセットアップをおこないます。[RT]")
		
		#############################
		# master環境情報の変更
		self.cCnfMasterConfig()
		global_val.gSTR_masterConfig['mRun'] = "on"
		global_val.gSTR_masterConfig['mMainte'] = "off"
		
		#############################
		# AdminUserの変更
		self.cCnfAdminUser()
		
		#############################
		# ユーザ登録=0の時、登録させる
		wList = global_val.gCLS_Regist.cGetUserList()
		if len(wList)==0 :
			wFLG_regist = False
			while True:
				global_val.gCLS_Init.cPrint( "ユーザの登録をおこないます。botで使うユーザ名をドメインを含めて入力してください。: 例= " + global_val.gCHR_ExampleAccount )
				wMasterUser = input("MasterUser？ => ")
				wRes = global_val.gCLS_Regist.cRegist( wMasterUser )
				if wRes==True :
					###登録できたので次へ
					break
				else :
					###登録できないと、登録できるまで継続したい
					global_val.gCLS_Init.cPrint( "ユーザの登録がないとbotが動作できません。" )
					wRes = input("登録を中止しますか？(y)=> ")
					if wRes=='y' :
						global_val.gCLS_Init.cPrint( "以後のユーザ登録は、ユーザ登録コマンドで実行してください。: python3 run.py -ur [ユーザ名(@ドメインを含む)]" + '\n' )
						break
		
		#############################
		# ユーザ登録がされている時は masterユーザを変更する
		else :
			self.cCnfMasterUser()
		
		return True



#####################################################
# master環境情報 操作
#####################################################
	def cCnfMasterConfig(self):
		#############################
		# ファイルの存在チェック
		if global_val.gCLS_File.cExist( global_val.gSTR_File['masterConfig_file'] )!=True :
			###ありえない
			global_val.gCLS_Init.cPrint( "CLS_Config: cCnfMasterConfig: masterConfig file is not found : " + global_val.gSTR_File['masterConfig_file'] )
			return False	#ない
		
		self.cCnfMasterConfig_Disp()
		wSelect = self._CnfMasterConfig_SelectDisp()
		if wSelect=='c' :
			###変更
			self._CnfMasterConfig_Change()
			self.cSetMasterConfig()
			global_val.gCLS_Init.cPrint( "変更した内容でmaster環境情報をセーブしました: " + global_val.gSTR_File['masterConfig_file'] + '\n' )
			
		elif wSelect=='s' :
			###セーブ
			self.cSetMasterConfig()
			global_val.gCLS_Init.cPrint( "master環境情報をセーブしました: " + global_val.gSTR_File['masterConfig_file'] + '\n' )
		
		return True

	#####################################################
	# 選択メニュー表示
	#####################################################
	def _CnfMasterConfig_SelectDisp(self):
		wStr = "操作メニューキーを押してください" + '\n'
		wStr = wStr + "c: 変更 / s:セーブ+終了 / other:なにもせず終了"
		global_val.gCLS_Init.cPrint( wStr )
		wSelect = input("選択? => ")
		return wSelect

	#####################################################
	# 変更メニュー表示
	#####################################################
	def _CnfMasterConfig_Change(self):
		for ikey in self.STR_cnfMasterConf :
			if ikey=='Twitter' and global_val.gSTR_masterConfig['twAS']=="" :
				###twitterのキー設定がされていなければメニューを出さない
				global_val.gSTR_masterConfig[ikey] = "off"
				continue
			
			if ikey=='MasterUser' or ikey=='AdminUser' or \
			   ikey=='mRun' or ikey=='mMainte' :
				###これらは別メニューで変更させる
				continue
			
			wStr = ikey + "= " + str( global_val.gSTR_masterConfig[ikey]) + " : "
			if global_val.gSTR_masterConfig[ikey]=="on" :
				wStr = wStr + "c: on→off"
				wChg = "off"
			else:
				wStr = wStr + "c: off→on"
				wChg = "on"
			
			wStr = wStr + " / other: 変更しない"
			global_val.gCLS_Init.cPrint( wStr )
			wSelect = input("選択? => ")
			
			if wSelect=="c" :
				###変更する
				global_val.gSTR_masterConfig[ikey] = wChg
		
		return



#####################################################
# master環境情報 表示
#####################################################
	def cCnfMasterConfig_Disp(self):
		wStr = "--------------------" + '\n'
		wStr = wStr + " master環境情報" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
		for ikey in self.STR_cnfMasterConf :
			wStr = wStr + ikey + " : " + str( global_val.gSTR_masterConfig[ikey])  + '\n'
		
		global_val.gCLS_Init.cDispClear()
		global_val.gCLS_Init.cPrint( wStr )
		return



#####################################################
# AdminUser変更(通知先ユーザ)
#####################################################
	def cCnfAdminUser(self):
		#############################
		# ファイルの存在チェック
		if global_val.gCLS_File.cExist( global_val.gSTR_File['masterConfig_file'] )!=True :
			###ありえない
			global_val.gCLS_Init.cPrint( "CLS_Config: cCnfAdminUser: masterConfig file is not found : " + global_val.gSTR_File['masterConfig_file'] )
			return False	#ない
		
		#############################
		# 変更メニュー表示
		if global_val.gSTR_masterConfig['AdminUser']=="" :
			wStr = "現在AdminUserは設定されていません。設定することで登録ユーザから通知を受け取ることができるようになります。"
			wSt2 = "AdminUserの設定をおこないますか？(y/N)=> "
		else :
			wStr = "現在AdminUserは次のアカウントが設定されています。: " + global_val.gSTR_masterConfig['AdminUser']
			wSt2 = "AdminUserの設定をおこないますか？(y:変更 /D:解除 /other: キャンセル)=> "
		
		global_val.gCLS_Init.cPrint( wStr )
		wSelect = input( wSt2 )
		if wSelect=="D" :
			###削除
			global_val.gSTR_masterConfig['AdminUser'] = ""
			self.cSetMasterConfig()
			global_val.gCLS_Init.cPrint( "AdminUserの設定を解除しました。" + '\n' )
			global_val.gCLS_Init.cPrint( "設定内容をmaster環境情報にセーブしました: " + global_val.gSTR_File['masterConfig_file'] + '\n' )
			return True
		elif wSelect!="y" :
			###設定しない
			global_val.gCLS_Init.cPrint( "キャンセルされました" )
			return True
		#############################
		# 名前入力
		wStr = "AdminUser(通知先アカウント)をドメインを含めて入力してください。 例= " + global_val.gCHR_ExampleAccount + '\n'
		wStr = wStr + "  ※ユーザ登録してないユーザも指定できます"
		global_val.gCLS_Init.cPrint( wStr )
		wAdminUser = input("AdminUser？ => ")
		
		if wAdminUser=="" or \
		   global_val.gSTR_masterConfig['AdminUser'] ==wAdminUser :
			###設定しない
			global_val.gCLS_Init.cPrint( "キャンセルされました" )
			return True
		
		#############################
		# ユーザ名の妥当性チェック
		wSTR_user = global_val.gCLS_Regist.cUserCheck( wAdminUser )
		if wSTR_user['Result']!=True :
			return False
		
		#############################
		# 通信テスト
		global_val.gCLS_Init.cPrint( "mastodonとの通信テスト中..." )
		if global_val.gCLS_Init.cPing( wSTR_user['Domain'] )!=True :
			global_val.gCLS_Init.cPrint( "mastodonとの通信テストに失敗したため、設定をキャンセルします。" )
			return False
		
		global_val.gCLS_Init.cPrint( "mastodonとの通信テストに成功しました。" + '\n' )
		
		#############################
		# 変更
		global_val.gSTR_masterConfig['AdminUser'] = wAdminUser
		self.cSetMasterConfig()
		global_val.gCLS_Init.cPrint( "設定内容をmaster環境情報にセーブしました: " + global_val.gSTR_File['masterConfig_file'] + '\n' )
		return True



#####################################################
# MasterUser変更(botとして使うユーザ)
#####################################################
	def cCnfMasterUser( self, fulluser="" ):
		#############################
		# ユーザ一覧の取得
		wList = global_val.gCLS_Regist.cGetUserList()
		
		#############################
		# 登録がない場合は、イレギュラーっぽくもある...
		if len(wList)==0 :
			global_val.gCLS_Init.cPrint( "ユーザが1件も登録されていないため、MasterUserの登録ができません。" )
			return False
		
		#############################
		# 1件しかない場合かつMasterUser登録済みの場合は変更できない
		elif len(wList)==1 and global_val.gSTR_masterConfig['MasterUser']!="" :
			wStr = "ユーザが1件しか登録されていないため、MasterUserの変更はできません。" + '\n'
			wStr = wStr + "現在のMasterUser: " + global_val.gSTR_masterConfig['MasterUser'] + '\n'
			global_val.gCLS_Init.cPrint( wStr )
			return False
		
		#############################
		# 1件しかない場合かつMasterUserが未登録の場合は、
		# その1件をMasterUserに設定してしまう
		elif len(wList)==1 :
			wStr = "ユーザが1件しか登録されていないため、当該ユーザをMasterUserに設定します。"  + '\n'
			global_val.gCLS_Init.cPrint( wStr )
			self._CnfMasterUser( wList[0] )
			return False
		
		#############################
		# 2件以上の場合は選択する
		else :
			global_val.gCLS_Regist.cViewList()
			wStr = "現在MasterUserに設定されているユーザは次のユーザです。: " + global_val.gSTR_masterConfig['MasterUser'] + '\n'
			wStr = wStr + "MasterUser(botとして使うユーザ)をドメインを含めて入力してください。 例= " + global_val.gCHR_ExampleAccount
			global_val.gCLS_Init.cPrint( wStr )
			wMasterUser = input("MasterUser？ => ")
			
			wFLG = False
			for ikey in wList :
				if wMasterUser==ikey :
					wFLG = True
			
			if wFLG!=True :
				global_val.gCLS_Init.cPrint( "登録されていないユーザです。変更をキャンセルします。" )
				return False
			
			self._CnfMasterUser( wMasterUser )
		
		return True



	#####################################################
	# MasterUser変更
	#####################################################
	def _CnfMasterUser( self, fulluser ):
		#############################
		# 変更＆反映
		global_val.gSTR_masterConfig['MasterUser'] = fulluser 
		global_val.gCLS_Config.cSetMasterConfig()
		
		wStr = fulluser + " をMasterUserに設定します。" + '\n'
		wStr = wStr + "master環境情報をセーブしました: " + global_val.gSTR_File['masterConfig_file'] + '\n'
		global_val.gCLS_Init.cPrint( wStr )
		return



#####################################################
# master運用操作
#####################################################
	def cCnfMasterRun(self):
		#############################
		# ファイルの存在チェック
		if global_val.gCLS_File.cExist( global_val.gSTR_File['masterConfig_file'] )!=True :
			###ありえない
			global_val.gCLS_Init.cPrint( "CLS_Config: cCnfMasterRun: masterConfig file is not found : " + global_val.gSTR_File['masterConfig_file'] )
			return False	#ない
		
		#############################
		# メニューの表示
		wStr = '\n' + "botの運用を設定します。現在の設定。 mRun= " + global_val.gSTR_masterConfig['mRun']
		global_val.gCLS_Init.cPrint( wStr )
		
		wStr = ""
		if global_val.gSTR_masterConfig['mRun']=="on" :
			wStr = wStr + "c: on→off"
			wChg = "off"
		else:
			wStr = wStr + "c: off→on"
			wChg = "on"
		
		wStr = wStr + " / other: 変更しない => "
		wSelect = input( wStr )
		
		if wSelect!="c" :
			###変更しない
			global_val.gCLS_Init.cPrint( "キャンセルされました" )
			return True
		
		#############################
		# 変更
		global_val.gSTR_masterConfig['mRun'] = wChg
		self.cSetMasterConfig()
		
		wStr = "botの運用設定を変更しました。 mRun= " + wChg + '\n'
		wStr = wStr + "変更した内容でmaster環境情報をセーブしました: " + global_val.gSTR_File['masterConfig_file'] + '\n'
		global_val.gCLS_Init.cPrint( wStr )
		return True



#####################################################
# masterメンテ操作
#####################################################
	def cCnfMasterMainte(self):
		#############################
		# ファイルの存在チェック
		if global_val.gCLS_File.cExist( global_val.gSTR_File['masterConfig_file'] )!=True :
			###ありえない
			global_val.gCLS_Init.cPrint( "CLS_Config: cCnfMasterMainte: masterConfig file is not found : " + global_val.gSTR_File['masterConfig_file'] )
			return False	#ない
		
		#############################
		# メニューの表示
		wStr = '\n' + "botをメンテナンス設定します。現在の設定。 mMainte= " + global_val.gSTR_masterConfig['mMainte']
		global_val.gCLS_Init.cPrint( wStr )
		
		wStr = ""
		if global_val.gSTR_masterConfig['mMainte']=="on" :
			wStr = wStr + "c: on→off"
			wChg = "off"
		else:
			wStr = wStr + "c: off→on"
			wChg = "on"
		
		wStr = wStr + " / other: 変更しない => "
		wSelect = input( wStr )
		
		if wSelect!="c" :
			###変更しない
			global_val.gCLS_Init.cPrint( "キャンセルされました" )
			return True
		
		#############################
		# 変更
		global_val.gSTR_masterConfig['mMainte'] = wChg
		self.cSetMasterConfig()
		
		wStr = "botをメンテナンス設定を変更しました。 mMainte= " + wChg + '\n'
		wStr = wStr + "変更した内容でmaster環境情報をセーブしました: " + global_val.gSTR_File['masterConfig_file'] + '\n'
		global_val.gCLS_Init.cPrint( wStr )
		return True



#####################################################
# 同報配信設定だけ読み込んで値を返す
#####################################################
	def cGetMulticast( self, path ):
		wRes = {
			"Result"	: False,
			"Flg"		: ""
		}
		
		#############################
		# ファイルの存在チェック
		if global_val.gCLS_File.cExist( path )!=True :
			###ありえない
			global_val.gCLS_Init.cPrint( "CLS_Config: cGetMulticast: config file is not found : " + path )
			return wRes		#ない
		
		#############################
		# ファイルを開く
		wFLG = ""
		for line in open( path, 'r'):
			#############################
			# 分解+要素数の確認
			line = line.strip()
			get_line = line.split("=")
			if len(get_line) != 2 :
				continue
			
			#############################
			# 同報配信キーか
			if get_line[0]=='Multicast' :
				wFLG = get_line[1]
				break
		
		#############################
		# 取得できたか
		if wFLG=="" :
			return wRes		#ない
		
		wRes['Flg']    = wFLG
		wRes['Result'] = True
		return wRes



#####################################################
# 環境設定の読み込み
#####################################################
	def cGet(self):
		for line in open( global_val.gConfig_file, 'r'):	#ファイルを開く
			#############################
			# 分解+要素数の確認
			line = line.strip()
			get_line = line.split("=")
			if len(get_line) != 2 :
				continue
			
			#############################
			# キーがあるか確認
			if get_line[0] not in global_val.gConfig :
				continue
			
			#############################
			# 更新する
			global_val.gConfig[get_line[0]] = get_line[1]
		
		#############################
		# 文字→数値へ変換
		global_val.gConfig["getPTLnum"] = int( global_val.gConfig["getPTLnum"] )
		global_val.gConfig["getRIPnum"] = int( global_val.gConfig["getRIPnum"] )
		global_val.gConfig["getFollowMnum"] = int( global_val.gConfig["getFollowMnum"] )
		global_val.gConfig["getRandVal"] = int( global_val.gConfig["getRandVal"] )
		global_val.gConfig["getRandRange"] = int( global_val.gConfig["getRandRange"] )
		
		#############################
		# 数値補正
		if global_val.gConfig["getRandVal"] < 0 :
			global_val.gConfig["getRandVal"] = 0
		elif global_val.gConfig["getRandVal"] > 100 :
			global_val.gConfig["getRandVal"] = 100
		
		if global_val.gConfig["getRandRange"] < 100 :
			global_val.gConfig["getRandRange"] = 100
		
		return



