#!/usr/bin/python
# coding: UTF-8
#####################################################
# るしぼっと4
#   Class   ：mastodon API (v1.3改)
#   Site URL：https://mynoghra.jp/
#   Update  ：2019/2/24
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

import global_val
#####################################################
class CLS_Mastodon_Use:
	__DEFAULT_BASE_URL = 'https://mastodon.social'
	__DEFAULT_TIMEOUT = 300
    
	Flg_Init = False						# 初期化完了
	Mastodon_use = ''						# Mastodonモジュール実体


#####################################################
# Init
#####################################################
	def cInit(self):
##		#############################
##		# configの確認
##		if global_val.gConfig["BaseUrl"] == "" or \
##		   global_val.gConfig["UserBot"] == "" :
##			return
		
##		#############################
##		# 自IDの設定
##		user_list = self.cGetMyAccountInfo()
##		if len( user_list ) == 0:
##			return	#configファイルの設定ミスかも
##		
##		user_id = user_list['id']
##		arr_user = global_val.gConfig["UserBot"].split('@')
##		global_val.gMyID = arr_user[0]
##		global_val.gMyIDnum = user_id
		
		#############################
		# 初期化完了
		self.Flg_Init = True
		return



#####################################################
# トゥート処理
#   status    ：トゥート本文
#   visibility：公開範囲
#   in_reply_to_id：紐付けリプライID
#####################################################
	def cToot( self, status, visibility='unlisted', in_reply_to_id=0 ):
		res = self.__get_api_responce()
		
		#############################
		# 空のトゥートは処理しない
		if status=='' :
			return res
		
		#############################
		# 紐付けオプションによる
		if in_reply_to_id == 0 :
			responce = self.__status_post( status=status, visibility=visibility )
		else :
			responce = self.__status_post( status=status, visibility=visibility, in_reply_to_id=in_reply_to_id )
		
		#############################
		# API処理結果の検証
		if responce['result']!=True :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Mastodon_Use：cToos：Post失敗：' + responce['reason'] )
			return responce
		
		return responce



#####################################################
# CW付きトゥート処理
#   spoiler_text：CWヘッダ
#   status    ：トゥート本文
#   visibility：公開範囲
#   in_reply_to_id：紐付けリプライID
#####################################################
	def cCwToot( self, spoiler_text, status, visibility='unlisted', in_reply_to_id=0 ):
		res = self.__get_api_responce()
		
		#############################
		# 空のトゥートは処理しない
		if spoiler_text=='' or status=='' :
			return res
		
		#############################
		# 紐付けオプションによる
		if in_reply_to_id == 0 :
			responce = self.__status_post( spoiler_text=spoiler_text, status=status, visibility=visibility )
		else :
			responce = self.__status_post( spoiler_text=spoiler_text, status=status, visibility=visibility, in_reply_to_id=in_reply_to_id )
		
		#############################
		# API処理結果の検証
		if responce['result']!=True :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Mastodon_Use：cCwToot：Post失敗：' + responce['reason'] )
			return responce
		
		return responce



#####################################################
# ローカルTL取得
#####################################################
	def cGetTimeline_Local( self, limit=40, max_id=0 ):
		res = self.__get_api_responce()
		
		#############################
		# max_idオプションによる
		if max_id == 0 :
			responce = self.__timeline_local( limit=limit )
		else :
			responce = self.__timeline_local( limit=limit, max_id=max_id )
		
		#############################
		# API処理結果の検証
		if responce['result']!=True :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Mastodon_Use：cGetTimeline_Local：TL取得失敗：' + responce['reason'] )
###			return []
		
###		return responce['responce']
		return responce



#####################################################
# ホームTL取得
#####################################################
	def cGetTimeline_Home( self, limit=40, max_id=0 ):
		res = self.__get_api_responce()
		
		#############################
		# max_idオプションによる
		if max_id == 0 :
			responce = self.__timeline_home( limit=limit )
		else :
			responce = self.__timeline_home( limit=limit, max_id=max_id )
		
		#############################
		# API処理結果の検証
		if responce['result']!=True :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Mastodon_Use：cGetTimeline_Home：TL取得失敗：' + responce['reason'] )
###			return []
		
###		return responce['responce']
		return responce



