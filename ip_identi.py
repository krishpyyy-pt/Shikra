import ipaddress

def classify_ip_add(ip_str):
	try:
		ip = ipaddress.ip_address (ip_str)
		
		if ip.is_link_local:
			return "Internal (Link-Local)"
		elif ip.is_private:
			return "Internal (Private/Segmented)"
		elif ip.is_loopback:
			return "Localhost (Same Machine)"
		else:
			return "Outsider (Public)"
	except ValueError:
		return "Unknown/Malformed"


#test
print(classify_ip_add("fe80::1"))
print(classify_ip_add("192.168.0.1"))
print(classify_ip_add("8.8.8.8"))
