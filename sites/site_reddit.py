#!/usr/bin/python

from basesite import basesite
from site_imgur import imgur
from json import loads
from time import sleep

class reddit(imgur):
	
	""" Parse/strip URL to acceptable format """
	def sanitize_url(self, url):
		if not 'reddit.com/' in url:
			raise Exception('')
		if not 'reddit.com/user/' in url:
			raise Exception('required /user/ not found in URL')
		user = url[url.find('/user/')+6:]
		if '/' in user: user = user[:user.find('/')]
		if '?' in user: user = user[:user.find('?')]
		if '#' in user: user = user[:user.find('#')]
		return 'http://reddit.com/user/%s' % user

	""" Discover directory path based on URL """
	def get_dir(self, url):
		user = url[url.find('/user/')+6:]
		return 'reddit_%s' % user

	def download(self):
		self.init_dir()
		params = ''
		index = 0
		total = 0
		while True:
			url = '%s/submitted.json%s' % (self.url, params)
			self.debug(url)
			r = self.web.get(url)
			try: json = loads(r)
			except: break
			if not 'data' in json: break
			if not 'children' in json['data']: break
			children = json['data']['children']
			total += len(children)
			for child in children:
				url = child['data']['url']
				index += 1
				if not 'imgur.com' in url: continue
				if 'imgur.com/a/' in url:
					self.download_album(url)
				elif not 'i.imgur.com' in url and not (url[-4] == '.' or url[-5] == '.'):
					# Need to get direct link to image
					iid = url[url.find('imgur.com/')+len('imgur.com/'):]
					if '/' in iid: iid = iid[:iid.find('/')]
					if '?' in iid: iid = iid[:iid.find('?')]
					if '#' in iid: iid = iid[:iid.find('#')]
					ir = self.web.get('http://api.imgur.com/2/image/%s' % iid)
					try: ijs = loads(ir)
					except: continue
					if not 'image' in ijs or not 'links' in ijs['image'] or not 'original' in ijs['image']['links']: continue
					url = ijs['image']['links']['original']
				self.download_image(url, index, total=total)
				if self.hit_image_limit(): break
			if self.hit_image_limit(): break
			count = len(children)
			after = json['data']['after']
			if count == 0 or after == None: break
			params = '?count=%d&after=%s' % (count, after)
			sleep(2)
		self.wait_for_threads()
	
