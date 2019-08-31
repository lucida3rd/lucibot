#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：bot実行 (Master用)
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/8/30
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

from bot_master import CLS_BOT_Master
from gval import gVal
#####################################################
CLS_BOT_Master.sRun()	#起動


