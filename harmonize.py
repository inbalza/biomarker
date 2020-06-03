import os 
from resource_ext import extract_cbd, extract_oncomx, extract_upbd
import warnings

warnings.filterwarnings('ignore')

##############################################################
#   Extract data from and adjust it to the biomarker model   #
##############################################################

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

# Urine Protein Biomarker Database
input_file = dname+'/upbd.xls'  
output_file = dname+'/bm_upbd.csv'
df_upbd = extract_upbd(input_file,output_file)

# Oncomx FDA Biomarkers
output_file = dname+'/bm_oncomx.csv'
df_oncomx = extract_oncomx(output_file)

# Colorectal cancer biomarker database
output_file = dname+'/bm_cbd.json'
df_cbd = extract_cbd(output_file)

#######################################################################
#   Example of creating new instances using biomarker ontology model  #   
#######################################################################

from owlready2 import *
bm = get_ontology("file://D:/ontoforce/model/bm_model2.owl").load()
print("Loading DOID ontology...")
doid = get_ontology("file://D:/ontoforce/model/doid-merged.owl").load() # downloaded from: https://github.com/DiseaseOntology/HumanDiseaseOntology/tree/master/src/ontology
print("Loading UBERON ontology...")
uberon = get_ontology("file://D:/ontoforce/model/uberon.owl").load() # downloaded from https://uberon.github.io/downloads.html
obo = get_namespace("http://purl.obolibrary.org/obo/")

print(df_oncomx.columns)

# Creating new individuals in biomarker ontology for OncoMX biomarkers
nr_inst = 10
for index, row in df_oncomx.head(nr_inst).iterrows():
    #print("Biomarker: {}".format(row))
    name = row['Name']
    bm_usgae = 'bm.'+row['Usage']
    bm_type = 'bm.'+row['Type']
    dis_id = 'obo.'+row['Disease ID']
    source = 'obo.'+row['Source ID']
    if row['In a panel'] == 'Y': in_panel = True 
    else: in_panel = False

    new_bm = eval(bm_usgae)(name)
    new_bm.is_a.append(eval(bm_type))
    new_bm.inPanel.append(in_panel)
    new_bm.hasMolecularType.append(row['Molecular type'])
    
    # source and disease are classes and not individuals
    # currently Relation between an individual and a class must be represented by a restriction
    new_bm.is_a.append(bm.indicatorOf.some(eval(dis_id))) 
    new_bm.is_a.append(bm.measuredIn.some(eval(source)))
    
    new_bm.measuredBy.append(row['Assay/Test'])
    new_bm.hasEvidenceLevel.append(row['Evidence level'])
    new_bm.hasClinicalTrialID.append(row['Clinical trail ID'])
    new_bm.hasDescription.append(row['Description'])

print("New instances created:")
for bm in bm.Biomarker.instances():
    print(bm)

bm.save(file='D:/ontoforce/model/model_with_instances.owl')

