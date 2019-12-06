import re
import json
import time
import requests
from multiprocessing import Process
from urllib.parse import urlencode
from requests.exceptions import ConnectionError, Timeout


class Spider:
	header = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15'
	}

	def __init__(self, index_url, accesstoken, name_txt, name_m3u, color):
		self.index_url = index_url
		self.actk = accesstoken
		self.name_txt = name_txt
		self.name_m3u = name_m3u
		self.color = color
		self.run()

	def get_each_index(self):
		try:
			rsp = requests.get(url=self.index_url, headers=self.header, timeout=5)
			if rsp.status_code == 200:
				data = json.loads(rsp.text)
				if data.get('chnl_list'):
					channels = data['chnl_list']
					pattern = re.compile('chnl_id\': (\d+).*?chnl_name\': \'(.*?)\'.*?\'livetv_url\': \[.*?\'(http.*?)\'', re.S)
					result = re.findall(pattern, str(channels))
					return result
				else:
					if 'pygdzhcs.com' in self.index_url:
						print(f'\n{self.index_url}\n无法获取: 山西广电3直播源列表。\n请检查账号是否失效，accesstoken是否正确。')
					elif 'yqdtv.com' in self.index_url:
						print(f'\n{self.index_url}\n无法获取: 山西广电2直播源列表。\n请检查账号是否失效，accesstoken是否正确。')
					elif 'nx96200.cn' in self.index_url:
						print(f'\n{self.index_url}\n无法获取: 宁夏广电直播源列表。\n请检查账号是否失效，accesstoken是否正确。')
					elif 'pyitv.com' in self.index_url:
						print(f'\n{self.index_url}\n无法获取: 广东广电直播源列表。\n请检查账号是否失效，accesstoken是否正确。')
					elif 'bfgd.com.cn' in self.index_url:
						print(f'\n{self.index_url}\n无法获取: 辽宁广电2直播源列表。\n请检查账号是否失效，accesstoken是否正确。')
					elif 'shuliyun.com' in self.index_url:
						print(f'\n{self.index_url}\n无法获取: 山西广电1直播源列表。\n请检查账号是否失效，accesstoken是否正确。')
					elif 'ttcatv.tv' in self.index_url:
						print(f'\n{self.index_url}\n无法获取: 辽宁广电1直播源列表。\n请检查账号是否失效，accesstoken是否正确。')
					elif 'jxtvnet.tv' in self.index_url:
						print(f'\n{self.index_url}\n无法获取: 江西广电直播源列表。\n请检查账号是否失效，accesstoken是否正确。')
					elif 'homed.hrtn.net' in self.index_url:
						print(f'\n{self.index_url}\n无法获取: 湖北广电直播源列表。\n请检查账号是否失效，accesstoken是否正确。')
					elif '122.194.12.25' in self.index_url:
						print(f'\n{self.index_url}\n无法获取: 江苏广电直播源列表。\n请检查账号是否失效，accesstoken是否正确。')
			else:
				print(f'{self.index_url}\n无法访问此源，请稍后再试。')
		except ConnectionError:
			print(f'\n{self.index_url} \n暂无法访问此源。若网络正常，请稍后再试。')
		except Timeout:
			print(f'\n{self.index_url} \n暂无法访问此源，稍后再试。')

	def format_url(self, details, color):
		if details:
			denominator = len(details)
			numerator = 0
			d = {
				'playtype': 'live',
				'protocol': 'hls',
				'accesstoken': self.actk,
				'playtoken': 'ABCDEFGHIGK',
			}
			params = urlencode(d)
			live_url_list = []
			for detail in details:
				url_base = detail[2]
				if 'jscnwx.com' in url_base:
					url_base = 'http://122.194.12.25:13164/playurl'
				elif 'httpdvb.slave.homed.hrtn.net:13164' in url_base:
					url_base = 'http://httpdvb.slave.homed.hrtn.net/playurl'
				else:
					pass
				live_url = f'{detail[1]},{url_base}?{params}&programid={detail[0]}.m3u8'
				live_url_check = f'{url_base}?{params}&programid={detail[0]}.m3u8'
				l = self.check_lives(live_url_check)
				time.sleep(0.9)
				if l:
					live_url_list.append([live_url])
				else:
					pass
				numerator += 1
				rate = int(numerator / denominator * 100)
				if numerator == 30:
					if len(live_url_list) < 1:
						print(f'\n请检查账号是否有效，accesstoken是否正确。\n{live_url}')
						break
				print('\r' + rate * f"\033[{self.color}█\033[0m" + f"\033[{self.color} {str(rate)}%\033[0m", end='')
			return live_url_list

	def check_lives(self, url):
		try:
			rsp = requests.get(url, headers=self.header, timeout=5)
			if rsp.status_code == 200:
				if '#EXTM3U' in rsp.text:
					return url
				else:
					pass
			else:
				pass
		except ConnectionError:
			pass
		except Timeout:
			pass

	def save_to_file(self, live_url_list):
		if live_url_list:
			with open(self.name_m3u, 'w+') as f:
				f.write('#EXTM3U\n')
				for i in live_url_list:
					a = i[0].split(',')
					f.write(f'#EXTINF:-1,{a[0]}\n{a[1]}\n')
			with open(self.name_txt, 'w+') as f:
				for i in live_url_list:
					f.write(f'{i[0]}\n')

	def run(self):
		details = self.get_each_index()
		live_url_list = self.format_url(details, self.color)
		self.save_to_file(live_url_list)


