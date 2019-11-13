#!/usr/bin/python
# coding: UTF-8
#####################################################
# public
#   Class   ：mastodon API
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/11/13
#####################################################
# Private Function:
#   __initIniStatus(self):
#   __json_date_parse(self, json_object):
#   __datetime_to_epoch(self, date_time):
#   __api_request(self, method, endpoint, params={}, files={}, do_ratelimiting=True):
#   __generate_params(self, params, exclude=[]):
#   __unpack_id(self, id):
#   __get_token_expired(self):
#   __set_token_expired(self, value):
#   __get_refresh_token(self):
#   __set_refresh_token(self, value):
#   __delPassword( self, inParams ):
#
# Instance Function:
# ◇クラスINIT and Login
#   __init__( self, client_id, api_base_url=__DEFAULT_BASE_URL,
#		access_token=None, flg_orginit=False ):
#   log_in(self, username=None, password=None,
#		code=None, redirect_uri="urn:ietf:wg:oauth:2.0:oob",
#		refresh_token=None, scopes=['read', 'write', 'follow'], to_file=None):
#
# ◇mastodon初期化確認用
#   TokenCheck(self):
#   GetIniStatus(self):
#
# ◇トゥート関数
#   Toot(self, status = None,
#		in_reply_to_id = None, media_ids = None, sensitive = False, visibility = 'unlisted',
#		spoiler_text = None):
#
# ◇TL取得系
#   GetLocalTL(self, timeline="local", max_id=None, since_id=None, limit=None):
#   GetHomeTL(self, timeline="home", max_id=None, since_id=None, limit=None):
#   GetPublicTL(self, timeline="public", max_id=None, since_id=None, limit=None):
#   GetHashtagTL(self, hashtag, local=False, max_id=None, since_id=None, limit=None, only_media=False):
#   GetListTL( self, id, timeline="", max_id=None, since_id=None, limit=None):
#   GetTrends( self, limit=None ):
#
# ◇一覧取得系
#   GetNotificationList(self, id=None, max_id=None, since_id=None, limit=None):
#   NotificationClear(self):
#   GetTootList(self, id, only_media=False, pinned=False, exclude_replies=False, max_id=None, since_id=None, limit=None):
#   GetFavoList(self, max_id=None, since_id=None, limit=None):
#   GetFollowingList(self, id, max_id=None, since_id=None, limit=None):
#   GetFollowersList(self, id, max_id=None, since_id=None, limit=None):
#
# ◇アカウント情報取得
#   GetMyAccountInfo(self):
#   GetAccountStat(self, id):
#
# ◇リアクション系
#   Follow( self, id, reblogs=True ):
#   Remove(self, id):
#   Favo(self, id):
#   Boost(self, id):
#   Block(self, id):
#   Unblock(self, id):
#   Mute(self, id):
#   Unmute(self, id):
#
# ◇リスト操作系
#   CreateList(self, title ):
#   UpdateList(self, id, title):
#   DeleteList(self, id):
#   AddAccount_List( self, id, account_ids ):
#   DelAccount_List(self, id, account_ids):
#
# Class Function(static):
#   sGet_API_Resp(cls):
#
# Static Function:
#   create_app( client_name, scopes=['read', 'write', 'follow'],
#		redirect_uris=None, website=None, to_file=None,
#		api_base_url=__DEFAULT_BASE_URL, request_timeout=__DEFAULT_TIMEOUT):
#   __protocolize(base_url):
#
#####################################################
import os
import os.path
import mimetypes
import time
import random
import string
import datetime
import collections
from contextlib import closing
import pytz
import requests
from requests.models import urlencode
import dateutil
import dateutil.parser
import re
import copy
import threading
import sys
import six
##from decorator import decorate
##from cryptography.hazmat.backends import default_backend
##from cryptography.hazmat.primitives.asymmetric import ec
##import http_ece
import base64
import json

try:
	from urllib.parse import urlparse
except ImportError:
	from urlparse import urlparse

try:
	import magic
except ImportError:
	magic = None



#####################################################
# Dict helper class.
# Defined at top level so it can be pickled.
#####################################################
class AttribAccessDict(dict):
	def __getattr__(self, attr):
		if attr in self:
			return self[attr]
		else:
			raise AttributeError("Attribute not found: " + str(attr))
	
	def __setattr__(self, attr, val):
		if attr in self:
			raise AttributeError("Attribute-style access is read only")
		super(AttribAccessDict, self).__setattr__(attr, val)



#####################################################
class CLS_Mastodon_Use:
#####################################################
	__DEFAULT_BASE_URL = 'https://mastodon.social'	#mastodon旗艦サーバ(mastodon.py 1.3のまま)
	__DEFAULT_TIMEOUT = 300
	__DEFAULT_STREAM_TIMEOUT = 300
	__DEFAULT_STREAM_RECONNECT_WAIT_SEC = 5
	__DEFAULT_SCOPES = ['read', 'write', 'follow', 'push']
	__SCOPE_SETS = {
		'read': [
			'read:accounts', 
			'read:blocks', 
			'read:favourites', 
			'read:filters', 
			'read:follows', 
			'read:lists', 
			'read:mutes', 
			'read:notifications', 
			'read:reports', 
			'read:search', 
			'read:statuses'
		],
		'write': [
			'write:accounts', 
			'write:blocks', 
			'write:favourites', 
			'write:filters', 
			'write:follows', 
			'write:lists', 
			'write:media', 
			'write:mutes', 
			'write:notifications', 
			'write:reports', 
			'write:statuses',
		],
		'follow': [
			'read:blocks',
			'read:follows',
			'read:mutes',
			'write:blocks',  
			'write:follows',
			'write:mutes', 
		]
	}
	
	IniStatus = ""

