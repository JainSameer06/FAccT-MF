import re
import pandas as pd
import os
import argparse

class Reference:
	def __init__(self, reference_string, conference_year):
		self.article_title = self.authorlist_str = self.venue = self.year = ""

		if conference_year != 2018:
			reference_elements = [element.strip() for element in re.split("([0-9]*)", reference_string, 1)]
			
			if len(reference_elements) == 3:
				reference_elements[2] = Reference.strip_string(reference_elements[2])
				if '.' in reference_elements[2]:
					self.article_title, self.venue = reference_elements[2].split(".", 1)
				else:
					self.article_title = reference_elements[2]
				self.authorlist_str = reference_elements[0]
				self.year = reference_elements[1]

			elif len(reference_elements) == 2:
				self.article_title = reference_elements[0]
				self.year = reference_elements[1]
			else:
				self.article_title = reference_elements[0]

		else:
			reference_elements = [element.strip() for element in re.split("\.", reference_string, 2)]
			
			if len(reference_elements) == 3:
				reference_elements[2] = Reference.strip_string(reference_elements[2])
				self.authorlist_str = reference_elements[0]
				self.article_title = reference_elements[1]
				self.venue = reference_elements[2]

			elif len(reference_elements) == 2:
				self.authorlist_str = reference_elements[0]
				self.article_title = reference_elements[1]
			else:
				self.article_title = reference_elements[0]
			self.year = re.search("[^0-9][0-9]{4}[^0-9]|$", reference_string).group(0)

		self.article_title = Reference.strip_string(self.article_title)
		self.authorlist_str = Reference.strip_string(self.authorlist_str)
		self.venue = Reference.strip_string(self.venue)
		self.year = Reference.strip_string(self.year)


	@staticmethod
	def strip_string(string):
		to_remove = [' ', '.']
		begin = end = 0
		for index, char in enumerate(string):
			if char not in to_remove:
				begin = index
				break
		for index, char in enumerate(reversed(string)):
			if char not in to_remove:
				end = index
				break
		stripped_string = string[begin:len(string) - end]
		return stripped_string


	def get_reference_as_list(self):
		return list([self.authorlist_str, self.article_title, self.venue, self.year])

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--in", dest = 'inputDirectory', type = str, help = "Path to the input directory")
	args = parser.parse_args()

	reference_list = []
	df = pd.DataFrame(columns = ["Source Article", "Authors", "Referenced Article", "Venue", "Year"])
	excel_path ="/home/sameer/Projects/Political-leaning/Data/TXTs/outr12.xlsx"
	writer = pd.ExcelWriter(excel_path, engine = 'xlsxwriter')

	i = 0
	for file in os.listdir(args.inputDirectory):
		filepath = os.path.join(args.inputDirectory, file)
		f = open(filepath, mode = 'r', newline = '')
		article_text = f.read()	
		f.close()

		year = 2018
		if year != 2018:
			# Extracting the References section of the article and removing line breaks
			try:
				reference_split = article_text.split("REFERENCES")[1].replace("-\n", "").replace("\n"," ")
			except IndexError:
				print ("REFERENCES not found in", file)
				continue

			# Splitting the References section into a list (of strings) of references using the reference format that starts with "[NUMBER]"
			reference_text_list = list(map(str.strip, re.split("\[[0-9]*\]", reference_split)))
			#print (reference_text_list)

		else:
			# Extracting the References section of the article and removing line breaks
			try:
				reference_split = article_text.split("References")[1].replace("-\n", "").replace("\n"," ")
			except IndexError:
				print ("References not found in", file)
				continue

			# Splitting the References section into a list (of strings) of references using the reference format that starts with "[NUMBER]"
			reference_text_list = list(map(str.strip, re.split("\*\*", reference_split)))
			#print (reference_text_list)

		# Removing empty strings from the reference list
		reference_text_list = list(filter(None, reference_text_list))

		# Generating list of Reference objects
		reference_object_list = list(map(lambda ref_str: Reference(ref_str, year), reference_text_list))

		article_title = file
		reference_list_list = list(map(lambda ref: ref.get_reference_as_list(), reference_object_list))
		for reference in reference_list_list:
			reference.insert(0, article_title) 
		print(reference_list_list)

		df_temp = pd.DataFrame(reference_list_list, columns = df.columns)
		print(df.columns)
		df= df.append(df_temp)

		i += 1
		if i > 11:
			print(file)
			print(df_temp)
			break

	df.to_excel(writer)
	df.to_csv("/home/sameer/Projects/Political-leaning/Data/TXTs/sample18.csv")
	writer.close()
