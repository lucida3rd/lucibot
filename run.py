#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：コンソール実行処理
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/10
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   (none)
#
# Class Function(static):
#   (none)
#
#####################################################
import sys
sys.path.append('script')

sys.path.append('script/api')
sys.path.append('script/cron')
sys.path.append('script/data')
sys.path.append('script/disp')
sys.path.append('script/func')
sys.path.append('script/oslib')

from main_console import CLS_Main_Console
from gval import gVal
#####################################################
CLS_Main_Console.sRun()		#コンソール起動



