# coding: UTF-8
#####################################################
# 十八試るしぼっと
#   Class   ：レジストファイル
#   Site URL：https://lucida-memo.info/
#   Update  ：2018/11/16
#####################################################
import os
import sys
gPath = os.path.dirname(os.path.abspath(__file__)) + "/../script"
sys.path.append(gPath)

from mastodon_use import CLS_Mastodon_Use

#############################
# ※ユーザ設定
cliant_name = "aaaaaaaaaa"							# クライアント名
api_base_url = "https://aaaa.net"					# アクセス先
user_mail_addr = "aaa@yahoo.co.jp"					# ID(登録メールアドレス)
user_password = "aaaaaaaa"							# password
#############################

CLS_Mastodon_Use.create_app(
				cliant_name, 
				api_base_url = api_base_url,
				to_file = '../data/reg_reg_file.txt')

mastodon = CLS_Mastodon_Use(
				client_id = "../data/reg_reg_file.txt",
				api_base_url = api_base_url )

mastodon.log_in(username = user_mail_addr,
				password = user_password,
				to_file = "../data/reg_user_file.txt")

dummy_val = input('>>>  ')