#####################################################
# 連合TL取得
#####################################################
	def cGetTimeline_Public( self, limit=40, max_id=0 ):
		res = self.__get_api_responce()
		
		#############################
		# max_idオプションによる
		if max_id == 0 :
			responce = self.__timeline_public( limit=limit )
		else :
			responce = self.__timeline_public( limit=limit, max_id=max_id )
		
		#############################
		# API処理結果の検証
		if responce['result']!=True :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Mastodon_Use：cGetTimeline_Public：TL取得失敗：' + responce['reason'] )
###			return []
		
###		return responce['responce']
		return responce



#####################################################
# 通知一覧取得
#####################################################
	def cGetNotificationList( self, limit=40, max_id=0 ):
		res = self.__get_api_responce()
		
		#############################
		# max_idオプションによる
		if max_id == 0 :
			responce = self.__notification_list( limit=limit )
		else :
			responce = self.__notification_list( limit=limit, max_id=max_id )
		
		#############################
		# API処理結果の検証
		if responce['result']!=True :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Mastodon_Use：cGetNotificationList：通知取得失敗：' + responce['reason'] )
###			return []
		
###		return responce['responce']
		return responce



#####################################################
# トゥート一覧取得
#####################################################
	def cGetTootList( self, id, limit=40, max_id=0 ):
		res = self.__get_api_responce()
		
		#############################
		# max_idオプションによる
		if max_id == 0 :
##			responce = self.__account_statuses( limit=limit )
			responce = self.__account_statuses( id=id, limit=limit )
		else :
##			responce = self.__account_statuses( limit=limit, max_id=max_id )
			responce = self.__account_statuses( id=id, limit=limit, max_id=max_id )
		
		#############################
		# API処理結果の検証
		if responce['result']!=True :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Mastodon_Use：cGetTootList：TL取得失敗：' + responce['reason'] )
###			return []
		
###		return responce['responce']
		return responce



#####################################################
# ファボ一覧取得
#####################################################
	def cGetFavoList( self, limit=40, max_id=0 ):
		res = self.__get_api_responce()
		
		#############################
		# max_idオプションによる
		if max_id == 0 :
			responce = self.__favourites( limit=limit )
		else :
			responce = self.__favourites( limit=limit, max_id=max_id )
		
		#############################
		# API処理結果の検証
		if responce['result']!=True :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Mastodon_Use：cGetFavoList：取得失敗：' + responce['reason'] )
###			return []
		
###		return responce['responce']
		return responce



#####################################################
# フォロー一覧取得
#####################################################
	def cGetFollowingList( self, id, limit=40, max_id=0 ):
		res = self.__get_api_responce()
		
		#############################
		# max_idオプションによる
		if max_id == 0 :
			responce = self.__account_following( limit=limit )
		else :
			responce = self.__account_following( limit=limit, max_id=max_id )
		
		#############################
		# API処理結果の検証
		if responce['result']!=True :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Mastodon_Use：cGetFollowingList：取得失敗：' + responce['reason'] )
###			return []
		
###		return responce['responce']
		return responce




#####################################################
# フォロワー一覧取得
#####################################################
	def cGetFollowersList( self, id, limit=40, max_id=0 ):
		res = self.__get_api_responce()
		
		#############################
		# max_idオプションによる
		if max_id == 0 :
			responce = self.__account_followers( limit=limit )
		else :
			responce = self.__account_followers( limit=limit, max_id=max_id )
		
		#############################
		# API処理結果の検証
		if responce['result']!=True :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Mastodon_Use：cGetFollowersList：取得失敗：' + responce['reason'] )
###			return []
		
###		return responce['responce']
		return responce



#####################################################
# 自アカウント情報取得
#####################################################
	def cGetMyAccountInfo(self):
		res = self.__get_api_responce()
		
		responce = self.__account_verify_credentials()
		
		#############################
		# API処理結果の検証
		if responce['result']!=True :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Mastodon_Use：cGetFollowersList：取得失敗：' + responce['reason'] )
###			return []
		
###		return responce['responce']
		return responce



