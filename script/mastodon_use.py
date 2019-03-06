#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：mastodon API (mastodon.py v1.3ベース改)
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/3/5
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
#
# ◇一覧取得系
#   GetNotificationList(self, id=None, max_id=None, since_id=None, limit=None):
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
import sys
import mimetypes
import time
import random
import string
import datetime
from contextlib import closing
import pytz
import requests
from requests.models import urlencode
import dateutil
import dateutil.parser
import re
import copy
import threading

#####################################################
class CLS_Mastodon_Use:
#####################################################
	__DEFAULT_BASE_URL = 'https://mastodon.social'	#mastodon旗艦サーバ(mastodon.py 1.3のまま)
	__DEFAULT_TIMEOUT  = 300
	
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
			"Responce" : None
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
			scopes=['read', 'write', 'follow'],
			redirect_uris=None, website=None, to_file=None,
			api_base_url=__DEFAULT_BASE_URL,
			request_timeout=__DEFAULT_TIMEOUT):
		
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
				request_data['redirect_uris'] = redirect_uris
			else:
				request_data['redirect_uris'] = 'urn:ietf:wg:oauth:2.0:oob'
			if website is not None:
				request_data['website'] = website
			
			response = requests.post(api_base_url + '/api/v1/apps', data=request_data, timeout=request_timeout)
			response = response.json()
		except Exception as e:
			wRes['Reason']   = "CLS_Mastodon_Use：create_app：Could not complete request：" + str(e)
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
	def __init__( self, client_id, api_base_url=__DEFAULT_BASE_URL, access_token=None, flg_orginit=False ):
		#############################
		# パラメータの設定
		self.api_base_url = CLS_Mastodon_Use.__protocolize(api_base_url)
		self.client_id = client_id
		self.access_token = access_token
		
		self.client_secret = None
		self.debug_requests = False
		self._token_expired = datetime.datetime.now()
		self._refresh_token = None
		self.request_timeout = self.__DEFAULT_TIMEOUT
		
		self.ratelimit_limit = 300
		self.ratelimit_reset = time.time()
		self.ratelimit_remaining = 300
		self.ratelimit_lastcall = time.time()
		
		#############################
		# Init状態
		self.__initIniStatus()
		
		#############################
		# シークレットキーの取得
		if os.path.isfile(self.client_id):
			with open(self.client_id, 'r') as secret_file:
				self.client_id = secret_file.readline().rstrip()
				self.client_secret = secret_file.readline().rstrip()
		else:
			self.IniStatus['Reason'] = "CLS_Mastodon_Use：__init__：Specified client id directly, but did not supply secret"
			self.IniStatus['Result'] = False
			return
		
		#############################
		# アクセストークンの取得
		if self.access_token is not None and os.path.isfile(self.access_token):
			with open(self.access_token, 'r') as token_file:
				self.access_token = token_file.readline().rstrip()
		
		#############################
		# オリジナルの初期化
		#   アクセストークン必須
		if flg_orginit==True:
			if self.access_token is None:
				self.IniStatus['Reason'] = "CLS_Mastodon_Use：__init__：access_token is None"
				return
			
			if self.access_token=="":
				self.IniStatus['Reason'] = "CLS_Mastodon_Use：__init__：access_token is null"
				return
		
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
			scopes=['read', 'write', 'follow'],
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
		
		requested_scopes = " ".join(sorted(scopes))
		received_scopes = " ".join(sorted(response["scope"].split(" ")))
		if requested_scopes != received_scopes:
			wRes['Reason'] = "CLS_Mastodon_Use：log_in：Granted scopes received."
			return wRes
		
		if to_file is not None:
			with open(to_file, 'w') as token_file:
				token_file.write(response['access_token'] + '\n')
		
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
	def GetHashtagTL(self, hashtag, local=False, max_id=None, since_id=None, limit=None, only_media=False):
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
	def __api_request(self, method, endpoint, params={}, files={}, do_ratelimiting=True):
		response = None
		headers = None
		remaining_wait = 0
		
		#############################
		# 応答形式の取得
		#  {"Result" : False, "Reason" : None, "Responce" : None}
		wRes = CLS_Mastodon_Use.sGet_API_Resp()
		
		#############################
		# リクエストヘッダー
		if self.access_token is not None:
			headers = {'Authorization': 'Bearer ' + self.access_token}
		
		#############################
		# リクエスト
		response_object = None
		try:
			if method == 'GET':
				response_object = requests.get(self.api_base_url + endpoint, params=params, 
												headers=headers, files=files, 
												timeout=self.request_timeout)
			if method == 'POST':
				response_object = requests.post(self.api_base_url + endpoint, data=params, headers=headers,
												files=files, timeout=self.request_timeout)
			if method == 'PATCH':
				response_object = requests.patch(self.api_base_url + endpoint, data=params, headers=headers,
												files=files, timeout=self.request_timeout)
			if method == 'DELETE':
				response_object = requests.delete(self.api_base_url + endpoint, data=params, headers=headers,
												files=files, timeout=self.request_timeout)
		except Exception as e:
			wRes['Reason'] = "API Responce: Could not complete request: " + str(e) + " method=" + method + " endpoint=" + endpoint + " " + self.__delPassword( params )
			return wRes
		
		#############################
		# 応答があったか
		if response_object is None:
			wRes['Reason'] = "API Responce：Illegal request：" + " method=" + method + " endpoint=" + endpoint + " " + self.__delPassword( params )
			return wRes
		
		if response_object.status_code == 404:
			wRes['Reason'] = "API Responce：404 ERR：" + " method=" + method + " endpoint=" + endpoint + " " + self.__delPassword( params )
			return wRes
		elif response_object.status_code == 500:
			wRes['Reason'] = "API Responce：500 ERR：" + " method=" + method + " endpoint=" + endpoint + " " + self.__delPassword( params )
			return wRes
		elif response_object.status_code != 200:
			wRes['Reason'] = "API Responce：" + str(response_object.status_code) + " ERR" + " method=" + method + " endpoint=" + endpoint + " " + self.__delPassword( params )
			return wRes
		
		#############################
		# レスポンスを取り込む
		try:
			res_json = response_object.json(object_hook=self.__json_date_parse)
		except:
			wRes['Reason'] = "API Responce：Could not parse response as JSON：status code：" + str(response_object.status_code) \
								+ " method=" + method + " endpoint=" + endpoint + " " + self.__delPassword( params )
			wRes['Responce'] = res_json
			return wRes
		
		if isinstance(res_json, dict) and 'error' in res_json:
			wRes['Reason'] = "API Responce：Mastodon API returned error：" + str(res_json['error']) \
								+ " method=" + method + " endpoint=" + endpoint + " " + self.__delPassword( params )
			wRes['Responce'] = res_json
			return wRes
		
		#############################
		# ページネーション属性を編集
		if isinstance(res_json, list) and \
			'Link' in response_object.headers and \
			response_object.headers['Link'] != "":
			tmp_urls = requests.utils.parse_header_links(
						response_object.headers['Link'].rstrip('>').replace('>,<', ',<'))
			for url in tmp_urls:
				if 'rel' not in url:
					continue
				
				if url['rel'] == 'next':
					# Be paranoid and extract max_id specifically
					next_url = url['url']
					matchgroups = re.search(r"max_id=([0-9]*)", next_url)
					if matchgroups:
						next_params = copy.deepcopy(params)
						next_params['_pagination_method'] = method
						next_params['_pagination_endpoint'] = endpoint
						next_params['max_id'] = int(matchgroups.group(1))
						if "since_id" in next_params:
							del next_params['since_id']
						res_json[-1]['_pagination_next'] = next_params
				
				if url['rel'] == 'prev':
					# Be paranoid and extract since_id specifically
					prev_url = url['url']
					matchgroups = re.search(r"since_id=([0-9]*)", prev_url)
					if matchgroups:
						prev_params = copy.deepcopy(params)
						prev_params['_pagination_method'] = method
						prev_params['_pagination_endpoint'] = endpoint
						prev_params['since_id'] = int(matchgroups.group(1))
						if "max_id" in prev_params:
							del prev_params['max_id']
							res_json[0]['_pagination_prev'] = prev_params
		
		wRes['Responce'] = res_json
		wRes['Result'] = True
		return wRes

#####################################################
	def __delPassword( self, inParams ):
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



