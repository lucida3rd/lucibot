# coding: UTF-8
#####################################################
# 十八試るしぼっと
#   Class   ：環境設定処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2018/11/24
#####################################################
import global_val
#####################################################
class CLS_Config:

#####################################################
# Init
#####################################################
	def __init__(self):
		return



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
		global_val.gConfig["studyNum"] = int( global_val.gConfig["studyNum"] )
		global_val.gConfig["studyMax"] = int( global_val.gConfig["studyMax"] )
		global_val.gConfig["studyDay"] = int( global_val.gConfig["studyDay"] )
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



