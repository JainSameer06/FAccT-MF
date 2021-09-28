from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from gensim.models.ldamodel import LdaModel
from gensim.models.ldamodel import CoherenceModel
from gensim.test.utils import datapath
from gensim import corpora
import argparse
import os

def prepareDoc(doc):
	tokenizer = RegexpTokenizer(r'\w+')
	tokens = tokenizer.tokenize(doc)
	en_stop = get_stop_words('en')
	text = [i.lower() for i in tokens if not i.lower() in en_stop]
	print(text)
	return text

def LDA(docs, modelPath, n_topics):
	dictionary = corpora.Dictionary(docs, n_topics)
	print(dictionary)
	corpus = [dictionary.doc2bow(doc) for doc in docs]
	# print(corpus)
	ldamodel = LdaModel(corpus, num_topics = n_topics, id2word = dictionary, passes = 50)
	#temp_file = datapath("model")
	ldamodel.save(modelPath)	
	print("Printing topics")
	for i in range(ldamodel.num_topics):
		print (ldamodel.print_topic(i))	
		print ("\n")	

	cm = CoherenceModel(model=ldamodel, corpus=corpus, coherence='u_mass')
	coherence = cm.get_coherence()  # get coherence value
	print(coherence)

	"""
	cm = CoherenceModel(model=ldamodel, corpus=corpus, coherence='c_v')
	coherence = cm.get_coherence()  # get coherence value
	print(coherence)
	"""

	return(n_topics, coherence)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--in", dest = 'inputDirectory', type = str, help = "Path to the directory containing topic modeling splits")
	parser.add_argument("--out", dest = 'modelSavePath', type = str, help = "Path to save model")
	parser.add_argument("--n", dest = 'n_topics', type = int, help = "Number of topics")
	args = parser.parse_args()

	docs = []
	for year in range(2018, 2021):
		inputDirectory_year = os.path.join(args.inputDirectory, str(year))
		for file in os.listdir(inputDirectory_year):
			inFilepath = os.path.join(inputDirectory_year, file)
			f_in = open(inFilepath, mode = 'r', newline = '')
			tm_text = f_in.read()	
			f_in.close()
			docs.append(prepareDoc(tm_text))

	LDA(docs, args.modelSavePath, args.n_topics)

	coh_lst = []

	for i in range(5, 16):
		coh_lst.append(LDA(docs, args.modelSavePath + '_' + str(i), i))

	print(coh_lst)

#python lda.py --in /home/sameer/Projects/Political-leaning/Data/TXTs/TM --out /home/sameer/Projects/Political-leaning/Data/TXTs/TM/lda_model --n 6
#from gensim.models.ldamodel import LdaModel
#lda = LdaModel.load("/home/sameer/Projects/Political-leaning/Data/TXTs/TM/lda_model")
#lda.print_topics()
