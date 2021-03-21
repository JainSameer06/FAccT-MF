import ijson
import json
import argparse
from collections import namedtuple
import networkx as nx
import networkx.algorithms.community as nx_comm
import os

#python extract_from_json.py ../dblp.v12.json False
class GraphGenerator:
	"""
	A class encapsulating the generation of a citation network of a subset of the articles from the Aminer dataset

	Attributes
	----------
	node_levels : dictionary
		A mapping from article ID to node level, where node level is 0 for FAccT papers, 1 for papers directly cited by FAccT papers, and so on.
	node_records : dictionary
		An mapping from article ID to the corresponding entry in the Aminer dataset
	extracted : bool
		True if all relevant article entries (network nodes) have already been extracted and stored in a new json file. False otherwise.
	sourceFile : file object
		Refers to the json file of extracted relevant articles if extracted is True. Refers to the Aminer json file if extracted is False.
	
	Methods
	-------
	explore_nodeset()
		Populates node_levels. Called only if extracted is False.

	extract_records()
		Populates node_records and saves the same to a new json. Called only if extracted is False.

	generate_network()
		Generates the network from node_records.
	"""
	NodeRecord = namedtuple('NodeRecord', ['level', 'record'])
	def __init__(self, sourceFilePath, extracted):
		self.node_levels = {}
		self.node_records = {}
		self.sourceFile = open(sourceFilePath, 'r')
		self.extracted = extracted
		self.G = nx.Graph()

	def explore_nodeset(self):
		i = 0
		for item in ijson.items(self.sourceFile, "item", use_float = True):
			i += 1
			if i % 1000000 == 0:
				print(i, " first pass")
			try:
				if ("Fairness" in item["venue"]["raw"] or "fairness" in item["venue"]["raw"]) and ("Accountability" in item["venue"]["raw"] or "accountability" in item["venue"]["raw"]) and ("conference" in item["venue"]["raw"] or "Conference" in item["venue"]["raw"]):
					node = item["id"]
					self.node_levels[node] = 0
					if "references" in item:
						for reference in item["references"]:
							if reference not in self.node_levels:
								self.node_levels[reference] = 1
			except KeyError:
				pass
		self.sourceFile.seek(0)
		i = 0
		for item in ijson.items(self.sourceFile, "item", use_float = True):
			i += 1
			if i % 1000000 == 0:
				print(i, " second pass")
			try:
				if item["id"] in self.node_levels and self.node_levels[item["id"]] == 1:
					node = item["id"]
					if "references" in item:
						for reference in item["references"]:
							if reference not in self.node_levels:
								self.node_levels[reference] = 2
			except KeyError:
				pass
		print (len(self.node_levels))

	def extract_records(self):
		self.sourceFile.seek(0)
		i = 0
		for item in ijson.items(self.sourceFile, "item", use_float = True):
			i += 1
			if i % 1000000 == 0:
				print(i, "extraction first pass")
			try:
				if item["id"] in self.node_levels:
					node = item["id"]
					self.node_records[node] = item
			except KeyError:
				pass
		extractedFile = os.path.join(os.path.dirname(self.sourceFile), "extracted.json")
		with open(extractedFile, 'w') as f_write:		
			json.dump(self.node_records, f_write)

	def generate_network(self):
		if self.extracted == True:
			self.node_records = json.load(self.sourceFile)
		else:
			self.explore_nodeset()
			self.extract_records()
		for node_id in self.node_records:
			node_record = self.node_records[node_id]
			if "references" in node_record:
				references = node_record["references"]
				for reference_id in references:
					self.G.add_edge(node_id, reference_id)


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('sourceFilePath', type = str, help = "Path to the Aminer json file or the extracted node file")
	parser.add_argument("skip_extraction", type = bool, help = "True if nodes have already been extracted from Aminer. In this case, the path argument gives the path to the extracted file")
	
	args = parser.parse_args()
	sourceFilePath = args.sourceFilePath
	skip_extraction = args.sourceFilePath
	g = GraphGenerator(sourceFilePath, skip_extraction)
	g.generate_network()

if __name__ == '__main__':
	main()

