#!/usr/bin/python3

import pandas as pd
import numpy as np

'''
Containing functions to be used for extracting biomarker information from different resources
'''

def adj_src(df):
    '''
    Input: a pandas.DataFrame object containing 'Source' column  
    Adjust source names to fit the biomarker model
    Add a column Source ID containing UBERON URIs
    Returns the processed DataFrame
    '''
    sources = {
        ("Tissue","Paraffin block","Paraffin Block","Parrafin block","paraffin block","parrafin block", "Fresh Tissue"):"tissue",
        ("Cell line","cell line"):"tissue",
        ("Urine"):"urine", 
        ("Blood"):"blood",
        ("Saliva"):"saliva",
        ("human stool","Stool","stool","Feces"):"feces"
    }
    source_ids = {
        "tissue":"http://purl.obolibrary.org/obo/UBERON_0000479",
        "urine":"http://purl.obolibrary.org/obo/UBERON_0001088", 
        "blood":"http://purl.obolibrary.org/obo/UBERON_0000178",
        "saliva":"http://purl.obolibrary.org/obo/UBERON_0001836",
        "feces":"http://purl.obolibrary.org/obo/UBERON_0001988"
    }

    for key, value in sources.items():
        df["Source"] = df["Source"].replace(to_replace = key, value = value,regex=True)

    df["Source ID"] = df["Source"]
    for key, value in source_ids.items():
        df["Source ID"] = df["Source ID"].replace(to_replace = key, value = value,regex=True)
    
    return df

def adj_usage(df):
    '''
    Input: a pandas.DataFrame object containing 'Usage' column  
    Adjust usage to fit the biomarker model
    Returns the processed DataFrame
    '''
    usage = {
        ('Prognosis','prognostic_','prognostic'):'PrognosticBM',
        ('Indicator of severity','Staging','Diease progression'):'PrognosticBM',
        ('diagnostic_','diagnostic','Diagnosis'):'DiagnosticBM',
        ('Early diagnosis','Indicator of physiological process','Classification'):'DiagnosticBM',
        ('predictive','Treatment','Prediction of response to treament'):'PredictiveBM',
        ('predisposition','Risk factor'):'RiskBM',
        }

    for keys, values in usage.items():
        df["Usage"] = df["Usage"].replace(to_replace = keys, value = values,regex=True)
    return df

def extract_upbd(input_file,output_file):
    """
    Read local csv file (input_file) downloaded from Urine Protein Biomarker Database 
    http://upbd.bmicc.cn/biomarker/web/indexdb
    Extract and adjust relevant information to fit the Biomarker model 
    Writes results to output_file (csv) and returns a DataFrame
    """
    print("\nExtracting Urine Protein Biomarker Database...")
    upbd = pd.read_excel(input_file,sheet_name='Page 1', index_col=None, na_values=['NA'])

    # Extracting relevant information
    #The dataset does not contain information about evidence level
    subset = upbd[['Protein name','Protein ID','Biomarker usage','Treatment','Disease','Disease ID','In a panel','Experiment','Pmid']]

    # Renaming columns to fit the biomarker model terminology and adding relevant columns
    subset.rename(columns={'Protein name':'Name','Protein ID':'Molecular ID','Biomarker usage':'Usage','Experiment':'Assay/Test'}, inplace=True)
    subset['Source'] = 'urine'
    subset['Type'] = 'MolecularBM'
    subset['Molecular type'] = 'Protein'
    subset['Evidence level'] = np.NaN

    # Converting usage to fit the biomarker model and add source id
    subset = adj_usage(subset)
    subset = adj_src(subset)

    # Remove biomarkers with no inforamtion about assay, usage or whether it's a singel or a panel
    nrow_before = subset.shape[0]
    subset = subset.dropna(subset = ['Assay/Test', 'Usage','In a panel'])
    nrow_after = subset.shape[0]
    dropped = nrow_before-nrow_after
    dropped_per = round(dropped/nrow_before*100,2)
    print("Dropped {} ({}%) rows with missing data over assay, usage or panel".format(dropped, dropped_per))

    # Write to csv file
    new_index = [
        'Name','Usage','Disease','Disease ID','In a panel','Evidence level','Type','Source','Source ID',
        'Assay/Test','Pmid','Molecular type','Molecular ID','Treatment']
    
    print("Writing to "+output_file)
    subset.to_csv(output_file, columns = new_index)
    return subset

