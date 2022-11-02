#!/bin/bash
#SBATCH --partition=all,special,inteli7
#SBATCH --account=praktikant
#SBATCH --cpus-per-task=10
#SBATCH --mem-per-cpu=3000mb
#SBATCH --job-name="addTaxa_try"
#SBATCH --output=addTaxa_%A_%a.o.out
#SBATCH --error=addTaxa_%A_%a.e.out
#SBATCH --array=3647-3648%2

echo This is task $SLURM_ARRAY_TASK_ID

SEED=$(awk "FNR==$SLURM_ARRAY_TASK_ID" /share/project/amine/Uni_13_07_2022/src/DataManagementSystem/updateapp/myupdatefiles/fdog_seed.csv)
NAME=`echo $SEED |cut -d ',' -f 1`
TAX=`echo $SEED |cut -d ',' -f 2`
END=`echo $SEED |cut -d ',' -f 3`

fdog.addTaxon -f /share/gluster/GeneSets/NCBI-Genomes/${NAME:4:3}/${NAME:7:3}/${NAME:10:3}/GCF_$NAME.$END/raw_dir/protein.faa -i $TAX -o /share/gluster/GeneSets/NCBI-Genomes/${NAME:4:3}/${NAME:7:3}/${NAME:10:3}/GCF_$NAME.$END/fdog -c --cpus 10 --replace -v $END
