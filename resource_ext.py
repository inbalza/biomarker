#!/usr/bin/python3

import pandas as pd
import numpy as np

'''
Containing functions to be used for extracting biomarker information from different resources
'''

source_ids = {
        "Tissue":"UBERON_0000479",
        "Urine":"UBERON_0001088", 
        "Blood":"UBERON_0000178",
        "Saliva":"UBERON_0001836",
        "Feces":"UBERON_0001988"
    }

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
        'Risk factor':'RiskBM',
        'Treatment':'PredictiveBM'
        }

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
    for key,value in usage.items():
        subset["Biomarker usage"] = subset["Biomarker usage"].replace({key:value},regex=True)

    # Remove biomarkers with no inforamtion about experiment type, usage or whether it's a singel or a panel
    nrow_before = subset.shape[0]
    subset = subset.dropna(subset = ['Experiment', 'Biomarker usage','In a panel'])
    nrow_after = subset.shape[0]
    dropped = nrow_before-nrow_after
    dropped_per = round(dropped/nrow_before*100,2)
    print("Dropped {} ({}%) rows with missing data over experiment, usage or panel".format(dropped, dropped_per))

    # Predictive biomarkers must contain a treatment as well
    #print("Checking for predictive biomarkers with no treatment:")
    #print(subset[subset['Biomarker usage'] == 'PredictiveBM'].isnull().sum()) 

    '''
    Adding relevant columns: 
    Source = Urine, Molecular type = Protein
    The dataset does not contain information about technology or evidence level - will not be added for now
    '''
    subset['Type'] = 'MolecularBM'
    subset['Source'] = 'Urine'
    subset['Source ID'] = source_ids['Urine']
    subset['Molecular type'] = 'Protein'

    # Renaming columns to fit the biomarker model terminology 
    subset.rename(columns={'Protein name':'Name','Protein ID':'Molecular ID','Biomarker usage':'Usage','Experiment':'Assay/Technology'}, inplace=True)

    # Write to csv file
    new_index = [
        'Name','Usage','Disease','Disease ID','In a panel','Evidence level',
        'Type','Source','Source ID','Assay/Technology','Pmid','Molecular type','Molecular ID','Treatment']

    print("Writing to "+output_file)
    subset.to_csv(output_file, columns = new_index)

def extract_oncomx(output_file):
    '''
    Oncomx contains datasets of FDA-approved or cleared nucleic acid-based human biomarker tests for cancer
    Each row represents one gene linked to its respective test. 
    Genes are labeled by relevant identifiers/accessions from UniProtKB, HGNC, and EDRN. 
    Tests are distinguished by manufacturer, FDA submission ID(s), clinical trial ID(s), and PubMed ID(s).
    '''
    # Read and join csv's into one dataframe
    base_url = "http://data.oncomx.org/ln2wwwdata/reviewed/human_cancer_biomarkers_FDA_"
    cancer_types = ["breast","colorectal","lung","ovarian","prostate","melanoma"]
    dfs = []
    for cn_type in cancer_types:
        url = base_url+cn_type+".csv"
        print("Reading from: "+url)
        dfs.append(pd.read_csv(url))
        
    joined_dfs = pd.concat(dfs,ignore_index=True)

    # Define relevant columns to extract
    cols = [
        "gene_symbol","test_is_a_panel","do_name","doid","actual_use","test_adoption_evidence",
        "specimen_type","test_trade_name","test_manufacturer","pmid",
        "biomarker_drug","biomarker_description","biomarker_origin","test_trial_id",
        ]

    subset = joined_dfs[cols]

    #Adjusting specimen type and usage to the biomarker model
    #Paraffin block refers to Formalin-Fixed Paraffin-Embedded (FFPE) tissue specimens 
    specimens = {
        ("Paraffin block","Paraffin Block","Parrafin block","paraffin block","parrafin block", "Fresh Tissue"):"Tissue",
        ("urine","Urine"):"Urine", 
        ("blood","Blood"):"Blood",
        ("saliva","Saliva"):"Saliva",
        ("human stool","Stool","stool"):"Feces"
        }

    for key, value in specimens.items():
        subset["specimen_type"] = subset["specimen_type"].replace(to_replace = key, value = value,regex=True)
    
    subset["Type"] = 'MolecularBM'
    subset["Molecular ID"] = subset["gene_symbol"]
    subset["doid"] = "DOID_" + subset["doid"].astype(str)
    
    usage = {
    "predisposition":"RiskBM",
    ("prognostic_","prognostic"):"PrognosticBM",
    ("diagnostic_","diagnostic"):"DiagnosticBM",
    "predictive":"PredictiveBM"
    }
    for keys, values in usage.items():
        subset["actual_use"] = subset["actual_use"].replace(to_replace = keys, value = values,regex=True)

    subset.rename(columns={
        'gene_symbol':'Name','test_is_a_panel':'In a panel','do_name':'Disease','doid':'Disease ID',
        'actual_use':'Usage','specimen_type':'Source','test_trade_name':'Test trade name',
        'test_manufacturer':'Test manufacturer','pmid':'Pmid','test_adoption_evidence':'Evidence level',
        'biomarker_drug':'Treatment','biomarker_description':'Description','biomarker_origin':'Molecular type','test_trial_id':'Clinical trail ID'
        }, inplace=True)
    
    # Write to csv file
    new_index = [
        'Name','Usage','Disease','Disease ID','In a panel','Evidence level','Type','Source','Source ID',
        'Test trade name','Test manufacturer','Pmid','Molecular type','Molecular ID','Treatment','Description','Clinical trail ID']
    
    print("Writing to "+output_file)
    subset.to_csv(output_file, columns = new_index)

