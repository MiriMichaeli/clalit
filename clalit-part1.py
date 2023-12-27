# requirements: bssh (bs) tool and bedtools installed and added to PATH
# python 3 (this code is written in env with python 3.11.3)
# Usage: python3 clalit-part1.py <proect_name> <path_to_output_folder>

import pandas as pd
import os
import argparse

# deal with user input:
parser = argparse.ArgumentParser()
parser.add_argument("project_name", help="The proejct name in Illumina database to work on. E.g.: DRAGEN Enrichment v3.10.403/31/2022 8:12:30")
parser.add_argument("output_folder", help="Full path of the output folder where the user wish to save results in.")

args = parser.parse_args()
# get the function variables:
output_folder = args.output_folder
project_name = args.project_name

# connect to bssh-cli:
# os.system("bs auth --api-server https://api.euc1.sh.basespace.illumina.com --force") # Authenticate on EUC1

os.chdir(output_folder) 
# PART 1:
# given the project id from user input, print the related app sessions:
print(f"List app sessions for project {project_name}:")

os.system(f"bs list appsessions --filter-field=Name --filter-term={project_name}")

# download the vc and mapping files:
print(f"Download vc and mapping into {output_folder}...")
os.system(f"bs list datasets --newer-than=400d --terse | xargs -I@ ./bs download dataset -i @ --no-metadata --extension=.mapping_metrics.csv -o {output_folder}")
os.system(f"bs list datasets --newer-than=400d --terse | xargs -I@ ./bs download dataset -i @ --no-metadata --extension=.vc_metrics.csv -o {output_folder}")

# parse the two files:
# the following code will output a summary file (mapping_and_vc_combined.csv) to the output_folder, 
# containing alignment and variant calling metrics results (only the "SUMMARY" lines) for each biosample 
# where each row is a biosample and the columns are the different metrics.

# this function gets a file name (res_file) to parse its content and 
# extension (ext) for parsing the biosample name out of the file name
def parse_file(res_file, ext):
    res_dict = []
    with open(res_file, 'r') as f:
        for line in f:
            if "SUMMARY" in line:
                res_dict.append(line.strip().split('SUMMARY,,')[1].split(',')[0:2])
    f.close()
    res_df = pd.DataFrame(res_dict).set_index(0).T
    res_df.insert(0, 'biosample', os.path.basename(res_file).split(ext)[0])
    return res_df

# combine data:
print("Parsing the mapping and vc files in order to combine the results:")
all_mapping_df = pd.DataFrame()
all_vc_df = pd.DataFrame()
for file in os.listdir(output_folder):
    # check the extensions:
    if file.endswith('.mapping_metrics.csv'):
        all_mapping_df = pd.concat([all_mapping_df,
                                    parse_file(os.path.join(output_folder,file), '.mapping_metrics.csv')], 
                                    ignore_index=True)
    elif file.endswith('.vc_metrics.csv'):
        all_vc_df = pd.concat([all_vc_df,
                               parse_file(os.path.join(output_folder,file), '.vc_metrics.csv')], 
                               ignore_index=True)

combined_data = all_vc_df.merge(all_mapping_df, on='biosample')
combined_data.to_csv(os.path.join(output_folder,'mapping_and_vc_combined.csv'), index=False)
print(f"Done. combined file was saved into {output_folder} as 'mapping_and_vc_combined.csv'")