#####################################################
# トークンチェック
#####################################################
	def TokenCheck(self):
		if self.access_token=="" :
			return False	#トークンなし
		
		###トークンが取れていれば OK
		return True



#####################################################
# 初期化状態取得
#####################################################
	def GetIniStatus(self):
		return self.IniStatus	#返すだけ



#####################################################
# 初期化状態取得
#####################################################
	def __initIniStatus(self):
		self.IniStatus = {
			"Result"   : False,
			"Reason"   : None,
			"Responce" : None,
			
		}
		return



#####################################################
# APIレスポンス取得
#####################################################
	@classmethod
	def sGet_API_Resp(cls):
		wRes = {
			"Result"   : False,
			"Reason"   : None,
			"Responce" : None }
		
		return wRes



#####################################################
# アプリ生成
# ★クライアント登録などに使うほう
#####################################################
	@staticmethod
	def create_app( client_name,
		scopes=__DEFAULT_SCOPES,
		redirect_uris=None, website=None, to_file=None,
		api_base_url=__DEFAULT_BASE_URL,
		request_timeout=__DEFAULT_TIMEOUT,
		session=None):
		
		api_base_url = CLS_Mastodon_Use.__protocolize(api_base_url)
		
		#############################
		# 応答形式の取得
		#  {"Result" : False, "Reason" : None, "Responce" : None}
		wRes = CLS_Mastodon_Use.sGet_API_Resp()
		
		request_data = {
			'client_name': client_name,
			'scopes': " ".join(scopes)
		}
		
		response = ""
		try:
			if redirect_uris is not None:
				if isinstance(redirect_uris, (list, tuple)):
					redirect_uris = "\n".join(list(redirect_uris))
				request_data['redirect_uris'] = redirect_uris
			else:
				request_data['redirect_uris'] = 'urn:ietf:wg:oauth:2.0:oob'
			if website is not None:
				request_data['website'] = website
			
			if session:
				ret = session.post(api_base_url + '/api/v1/apps', data=request_data, timeout=request_timeout)
				response = ret.json()
			else:
				response = requests.post(api_base_url + '/api/v1/apps', data=request_data, timeout=request_timeout)
				response = response.json()
			
		except Exception as e:
##			wRes['Reason']   = "CLS_Mastodon_Use：create_app：Could not complete request：" + str(e)
			#######
###			wStr = "CLS_Mastodon_Use：create_app：Could not complete request：" + str(e) + \
###					" base_url=" + api_base_url + " responce=" + str(response) + " session=" + str(session) + \
###					" request_data=" + str(request_data)
			wStr = "CLS_Mastodon_Use：create_app：Could not complete request：" + str(e) + " responce=" + str(response)
			#######
			wRes['Reason']   = wStr
			wRes['Responce'] = response
			return wRes
		
		if to_file is not None:
			with open(to_file, 'w') as secret_file:
				secret_file.write(response['client_id'] + '\n')
				secret_file.write(response['client_secret'] + '\n')
		
		wRes['Responce'] = {}
		wRes['Responce'].update({ "client_id" : response['client_id'] })
		wRes['Responce'].update({ "client_secret" : response['client_secret'] })
		wRes['Result']   = True
		return wRes



#####################################################
	@staticmethod
	def __protocolize(base_url):
		if not base_url.startswith("http://") and not base_url.startswith("https://"):
			base_url = "https://" + base_url
		base_url = base_url.rstrip("/")
		return base_url



#####################################################
# Init
# ★オブジェクト生成時に使用
#####################################################
	def __init__(self, client_id=None,
		client_secret=None, access_token=None,
		api_base_url=__DEFAULT_BASE_URL,
		debug_requests=False,
##		ratelimit_method="wait",
##		ratelimit_pacefactor=1.1,
		rate429_waittime=1,
		max_rate429_wait=3,
		request_timeout=__DEFAULT_TIMEOUT,
##		mastodon_version=None,
##		version_check_mode = "created",
		session=None):
		
		#############################
		# Init状態
		self.__initIniStatus()
		
		#############################
		# パラメータの設定
		self.api_base_url = CLS_Mastodon_Use.__protocolize(api_base_url)
		self.client_id = client_id
		self.client_secret = client_secret
		self.access_token = access_token
		self.debug_requests = debug_requests
##		self.ratelimit_method = ratelimit_method
		self.rate429_waittime = rate429_waittime
		self.max_rate429_wait = max_rate429_wait
		
		self._token_expired = datetime.datetime.now()
		self._refresh_token = None
		
		self.__logged_in_id = None
		
		self.ratelimit_limit = 300
		self.ratelimit_reset = time.time()
		self.ratelimit_remaining = 300
		self.ratelimit_lastcall = time.time()
##		self.ratelimit_pacefactor = ratelimit_pacefactor
		
		self.request_timeout = request_timeout
		
		if session:
			self.session = session
		else:
			self.session = requests.Session()
		
