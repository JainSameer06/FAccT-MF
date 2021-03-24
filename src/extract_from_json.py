import ijson
import json
import argparse
from collections import namedtuple
import networkx as nx
import networkx.algorithms.community as nx_comm
import os
import csv

#python extract_from_json.py ../dblp.v12.json False 10
#python extract_from_json.py /home/sameer/Projects/Political-leaning/extracted_l1.json /home/sameer/Projects/Political-leaning/clusters.csv True 10
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
		self.sourceFilePath = sourceFilePath
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
		extractedFile = os.path.join(os.path.dirname(self.sourceFilePath), "extracted_l0.json")
		with open(extractedFile, 'w') as f_write:		
			json.dump(self.node_records, f_write, indent = 0)

	def generate_network(self):
		print("inside generate_network()")
		print(self.extracted)
		print(self.sourceFilePath)

		if self.extracted == True:
			print("loading from extracted")
			self.node_records = json.load(self.sourceFile)
			#print(self.node_records)
		else:
			self.explore_nodeset()
			self.extract_records()
		for node_id in self.node_records:
			#print (node_id)
			node_record = self.node_records[node_id]
			#print(node_record)
			if "references" in node_record:
				#print("references found")
				references = node_record["references"]
				#print (references)
				for reference_id in references:
					if str(reference_id) in self.node_records:
						self.G.add_edge(int(node_id), reference_id)
					#print(self.G)
		#print("g: ", self.G.nodes)
		for node_id in self.node_records:
			node_record = self.node_records[node_id]
			node_id = int(node_id)
			if node_id in self.G.nodes:
				nx.set_node_attributes(self.G, {node_id: {"article_title": node_record["title"]}})
		"""
		for node in self.G.nodes:
			if "article_title" not in self.G.nodes[node]:
				self.G.remove_node(node)
		"""
		print("levels", len(self.node_levels))
		print("records", len(self.node_records))
		print("tot_nodes", len(self.G.nodes))
		return self.G

def edge_to_remove(g):
	print("inside edge_to_remove()")
	d1 = nx.edge_betweenness_centrality(g, k = 300) 
	print("computed ebc")
	list_of_tuples = list(d1.items()) 
	
	  
	max_tuple_ebc = max(list_of_tuples, key = lambda x:x[1]) 
	# Will return in the form (a,b) 
	return max_tuple_ebc[0] 

def girvan(g, k):
	a = nx.connected_components(g) 
	lena = len(list(a)) 
	print (' The number of connected components is ', lena) 
	while (lena < k): 
		u, v = edge_to_remove(g) 
		g.remove_edge(u, v)  
		a = nx.connected_components(g) 
		lena = len(list(a)) 
		print (' The number of connected components is ', lena) 
	a = list(sorted(nx.connected_components(g), key = len, reverse = True))
	components_sorted = []
	for component in a:
		sources = [node for node in component if int(node) < 1000]
		sources = sorted(sources, key = g.degree, reverse = True)
		destinations = [node for node in component if int(node) >= 1000]
		destinations = sorted(destinations, key = g.degree, reverse = True)
		components_sorted.append(sources + destinations)
	#print(components_sorted)
	return components_sorted

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('sourceFilePath', type = str, help = "Path to the Aminer json file or the extracted node file")
	parser.add_argument('destinationFilePath', type = str, help = "Path to the destination (cluster) file")
	parser.add_argument("skip_extraction", type = bool, help = "True if nodes have already been extracted from Aminer. In this case, the path argument gives the path to the extracted file")
	parser.add_argument("num_clusters", type = int, help = "Number of clusters to split the network into")
	
	args = parser.parse_args()
	sourceFilePath = args.sourceFilePath
	skip_extraction = args.skip_extraction
	destinationFilePath = args.destinationFilePath
	G = GraphGenerator(sourceFilePath, skip_extraction)
	g = G.generate_network()
	print(g)

	i = 0
	for node in g.nodes:
		#print(g.nodes[node])
		if "article_title" in g.nodes[node]:
			i += 1
		else:
			print("fix")
	print("nodes", i)

	component_list = girvan(g, args.num_clusters) 
	with open(destinationFilePath, 'w', newline='') as csvfile:
		csv_writer = csv.writer(csvfile)
		for component in component_list: 
			for node in component:
				csv_writer.writerow([node, g.nodes[node]['article_title'], g.degree[node]])
			csv_writer.writerow(['.............', '............']) 
		print(nx_comm.modularity(g, component_list))

if __name__ == '__main__':
	main()

