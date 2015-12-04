# -*- encoding: utf-8 -*-

##############################################################################
#
#
##############################################################################

#import mandrill
#mandrill_client = mandrill.Mandrill('xxx')
#result = mandrill_client.messages.info(id='xxx')
#print result


def parse_mail(head_str):
	parse=head_str.split('<')
	name=parse[0]
	email=parse[1].replace('>', '')
	return name, email
#print parse_mail('vladimir sdf * sdfsdf <trokbrok@yandex.ru>')

def peplace_email(head_str, email):
	start=head_str.find('<')
	stop=head_str.find('>')
	bad_str=head_str[start+1:stop]
	print bad_str
	return head_str.replace(bad_str, email)
	
#print peplace_email('?utf-8?b?0KHQodCjIOKEljU=?= <info@yourcompany.com>', 'admin@udaff.com')
