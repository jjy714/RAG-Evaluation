
import argparse
import datasets
from pathlib import Path
from dotenv import load_dotenv

parser = argparse.ArgumentParser()
# action="store_true"
parser.add_argument("-m", "--metrics", type=str,help="Which Metrics to evaluate" )        
parser.add_argument("-d", "--dataset",type=str, help="Dataset to evaluate on")    
parser.add_argument("-M", "--mode", type=str, help="Evaluate on Retrieval, Generator, or Overall")     
args = parser.parse_args()




def evaluator():
    dataset = load_dataset(args.dataset)
    metrics = args.metrics.split(",")
    selected_metrices=args.mode.split(",")

    


if __name__ == '__main__':
    evaluator()