if __name__ == '__main__':
	# args 依次填入 直播源列表地址, accesstoken, 保存直播源的txt文件名, 保存直播源的m3u文件名, 进度条颜色
	
	# 湖北广电 ★★★
	hb_accesstoken = 'R5D22D2B7U309E0093K7735BBEDIAC2DC601PBM3187915V10453Z6B7EDWE3620470C71'
	hb_url = 'http://slave.homed.hrtn.net:13160/media/channel/get_list?pageidx=1&pagenum=500&accesstoken=' + hb_accesstoken
	p1 = Process(target=Spider, args=(hb_url, hb_accesstoken, 'hb.txt', 'hb.m3u', '35m'))
	# p1.start()

	# 江苏广电 ★★★
	js_accesstoken = '注册账号后，在此处引号内填写你的accesstoken'
	js_url = 'http://122.194.12.25:13160/media/channel/get_list?pageidx=1&pagenum=500&accesstoken=' + js_accesstoken
	p2 = Process(target=Spider, args=(js_url, js_accesstoken, 'js.txt', 'js.m3u', '36m'))
	# p2.start()

	# 江西广电 ★★★
	jx_accesstoken = '注册账号后，在此处引号内填写你的accesstoken'
	jx_url = 'http://slave.jxtvnet.tv:81/media/channel/get_list?pageidx=1&pagenum=500&accesstoken=' + jx_accesstoken
	p3 = Process(target=Spider, args=(jx_url, jx_accesstoken, 'jx.txt', 'jx.m3u', '34m'))
	# p3.start()

	# 辽宁广电1 
	ln1_accesstoken = '注册账号后，在此处引号内填写你的accesstoken'
	ln1_url = 'http://slave.ttcatv.tv:13160/media/channel/get_list?pageidx=1&pagenum=500&accesstoken=' + ln1_accesstoken
	p4 = Process(target=Spider, args=(ln1_url, ln1_accesstoken, 'ln1.txt', 'ln1.m3u', '33m'))
	# p4.start()

	# 山西广电1
	sx_accesstoken = '注册账号后，在此处引号内填写你的accesstoken'
	sx_url = 'http://slave.shuliyun.com:13160/media/channel/get_list?pageidx=1&pagenum=500&accesstoken=' + sx_accesstoken
	p5 = Process(target=Spider, args=(sx_url, sx_accesstoken, 'sx1.txt', 'sx1.m3u', '31m'))
	# p5.start()

	# 辽宁广电2 强烈不推荐。频繁无法访问，accesstoken失效极快。
	ln2_accesstoken = '注册账号后，在此处引号内填写你的accesstoken'
	ln2_url = 'http://slave.bfgd.com.cn:13160/media/channel/get_list?pageidx=1&pagenum=500&accesstoken=' + ln2_accesstoken
	p6 = Process(target=Spider, args=(ln2_url, ln2_accesstoken, 'ln2.txt', 'ln2.m3u', '32m'))
	# p6.start()

	# 广东广电 不推荐。accesstoken失效极快。
	gd_accesstoken = '注册账号后，在此处引号内填写你的accesstoken'
	gd_url = 'http://slave.pyitv.com/media/channel/get_list?pageidx=1&pagenum=500&accesstoken=' + gd_accesstoken
	p7 = Process(target=Spider, args=(gd_url, gd_accesstoken, 'gd.txt', 'gd.m3u', '30m'))
	# p7.start()

	# 宁夏广电 不推荐。accesstoken失效极快。
	nx_accesstoken = '注册账号后，在此处引号内填写你的accesstoken'
	nx_url = 'http://slave.nx96200.cn:13160/media/channel/get_list?pageidx=1&pagenum=500&accesstoken=' + nx_accesstoken
	p8 = Process(target=Spider, args=(nx_url, nx_accesstoken, 'nx.txt', 'nx.m3u', '37m'))
	# p8.start()

	# 山西广电2 不推荐。accesstoken失效极快。
	sx2_accesstoken = '注册账号后，在此处引号内填写你的accesstoken'
	sx2_url = 'http://slave.yqdtv.com:13160/media/channel/get_list?pageidx=1&pagenum=500&accesstoken=' + sx2_accesstoken
	p9 = Process(target=Spider, args=(sx2_url, sx2_accesstoken, 'sx2.txt', 'sx2.m3u', '36m'))
	# p9.start()

	# 山西广电3 强烈不推荐。账号失效极快。
	sx3_accesstoken = '注册账号后，在此处引号内填写你的accesstoken'
	sx3_url = 'http://slave.pygdzhcs.com:13160/media/channel/get_list?pageidx=1&pagenum=500&accesstoken=' + sx3_accesstoken
	p10 = Process(target=Spider, args=(sx3_url, sx3_accesstoken, 'sx3.txt', 'sx3.m3u', '35m'))
	# p10.start()