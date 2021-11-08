import requests
import bs4
import configparser
import time
import csv
from datetime import datetime

#Load config
config = configparser.ConfigParser()
config.read("settings.ini", encoding="utf-8")

url = "https://www.cbinsights.com/research-unicorn-companies"
#Получить количество компаний и сохранить их в settings.ini
def get_company_numbers():
	req = requests.get(url)
	company_numb = bs4.BeautifulSoup(req.text, "html.parser")
	company_numb = company_numb.find('span', class_="x_d9de4c49").text
	current_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
	config.set('Options', 'current_date', str(current_datetime))
	config.set('Options', 'company_numb', str(company_numb))
	with open('settings.ini', 'w') as configfile:
		config.write(configfile)
	configfile.close()
	return company_numb

#Парсинг всех данных в таблицу company.csv
def get_data(name='company'):
	req = requests.get(url)
	data = bs4.BeautifulSoup(req.text, "html.parser")
	data = data.find('table')
	rows = data.find_all('tr')
	with open(name+'.csv', 'w') as file:
		writer = csv.writer(file, delimiter=";", lineterminator="\r")
		writer.writerow((
			'Company',
			'Valuation($B)',
			'Date_Joined',
			'Country',
			'City',
			'Industry',
			'Select_Investors',
			'Url'))
		for i in range(1, len(rows)):
			writer.writerow((
				rows[i].find_all('td')[0].text,
				rows[i].find_all('td')[1].text,
				rows[i].find_all('td')[2].text,
				rows[i].find_all('td')[3].text,
				rows[i].find_all('td')[4].text,
				rows[i].find_all('td')[5].text,
				rows[i].find_all('td')[6].text,
				rows[i].find_all('td')[0].find('a').get('href')
			))
	file.close()
	print('Данные успешно сохранены в таблицу!')

#Запуск программы по таймеру
def timer(timeout=3600):
	print(f'{config["Options"]["current_date"]}: Количество компаний: {config["Options"]["company_numb"]}')
	while True:
		if config["Options"]["company_numb"] == str(get_company_numbers()):
			print(datetime.now().strftime("%d/%m/%Y %H:%M:%S")+': Новых компаний не появилось')
			difference()
		else:
			print('Появились изменения!')
			get_data('company_new')
			difference()
			get_company_numbers()

		print(f'Следующая проверка через {timeout} секунд... ')
		time.sleep(timeout)

#Определение новой компании и запись ее в отдельную таблицу new.csv
def difference():
	f_old = open("company.csv")
	f_new = open("company_new.csv")
	old = csv.DictReader(f_old, delimiter=";")
	new = csv.DictReader(f_new, delimiter=";")
	company_old=[]
	company_new=[]
	for row in old:
		company_old.append(row['Company'])
	for row in new:
		company_new.append(row['Company'])
	if len(company_old) == len(company_new):
		difference_val()
	elif len(company_old) < len(company_new):
		result=list(set(company_old) ^ set(company_new))
		index=[]
		for i in result:
			index.append(company_new.index(i))
		f_old.close()
		f_new.close()
		diff = open('company_new.csv')
		csvFileArray = []
		for row in csv.reader(diff, delimiter=';'):
			csvFileArray.append(row)
		with open('new.csv', 'w') as file:
			writer = csv.writer(file, delimiter=";", lineterminator="\r")
			writer.writerow((
				'Company',
				'Valuation($B)',
				'Date_Joined',
				'Country',
				'City',
				'Industry',
				'Select_Investors',
				'Url'))
			for i in index:
				writer.writerow((
					csvFileArray[i+1][0],
					csvFileArray[i+1][1],
					csvFileArray[i+1][2],
					csvFileArray[i+1][3],
					csvFileArray[i+1][4],
					csvFileArray[i+1][5],
					csvFileArray[i+1][6],
					csvFileArray[i+1][7]
				))
				print(f'Добавлена новая компания: {csvFileArray[i+1][0]}')
		diff.close()
		file.close()
	else:
		print('Компанйи стало меньше!')
		result = list(set(company_new) ^ set(company_old))
		index = []
		for i in result:
			index.append(company_old.index(i))
		f_old.close()
		f_new.close()
		diff = open('company_new.csv')
		csvFileArray = []
		for row in csv.reader(diff, delimiter=';'):
			csvFileArray.append(row)
		with open('test_del.csv', 'w') as file:
			writer = csv.writer(file, delimiter=";", lineterminator="\r")
			writer.writerow((
				'Company',
				'Valuation($B)',
				'Date_Joined',
				'Country',
				'City',
				'Industry',
				'Select_Investors',
				'Url'))
			for i in index:
				writer.writerow((
					csvFileArray[i + 1][0],
					csvFileArray[i + 1][1],
					csvFileArray[i + 1][2],
					csvFileArray[i + 1][3],
					csvFileArray[i + 1][4],
					csvFileArray[i + 1][5],
					csvFileArray[i + 1][6],
					csvFileArray[i + 1][7]
				))
				print(f'Удалилась компания: {csvFileArray[i + 1][0]}')
			diff.close()
			file.close()
		print('Данные успешно сохранены в таблицу!')