#####################################################
# 対アカウント情報取得
# [{ u'requested': False,
#    u'muting': False,
#    u'followed_by': False,
#    u'blocking': False,
#    u'following': False,
#    u'id': id }]
#####################################################
	def cGetAccountStat( self, id ):
		res = self.__get_api_responce()
		
		responce = self.__account_relationships(id)
		
		#############################
		# API処理結果の検証
		if responce['result']!=True :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Mastodon_Use：cGetAccountStat：取得失敗：' + responce['reason'] )
###			return []
		
###		return responce['responce']
		return responce



#####################################################
# フォローする
#####################################################
	def cIDFollow( self, id ):
		res = self.__get_api_responce()
		
		responce = self.__account_follow(id)
		
		#############################
		# API処理結果の検証
		if responce['result']!=True :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Mastodon_Use：cIDFollow：フォロー失敗：' + responce['reason'] )
###			return False
		
###		return True
		return responce



#####################################################
# リムーブする
#####################################################
	def cIDRemove( self, id ):
		res = self.__get_api_responce()
		
		responce = self.__account_unfollow(id)
		
		#############################
		# API処理結果の検証
		if responce['result']!=True :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Mastodon_Use：cIDRemove：リムーブ失敗：' + responce['reason'] )
###			return False
		
###		return True
		return responce



#####################################################
# ファボる
#####################################################
	def cFavourite( self, id ):
		res = self.__get_api_responce()
		
		responce = self.__status_favourite(id)
		
		#############################
		# API処理結果の検証
		if responce['result']!=True :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Mastodon_Use：cFavourite：ファボ失敗：' + responce['reason'] )
###			return False
		
###		return True
		return responce



#####################################################
# ブースト
#####################################################
	def cBoost( self, id ):
		res = self.__get_api_responce()
		
		responce = self.__status_reblog(id)
		
		#############################
		# API処理結果の検証
		if responce['result']!=True :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Mastodon_Use：cBoost：ファボ失敗：' + responce['reason'] )
###			return False
		
###		return True
		return responce



#####################################################
# ブロック
#####################################################
	def cBlock( self, id ):
		res = self.__get_api_responce()
		
		responce = self.__status_block(id)
		
		#############################
		# API処理結果の検証
		if responce['result']!=True :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Mastodon_Use：cBlock：ブロック失敗：' + responce['reason'] )
###			return False
		
###		return True
		return responce



#####################################################
# ブロック解除
#####################################################
	def cUnblock( self, id ):
		res = self.__get_api_responce()
		
		responce = self.__status_unblock(id)
		
		#############################
		# API処理結果の検証
		if responce['result']!=True :
			global_val.gCLS_Mylog.cLog('a', 'CLS_Mastodon_Use：cUnblock：ブロック解除失敗：' + responce['reason'] )
###			return False
		
###		return True
		return responce



#####################################################
# API部
#####################################################
#####################################################
# アプリ生成
#####################################################
	@staticmethod
	def create_app( client_name,
			scopes=['read', 'write', 'follow'],
			redirect_uris=None, website=None, to_file=None,
			api_base_url=__DEFAULT_BASE_URL,
			request_timeout=__DEFAULT_TIMEOUT):
		
		api_base_url = CLS_Mastodon_Use.__protocolize(api_base_url)
		
		request_data = {
			'client_name': client_name,
			'scopes': " ".join(scopes)
		}
		
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
			print( "CLS_Mastodon_Use：create_app：Could not complete request：" + str(e) )
			return (response['client_id'], response['client_secret'])
		
		if to_file is not None:
			with open(to_file, 'w') as secret_file:
				secret_file.write(response['client_id'] + '\n')
				secret_file.write(response['client_secret'] + '\n')
		
		return (response['client_id'], response['client_secret'])



#####################################################
	@staticmethod
	def __protocolize(base_url):
		if not base_url.startswith("http://") and not base_url.startswith("https://"):
			base_url = "https://" + base_url
		base_url = base_url.rstrip("/")
		return base_url



#####################################################
# Init
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
		# シークレットキーの取得
		if os.path.isfile(self.client_id):
			with open(self.client_id, 'r') as secret_file:
				self.client_id = secret_file.readline().rstrip()
				self.client_secret = secret_file.readline().rstrip()
		else:
			msg = "CLS_Mastodon_Use：__init__：Specified client id directly, but did not supply secret"
			cPrint(msg)
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
				msg = "CLS_Mastodon_Use：__init__：access_token is None"
				cPrint(msg)
				return
			self.cInit()
		return