def extract_oncomx(output_file):
    '''
    Oncomx contains datasets of FDA-approved or cleared nucleic acid-based human biomarker tests for cancer
    Each row represents one gene linked to its respective test. 
    Genes are labeled by relevant identifiers/accessions from UniProtKB, HGNC, and EDRN. 
    Tests are distinguished by manufacturer, FDA submission ID(s), clinical trial ID(s), and PubMed ID(s).
    Writes results to output_file (csv) and returns a DataFrame
    '''
    # Read and join csv's into one dataframe
    print("\nExtracting Oncomex Database...")
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

    # Renaming, adding relevant columns, adjusting usage and source
    subset.rename(columns={
        'gene_symbol':'Name','test_is_a_panel':'In a panel','do_name':'Disease','doid':'Disease ID',
        'actual_use':'Usage','specimen_type':'Source','test_trade_name':'Assay/Test',
        'test_manufacturer':'Test manufacturer','pmid':'Pmid','test_adoption_evidence':'Evidence level',
        'biomarker_drug':'Treatment','biomarker_description':'Description','biomarker_origin':'Molecular type','test_trial_id':'Clinical trail ID'
        }, inplace=True)
    subset["Type"] = 'MolecularBM'
    subset["Molecular ID"] = subset["Name"]
    subset["Disease ID"] = "http://purl.obolibrary.org/obo/DOID_" + subset["Disease ID"].astype(str)
    subset = adj_usage(subset)
    subset = adj_src(subset)
    
    # Write to csv file
    new_index = [
        'Name','Usage','Disease','Disease ID','In a panel','Evidence level','Type','Source','Source ID',
        'Assay/Test','Test manufacturer','Pmid','Molecular type','Molecular ID','Treatment','Description','Clinical trail ID']
    
    print("Writing to "+output_file)
    subset.to_csv(output_file, columns = new_index)
    return subset

def extract_cbd(output_file):
    """
    CBD: Colorectal Cancer Biomarker Database http://sysbio.suda.edu.cn/CBD/index.html
    Missing information in DB: In a panel, Evidence level, Molecular ID (assinged NaN values)
    Writes results to output_file (csv) and returns a DataFrame
    """
    print("\nExtracting Colorectal Cancer Biomarker Database...")
    url = "http://sysbio.suda.edu.cn/CBD/download/data.xlsx"
    cbd = pd.read_excel(url, index_col=None)
    
    # Extract relevant information
    subset = cbd[["Biomarker","Categary","Discription","Location","Source","Experiment","Application","PMID","Statictics","Conclusion"]]
    subset.rename(columns={
        'Biomarker':'Name','Application':'Usage','PMID':'Pmid','Categary':'Molecular type', 'Experiment':'Assay/Test'}, inplace=True)
    
    # Join all columns decscribing the experiment and its results and conclusions into one column
    subset["Description"] = subset.apply(lambda x: '_'.join(x[["Discription","Statictics","Conclusion"]].dropna().astype(str).values), axis=1)
    subset = subset.drop(["Discription","Statictics","Conclusion"],axis=1)

    # Dropping rows with no data over Experiment (assay) or Source
    nrow_before = subset.shape[0]
    subset = subset.dropna(subset = ["Assay/Test","Source","Usage"])
    nrow_after = subset.shape[0]
    dropped = nrow_before-nrow_after
    dropped_per = round(dropped/nrow_before*100,2)
    print("Dropped {} ({}%) rows with missing data over assay, source or usage".format(dropped, dropped_per))
    
    subset.loc[subset["Molecular type"] == "Other","Molecular type"] = np.NaN
    
    subset['Disease'] = 'Colorectal Cancer'
    subset['Disease ID'] = 'http://purl.obolibrary.org/obo/DOID_9256'
    subset['Type'] = 'MolecularBM'
    subset['In a panel'] = np.NaN
    subset['Evidence level'] = np.NaN
    subset['Molecular ID'] = np.NaN

    subset = adj_src(subset)
    subset = adj_usage(subset)
    
    # Some rows have multiple values for source, which are mostly duplicates
    # Remove duplicate values for source
    for index, row in subset.iterrows():
        src = row['Source'].split(", ")
        unique_src = list(dict.fromkeys(src))
        subset.at[index,'Source'] = '_'.join(unique_src)
    # Remove rows with more than once source 
    nrow_before = subset.shape[0]
    subset = subset.drop(subset[subset['Source'].str.contains('_')].index)
    nrow_after = subset.shape[0]
    dropped = nrow_before-nrow_after
    dropped_per = round(dropped/nrow_before*100,2)
    print("Dropped {} ({}%) rows with more than one source".format(dropped, dropped_per))
    
    # Write to csv file
    new_index = ['Name','Usage','Disease','Disease ID','In a panel','Evidence level','Type',
                'Source','Source ID','Assay/Test','Pmid','Molecular type','Molecular ID','Description']
    
    print("Writing to "+output_file)
    subset.to_csv(output_file, columns = new_index)  
    return subset  