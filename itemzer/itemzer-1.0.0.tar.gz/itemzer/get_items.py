from itemzer.request_page import RequestPage


class GetItems:

	def __init__(self, name):
		self.name = name

	def get_items(self):

		list_items = []
		
		items = RequestPage(self.name).return_content_bs().find("div", class_="build-wrapper")

		for lien in items.find_all('a', href=True):
			list_items.append(lien['href'].split('/')[-1])

		item_index = 1

		print("\u001b[31m === ITEMS ===")

		for value_item in list_items:
			print(u"\u001b[32m%s\u001b[0m: \u001b[36m%s\u001b[0m" % (item_index, value_item))
			item_index += 1