##		if ratelimit_method not in ["throw", "wait", "pace"]:
##			self.IniStatus['Reason'] = "CLS_Mastodon_Use：__init__：Invalid ratelimit method"
##			self.IniStatus['Result'] = False
##			return
		
		#############################
		# シークレットキーの取得
		if self.client_id is None and self.access_token is None:
			self.IniStatus['Reason'] = "CLS_Mastodon_Use：__init__：No credentials were given"
			self.IniStatus['Result'] = False
			return
		
		if self.client_id is not None:
			if os.path.isfile(self.client_id):
				with open(self.client_id, 'r') as secret_file:
					self.client_id = secret_file.readline().rstrip()
					self.client_secret = secret_file.readline().rstrip()
			else:
				if self.client_secret is None:
					self.IniStatus['Reason'] = "CLS_Mastodon_Use：__init__：Specified client id directly, but did not supply secret"
					self.IniStatus['Result'] = False
					return
		
		#############################
		# アクセストークンの取得
		if self.access_token is not None and os.path.isfile(self.access_token):
			with open(self.access_token, 'r') as token_file:
				self.access_token = token_file.readline().rstrip()
		
##		if self.access_token is None:
##			self.IniStatus['Reason'] = "CLS_Mastodon_Use：__init__：access_token is None"
##			return
##		elif self.access_token=="":
##			self.IniStatus['Reason'] = "CLS_Mastodon_Use：__init__：access_token is null"
##			return
		
		self.IniStatus['Result'] = True
		return



#####################################################
# ログイン
# ★クライアントorアプリ mastodonログイン
#####################################################
	def log_in(self, username=None, password=None,
			code=None,
			redirect_uri="urn:ietf:wg:oauth:2.0:oob",
			refresh_token=None,
			scopes=__DEFAULT_SCOPES,
			to_file=None):
		
		#############################
		# 応答形式の取得
		#  {"Result" : False, "Reason" : None, "Responce" : None}
		wRes = CLS_Mastodon_Use.sGet_API_Resp()
		
		#############################
		# 初期化されてるか
		if self.IniStatus['Result']!=True :
			wRes['Reason'] = "CLS_Mastodon_Use: log_in: Init failer: " + self.IniStatus['Reason']
			return wRes
		
		if username is not None and password is not None:
			params = self.__generate_params(locals(), ['scopes', 'to_file', 'code', 'refresh_token'])
			params['grant_type'] = 'password'
		elif code is not None:
			params = self.__generate_params(locals(), ['scopes', 'to_file', 'username', 'password', 'refresh_token'])
			params['grant_type'] = 'authorization_code'
		elif refresh_token is not None:
			params = self.__generate_params(locals(), ['scopes', 'to_file', 'username', 'password', 'code'])
			params['grant_type'] = 'refresh_token'
		else:
			wRes['Reason'] = "CLS_Mastodon_Use：log_in：Invalid arguments given. username and password or code are required."
			return wRes
		
		params['client_id'] = self.client_id
		params['client_secret'] = self.client_secret
		params['scope'] = " ".join(scopes)
		
		try:
			res_api = self.__api_request('POST', '/oauth/token', params, do_ratelimiting=False)
			if res_api['Result']!=True :
				wRes['Reason'] = "CLS_Mastodon_Use：log_in：__api_request Failed：" + res_api['Reason']
				return wRes
			
			response = res_api['Responce']
			self.access_token = response['access_token']
			self.__set_refresh_token(response.get('refresh_token'))
			self.__set_token_expired(int(response.get('expires_in', 0)))
		except Exception as e:
			if username is not None or password is not None:
				msg = "CLS_Mastodon_Use：log_in：Invalid user name, password, or redirect_uris：" + str(e)
			elif code is not None:
				msg = "CLS_Mastodon_Use：log_in：Invalid access token or redirect_uris：" + str(e)
			else:
				msg = "CLS_Mastodon_Use：log_in：Invalid request：" + str(e)
			
			wRes['Reason'] = msg
			return wRes
		
		received_scopes = response["scope"].split(" ")
		for scope_set in self.__SCOPE_SETS.keys():
			if scope_set in received_scopes:
				received_scopes += self.__SCOPE_SETS[scope_set]
		
		if not set(scopes) <= set(received_scopes):
			wRes['Reason'] = "CLS_Mastodon_Use：log_in：'Granted scopes "+ " ".join(received_scopes) + " do not contain all of the requested scopes " + " ".join(scopes)
			return wRes
		
		if to_file is not None:
			with open(to_file, 'w') as token_file:
				token_file.write(response['access_token'] + '\n')
		
		self.__logged_in_id = None
		
		wRes['Responce'] = response['access_token']
		wRes['Result']   = True
		return wRes



