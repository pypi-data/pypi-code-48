from itemzer.request_page import RequestPage


class GetSkills:

	def __init__(self, name):
		self.name = name

	def get_skills(self):
		counter_skills = 1
		get = RequestPage(self.name).return_content_op().find('table', class_='champion-skill-build__table')
		get_table = get.find_all('td')
		list_skills = [value.text.replace('\t', '').replace('\n', '') for value in get_table]

		print("\u001b[31m === FIRST 3 SKILLS === ")
		for value in list_skills[:3]:
			print(u"\u001b[32m%s\u001b[0m:\u001b[36m%s\u001b[0m " % (counter_skills, value), end=" ")

			counter_skills += 1
