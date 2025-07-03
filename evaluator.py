
import argparse
import datasets
from pathlib import Path
from dotenv import load_dotenv
from datasets import load_dataset, Dataset

EXAMPLE_DATASET="allganize/RAG-Evaluation-Dataset-KO"

# action="store_true"
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--metrics", type=str,help="Which Metrics to evaluate" )        
parser.add_argument("-d", "--dataset",type=str, help="Dataset to evaluate on")    
parser.add_argument("-M", "--mode", type=str, help="Evaluate on Retrieval, Generator, or Overall")     
args = parser.parse_args()


def evaluator():
    # dataset = load_dataset(args.dataset)
    dataset = load_dataset(EXAMPLE_DATASET)
    # metrics = args.metrics.split(",")
    # selected_metrices=args.mode.split(",")

    


if __name__ == '__main__':
    evaluator()