#####################################################
# トゥート処理
#   spoiler_textにテキストを入れるとCWトゥートになる
#####################################################
	def Toot(self, status = None,
			in_reply_to_id = None,
			media_ids = None,
			sensitive = False,
			visibility = 'unlisted',
			spoiler_text = None):
		
		#############################
		# 応答形式の取得
		#  {"Result" : False, "Reason" : None, "Responce" : None}
		wRes = CLS_Mastodon_Use.sGet_API_Resp()
		
		#############################
		# 空のトゥートは処理しない
		if status==None or status=="" :
			wRes['Reason'] = "CLS_Mastodon_Use：Toot：Status None or null"
			return wRes
		
		#############################
		# 引数を辞書にまとめる
		params_initial = locals()
		
		valid_visibilities = ['private', 'public', 'unlisted', 'direct', '']
		if params_initial['visibility'].lower() not in valid_visibilities:
			wRes['Reason'] = "CLS_Mastodon_Use：Toot：Invalid visibility value"
			return wRes
		
		if params_initial['sensitive'] is False:
			del [params_initial['sensitive']]
		
		if media_ids is not None:
			try:
				media_ids_proper = []
				for media_id in media_ids:
					if isinstance(media_id, dict):
						media_ids_proper.append(media_id["id"])
					else:
						media_ids_proper.append(media_id)
			except Exception as e:
				wRes['Reason'] = "CLS_Mastodon_Use：Toot：Invalid media：" + str(e)
				return wRes
			
			params_initial["media_ids"] = media_ids_proper
		
		#############################
		# APIを叩く
		params = self.__generate_params(params_initial)
		wRes = self.__api_request('POST', '/api/v1/statuses', params)
		return wRes



#####################################################
# ローカルTL取得
#####################################################
	def GetLocalTL(self, timeline="local", max_id=None, since_id=None, limit=None):
		#############################
		# 引数を辞書にまとめる
		if max_id != None:
			max_id = self.__unpack_id(max_id)
		
		if since_id != None:
			since_id = self.__unpack_id(since_id)
		
		params_initial = locals()
		timeline = "public"
		params_initial['local'] = True
		
		#############################
		# APIを叩く
		params = self.__generate_params(params_initial, ['timeline'])
		url = '/api/v1/timelines/{0}'.format(timeline)
		wRes = self.__api_request('GET', url, params)
		return wRes



#####################################################
# ホームTL取得
#####################################################
	def GetHomeTL(self, timeline="home", max_id=None, since_id=None, limit=None):
		#############################
		# 引数を辞書にまとめる
		if max_id != None:
			max_id = self.__unpack_id(max_id)
		
		if since_id != None:
			since_id = self.__unpack_id(since_id)
		
		params_initial = locals()
		
		#############################
		# APIを叩く
		params = self.__generate_params(params_initial, ['timeline'])
		url = '/api/v1/timelines/{0}'.format(timeline)
		wRes = self.__api_request('GET', url, params)
		return wRes



#####################################################
# 連合TL取得
#####################################################
	def GetPublicTL(self, timeline="public", max_id=None, since_id=None, limit=None):
		#############################
		# 引数を辞書にまとめる
		if max_id != None:
			max_id = self.__unpack_id(max_id)
		
		if since_id != None:
			since_id = self.__unpack_id(since_id)
		
		params_initial = locals()
		
		#############################
		# APIを叩く
		params = self.__generate_params(params_initial, ['timeline'])
		url = '/api/v1/timelines/{0}'.format(timeline)
		wRes = self.__api_request('GET', url, params)
		return wRes



#####################################################
# ハッシュタグTL取得
#####################################################
##	def GetHashtagTL(self, hashtag, local=False, max_id=None, since_id=None, limit=None, only_media=False):
	def GetHashtagTL(self, hashtag, local=False, max_id=None, min_id=None, since_id=None, limit=None, only_media=False):
		#############################
		# 応答形式の取得
		#  {"Result" : False, "Reason" : None, "Responce" : None}
		wRes = CLS_Mastodon_Use.sGet_API_Resp()
		
		#############################
		# ハッシュタグが設定されているか
		if hashtag.startswith("#"):
			wRes['Reason'] = "CLS_Mastodon_Use: GetHashtagTL: Hashtag parameter should omit leading #"
			return wRes
		
		#############################
		# 引数を辞書にまとめる
		if max_id != None:
			max_id = self.__unpack_id(max_id)
		
		if min_id != None:
			min_id = self.__unpack_id(min_id)
		
		if since_id != None:
			since_id = self.__unpack_id(since_id)
		
		params_initial = locals()
		
		if local == False:
			del params_initial['local']
		
		if only_media == False:
			del params_initial['only_media']
		
		#############################
		# APIを叩く
		params = self.__generate_params(params_initial, ['hashtag'])
		url = '/api/v1/timelines/tag/{0}'.format(hashtag)
		wRes = self.__api_request('GET', url, params)
		return wRes



#####################################################
# トレンドハッシュタグ取得
#  *limitの最大値は10
#####################################################
	def GetTrends( self, limit=None ):
#		#############################
#		# 応答形式の取得
#		#  {"Result" : False, "Reason" : None, "Responce" : None}
#		wRes = CLS_Mastodon_Use.sGet_API_Resp()
		
		#############################
		# APIを叩く
		params = self.__generate_params(locals())
		url = '/api/v1/trends'
		wRes = self.__api_request('GET', url, params)
		return wRes



#####################################################
# リストTL取得
#####################################################
	def GetListTL( self, id, timeline="", max_id=None, since_id=None, limit=None):
		#############################
		# ベースソースからの取り込み
		id = self.__unpack_id(id)
		timeline='list/{0}'.format(id)
		
		#############################
		# 引数を辞書にまとめる
		if max_id != None:
			max_id = self.__unpack_id(max_id)
		
		if since_id != None:
			since_id = self.__unpack_id(since_id)
		
		params_initial = locals()
		del params_initial['id']
		
		#############################
		# APIを叩く
		params = self.__generate_params(params_initial, ['timeline'])
		url = '/api/v1/timelines/{0}'.format(timeline)
		wRes = self.__api_request('GET', url, params)
		return wRes



