#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：グローバル値
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/2/24
#####################################################
import os

#############################
# スクリプトのパス(grobal_val専用)
gScriptPath = os.path.dirname(__file__) + '/../'

#############################
# システム情報
gSTR_SystemInfo = {
	"BotName"		: "",
	"BotDate"		: "",
	"Version"		: "",
	"Admin"			: "",
	"github"		: "",
	"PythonVer"		: 0,
	"(dummy)"		: 0
}

#############################
# システム情報
gSTR_File = {
	"Readme"		: gScriptPath + "readme.txt",
	"(dummy)"		: 0
}





#############################
# クラス実体
gCLS_Init = ''					#CLS_Initクラス用










#############################
# スコア ※遊び要素
#############################
gScore = {
	"Reply"			: 4,
	"Boost"			: 2,
	"Favo"			: 1,
	"(dummy)"		: 0
}

#############################
# config    ※いじらない。設定変更はconfigファイルをいじってロードする
#############################
gConfig = {
	"UserBot"		: "",						#ユーザ情報の枠
	"UserMaster"	: "",
	"BaseUrl"		: "",
	"twCK"			: "",
	"twCS"			: "",
	"twAT"			: "",
	"twAS"			: "",
	
	"BotStart"		: "on",						#botの動作　on以外は起動しない
	"Twitter"		: "off",					#Twitterとの連携
	"JPonly"		: "on",						#日本人のみ監視
	
	"RandToot"		: "off",					#ランダムトゥートモード
	"getRandVal"	: 70,						#トゥート頻度 0-100
	"getRandRange"	: 1000,						#トゥート頻度 乱数幅
	
	"getPTLnum"			: 120,					#PTL取得数
	"PTL_Favo"			: "off",				#PTLニコる
	"PTL_Boot"			: "off",				#PTLブースト
	"PTL_HRip"			: "off",				#PTL紐エアリプ
	"PTL_ARip"			: "off",				#PTLエアリプ
	"PTL_WordOpe"		: "off",				#ワード監視
	
	"CircleToot"	: "off",					#周期トゥート
	
	"WordStudy"		: "off",					#ワード学習
	"studyNum"			: 10,					#学習範囲（トゥート数）
	"studyMax"			: 1000,					#最大学習単語数
	"studyDay"			: 14,					#単語を覚えておく日数
	
	"Traffic"		: "off",					#トラヒック集計
	
##	"LookRIP"		: "off",					#リプライ監視モード
	"getRIPnum"			: 120,					#リプライ取得数
	"RIP_Favo"			: "off",				#リプニコる
##	"RIP_Boot"			: "off",				#リプブースト
	"IND_Favo"			: "off",				#ファボ監視
	"IND_FavoTag"		: "favoind",			#ファボ監視タグ
	"IND_Favo_Unl"		: "off",				#ファボ監視 privateの通知を許可
	
	"AutoFollow"	: "off",					#フォロー監視モード
	"getFollowMnum"		: 10,					#フォロー処理数
	
	"LookHard"		: "off",					#ハード監視モード
	
	"LogLevel"		: "a",						#ログレベル
												# a=a,b,c：全て出力
												# b=a,b：警告レベルまで
												# c=a：重要なもののみ
	
	"Lock"			: "on",						#排他処理
	"Mainte"		: "off"						#メンテモード
}


#############################
# グローバル値  ※いじらない
#############################
gVisi_Range  = 'unlisted'						#botのトゥート公開範囲
gToot_Range  = 'public'							#手動トゥートしたときの公開範囲
gMyID        = ''
gMyIDnum     = 0

gCircle_Time = 30								#スレッドmain処理の起動周期(秒)
gCHR_Border  = '|,|'							#閾値
gLockWait_Num = 18								#ロック解除待ち回数  5*N 秒
gClazList_Num = 50								#品詞リスト登録数

gOBJ_TimeDate = ""								# datetime.now()
gFull_TimeDate = ""								# datetime.strptime(str(global_val.gOBJ_TimeDate), "%Y-%m-%d %H:%M:%S")
gTraffic_1HourSkip = False						#1時間スキップ
gFlg_1HourTime = False							#1時間経過
												#  False = たってない
												#  True  = 1時間
												
