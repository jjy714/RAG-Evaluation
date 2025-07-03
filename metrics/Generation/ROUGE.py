from ragas.metrics import RougeScore


def rouge(self):
    """
    DOCUMENTATION
    
    You can change the rouge_type to rouge1 or rougeL 
    to calculate the ROUGE score based on unigrams or longest common subsequence respectively.
    
    You can change the mode to precision, recall, or fmeasure 
    to calculate the ROUGE score based on precision, recall, or F1 score respectively.
    
    """
    scorer = RougeScore(rouge_type="rouge1")
    scorer2 = RougeScore(mode="recall")
    
    pass