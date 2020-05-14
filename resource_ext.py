#!/usr/bin/python3

import pandas as pd
import numpy as np
import os 


def extract_upbd(input_file,output_file):
    """
    Read local csv file downloaded from Urine Protein Biomarker Database 
    http://upbd.bmicc.cn/biomarker/web/indexdb
    Extract and adjust relevant information to fit the Biomarker model 
    Save to a new csv file
    """
    upbd = pd.read_excel(input_file,sheet_name='Page 1', index_col=None, na_values=['NA'])

    # Extracting relevant information
    subset = upbd[['Protein name','Protein ID','Biomarker usage','Treatment','Disease','Disease ID','In a panel','Experiment','Pmid']]

    # Converting usage to fit the biomarker model
    usage = {
        'Diagnosis':'DiagnosticBM',
        'Prediction of response to treament':'PredictiveBM',
        'Early diagnosis':'DiagnosticBM',
        'Indicator of physiological process':'DiagnosticBM',
        'Classification':'DiagnosticBM',
        'Prognosis':'PrognosticBM',
        'Indicator of severity':'PrognosticBM',
        'Staging':'PrognosticBM',
        'Diease progression':'PrognosticBM',
        'Risk factor':'RiskBM'
        }
    for key,value in usage.items():
        subset["Biomarker usage"] = subset["Biomarker usage"].replace({key:value},regex=True)

    #print(subset['Biomarker usage'].value_counts())
    #print(subset.shape)
    #print(subset.isnull().sum())

    # Remove biomarkers with no inforamtion about experiment type, usage or whether it's a singel or a panel
    subset = subset.dropna(subset = ['Experiment', 'Biomarker usage','In a panel'])

    # Predictive biomarkers must contain a treatment as well
    #print("Checking for predictive biomarkers with no treatment:")
    #print(subset[subset['Biomarker usage'] == 'PredictiveBM'].isnull().sum())

    '''
    Adding relevant columns: 
    Source = Urine, Molecular type = Protein
    The dataset does not contain information about technology or evidence level
    For now, 'experimental' status will be assigned to all biomarkers and technology will not be specified
    '''
    subset['Type'] = 'MolecularBM'
    subset['Source'] = 'http://purl.obolibrary.org/obo/UBERON_0001088'
    subset['Molecular type'] = 'http://ns.ontoforce.com/ontologies/integration_ontology#Protein'
    subset['Evidence level'] = 'Experimental'

    # Renaming columns to fit the biomarker model terminology 
    subset.rename(columns={'Protein name':'Name','Protein ID':'Molecular ID','Biomarker usage':'Usage','Experiment':'Assay/Technology'}, inplace=True)

    # Write to csv file
    new_index = [
        'Name','Usage','Disease','Disease ID','In a panel','Evidence level',
        'Type','Source','Assay/Technology','Pmid','Molecular type','Molecular ID','Treatment']
    #subset.reindex(new_index)
    print("Writing to "+output_file)
    subset.to_csv(output_file, columns = new_index)

def extract_resdb(output_file):
    resdb_url = "http://resmarkerdb.org/static/biomarker/files/2018_TREC_Precision_Medicine_Challenge_Data.csv"
    resdb = pd.read_csv(resdb_url, sep='\t')
    resdb.to_csv(output_file)

def extract_oncomx(output_file):
    base_url = "http://data.oncomx.org/ln2wwwdata/reviewed/human_cancer_biomarkers_FDA_"
    cancer_types = ["breast","colorectal","lung","ovarian","prostate","melanoma"]
    dfs = []
    for cn_type in cancer_types:
        url = base_url+cn_type+".csv"
        print("Reading from: "+url)
        dfs.append(pd.read_csv(url))
        
    joined_dfs = pd.concat(dfs,ignore_index=True)
#    joined_dfs.to_csv(output_dir+"/joined_dfs.csv")

    cols = [
        "gene_symbol","test_is_a_panel","doid","actual_use","test_adoption_evidence",
        "specimen_type","test_trade_name","test_manufacturer","pmid",
        "biomarker_drug","biomarker_description"
        ]

    subset = joined_dfs[cols]
#    subset.to_csv(output_dir+"/subset.csv")

    #Assigning URIs for disease, specimen, molecular type, molcular id      
    subset.loc[subset.index, 'doid'] = 'http://purl.obolibrary.org/obo/DOID_' + subset['doid'].astype(str)
    
    #Paraffin block refers to Formalin-Fixed Paraffin-Embedded (FFPE) tissue specimens 
    specimens = {
        ("Paraffin block","Paraffin Block","Parrafin block","paraffin block","parrafin block", "Fresh Tissue"):"http://purl.obolibrary.org/obo/UBERON_0000479",
        ("urine","Urine"):"http://purl.obolibrary.org/obo/UBERON_0001088", 
        ("blood","Blood"):"http://purl.obolibrary.org/obo/UBERON_0000178",
        ("saliva","Saliva"):"http://purl.obolibrary.org/obo/UBERON_0001836",
        ("human stool","Stool","stool"):"http://purl.obolibrary.org/obo/UBERON_0001988"
        }
    for keys, values in specimens.items():
        subset["specimen_type"] = subset["specimen_type"].replace(to_replace = keys, value = values,regex=True)

    subset["Type"] = 'MolecularBM'
    subset["Molecular type"] = 'http://ns.ontoforce.com/ontologies/integration_ontology#Gene'
    subset["Molecular ID"] = 'http://identifiers.org/hgnc.symbol/'+subset["gene_symbol"]
    
    usage = {
    "predisposition":"RiskBM",
    ("prognostic_","prognostic"):"PrognosticBM",
    ("diagnostic_","diagnostic"):"DiagnosticBM",
    "predictive":"PredictiveBM"
    }
    for keys, values in usage.items():
        subset["actual_use"] = subset["actual_use"].replace(to_replace = keys, value = values,regex=True)

    subset.rename(columns={
        'gene_symbol':'Name','test_is_a_panel':'In a panel','doid':'Disease ID',
        'actual_use':'Usage','specimen_type':'Source','test_trade_name':'Test trade name',
        'test_manufacturer':'Test manufacturer','pmid':'Pmid','test_adoption_evidence':'Evidence level',
        'biomarker_drug':'Treatment','biomarker_description':'Description'
        }, inplace=True)
    
    # Write to csv file
    new_index = [
        'Name','Usage','Disease ID','In a panel','Evidence level',
        'Type','Source','Test trade name','Test manufacturer','Pmid','Molecular type','Molecular ID','Treatment']
    
    print("Writing to "+output_file)
    subset.to_csv(output_file, columns = new_index)


# Extract resources
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
input_file = dname+'/upbd.xls'
output_file = dname+'/bm_upbd.csv'

#extract_upbd(input_file,output_file)

output_file = dname+'/bm_res.csv'
#extract_resdb(output_file)

output_file = dname+'/bm_oncomx.csv'
extract_oncomx(output_file)

