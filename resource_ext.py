#!/usr/bin/python3

import pandas as pd
import numpy as np

'''
Containing functions to be used for extracting biomarker information from different resources
'''

def adj_src(df,del_duplicate):
    '''
    Input: a pandas.DataFrame object containing 'Source' column  
    Adjust source names to fit the biomarker model
    Add a column Source ID containing UBERON URIs
    Returns the processed DataFrame
    '''
    sources = {
        ("Fresh Tissue","Paraffin block","Paraffin Block","Parrafin block","paraffin block","parrafin block", "tissue"):"Tissue",
        ("Cell line","cell line"):"Tissue",
        ("urine"):"Urine", 
        ("blood"):"Blood",
        ("saliva"):"Saliva",
        ("human stool","Stool","stool","feces"):"Feces"
    }
    '''
    # to be used in DISQOVER
    source_ids = {
        "Tissue":"http://purl.obolibrary.org/obo/UBERON_0000479",
        "Urine":"http://purl.obolibrary.org/obo/UBERON_0001088", 
        "Blood":"http://purl.obolibrary.org/obo/UBERON_0000178",
        "Saliva":"http://purl.obolibrary.org/obo/UBERON_0001836",
        "Feces":"http://purl.obolibrary.org/obo/UBERON_0001988"
    }
    '''
    # to be used in ontology graph
    source_ids = {
        "Tissue":"UBERON_0000479",
        "Urine":"UBERON_0001088", 
        "Blood":"UBERON_0000178",
        "Saliva":"UBERON_0001836",
        "Feces":"UBERON_0001988"
    }

    for key, value in sources.items():
        df["Source"] = df["Source"].replace(to_replace = key, value = value,regex=True)

    if del_duplicate:
        # Remove duplicate values for source
        for index, row in df.iterrows():
            src = row['Source'].split(", ")
            unique_src = list(dict.fromkeys(src))
            df.at[index,'Source'] = '_'.join(unique_src)

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
    '''
    # to be used in DISQOVER
    usage = {
        ('Prognosis','prognostic_','prognostic','prognosis'):'Prognosis',
        ('Indicator of severity','Staging','Diease progression'):'Prognosis',
        ('diagnostic_','diagnostic','Diagnosis'):'Diagnosis',
        ('Early diagnosis','Indicator of physiological process','Classification'):'Diagnosis',
        ('predictive','Treatment','Prediction of response to treament'):'Prediction of response',
        ('predisposition','Risk factor'):'Susceptibility/Risk evaluation'
        }
    '''
    # to be used in ontology graph
    usage = {
        ('Prognosis','prognostic_','prognostic','prognosis'):'PrognosticBM',
        ('Indicator of severity','Staging','Diease progression'):'PrognosticBM',
        ('diagnostic_','diagnostic','Diagnosis'):'DiagnosticBM',
        ('Early diagnosis','Indicator of physiological process','Classification'):'DiagnosticBM',
        ('predictive','Treatment','Prediction of response to treament'):'PredictiveBM',
        ('predisposition','Risk factor'):'RiskBM'
        }


    for keys, values in usage.items():
        df["Usage"] = df["Usage"].replace(to_replace = keys, value = values,regex=True)
    return df

