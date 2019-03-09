#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：グローバル値
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/7
#####################################################

#####################################################
class gVal() :

#############################
# ※ユーザ自由変更※
	DEF_EXAMPLE_ACCOUNT = "lucida3rd@mstdn.mynoghra.jp"		#画面に記載例として表示するアカウント
	DEF_USERDATA_PATH   = '../botdata/'						#ユーザデータフォルダ
	DEF_TIMEZONE = 9										# 9=日本時間 最終更新日補正用
	DEF_MOJI_ENCODE = 'utf-8'								#文字エンコード

#############################
# システム情報
	#データversion(文字)
	DEF_CONFIG_VER = "1"

	STR_SystemInfo = {
		"Client_Name"	: "るしぼっと",
		"BotName"		: "",
		"BotDate"		: "",
		"Version"		: "",
		"Admin"			: "",
		"github"		: "",
		
		"PythonVer"		: 0,
		"HostName"		: ""
	}

#############################
# Master環境情報
	STR_MasterConfig = {
		"MasterUser"	: "",						#masterユーザ
		"AdminUser"		: "",						#監視ユーザ(通知先)
		"PRUser"		: "",						#PRユーザ(広報・周期トゥート用)
		"mTootTag"			: "[Sender]",				#手動トゥートタグ
		
		"TwitterUser"	: "",						#twiterユーザ
		"Twitter"		: "off",					#twiter連携
		"twCK"				: "",
		"twCS"				: "",
		"twAT"				: "",
		"twAS"				: "",
		
		"PTL_Favo"		: "off",					#PTLニコる
		"PTL_Boot"		: "off",					#PTLブースト
		"PTL_HRip"		: "off",					#PTL紐エアリプ
		"PTL_ARip"		: "off",					#PTLエアリプ
		"PTL_WordOpe"	: "off",					#ワード監視
		"getPTLnum"			: 120,						#PTL取得数
		
		"RandToot"		: "off",					#ランダムトゥートモード
		"getRandVal"		: 70,						#トゥート頻度 0-100
		"getRandRange"		: 1000,						#トゥート頻度 乱数幅
		
		"CircleToot"	: "off",					#周期トゥート
		
		"Multicast"		: "off",					#同報配信リプライ 有効
		
		"Traffic"		: "off",					#トラヒック集計
		
		"LookHard"		: "off",					#ハード監視
		
		"WordStudy"		: "off",					#ワード学習
		"studyNum"			: 10,					#学習範囲（トゥート数）
		"studyMax"			: 1000,					#最大学習単語数
		"studyDay"			: 14,					#単語を覚えておく日数
		
		"getMcDelay"			: 5,						#同報配信ディレイ
		
		"LogLevel"		: "a",						#ログレベル
													# a=a,b,c：全て出力
													# b=a,b：警告レベルまで
													# c=a：重要なもののみ
		
		"Lock"			: "on",							#排他機能
		"mMainte"		: "off",					#全体メンテモード
		
		"DataVer"		: DEF_CONFIG_VER				#データversion
	}

#############################
# 環境情報
	STR_Config = {
		"Multicast"		: "off",					#同報配信対象
		
		"getLTLnum"			: 120,						#LTL取得数
		
		"RIP_Favo"		: "off",					#リプニコる
		"IND_Favo"		: "off",					#ファボ監視
		"IND_Favo_Unl"		: "off",					#ファボ監視 privateの通知を許可
		"IND_FavoTag"		: "favoind",				#ファボ監視タグ
		"getRIPnum"			: 120,						#リプライ取得数
		
		"TrafficCnt"	: "off",					#トラヒック集計
		
		"WordCorrect"	: "off",					#個別ワード収集
		
		"AutoFollow"	: "off",					#フォロー監視モード
		"getFollowMnum"		: 10,						#フォロー処理数
		
		"Mainte"		: "off",					#メンテモード
		
		"JPonly"		: "off"						#日本人のみ監視
	}

#############################
# ファイルパス
#   ファイルは語尾なし、フォルダは_path

	DEF_MASTERCONFIG_NAME = "masterConfig"
	DEF_MASTERCONFIG      = DEF_USERDATA_PATH + DEF_MASTERCONFIG_NAME + "/"

	STR_File = {
		"Readme"				: "readme.txt",
		"defUserdata_path"		: "_default/",
		"defMasterdata_path"	: "_master/",
		"defMasterConfig"		: "_master/mconfig.txt",
		
		"MasterConfig_path"		: DEF_MASTERCONFIG,
		"MasterConfig"			: DEF_MASTERCONFIG + "mconfig.txt",
		"MasterLog_path"		: DEF_MASTERCONFIG + "log/",
		
		"UserConfig"			: "config.txt",
		"Reg_RegFile"			: "data/reg_reg_file.txt",
		"Reg_UserFile"			: "data/reg_user_file.txt",
		"UserLog_path"			: "log/",
		
		"(dummy)"				: 0
	}

	DEF_DISPPATH = "script/disp/"

	STR_DispFile = {
		"MainConsole"			: DEF_DISPPATH + "main_console.disp",
		"(dummy)"				: 0
	}

#############################
# デフォルトのトゥート公開設定
	STR_defaultRange = {
		"ManualToot"	: "public",
		"Multicast"		: "unlisted",
		"Bot"			: "unlisted"
	}
###	'public'   ..公開
###	'unlisted' ..未収載
###	'private'  ..非公開

#############################
# Cron情報
	STR_CronInfo = {
						##TestLog Enable
		"_master.py"	: True,
		"_sub.py"		: True,
		"_back.py"		: True,
		
		"CronName"		: "lucibot",
		"Log_path"		: STR_File['MasterLog_path'],
		"(dummy)"		: 0
	}
	
	DEF_CRON_MASTER = "_master.py"
	DEF_CRON_SUB    = "_sub.py"
	DEF_CRON_BACK   = "_back.py"
	
	DEF_CRON_ACCOUNT_BACKGROUND = "BACKGROUND"



#############################
# 登録禁止サーバ(間違えやすいドメインとか)
	STR_NoRegistDomain = [
		"yahoo.co.jp",
		"ybb.ne.jp",
		"gmail.com",
		"outlook.jp",
		"outlook.com",
		"hotmail.co.jp",
		"live.jp",
		"(dummy)"
	]



#############################
# 定数
															#Twitterホスト名
	DEF_TWITTER_HOSTNAME = "twitter.com"
															#ツイート投稿用のURL
	DEF_TWITTER_URL = "https://api.twitter.com/1.1/statuses/update.json"
	
	DEF_PROF_SUBURL = "/web/accounts/"						#プロフ用サブURL



#############################
# 変数
	FLG_Console_Mode = False								#画面出力の有無



#####################################################
# Init
#####################################################
##	def __init__(self):
##		self.STR_SystemInfo = {
##			"BotName"		: "",
##			"HostName"		: ""
##		}
##		return



