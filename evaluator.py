from metrics import GenerationEvaluator, RetrievalEvaluator

import argparse
import datasets
from pathlib import Path
from dotenv import load_dotenv

parser = argparse.ArgumentParser()
# action="store_true"
parser.add_argument("-m", "--metrics")        
parser.add_argument("-d", "--dataset")         
args = parser.parse_args()


def evaluator():
    pass



if __name__ == '__main__':
    evaluator()