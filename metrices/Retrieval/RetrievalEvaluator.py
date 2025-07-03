from accuracy import accuracy
from typing import Dict, List, Any, Optional
import json
from tqdm import tqdm
import re
from collections import Counter
import numpy as np


class ConfusionMatrix:

    def __init__(self, prediction: List, answer_label: List):
        
        self.prediction = prediction
        self.answer_label = answer_label    

        self.true_positive = []
        self.true_negative = []
        self.false_positive = []
        self.false_negative = []
        
        self._process()

    def has_intersection(self, a, b):
        a_words = set(a.split())
        b_words = set(b.split())
        return len(a_words.intersection(b_words)) > 0
    
    def _process(self):
        """
        Iterates through predictions and answers to populate the TP, FP, and FN lists.
        """
        # Clear lists to ensure idempotent behavior if called multiple times
        self.true_positive = []
        self.true_negative = []
        self.false_positive = []
        self.false_negative = []

        self.true_positive = sum(1 for pred, ans in zip(self.prediction, self.answer_label) if self.has_intersection(pred.lower(), ans.lower()))
        self.false_positive = sum(1 for pred, ans in zip(self.prediction, self.answer_label) if not self.has_intersection(pred.lower(), ans.lower()))
        self.false_negative  = len(self.answer_label) - self.true_positive
        self.true_negative = len(self.prediction) - self.true_positive


class RetrievalEvaluator:
    
    """
    RANK-UNAWARE
    Description: 
    
    Do an evaluation on the dataset which contains the query, answer label, and retrieved document. 

    Receives the following parameters to init:
        Dataset: Path to the dataset. Needs to be in (json, csv, txt) format
        metrics: which metric to work on. Can be multiple
    Functions:
        
    
    """

    def __init__(
            self, 
            dataset: str,
            metrics: List[str] | str 
            ):
        self.dataset = dataset
        self.metrics = metrics
        self.user_query = []
        self.prediction_list = []
        self.answer_label_list = []
        self._process_data()
        self._confusion_matrix = ConfusionMatrix(
            prediction=self.prediction_list, 
            answer_label=self.answer_label_list
            )


    def check_file_type(self):
        #check file type. return the type. 
        pass
    def _process_data(self):
        """
        Args: self 
        Returns: 
            user query list
            prediction list
            answer label list 
        """
        self.user_query=[]
        self.prediction_list=[] # List of Dict -> {"doc id", "doc content", "rank"}
        self.answer_label_list=[] # List of Relevant Documents("doc id", "doc content") per query,
        return 
    
    def precision(self):
        true_positive = self._confusion_matrix.true_positive
        false_positive = self._confusion_matrix.false_positive
        return true_positive / (true_positive + false_positive) if true_positive + false_positive > 0 else 0

    def recall(self):
        true_positive = self._confusion_matrix.true_positive
        false_negative = self._confusion_matrix.false_negative
        return true_positive / (true_positive + false_negative) if true_positive + false_negative > 0 else 0

    def f1(self):
        precision = self.precision()
        recall = self.recall()
        return 2 * (precision * recall) / (precision + recall) if precision + recall > 0 else 0

    def accuracy(self):
        true_positive = self._confusion_matrix.true_positive
        false_positive = self._confusion_matrix.false_positive
        false_negative = self._confusion_matrix.false_negative
        true_negative = self._confusion_matrix.true_negative        
        return (true_positive + true_negative) / (true_positive + true_negative + false_positive + false_negative) if (true_positive + true_negative + false_positive + false_negative) > 0 else 0

    def MRR(self, retrieved_docs, ground_truth_ids):
        
        reciprocal_ranks = []

    # Iterate through each query's results
        for i, retrieved in enumerate(retrieved_docs):
            relevant_ids_for_query = set(ground_truth_ids[i])
            
            # Sort retrieved documents by rank to be sure
            sorted_retrieved = sorted(retrieved, key=lambda x: x['rank'])
            
            rank = 0
            for doc in sorted_retrieved:
                if doc['doc_id'] in relevant_ids_for_query:
                    # Found the first relevant document, calculate reciprocal rank and break
                    rank = doc['rank']
                    reciprocal_ranks.append(1.0 / rank)
                    break
            
            # If no relevant document was found for this query, rank is 0
            if rank == 0:
                reciprocal_ranks.append(0.0)

        # Calculate the mean of all reciprocal ranks
        mrr_score = np.mean(reciprocal_ranks) if reciprocal_ranks else 0.0
        return mrr_score
            
    def MAP(self, retrieved_docs, ground_truth_ids) -> float:
        """
        Calculates the Mean Average Precision (MAP) for a set of queries.

        MAP provides a more comprehensive measure than MRR by considering the
        precision at each relevant document's position.
        """
        average_precisions = []
        for i, retrieved in enumerate(retrieved_docs):
            relevant_ids_for_query = set(ground_truth_ids[i])
            if not relevant_ids_for_query:
                average_precisions.append(0.0)
                continue
            sorted_retrieved = sorted(retrieved, key=lambda x: x['rank'])
            hits = 0
            precisions_at_k = []
            for k, doc in enumerate(sorted_retrieved, 1):
                if doc['doc_id'] in relevant_ids_for_query:
                    hits += 1
                    precision_at_k = hits / k
                    precisions_at_k.append(precision_at_k)
            if not precisions_at_k:
                average_precisions.append(0.0)
            else:
                average_precisions.append(np.mean(precisions_at_k))
        return np.mean(average_precisions) if average_precisions else 0.0

    def precision_at_k(self, retrieved_docs, ground_truth_ids, k) -> float:
        """
        Calculates the Mean Precision@K for a set of queries.

        Precision@K is the proportion of retrieved documents in the top K
        that are relevant.
        """
        all_precisions_at_k = []
        for i, retrieved in enumerate(retrieved_docs):
            relevant_ids_for_query = set(ground_truth_ids[i])
            top_k_docs = sorted([d for d in retrieved if d['rank'] <= k], key=lambda x: x['rank'])
            
            hits = 0
            for doc in top_k_docs:
                if doc['doc_id'] in relevant_ids_for_query:
                    hits += 1
            
            precision_at_k = hits / k if k > 0 else 0.0
            all_precisions_at_k.append(precision_at_k)
            
        return np.mean(all_precisions_at_k) if all_precisions_at_k else 0.0