gTimeZone   = 9									#9=日本時間  最終更新日補正用


gMastodonParam = {								#Mastodonクラスに与えるパラメータ
	"RegFilePath"			: gScriptPath + "../data/reg_reg_file.txt",
													# レジストレーションでできたやつ
	"UserFilePath"			: gScriptPath + "../data/reg_user_file.txt"
													# ログインでできたやつ
##	"API_BaseUrl"			: gAPI_BaseUrl
}

												# ツイート投稿用のURL
gTwitter_url = "https://api.twitter.com/1.1/statuses/update.json"

gProfSuburl = "/web/accounts/"					#プロフ用サブURL



#############################
# ファイルパス
gConfig_file = gScriptPath + '../toot/config.txt'			#環境設定ファイル
g1HourTimeCheck_file = gScriptPath + '../data/chk1hour.txt'	#1時間監視

gLookPTL_file = gScriptPath + '../toot/pptl.txt'			#PTL監視ファイル
gLookRTL_file = gScriptPath + '../toot/reply.txt'			#リプライ監視ファイル
gRateLTL_file = gScriptPath + '../data/rltl.txt'			#過去LTLファイル(トゥートidを保管)
gRatePTL_file = gScriptPath + '../data/rptl.txt'			#過去PTLファイル(トゥートidを保管)
gRateRTL_file = gScriptPath + '../data/rreply.txt'			#過去リプライファイル(トゥートidを保管)
gRateFav_file = gScriptPath + '../data/rfav.txt'			#過去ファボファイル(トゥートidを保管)

gCircleToot_file = gScriptPath + '../toot/ctoot.txt'		#周期トゥートファイル
gCircleTootDat_file = gScriptPath + '../data/ctootd.txt'	#周期トゥートデータファイル
gCircleToot_folder = gScriptPath + '../toot/'				#周期トゥート トゥートファイルのフォルダ

gFollowCheck_file = gScriptPath + '../data/chkfollow.txt'	#フォローチェック時間記録
gTraffic_file = gScriptPath + '../toot/traffic.txt'			#トラヒック収集先
gNowTraffic_file = gScriptPath + '../data/traffic_now.txt'	#現在トラヒック
gRatTraffic_file = gScriptPath + '../data/traffic_rat.txt'	#過去トラヒック
gLock_file = gScriptPath + '../data/_lock.txt'				#排他データファイル

##gAutolog_file = gScriptPath + '../log/autolog.txt'		#ログファイル
gMyLog_path     = gScriptPath + '../log/'					#ログパス
gMyLog_Hard     = 'hard'									#ログ識別子：ハード監視用
gReplyFile_dir  = gScriptPath + '../toot/'					#リプライファイル

gUserCorr_file = gScriptPath + '../user/usercorr.csv'		#ユーザ収集ファイル
gUserCorrRem_file = gScriptPath + '../toot/usercorr_rem.txt'	#ユーザ収集除外ファイル
gUserDic_file = gScriptPath + '../user/userdic.csv'			#ユーザ辞書ファイル
gUserDicRem_file = gScriptPath + '../toot/xxword.txt'		#禁止ワードファイル
gClazList_file = gScriptPath + '../data/clazlist.txt'		#品詞リストファイル



#############################
# クラス
gCLS_MainProc = ''											#MainProcクラス用
gCLS_Mastodon = ''											#Mastodonクラス用
gCLS_Twitter = ''											#Twitterクラス用
gCLS_Config  = ''											#Configクラス用
gCLS_RandToot = ''											#RandTootクラス用
gCLS_LookPTL = ''											#LookPTLクラス用
gCLS_LookRIP = ''											#LookRIPクラス用
gCLS_CircleToot = ''										#CLS_CircleTootクラス用
gCLS_UserInfo = ''											#ユーザ情報管理クラス用
gCLS_TootCorrect = ''										#トゥート収集処理クラス用
gCLS_Traffic = ''											#トラヒック処理クラス用
gCLS_LookHard = ''											#LookHardクラス用
gCLS_Mylog = ''												#CLS_Mylogクラス用

