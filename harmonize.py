#!/usr/bin/python3

import os 
from resource_ext import extract_cbd, extract_oncomx, extract_upbd
#from owlready2 import *

# Extracting data and saving to csv files
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

input_file = dname+'/upbd.xls'
output_file = dname+'/bm_upbd.csv'
df_upbd = extract_upbd(input_file,output_file)

output_file = dname+'/bm_oncomx.csv'
df_oncomx = extract_oncomx(output_file)

output_file = dname+'/bm_cbd.csv'
df_cbd = extract_cbd(output_file)

#output_file = dname+'/bm_ptsd.csv'
#extract_ptsd(output_file)
'''
# Creating new individuals in biomarker ontology
bm = get_ontology("file://D:/ontoforce/model/bm_model2.owl").load()
doid = get_ontology("file://D:/ontoforce/model/doid-merged.owl").load()
uberon = get_ontology("file://D:/ontoforce/model/uberon.owl").load()
obo = get_namespace("http://purl.obolibrary.org/obo/")

# Create an instance - example
desc = 'From FDA The report describes if a woman is at increased risk of developing breast and ovarian cancer_ and if a man is at increased risk of developing breast cancer or may be at increased risk of developing prostate cancer. From EDRN BRCA1 is a nuclear phosphoprotein that functions as a tumor suppressor...[and] thus plays a role in transcription_ DNA repair of double-stranded breaks_ and recombination. Mutations in this gene are responsible for approximately 40% of inherited breast cancers and more than 80% of inherited breast and ovarian cancers.'
bm1 = RiskBM()
bm1.is_a.append(MolecularBM)
bm1.is_a.append(indicatorOf.some(obo.DOID_1612))
bm1.inPanel.append(True)
bm1.hasEvidenceLevel.append('Experimental')
bm1.hasClinicalTrialID.append('NCT01598597')
bm1.hasDescription.append(desc)
bm1.is_a.append(measuredIn.some(obo.UBERON_0001836))
bm1.hasMolecularType.append('somatic mutation')
bm1.assesedBy.append('Assay')
bm1.assesedBy.append('Tech')

for i in Biomarker.instances():
    print(i)
    print(i.is_a)
    #destroy_entity(i)

# Creating panels

bm.save()

'''