# Seperate multiple values by '|'
def adj_mult(val,sep):
    if val is np.NaN:
        return val
    else:
        val_list = [x.strip() for x in str(val).split(sep)]
        new_val = "|".join(val_list)
        return new_val
    
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
    # The dataset does not contain information about evidence level
    subset = upbd[['Protein name','Protein ID','Biomarker usage','Treatment','Disease','Disease ID','In a panel','Experiment','Pmid']]

    # Ajust Disease URIs to fit DISQOVER
    #  http://purl.bioontology.org/ontology/ICD10CM/C67 -> http://ns.ontoforce.com/datasets/icd10/C67
    # http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C114841 -> http://ns.ontoforce.com/datasets/nci/C114841
    def adj_dis_id(val):
        new_id = val
        if val.startswith('http://purl.bioontology.org/'):
            var_list = val.split('/')
            new_id = 'http://ns.ontoforce.com/datasets/'+var_list[-2][:-2].lower()+'/'+var_list[-1]
        if val.startswith('http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl'):
            var_list = val.split('#')
            new_id = 'http://ns.ontoforce.com/datasets/nci/'+var_list[-1]
        return new_id

    subset["Disease ID"] = subset.apply(lambda x:adj_dis_id(x["Disease ID"]), axis = 1)

    # Renaming columns to fit the biomarker model terminology and adding relevant columns
    subset.rename(columns={'Protein name':'Name','Protein ID':'Molecular ID','Biomarker usage':'Usage','Experiment':'Assay/Test'}, inplace=True)
    subset['Source'] = 'Urine'
   # subset['Type'] = 'MolecularBM'
    subset['Type'] = 'Molecular Biomarker'
    subset['Molecular type'] = 'Protein'
    subset['Evidence level'] = np.NaN

    # Converting usage to fit the biomarker model and add source id
    subset = adj_usage(subset)
    subset = adj_src(subset, False)

    # Remove biomarkers with no inforamtion about assay, usage or whether it's a singel or a panel
    nrow_before = subset.shape[0]
    subset = subset.dropna(subset = ['Assay/Test', 'Usage','In a panel'])
    nrow_after = subset.shape[0]
    dropped = nrow_before-nrow_after
    dropped_per = round(dropped/nrow_before*100,2)
    print("Dropped {} ({}%) rows with missing data over assay, usage or panel".format(dropped, dropped_per))

    # seperate panels to single components
    panels_df = subset[subset['Molecular ID'].str.contains("\\|", na=False)]
    singles_df = subset[~subset['Molecular ID'].str.contains("\\|", na=False)]
    panels_df.to_csv('D:/ontoforce/sources/panels.csv')
    for index, row in panels_df.iterrows():
        names = row['Name'].split('|')
        prot_ids = row['Molecular ID'].split('|')
        for name, prot_id in zip(names, prot_ids):
            single_bm = row
            single_bm['Name'] = name
            single_bm['Molecular ID'] = prot_id
            single_bm['In a panel'] = 'TRUE'
            singles_df = singles_df.append(single_bm, ignore_index=True)
    
    singles_df['In a panel'] = singles_df['In a panel'].replace({'FALSE':'No', 'TRUE':'Yes',False:'No', True:'Yes'})
    singles_df['Id'] = singles_df.index+1
    # Write to csv file
    new_index = [
        'Id','Name','Usage','Disease','Disease ID','In a panel','Evidence level','Type','Source','Source ID',
        'Assay/Test','Pmid','Molecular type','Molecular ID','Treatment']
    
    print("Writing to "+output_file)
    singles_df.to_csv(output_file, columns = new_index, index = False)
    return singles_df