#####################################################
# ログイン
#####################################################
	def log_in(self, username=None, password=None,
			code=None,
			redirect_uri="urn:ietf:wg:oauth:2.0:oob",
			refresh_token=None,
			scopes=['read', 'write', 'follow'],
			to_file=None):
		
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
			msg = "CLS_Mastodon_Use：log_in：Invalid arguments given. username and password or code are required."
			self.cPrint(msg)
			return ""
		
		params['client_id'] = self.client_id
		params['client_secret'] = self.client_secret
		params['scope'] = " ".join(scopes)
		try:
			res_api = self.__api_request('POST', '/oauth/token', params, do_ratelimiting=False)
			if res_api['result']!=True :
				msg = "CLS_Mastodon_Use：log_in：__api_request Failed：" + res_api['reason']
				self.cPrint(msg)
				return ""
			response = res_api['responce']
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
			self.cPrint(msg)
			return ""
		
		requested_scopes = " ".join(sorted(scopes))
		received_scopes = " ".join(sorted(response["scope"].split(" ")))
		if requested_scopes != received_scopes:
			msg = "CLS_Mastodon_Use：log_in：Granted scopes received."
			self.cPrint(msg)
			return ""
		
		if to_file is not None:
			with open(to_file, 'w') as token_file:
				token_file.write(response['access_token'] + '\n')
		
		return response['access_token']



#####################################################
# 投稿
#####################################################
	def __status_post(self, status,
			in_reply_to_id=None,
			media_ids=None,
			sensitive=False,
			visibility='',
			spoiler_text=None):
		
		response = None
		res = self.__get_api_responce()
		#############################
		# 引数を辞書にまとめる
		params_initial = locals()
		
		valid_visibilities = ['private', 'public', 'unlisted', 'direct', '']
		if params_initial['visibility'].lower() not in valid_visibilities:
			res['reason'] = "CLS_Mastodon_Use：__status_post：Invalid visibility value"
			return res
		
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
				res['reason'] = "CLS_Mastodon_Use：__status_post：Invalid media：" + str(e)
				return res
			
			params_initial["media_ids"] = media_ids_proper
		
		params = self.__generate_params(params_initial)
		response = self.__api_request('POST', '/api/v1/statuses', params)
		
		return response



#####################################################
# API ローカルタイムライン取得
#####################################################
	def __timeline_local(self, timeline="local", max_id=None, since_id=None, limit=None):
		params_initial = locals()
		timeline = "public"
		params_initial['local'] = True
		
		params = self.__generate_params(params_initial, ['timeline'])
		url = '/api/v1/timelines/{0}'.format(timeline)
		response = self.__api_request('GET', url, params)
		return response



#####################################################
# API ホームタイムライン取得
#####################################################
	def __timeline_home(self, timeline="home", max_id=None, since_id=None, limit=None):
		params_initial = locals()
		
		params = self.__generate_params(params_initial, ['timeline'])
		url = '/api/v1/timelines/{0}'.format(timeline)
		response = self.__api_request('GET', url, params)
		return response



#####################################################
# API 連合タイムライン取得
#####################################################
	def __timeline_public(self, timeline="public", max_id=None, since_id=None, limit=None):
		params_initial = locals()
		
		params = self.__generate_params(params_initial, ['timeline'])
		url = '/api/v1/timelines/{0}'.format(timeline)
		response = self.__api_request('GET', url, params)
		return response



#####################################################
# API 通知一覧取得
#####################################################
	def __notification_list(self, id=None, max_id=None, since_id=None, limit=None):
		if max_id != None:
			max_id = self.__unpack_id(max_id)
		if since_id != None:
			since_id = self.__unpack_id(since_id)
		
		if id is None:
			params = self.__generate_params(locals(), ['id'])
			response = self.__api_request('GET', '/api/v1/notifications', params)
		else:
			id = self.__unpack_id(id)
			url = '/api/v1/notifications/{0}'.format(str(id))
			response = self.__api_request('GET', url)
		
		return response



#####################################################
# API トゥート一覧取得
#####################################################
	def __account_statuses(self, id, max_id=None, since_id=None, limit=None):
		params = self.__generate_params(locals(), ['id'])
		url = '/api/v1/accounts/{0}/statuses'.format(str(id))
		response = self.__api_request('GET', url, params)
		return response