#####################################################
# 通知一覧取得
#####################################################
	def GetNotificationList(self, id=None, max_id=None, since_id=None, limit=None):
		#############################
		# 引数を辞書にまとめる
		if max_id != None:
			max_id = self.__unpack_id(max_id)
		if since_id != None:
			since_id = self.__unpack_id(since_id)
		
		#############################
		# APIを叩く
		if id is None:
			params = self.__generate_params(locals(), ['id'])
			wRes = self.__api_request('GET', '/api/v1/notifications', params)
		else:
			id = self.__unpack_id(id)
			url = '/api/v1/notifications/{0}'.format(str(id))
			wRes = self.__api_request('GET', url)
		
		return wRes



#####################################################
# 通知クリア
#####################################################
	def NotificationClear(self):
		#############################
		# APIを叩く
		url = '/api/v1/notifications/clear'
		wRes = self.__api_request('POST', url)
		
		return wRes



#####################################################
# トゥート一覧取得
#####################################################
	def GetTootList(self, id, only_media=False, pinned=False, exclude_replies=False, max_id=None, since_id=None, limit=None):
		#############################
		# 引数を辞書にまとめる
		id = self.__unpack_id(id)
		
		if max_id != None:
			max_id = self.__unpack_id(max_id)
		if since_id != None:
			since_id = self.__unpack_id(since_id)
		
		params = self.__generate_params(locals(), ['id'])
		if pinned == False:
			del params["pinned"]
		if only_media == False:
			del params["only_media"]
		if exclude_replies == False:
			del params["exclude_replies"]
		
		#############################
		# APIを叩く
		url = '/api/v1/accounts/{0}/statuses'.format(str(id))
		wRes = self.__api_request('GET', url, params)
		return wRes



#####################################################
# ファボ一覧
#####################################################
	def GetFavoList(self, max_id=None, since_id=None, limit=None):
		#############################
		# 引数を辞書にまとめる
		if max_id != None:
			max_id = self.__unpack_id(max_id)
		if since_id != None:
			since_id = self.__unpack_id(since_id)
		
		#############################
		# APIを叩く
		params = self.__generate_params(locals())
		url = '/api/v1/favourites'
		wRes = self.__api_request('GET', url, params)
		return wRes



#####################################################
# フォロー一覧
#####################################################
	def GetFollowingList(self, id, max_id=None, since_id=None, limit=None):
		#############################
		# 引数を辞書にまとめる
		id = self.__unpack_id(id)
		
		if max_id != None:
			max_id = self.__unpack_id(max_id)
		if since_id != None:
			since_id = self.__unpack_id(since_id)
		
		#############################
		# APIを叩く
		params = self.__generate_params(locals(), ['id'])
		url = '/api/v1/accounts/{0}/following'.format(str(id))
		wRes = self.__api_request('GET', url, params)
		return wRes



#####################################################
# フォロワー一覧
#####################################################
	def GetFollowersList(self, id, max_id=None, since_id=None, limit=None):
		#############################
		# 引数を辞書にまとめる
		id = self.__unpack_id(id)
		
		if max_id != None:
			max_id = self.__unpack_id(max_id)
		if since_id != None:
			since_id = self.__unpack_id(since_id)
		
		#############################
		# APIを叩く
		params = self.__generate_params(locals(), ['id'])
		url = '/api/v1/accounts/{0}/followers'.format(str(id))
		wRes = self.__api_request('GET', url, params)
		return wRes



#####################################################
# 自アカウント情報取得
#####################################################
	def GetMyAccountInfo(self):
		#############################
		# APIを叩く
		url = '/api/v1/accounts/verify_credentials'
		wRes = self.__api_request('GET', url)
		return wRes



#####################################################
# 対アカウント情報取得
#####################################################
	def GetAccountStat(self, id):
		#############################
		# 引数を辞書にまとめる
		id = self.__unpack_id(id)
		params = self.__generate_params(locals())
		
		#############################
		# APIを叩く
		url = '/api/v1/accounts/relationships'
		wRes = self.__api_request('GET', url, params)
		return wRes



#####################################################
# フォロー
#####################################################
	def Follow( self, id, reblogs=True ):
		#############################
		# 引数を辞書にまとめる
		id = self.__unpack_id(id)
		params = self.__generate_params(locals())
		
		if params["reblogs"] == None:
			del params["reblogs"]
		
		#############################
		# APIを叩く
		url = '/api/v1/accounts/{0}/follow'.format(str(id))
		wRes = self.__api_request('POST', url)
		return wRes



#####################################################
# リムーブ
#####################################################
	def Remove(self, id):
		#############################
		# 引数を辞書にまとめる
		id = self.__unpack_id(id)
		
		#############################
		# APIを叩く
		url = '/api/v1/accounts/{0}/unfollow'.format(str(id))
		wRes = self.__api_request('POST', url)
		return wRes



#####################################################
# ファボ
#####################################################
	def Favo(self, id):
		#############################
		# 引数を辞書にまとめる
		id = self.__unpack_id(id)
		
		#############################
		# APIを叩く
		url = '/api/v1/statuses/{0}/favourite'.format(str(id))
		wRes = self.__api_request('POST', url)
		return wRes



