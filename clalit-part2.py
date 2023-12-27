# requirements: bssh (bs) tool and bedtools installed and added to PATH
# python 3 (this code is written in env with python 3.11.3)
# save the genes_and_clinvar.sh script to the output_folder directory
# Usage: python3 clalit-part2.py <path_to_output_folder_with_genes_and_clinvar.sh_script_saved_there>

import os
import argparse

# deal with user input:
parser = argparse.ArgumentParser()
parser.add_argument("output_folder", help="Full path of the output folder where the user wish to save results in.")

args = parser.parse_args()
# get the function variables:
output_folder = args.output_folder

os.chdir(output_folder) 
# download the bam files for next step:
print("Download bam...")
# os.system(f"bs list datasets --newer-than=400d --terse | xargs -I@ bs download dataset -i @ --no-metadata --extension=.bam -o {output_folder}")
# os.system(f"bs list datasets --newer-than=400d --terse | xargs -I@ bs download dataset -i @ --no-metadata --extension=.bai -o {output_folder}")


# the following script will generate a bed file with all genomic locations of genes (build 38), 
# and will download and prepare the clinvar file with pathogenic and likely pathogenic variants.
# output will be saved to the output folder for further usage.
os.system("./genes_and_clinvar.sh")

# intersect the variants vs the genes:
os.system("""bedtools intersect -a pathogenic_and_likely_with_chr.vcf -b genes.bed > -b intersect_var_with_genes.vcf """)

# for each bam file in output_folder, remove unwanted chr-like entries from bam, 
# then intersect with the clinvar and genes, then calculate coverage.
# filter those with < 10x
print("The following step takes time! It will calculate coverage in the input bam files for clinvar pathogenic \
      and likely pathogenic variants found in the coding regions.")
for file in os.listdir(output_folder):
    # check the extensions:
    if file.endswith('.bam'):
        # filter chromosomes only:
        os.system(f"""samtools view -b {os.path.join(output_folder,file)}"""+" chr{1..22} > "+f"""{os.path.basename(file)}_filtered.bam""")
        # intersect the variants in the genes with the input bam:
        os.system(f"""bedtools coverage -a {os.path.basename(file)}_filtered.bam -b intersect_var_with_genes.vcf \
            > {os.path.basename(file)}_coverage.txt """)

# TODO filter those with <10 coverage, add the transcript name.