#####################################################
# API ファボ一覧
#####################################################
	def __favourites(self, max_id=None, since_id=None, limit=None):
		params = self.__generate_params(locals())
		
		url = '/api/v1/favourites'
		response = self.__api_request('GET', url, params)
		return response



#####################################################
# API フォロー一覧
#####################################################
	def __account_following(self, id, max_id=None, since_id=None, limit=None):
		params = self.__generate_params(locals(), ['id'])
		url = '/api/v1/accounts/{0}/following'.format(str(id))
		response = self.__api_request('GET', url, params)
		return response



#####################################################
# API フォロワー一覧
#####################################################
	def __account_followers(self, id, max_id=None, since_id=None, limit=None):
		params = self.__generate_params(locals(), ['id'])
		url = '/api/v1/accounts/{0}/followers'.format(str(id))
		response = self.__api_request('GET', url, params)
		return response



#####################################################
# API 自アカウント情報取得
#####################################################
	def __account_verify_credentials(self):
		url = '/api/v1/accounts/verify_credentials'
		response = self.__api_request('GET', url)
		return response



#####################################################
# API 対アカウント情報取得
#####################################################
	def __account_relationships(self, id):
		params = self.__generate_params(locals())
		url = '/api/v1/accounts/relationships'
		response = self.__api_request('GET', url, params)
		return response



#####################################################
# API フォロー
#####################################################
	def __account_follow(self, id):
		url = '/api/v1/accounts/{0}/follow'.format(str(id))
		response = self.__api_request('POST', url)
		return response



#####################################################
# API リムーブ
#####################################################
	def __account_unfollow(self, id):
		url = '/api/v1/accounts/{0}/unfollow'.format(str(id))
		response = self.__api_request('POST', url)
		return response



#####################################################
# API ファボ
#####################################################
	def __status_favourite(self, id):
		url = '/api/v1/statuses/{0}/favourite'.format(str(id))
		response = self.__api_request('POST', url)
		return response



#####################################################
# API ブースト
#####################################################
	def __status_reblog(self, id):
		url = '/api/v1/statuses/{0}/reblog'.format(str(id))
		response = self.__api_request('POST', url)
		return response



#####################################################
# API ブロック
#####################################################
	def __status_block(self, id):
		url = '/api/v1/accounts/{0}/block'.format(str(id))
		response = self.__api_request('POST', url)
		return response



#####################################################
# API ブロック解除
#####################################################
	def __status_unblock(self, id):
		url = '/api/v1/accounts/{0}/unblock'.format(str(id))
		response = self.__api_request('POST', url)
		return response



#####################################################
# APIレスポンス取得  (**追加実装)
#####################################################
	def __get_api_responce(self):
		res = { "result"   : False,
				"reason"   : None,
				"responce" : None }
		
		return res



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
		
		res = self.__get_api_responce()
		
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
			res['reason'] = "API Responce：Could not complete request：" + str(e)
			return res
		
		#############################
		# 応答があったか
		if response_object is None:
			res['reason'] = "API Responce：Illegal request："
			return res
		
		if response_object.status_code == 404:
			res['reason'] = "API Responce：404 ERR："
			return res
		elif response_object.status_code == 500:
			res['reason'] = "API Responce：500 ERR："
			return res
		elif response_object.status_code != 200:
			res['reason'] = "API Responce：" + str(response_object.status_code) + " ERR"
			return res
		
		#############################
		# レスポンスを取り込む
		try:
			res_json = response_object.json(object_hook=self.__json_date_parse)
		except:
			res['reason'] = "API Responce：Could not parse response as JSON：status code：" + str(response_object.status_code)
			res['responce'] = res_json
			return res
		
		if isinstance(res_json, dict) and 'error' in res_json:
			res['reason'] = "API Responce：Mastodon API returned error：" + str(res_json['error'])
			res['responce'] = res_json
			return res
		
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
		
		res['result'] = True
		res['responce'] = res_json
		return res



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



#####################################################
# print出力
#####################################################
	def cPrint( self, msg ):
##		if sys.version_info.major==3 :
##			print(msg)
##		else :
##			print msg
		print(msg)
		return