#####################################################
# ブースト
#####################################################
	def Boost(self, id):
		#############################
		# 引数を辞書にまとめる
		id = self.__unpack_id(id)
		
		#############################
		# APIを叩く
		url = '/api/v1/statuses/{0}/reblog'.format(str(id))
		wRes = self.__api_request('POST', url)
		return wRes



#####################################################
# ブロック
#####################################################
	def Block(self, id):
		#############################
		# 引数を辞書にまとめる
		id = self.__unpack_id(id)
		
		#############################
		# APIを叩く
		url = '/api/v1/accounts/{0}/block'.format(str(id))
		wRes = self.__api_request('POST', url)
		return wRes



#####################################################
# ブロック解除
#####################################################
	def Unblock(self, id):
		#############################
		# 引数を辞書にまとめる
		id = self.__unpack_id(id)
		
		#############################
		# APIを叩く
		url = '/api/v1/accounts/{0}/unblock'.format(str(id))
		wRes = self.__api_request('POST', url)
		return wRes



#####################################################
# ミュート
#####################################################
	def Mute(self, id):
		#############################
		# 引数を辞書にまとめる
		id = self.__unpack_id(id)
		
		#############################
		# APIを叩く
		url = '/api/v1/accounts/{0}/mute'.format(str(id))
		wRes = self.__api_request('POST', url)
		return wRes



#####################################################
# ブロック解除
#####################################################
	def Unmute(self, id):
		#############################
		# 引数を辞書にまとめる
		id = self.__unpack_id(id)
		
		#############################
		# APIを叩く
		url = '/api/v1/accounts/{0}/unmute'.format(str(id))
		wRes = self.__api_request('POST', url)
		return wRes



#####################################################
# リスト作成
#####################################################
	def CreateList(self, title ):
		#############################
		# 引数を辞書にまとめる
		params = self.__generate_params(locals())
		
		#############################
		# APIを叩く
		url = '/api/v1/lists'
		wRes = self.__api_request('POST', url, params)
		return wRes



#####################################################
# リスト更新 (名前変更)
#####################################################
	def UpdateList(self, id, title):
		#############################
		# 引数を辞書にまとめる
		id = self.__unpack_id(id)
		params = self.__generate_params(locals(), ['id'])
		
		#############################
		# APIを叩く
		url = '/api/v1/lists/{0}'.format(id)
		wRes = self.__api_request('PUT', url, params)
		return wRes



#####################################################
# リスト更新 (名前変更)
#####################################################
	def DeleteList(self, id):
		#############################
		# 引数を辞書にまとめる
		id = self.__unpack_id(id)
		
		#############################
		# APIを叩く
		url = '/api/v1/lists/{0}'.format(id)
		wRes = self.__api_request('DELETE', url, params)
		return wRes



#####################################################
# リスト アカウント追加
#####################################################
	def AddAccount_List( self, id, account_ids ):
		#############################
		# 引数を辞書にまとめる
		id = self.__unpack_id(id)
		
		if not isinstance(account_ids, list):
			account_ids = [account_ids]
		
		account_ids = list(map(lambda x: self.__unpack_id(x), account_ids))
		params = self.__generate_params(locals(), ['id'])		
		
		#############################
		# APIを叩く
		url = '/api/v1/lists/{0}/accounts'.format(id)
		wRes = self.__api_request('POST', url, params)
		return wRes



#####################################################
# リスト アカウント削除
#####################################################
	def DelAccount_List(self, id, account_ids):
		#############################
		# 引数を辞書にまとめる
		id = self.__unpack_id(id)
		
		if not isinstance(account_ids, list):
			account_ids = [account_ids]
		
		account_ids = list(map(lambda x: self.__unpack_id(x), account_ids))
		params = self.__generate_params(locals(), ['id'])		
		
		#############################
		# APIを叩く
		url = '/api/v1/lists/{0}/accounts'.format(id)
		wRes = self.__api_request('DELETE', url, params)
		return wRes



#####################################################
# json data parse
#####################################################
	def __json_date_parse(self, json_object):
		known_date_fields = ["created_at"]
		for k, v in json_object.items():
			if k in known_date_fields:
				if isinstance(v, int):
					json_object[k] = datetime.datetime.fromtimestamp(v, pytz.utc)
				else:
					json_object[k] = dateutil.parser.parse(v)
				
		return json_object



#####################################################
# API datetime_to_epoch
#####################################################
	def __datetime_to_epoch(self, date_time):
		date_time_utc = None
		if date_time.tzinfo is None:
			date_time_utc = date_time.replace(tzinfo=pytz.utc)
		else:
			date_time_utc = date_time.astimezone(pytz.utc)
		
		epoch_utc = datetime.datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
		return (date_time_utc - epoch_utc).total_seconds()



#####################################################
# APIリクエスト
#####################################################
	def __api_request(self, method, endpoint, params={}, files={}, headers={}, do_ratelimiting=True):
		#############################
		# 応答形式の取得
		#  {"Result" : False, "Reason" : None, "Responce" : None}
		wRes = CLS_Mastodon_Use.sGet_API_Resp()
		
		response = None
		
