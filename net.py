from subprocess import Popen, PIPE
import sys
from concurrent import futures


def quad_to_hex(_q):
	return hex(sum(int(q) << 8*i for i, q in enumerate(reversed(_q.split('.')))))


def hex_to_quad(_h):
	return '.'.join(str(int(_h, 16) >> 8*(3-i) & 255) for i in range(4))


def hex_inc(_h):
	assert 0 <= hex_to_int(_h) < hex_to_int('0xffffffff')
	return hex(int(_h, 16) + 1)


def quad_inc(_q):
	return hex_to_quad(
		hex_inc(quad_to_hex(_q)))


def hex_to_int(_h):
	return int(_h, 16)


def int_to_hex(_i):
	return hex(_i)


def quad_to_int(_q):
	return hex_to_int(quad_to_hex(_q))


def int_to_quad(_i):
	return hex_to_quad(int_to_hex(_i))


def get_start_hex(net, mask):
	return hex(hex_to_int(net) & hex_to_int(mask))


def hex_inverse(_h):
	return '0x' + ''.join(str(hex(int('ff', 16) ^ (255 & int(_h, 16) >> 8*(3-i))))[2:] for i in range(4))


def get_start_quad(net, mask):
	return hex_to_quad(
		get_start_hex(quad_to_hex(net), quad_to_hex(mask)))


def get_end_hex(net, mask):
	return hex(hex_to_int(net) | (hex_to_int(hex_inverse(mask)) ^ hex_to_int(get_start_hex(net, mask))))


def get_end_quad(net, mask):
	return hex_to_quad(
		get_end_hex(
			quad_to_hex(net), quad_to_hex(mask)))


def get_hexs_on_subnet(net, mask):
	return [int_to_hex(i) for i in range(hex_to_int(get_start_hex(net, mask)), hex_to_int(get_end_hex(net, mask))+1):


def get_quads_on_subnet(net, mask):
	return [int_to_quad(i) for i in range(quad_to_int(get_start_quad(net, mask)), quad_to_int(get_end_quad(net, mask))+1)]


def get_net_and_mask():
	for line in Popen('ifconfig -a', shell=True, stdout=PIPE).communicate()[0].split('\n'):
		if ('inet' if sys.platform == 'darwin' else 'inet addr') in line and ('netmask' if sys.platform == 'darwin' else 'Mask') in line:
			addr = line.split(('inet' if sys.platform == 'darwin' else 'inet addr:'))[1].strip().split()[0]
			mask = line.split(('netmask' if sys.platform == 'darwin' else 'Mask:'))[1].strip().split()[0]
			if '127.0.0.1' == addr:
				continue
			else:
				return addr, hex_to_quad(mask)


def do_sys_ping(addr):
	return 'bytes from' in Popen('ping -c 1 %s %s' % (['-w 1', '-t 1']['darwin' == sys.platform], addr), shell=True, stdout=PIPE).communicate()[0]


def ping_all_on_net(net, mask):
	executor = futures.ThreadPoolExecutor(200)
	actives = {executor.submit(do_sys_ping, quad):quad for quad in get_quads_on_subnet(net, mask)}
	try:
		for future in futures.as_completed(actives, 2):
			if future.result() == True:
				yield actives[future]
	except futures._base.TimeoutError:
		pass
	executor.shutdown(False)


if __name__ == '__main__':
	print '\n'.join('%s is active' % ip for ip in ping_all_on_net(*get_net_and_mask()))