def extract_cbd(output_file):
    """
    CBD: Colorectal Cancer Biomarker Database http://sysbio.suda.edu.cn/CBD/index.html
    """
    url = "http://sysbio.suda.edu.cn/CBD/download/data.xlsx"
    cbd = pd.read_excel(url, index_col=None)
    
    # Extract relevant information
    subset = cbd[["Biomarker","Categary","Discription","Location","Source","Experiment","Application","PMID","Statictics","Conclusion"]]

    # Join all columns decscribing the experiment and its results and conclusions into one column
    subset["Description"] = subset.apply(lambda x: '_'.join(x[["Discription","Statictics","Conclusion"]].dropna().astype(str).values), axis=1)
    subset = subset.drop(["Discription","Statictics","Conclusion"],axis=1)

    # Dropping rows with no data over Experiment (assay) or Source
    nrow_before = subset.shape[0]
    subset = subset.dropna(subset = ["Experiment","Source"])
    nrow_after = subset.shape[0]
    dropped = nrow_before-nrow_after
    dropped_per = round(dropped/nrow_before*100,2)
    print("Dropped {} ({}%) rows with missing data over experiment or source".format(dropped, dropped_per))

    # Adjusting 
    molecular_types = {
        ('Protein','protein'):'Protein',
        ('DNA','RNA','MicroRNA','LncRNA','LncRNA ','Small nucleolar RNAs (snoRNAs)','Circular RNA'):'Nucleic acid',
        'Other':np.NaN
    }
    for key,value in molecular_types.items():
        subset["Categary"] = subset["Categary"].replace(to_replace = key, value = value)

    # Replace 'cell line' as source with Tissue
    subset['Source']=subset['Source'].replace(to_replace=('Cell line','cell line'),value='Tissue',regex=True)

    # Remove duplicate values for source
    # Adjust usage
    for index, row in subset.iterrows():
        src = row['Source'].split(", ")
        unique_src = list(dict.fromkeys(src))
        subset.at[index,'Source'] = '_'.join(unique_src)

        apps = row['Application'].split(", ")
        new_app = usage[apps[0]]
        if len(apps) > 1:
            apps.pop(0)
            for item in apps:
                new_app = new_app + '|' + usage[item]
        subset.at[index,'Application'] = new_app
    
    # Remove rows with more than once source 
    nrow_before = subset.shape[0]
    subset = subset.drop(subset[subset['Source'].str.contains('_')].index)
    nrow_after = subset.shape[0]
    dropped = nrow_before-nrow_after
    dropped_per = round(dropped/nrow_before*100,2)
    print("Dropped {} ({}%) rows with more than one source".format(dropped, dropped_per))

    # Add source ID
    subset["Source ID"] = subset["Source"]
    for key, value in source_ids.items():
        subset["Source ID"] = subset["Source ID"].replace(to_replace = key, value = value,regex=True)

    subset['Disease'] = 'Colorectal Cancer'
    subset['Disease ID'] = 'DOID_9256'
    subset['Type'] = 'MolecularBM'

    subset.rename(columns={
        'Biomarker':'Name','Application':'Usage','PMID':'Pmid','Categary':'Molecular type'}, inplace=True)
    
    # Write to csv file
    new_index = ['Name','Usage','Disease','Disease ID','Type','Source','Source ID','Experiment','Pmid','Molecular type','Description']
    
    print("Writing to "+output_file)
    subset.to_csv(output_file, columns = new_index)    