#Определение разницы между двумя ценами и запись в таблицу val.csv
def difference_val():
	f_old = open("company.csv")
	f_new = open("company_new.csv")
	old = csv.DictReader(f_old, delimiter=";")
	new = csv.DictReader(f_new, delimiter=";")
	val_old = []
	val_new = []
	for row in old:
		val_old.append(row['Valuation($B)'])
	for row in new:
		val_new.append(row['Valuation($B)'])
	f_old.close()
	f_new.close()
	diff_val_old = open('company.csv')
	csvFileArray_val_old = []
	for row in csv.reader(diff_val_old, delimiter=';'):
		csvFileArray_val_old.append(row)
	diff_val_old.close()
	diff_val_new = open('company_new.csv')
	csvFileArray_val_new = []
	for row in csv.reader(diff_val_new, delimiter=';'):
		csvFileArray_val_new.append(row)
	diff_val_new.close()
	with open('val.csv', 'w') as file:
		writer = csv.writer(file, delimiter=";", lineterminator="\r")
		writer.writerow((
			'Company',
			'Valuation($B)_old',
			'Valuation($B)_new'))
	file.close()
	with open('val.csv', 'w') as file:
		writer = csv.writer(file, delimiter=";", lineterminator="\r")
		for val in range(len(val_old)):
			if val_old[val] != val_new[val]:
					writer.writerow((csvFileArray_val_old[val+1][0],
						csvFileArray_val_old[val+1][1],
						csvFileArray_val_new[val+1][1]))
					msg=1
			else:
				msg=2
		file.close()
		if msg==1:
			print('Обновилась разница')
		else:
			print('Новых данных нет!')

#Определение разницы между двумя ценами и запись в таблицу test_val.csv для отладки
def difference_val_test():
	f_old = open("test_company.csv")
	f_new = open("test_company_new.csv")
	old = csv.DictReader(f_old, delimiter=";")
	new = csv.DictReader(f_new, delimiter=";")
	val_old = []
	val_new = []
	for row in old:
		val_old.append(row['Valuation($B)'])
	for row in new:
		val_new.append(row['Valuation($B)'])
	f_old.close()
	f_new.close()
	diff_val_old = open('test_company.csv')
	csvFileArray_val_old = []
	for row in csv.reader(diff_val_old, delimiter=';'):
		csvFileArray_val_old.append(row)
	diff_val_old.close()
	diff_val_new = open('test_company_new.csv')
	csvFileArray_val_new = []
	for row in csv.reader(diff_val_new, delimiter=';'):
		csvFileArray_val_new.append(row)
	diff_val_new.close()
	with open('test_val.csv', 'w') as file:
		writer = csv.writer(file, delimiter=";", lineterminator="\r")
		writer.writerow((
			'Company',
			'Valuation($B)_old',
			'Valuation($B)_new'))
	file.close()
	with open('test_val.csv', 'w') as file:
		writer = csv.writer(file, delimiter=";", lineterminator="\r")
		for val in range(len(val_old)):
			if val_old[val] != val_new[val]:
					writer.writerow((csvFileArray_val_old[val+1][0],
						csvFileArray_val_old[val+1][1],
						csvFileArray_val_new[val+1][1]))
		file.close()
	print('Сохранилась разница!')

#Сохранение страницы в data.html для отладки
def save_to_html():
	req = requests.get(url)
	data = bs4.BeautifulSoup(req.text, "html.parser")
	f = open("data.html", "w", encoding="utf-8")
	f.write(str(data))
	f.close()

