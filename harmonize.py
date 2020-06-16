import os 
from resource_ext import extract_cbd, extract_oncomx, extract_upbd
import warnings

warnings.filterwarnings('ignore')

######################################################################
#   Extract data from sources and adjust it to the biomarker model   #
######################################################################

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

# Urine Protein Biomarker Database
input_file = dname+'/upbd.xls'  
output_file = dname+'/bm_upbd.csv'
# Use 'disqover' parameter to fit to subsequent use (in DISQOVER or in Ontology model)
df_upbd = extract_upbd(input_file,output_file,disqover=False)

# Oncomx FDA Biomarkers
output_file = dname+'/bm_oncomx.json'
df_oncomx = extract_oncomx(output_file,disqover=False)

# Colorectal cancer biomarker database
output_file = dname+'/bm_cbd.json'
df_cbd = extract_cbd(output_file,disqover=False)


# Merge data from different sources
df_upbd['Id'] = 'upbd_'+ df_upbd['Id'].astype(str)
df_oncomx['Id'] = 'oncomx_'+ df_oncomx['Id'].astype(str)
df_cbd['Id'] = 'cbd_'+ df_cbd['Id'].astype(str)
 
merged = df_upbd.append(df_oncomx).append(df_cbd)
index = [
        'Id','Name','Usage','Disease','Disease ID','In a panel','Evidence level','Type','Source','Source ID',
        'Assay/Test','Test manufacturer','Pmid','Molecular type','Molecular ID','Treatment','Description','Clinical trail ID']
merged.to_excel('merged.xlsx',columns = index, index = False)

############################################################
#   Creating individuals using biomarker ontology model    #   
############################################################

from owlready2 import *
import pandas as pd

print("Loading Biomarker ontology..")
biomarker = get_ontology("file://D:/ontoforce/model/bm_model.owl").load()

# Creating new individuals in biomarker ontology for OncoMX biomarkers
print("Creating individuals..")

# Iterate over merged data and extract relevant information
# Use information to create objects and describe their relationships
for index, row in merged.iterrows():

    # Create instances of classes
    bm_usage = row['Usage'].split('|')
    disease = biomarker.Disease(row['Disease ID'])
    disease.label = row['Disease']
    source = biomarker.AnatomicalEntity(row['Source ID'])
    source.label = row['Source']
    assay = biomarker.AssayTest(row['Assay/Test'])
    new_bm = biomarker.MolecularBM(row['Id'])
    new_bm.label = row['Name']
    
    # Create relations between instances (object properties)
    for item in bm_usage:
        usage = 'biomarker.'+item
        new_bm.is_a.append(eval(usage))
    new_bm.indicatorOf.append(disease) 
    new_bm.measuredIn.append(source)
    new_bm.measuredBy.append(assay)

    # Some information is not provided for all biomarkers
    molecular_type = row['Molecular type']
    molecular_id = row['Molecular ID']
    evidence_level = row['Evidence level']
    desc = row['Description']
    pmid = row['Pmid']
    if not pd.isnull(evidence_level) : new_bm.hasEvidenceLevel.append(evidence_level)
    if not pd.isnull(desc): new_bm.hasDescription.append(desc)
    if not pd.isnull(molecular_type): new_bm.hasMolecularType.append(molecular_type)
    if not pd.isnull(molecular_id): new_bm.hasMolecularID.append(molecular_id)
    if not pd.isnull(pmid): 
        publication = biomarker.Publication(str(pmid))
        new_bm.hasEvidence.append(publication)

print('Saving to file')
biomarker.save(file='D:/ontoforce/model/bm_db.owl',format='rdfxml')

