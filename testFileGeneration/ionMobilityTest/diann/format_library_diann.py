# This script formats an OSW library to be used with DIA-NN

import argparse
import pandas as pd


parser = argparse.ArgumentParser(description='format osw library to be compatible with DIA-NN')
parser.add_argument('fIn', help='.tsv file in')
parser.add_argument('fOut', help='.tsv file out')


args = parser.parse_args()


fIn = pd.read_csv(args.fIn, sep='\t')
fIn = fIn[fIn['Decoy'] == 0]

fIn = fIn.drop(columns=['PeptideGroupLabel', 'LabelType', 'CompoundName', 'SumFormula', 'SMILES', 'Adducts', 'UniprotId', 'CollisionEnergy', 'TransitionGroupId', 'TransitionId', 'Decoy', 'DetectingTransition', 'IdentifyingTransition', 'QuantifyingTransition', 'Peptidoforms'])

fIn.to_csv(args.fOut, sep='\t', index=False)