##		#############################
##		# レートリミットの設定
##		#   デフォルトだと未設定になる。いらないかも...
##		remaining_wait = 0
##		if do_ratelimiting and self.ratelimit_method == "pace":
##			if self.ratelimit_remaining == 0:
##				to_next = self.ratelimit_reset - time.time()
##				if to_next > 0:
##					# 最長5分待ち？
##					to_next = min(to_next, 5 * 60)
##					time.sleep(to_next)
##			else:
##				time_waited = time.time() - self.ratelimit_lastcall
##				time_wait = float(self.ratelimit_reset - time.time()) / float(self.ratelimit_remaining)
##				remaining_wait = time_wait - time_waited
##			
##			if remaining_wait > 0:
##				to_next = remaining_wait / self.ratelimit_pacefactor
##				to_next = min(to_next, 5 * 60)
##				time.sleep(to_next)
		
		#############################
		# リクエストヘッダー
		headers = copy.deepcopy(headers)
		if self.access_token is not None:
			headers['Authorization'] = 'Bearer ' + self.access_token

		
####デバッグ情報のため使わない
###		if self.debug_requests:
##			print('Mastodon: Request to endpoint "' + endpoint + '" using method "' + method + '".')
##			print('Parameters: ' + str(params))
##			print('Headers: ' + str(headers))
##			print('Files: ' + str(files))
####
		
		#############################
		# リクエスト
		#   応答429が受かったらもう1周待つ
		request_complete  = False
		self.rate429_wait = 0
		while not request_complete:	
			request_complete = True	#何もなければこの周でloop終わり
			response_object  = None
			
			try:
				kwargs = dict(headers=headers, files=files, timeout=self.request_timeout)
				if method == 'GET':
					kwargs['params'] = params
				else:
					kwargs['data'] = params
				
				response_object = self.session.request(method, self.api_base_url + endpoint, **kwargs)
			except Exception as e:
				wStr = "__api_request: Could not complete request: " + str(e)
				wStr = wStr + " method=" + method + " endpoint=" + endpoint + " " + self.__delPassword( params )
				wRes['Reason'] = wStr
				return wRes
			
			#############################
			# 応答がない(=異常)
			if response_object is None:
				wStr = "__api_request: Illegal request"
				wRes['Reason'] = wStr
				return wRes
			
			#############################
			# 待機時間の設定
			if 'X-RateLimit-Remaining' in response_object.headers and do_ratelimiting:
				self.ratelimit_remaining = int(response_object.headers['X-RateLimit-Remaining'])
				self.ratelimit_limit	 = int(response_object.headers['X-RateLimit-Limit'])
				try:
					ratelimit_reset_datetime = dateutil.parser.parse(response_object.headers['X-RateLimit-Reset'])
					self.ratelimit_reset	 = self.__datetime_to_epoch(ratelimit_reset_datetime)
					
					# Adjust server time to local clock
					if 'Date' in response_object.headers:
						server_time_datetime = dateutil.parser.parse(response_object.headers['Date'])
						server_time	  = self.__datetime_to_epoch(server_time_datetime)
						server_time_diff = time.time() - server_time
						self.ratelimit_reset += server_time_diff
						self.ratelimit_lastcall = time.time()
				except Exception as e:
					wStr = "__api_request: Rate limit time calculations failed: " + str(e)
					wRes['Reason'] = wStr
					return wRes
			

####デバッグ
##			if self.debug_requests:
##				print('Mastodon: Response received with code ' + str(response_object.status_code) + '.')
##				print('response headers: ' + str(response_object.headers))
##				print('Response text content: ' + str(response_object.text))
####

			#############################
			# 無応答だった場合
			if not response_object.ok:
				try:
					response = response_object.json(object_hook=self.__json_hooks)
					if not isinstance(response, dict) or 'error' not in response:
						error_msg = None
					error_msg = response['error']
				except ValueError:
					error_msg = None
				
				#############################
				# 応答=429 wait
				if response_object.status_code == 429:
##					if self.ratelimit_method == 'throw' or not do_ratelimiting:
##						raise MastodonRatelimitError('Hit rate limit.')
##					elif self.ratelimit_method in ('wait', 'pace'):
##						to_next = self.ratelimit_reset - time.time()
##						if to_next > 0:
##							# As a precaution, never sleep longer than 5 minutes
##							to_next = min(to_next, 5 * 60)
##							time.sleep(to_next)
##							request_complete = False
##							continue
					
					if self.max_rate429_wait>self.rate429_wait :
						time.sleep( self.rate429_waittime )
						self.rate429_wait += 1
						request_complete = False
						continue
					else :
						### 待ちタイムアウト
						wStr = "__api_request: Responce 429 : Rate over: Wait time=" + str( self.rate429_waittime * self.max_rate429_wait ) + ".s"
						wRes['Reason'] = wStr
						return wRes
				
				#############################
				# 応答=404 無応答
				if response_object.status_code == 404:
					wStr = "__api_request: Responce 404 : Endpoint is not found: "
				
				#############################
				# 応答=401
				elif response_object.status_code == 401:
					wStr = "__api_request: Responce 401 : Unauthorized error: "
				
				#############################
				# その他のエラー
				else:
					wStr = "__api_request: API error: "
				
				#############################
				# 応答を返す( NGルート)
				wStr = wStr + "Status code=" + str(response_object.status_code)
				wStr = wStr + " Reason=" + str(response_object.reason) + " Msg=" + str(error_msg)
				wRes['Reason'] = wStr
				return wRes
			
			#############################
			# レスポンスを取り込む
			try:
				response = response_object.json( object_hook=self.__json_hooks )
			
			except:
				wStr = "__api_request: API error: Could not parse response as JSON: "
				wStr = wStr + "Status code=" + str(response_object.status_code)
				wStr = wStr + " Content=" + str(response_object.content)
				wRes['Reason'] = wStr
				return wRes
			
			#############################
			# Parse link headersの編集
			if isinstance(response, list) and \
					'Link' in response_object.headers and \
					response_object.headers['Link'] != "":
				tmp_urls = requests.utils.parse_header_links(
					response_object.headers['Link'].rstrip('>').replace('>,<', ',<'))
				for url in tmp_urls:
					if 'rel' not in url:
						continue
					
					if url['rel'] == 'next':
						next_url = url['url']
						matchgroups = re.search(r"max_id=([0-9]*)", next_url)
						
						if matchgroups:
							next_params = copy.deepcopy(params)
							next_params['_pagination_method'] = method
							next_params['_pagination_endpoint'] = endpoint
							next_params['max_id'] = int(matchgroups.group(1))
							if "since_id" in next_params:
								del next_params['since_id']
							response[-1]._pagination_next = next_params
					
					if url['rel'] == 'prev':
						prev_url = url['url']
						matchgroups = re.search(r"since_id=([0-9]*)", prev_url)
					
						if matchgroups:
							prev_params = copy.deepcopy(params)
							prev_params['_pagination_method'] = method
							prev_params['_pagination_endpoint'] = endpoint
							prev_params['since_id'] = int(matchgroups.group(1))
							if "max_id" in prev_params:
								del prev_params['max_id']
							response[0]._pagination_prev = prev_params
			#############################
		
###		return response
		wRes['Responce'] = response
		wRes['Result'] = True
		return wRes



#####################################################
	@staticmethod
	def __json_hooks( json_object ):
		json_object = CLS_Mastodon_Use.__json_strnum_to_bignum( json_object )
		json_object = CLS_Mastodon_Use.__json_date_parse( json_object )
		json_object = CLS_Mastodon_Use.__json_truefalse_parse( json_object )
		json_object = CLS_Mastodon_Use.__json_allow_dict_attrs( json_object )
		return json_object

	@staticmethod
	def __json_strnum_to_bignum(json_object):
		for key in ('id', 'week', 'in_reply_to_id', 'in_reply_to_account_id', 'logins', 'registrations', 'statuses'):
			if (key in json_object and isinstance(json_object[key], six.text_type)):
				try:
					json_object[key] = int(json_object[key])
				except ValueError:
					pass
		
		return json_object

	@staticmethod
	def __json_date_parse(json_object):
		known_date_fields = ["created_at", "week", "day", "expires_at"]
		for k, v in json_object.items():
			if k in known_date_fields:
				if v != None:
					try:
						if isinstance(v, int):
							json_object[k] = datetime.datetime.fromtimestamp(v, pytz.utc)
						else:
							json_object[k] = dateutil.parser.parse(v)
					except:
###						raise MastodonAPIError('Encountered invalid date.')
						pass
		
		return json_object

	@staticmethod
	def __json_truefalse_parse(json_object):
		for key in ('follow', 'favourite', 'reblog', 'mention'):
			if (key in json_object and isinstance(json_object[key], six.text_type)):
				if json_object[key] == 'True':
					json_object[key] = True
				if json_object[key] == 'False':
					json_object[key] = False
		
		return json_object

	@staticmethod
	def __json_allow_dict_attrs(json_object):
		if isinstance(json_object, dict):
			return AttribAccessDict(json_object)
		return json_object

#####################################################
	@staticmethod
	def __delPassword( inParams ):
		wParams = inParams
		if 'username' in wParams :
			del wParams['username']
		if 'password' in wParams :
			del wParams['password']
		if 'client_id' in wParams :
			del wParams['client_id']
		if 'client_secret' in wParams :
			del wParams['client_secret']
		
		return str(wParams)



#####################################################
# 引数の辞書化
#####################################################
	def __generate_params(self, params, exclude=[]):
		params = dict(params)
		del params['self']
		param_keys = list(params.keys())
		for key in param_keys:
			if params[key] is None or key in exclude:
				del params[key]
		
		param_keys = list(params.keys())
		for key in param_keys:
			if isinstance(params[key], list):
				params[key + "[]"] = params[key]
				del params[key]
		
		return params

#####################################################
# Internal object-to-id converter
#####################################################
	def __unpack_id(self, id):
		if isinstance(id, dict) and "id" in id:
			return id["id"]
		else:
			return id

#####################################################
# Internal helper for oauth code
#####################################################
	def __get_token_expired(self):
		return self._token_expired < datetime.datetime.now()

#####################################################
# Internal helper for oauth code
#####################################################
	def __set_token_expired(self, value):
		self._token_expired = datetime.datetime.now() + datetime.timedelta(seconds=value)
		return

#####################################################
# Internal helper for oauth code
#####################################################
	def __get_refresh_token(self):
		return self._refresh_token

#####################################################
# Internal helper for oauth code
#####################################################
	def __set_refresh_token(self, value):
		self._refresh_token = value
		return