def extract_oncomx(output_file):
    '''
    Oncomx contains datasets of FDA-approved or cleared nucleic acid-based human biomarker tests for cancer
    Each row represents one gene linked to its respective test. 
    Genes are labeled by relevant identifiers/accessions from UniProtKB, HGNC, and EDRN. 
    Tests are distinguished by manufacturer, FDA submission ID(s), clinical trial ID(s), and PubMed ID(s).
    Writes results to output_file (csv) and returns a DataFrame
    '''
    # Read and join csv's into one dataframe
    print("\nExtracting data from Oncomex...")
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
    
    subset["Molecular ID"] = "http://identifiers.org/hgnc.symbol/" + subset["Name"].str.upper()
    
    subset["Type"] = 'MolecularBM'
    subset["Disease ID"] = "DOID_" + subset["Disease ID"].astype(str)
    
    '''
    # DISQOVER
    subset["Type"] = 'Molecular Biomarker'
    subset["Disease ID"] = "http://purl.obolibrary.org/obo/DOID_" + subset["Disease ID"].astype(str)
    '''
    
    subset = adj_src(subset, False)

    # Adjust multiple values to be seperated by "|"
    subset.loc[subset["Clinical trail ID"] == "-","Clinical trail ID"] = np.NaN
    subset["Clinical trail ID"] = subset.apply(lambda x:adj_mult(x["Clinical trail ID"],"_"), axis = 1)
    subset["Clinical trail ID"] = subset.apply(lambda x:adj_mult(x["Clinical trail ID"],"/"), axis = 1)
    subset["Assay/Test"] = subset.apply(lambda x:adj_mult(x["Assay/Test"],"_ "), axis = 1)
    subset["Usage"] = subset.apply(lambda x:adj_mult(x["Usage"],None), axis = 1)
    subset = adj_usage(subset)
    subset["Pmid"] = subset.apply(lambda x:adj_mult(x["Pmid"],"_"), axis = 1)
    subset["Pmid"] = subset.apply(lambda x:adj_mult(x["Pmid"],None), axis = 1)

    subset['Id'] = subset.reset_index().index+1

    # Write to csv file
    new_index = [
        'Id','Name','Usage','Disease','Disease ID','In a panel','Evidence level','Type','Source','Source ID',
        'Assay/Test','Test manufacturer','Pmid','Molecular type','Molecular ID','Treatment','Description','Clinical trail ID']
    
    print("Writing to "+output_file)
    subset.to_csv(output_file, columns = new_index, index = False)
    return subset

def extract_cbd(output_file):
    """
    CBD: Colorectal Cancer Biomarker Database http://sysbio.suda.edu.cn/CBD/index.html
    Missing information in DB: In a panel, Evidence level, Molecular ID (assinged NaN values)
    Writes results to output_file (csv) and returns a DataFrame
    """
    print("\nExtracting data from Colorectal Cancer Biomarker Database...")
    url = "http://sysbio.suda.edu.cn/CBD/download/data.xlsx"
    cbd = pd.read_excel(url, index_col=None)

    
    # Extract relevant information
    subset = cbd[["Biomarker","Categary","Discription","Location","Source","Experiment","Application","PMID","Statictics","Conclusion"]]
    subset.rename(columns={
        'Biomarker':'Name','Application':'Usage','PMID':'Pmid','Categary':'Molecular type', 'Experiment':'Assay/Test'}, inplace=True)
    
    # Join all columns decscribing the experiment and its results and conclusions into one column
    subset["Description"] = subset.apply(lambda x: ' '.join(x[["Discription","Statictics","Conclusion"]].dropna().astype(str).values), axis=1)
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
    subset['Type'] = 'Molecular Biomarker'
    subset['In a panel'] = np.NaN
    subset['Evidence level'] = np.NaN
    subset['Molecular ID'] = np.NaN

    subset = adj_usage(subset)
    subset["Usage"] = subset.apply(lambda x:adj_mult(x["Usage"],","), axis = 1)

    # Some rows have multiple values for source, which are mostly duplicates, therefore rem_duplicate = True
    subset = adj_src(subset, True)
    # Remove rows with more than once source 
    nrow_before = subset.shape[0]
    subset = subset.drop(subset[subset['Source'].str.contains('_')].index)
    nrow_after = subset.shape[0]
    dropped = nrow_before-nrow_after
    dropped_per = round(dropped/nrow_before*100,2)
    print("Dropped {} ({}%) rows with more than one source".format(dropped, dropped_per))

    #subset["Name"] = subset.apply(lambda x:adj_mult(x["Name"],","), axis = 1)
    subset["Assay/Test"] = subset.apply(lambda x:adj_mult(x["Assay/Test"],","), axis = 1)
    subset['Id'] = subset.reset_index().index+1
    
    print("Writing to "+output_file)
    subset.to_json(output_file,orient='records')

    return subset