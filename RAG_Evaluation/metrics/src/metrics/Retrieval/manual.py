from accuracy import accuracy
from typing import Dict, List, Any, Optional
import json
from tqdm import tqdm
import re
from collections import Counter
import numpy as np



class ManualConfusionMatrix:

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

class ManualRetrievalEvaluator:
    
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

    
    