#Создание таблицы company_savw.csv из сохраненной data.html для отладки
def get_save_data():
	# company=rows[1].find_all('td')[0].text
	# valuation=rows[1].find_all('td')[1].text
	# date_joined=rows[1].find_all('td')[2].text
	# country=rows[1].find_all('td')[3].text
	# city=rows[1].find_all('td')[4].text
	# industry=rows[1].find_all('td')[5].text
	# select_investors=rows[1].find_all('td')[6].text
	# url=rows[1].find_all('td')[0].find('a').get('href')
	f = open('data.html', "r", encoding="utf-8")
	data=bs4.BeautifulSoup(f.read(), "html.parser")
	data = data.find('table')
	rows = data.find_all('tr')
	with open('company_save.csv', 'w') as file:
		writer = csv.writer(file, delimiter=";",lineterminator="\r")
		writer.writerow((
			'Company',
			'Valuation($B)',
			'Date_Joined',
			'Country',
			'City',
			'Industry',
			'Select_Investors',
			'Url'))
		for i in range(1,len(rows)):
			writer.writerow((
				rows[i].find_all('td')[0].text,
				rows[i].find_all('td')[1].text,
				rows[i].find_all('td')[2].text,
				rows[i].find_all('td')[3].text,
				rows[i].find_all('td')[4].text,
				rows[i].find_all('td')[5].text,
				rows[i].find_all('td')[6].text,
				rows[i].find_all('td')[0].find('a').get('href')
			))
	print("Данные успешно сохранены!")

#Тест, для удаливщихся компанйи поменять местами f_old  и f_new
def difference_test():
	f_old = open("test_company.csv")
	f_new = open("test_company_new.csv")
	old = csv.DictReader(f_old, delimiter=";")
	new = csv.DictReader(f_new, delimiter=";")
	company_old = []
	company_new = []
	for row in old:
		company_old.append(row['Company'])
	for row in new:
		company_new.append(row['Company'])
	if len(company_old) == len(company_new):
		difference_val_test()
	elif len(company_old)< len(company_new):
		result = list(set(company_old) ^ set(company_new))
		index = []
		for i in result:
			index.append(company_new.index(i))
		f_old.close()
		f_new.close()
		diff = open('company_new.csv')
		csvFileArray = []
		for row in csv.reader(diff, delimiter=';'):
			csvFileArray.append(row)
		with open('test_new.csv', 'w') as file:
			writer = csv.writer(file, delimiter=";", lineterminator="\r")
			writer.writerow((
				'Company',
				'Valuation($B)',
				'Date_Joined',
				'Country',
				'City',
				'Industry',
				'Select_Investors',
				'Url'))
			for i in index:
				writer.writerow((
					csvFileArray[i + 1][0],
					csvFileArray[i + 1][1],
					csvFileArray[i + 1][2],
					csvFileArray[i + 1][3],
					csvFileArray[i + 1][4],
					csvFileArray[i + 1][5],
					csvFileArray[i + 1][6],
					csvFileArray[i + 1][7]
				))
				print(f'Добавлена новая компания: {csvFileArray[i + 1][0]}')
			diff.close()
			file.close()
	else:
		print('Компанйи стало меньше!')
		result = list(set(company_new) ^ set(company_old))
		index = []
		for i in result:
			index.append(company_old.index(i))
		f_old.close()
		f_new.close()
		diff = open('company_new.csv')
		csvFileArray = []
		for row in csv.reader(diff, delimiter=';'):
			csvFileArray.append(row)
		with open('test_del.csv', 'w') as file:
			writer = csv.writer(file, delimiter=";", lineterminator="\r")
			writer.writerow((
				'Company',
				'Valuation($B)',
				'Date_Joined',
				'Country',
				'City',
				'Industry',
				'Select_Investors',
				'Url'))
			for i in index:
				writer.writerow((
					csvFileArray[i + 1][0],
					csvFileArray[i + 1][1],
					csvFileArray[i + 1][2],
					csvFileArray[i + 1][3],
					csvFileArray[i + 1][4],
					csvFileArray[i + 1][5],
					csvFileArray[i + 1][6],
					csvFileArray[i + 1][7]
				))
				print(f'Удалилась компания: {csvFileArray[i+1][0]}')
			diff.close()
			file.close()


	print('Данные успешно сохранены в таблицу!')

#Запуск программы в timer  указать время (например timer(10)- каждые 10 сек), по умолчанию 1 час
if __name__ == '__main__':
	get_company_numbers()
	get_data('company_new')
	get_data()
	timer(100)
	#difference_test()
	#difference_val_test()

