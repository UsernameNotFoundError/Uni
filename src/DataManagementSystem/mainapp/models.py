# Added "related_name"  in Analysis, assemblystatistic, bookmark, genomicannotation
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfileInfo(models.Model):
    # Create relationship (don't inherit from User!)
    user = models.OneToOneField(
                        User,
                        on_delete=models.CASCADE,
                        primary_key=True
                        )

    # Add any additional attributes you want
    portfolio_site = models.URLField(blank=True)
    # pip install pillow to use this!
    profile_pic = models.ImageField(upload_to='profile_pics',blank=True)
    #date_of_the_experiment = models.DateField(default=timezone.now)
    #mysql_results = models.CharField(max_length=2000, blank=True)
    #querry_used = models.CharField(max_length=255, blank=True)

    def __str__(self):
        # Built-in attribute of django.contrib.auth.models.User !
        return self.user.username


class Searchregister(models.Model):
    user = models.ForeignKey(User, models.CASCADE, db_column='User_id', blank=True, null=True)  # Field name made lowercase.
    search_id = models.AutoField(db_column='Search_ID', primary_key=True)  # Field name made lowercase.
    date_of_the_experiment = models.DateField(blank=True, null=True, default=timezone.now)
    querry_used = models.CharField(max_length=1000)
    class Meta:
        managed = False
        db_table = 'searchregister'


    def __str__(self):
        return str(self.search_id)

class Searchresults(models.Model):
    file_type = models.CharField(db_column='file_type', max_length=40)
    id = models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
    search_id = models.ForeignKey(Searchregister, models.CASCADE, db_column='search_id', blank=True, null=True)
    # assembly.Assembly_ID, assembly.assembly_version, species.ncbi_id, species.species_name, species.alias,  assembly.Assembly_Source, proteinset.File_Location
    assembly_id = models.IntegerField(db_column='Assembly_ID')  # Field name made lowercase.
    assembly_version = models.IntegerField(db_column='Assembly_Version')
    ncbi_id = models.IntegerField(db_column='NCBI_ID')
    species_name = models.CharField(db_column='Species_Name', max_length=100)
    alias = models.CharField(db_column='Alias', max_length=40, blank=True, null=True)
    assembly_source = models.CharField(db_column='Assembly_Source', max_length=40, blank=True, null=True)
    file_location = models.CharField(db_column='File_Location', max_length=255)

    class Meta:
        managed = False
        db_table = 'searchresults'

    def __what__(self):
        return 'self.user.username'



# mySQL Models
class Species(models.Model):
    species_id = models.AutoField(db_column='Species_ID', primary_key=True)  # Field name made lowercase.
    ncbi_id = models.IntegerField(db_column='NCBI_ID')  # Field name made lowercase.
    species_name = models.CharField(db_column='Species_Name', max_length=100)  # Field name made lowercase.
    species_code = models.CharField(db_column='Species_code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    alias = models.CharField(db_column='Alias', max_length=40, blank=True, null=True)  # Field name made lowercase.
    category = models.CharField(db_column='Category', max_length=40, blank=True, null=True)  # Field name made lowercase.
    commun_name = models.CharField(db_column='Commun_name', max_length=40, blank=True, null=True)  # Field name made lowercase.
    taxonomy = models.CharField(max_length=1000, blank=True, null=True)
    image_path = models.CharField(db_column='Image_path', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Species'


class Assembly(models.Model):
    species = models.ForeignKey('Species', db_column='Species', blank=True, null=True, on_delete=models.DO_NOTHING)  # Field name made lowercase.
    assembly_id = models.IntegerField(db_column='Assembly_ID', primary_key=True)  # Field name made lowercase.
    assembly_version = models.IntegerField(db_column='Assembly_Version')  # Field name made lowercase.
    assembly_source = models.CharField(db_column='Assembly_Source', max_length=40, blank=True, null=True)  # Field name made lowercase.
    addditional_notes = models.CharField(db_column='Addditional_Notes', max_length=255, blank=True, null=True)  # Field name made lowercase.
    dir_location = models.CharField(db_column='Dir_Location', max_length=255, blank=True, null=True)  # Field name made lowercase.
    file_location = models.CharField(db_column='File_Location', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Assembly'
        unique_together = (('assembly_id', 'assembly_version'),)


class Genomicannotation(models.Model):
    assembly = models.ForeignKey(Assembly, db_column='Assembly_ID', on_delete=models.DO_NOTHING, related_name='assembly_id_genomicannotation')  # Field name made lowercase.
    assembly_version = models.ForeignKey(Assembly, db_column='Assembly_Version', on_delete=models.DO_NOTHING, related_name='assembly_version_genomicannotation')  # Field name made lowercase.
    annotation_id = models.AutoField(db_column='Annotation_ID', primary_key=True)  # Field name made lowercase.
    annotation_version = models.CharField(db_column='Annotation_Version', max_length=255, blank=True, null=True)  # Field name made lowercase.
    file_location = models.CharField(db_column='File_Location', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GenomicAnnotation'


class Noncodingrna(models.Model):
    annotation = models.ForeignKey(Genomicannotation, db_column='Annotation_ID', on_delete=models.DO_NOTHING)  # Field name made lowercase.
    rna_id = models.AutoField(db_column='RNA_ID', primary_key=True)  # Field name made lowercase.
    rna_version = models.CharField(db_column='RNA_Version', max_length=55, blank=True, null=True)  # Field name made lowercase.
    file_location = models.CharField(db_column='File_Location', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'NonCodingRNA'


class Proteinset(models.Model):
    annotation = models.ForeignKey(Genomicannotation, db_column='Annotation_ID', on_delete=models.DO_NOTHING)  # Field name made lowercase.
    protein_id = models.AutoField(db_column='Protein_ID', primary_key=True)  # Field name made lowercase.
    file_type = models.CharField(max_length=50, blank=True, null=True)
    date_of_the_data = models.DateField(db_column='Date_of_the_Data', blank=True, null=True)  # Field name made lowercase.
    file_location = models.CharField(db_column='File_Location', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ProteinSet'


class Blastdb(models.Model):
    protein = models.ForeignKey('Proteinset', db_column='Protein_ID', blank=True, null=True, on_delete=models.DO_NOTHING)  # Field name made lowercase.
    blast_id = models.AutoField(db_column='Blast_ID', primary_key=True)  # Field name made lowercase.
    blast_version = models.CharField(db_column='Blast_Version', max_length=255, blank=True, null=True)  # Field name made lowercase.
    dir_location = models.CharField(db_column='Dir_Location', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BlastDB'


class Featureannotation(models.Model):
    protein = models.ForeignKey('Proteinset', db_column='Protein_ID', blank=True, null=True, on_delete=models.DO_NOTHING)  # Field name made lowercase.
    featureannotation_id = models.AutoField(db_column='FeatureAnnotation_ID', primary_key=True)  # Field name made lowercase.
    featureannotation_version = models.CharField(db_column='FeatureAnnotation_Version', max_length=255, blank=True, null=True)  # Field name made lowercase.
    tool = models.CharField(db_column='Tool', max_length=255, blank=True, null=True)  # Field name made lowercase.
    additional_info = models.CharField(db_column='Additional_Info', max_length=255, blank=True, null=True)  # Field name made lowercase.
    file_location = models.CharField(db_column='File_Location', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'FeatureAnnotation'


class Diamonddb(models.Model):
    protein = models.ForeignKey('Proteinset', db_column='Protein_ID', on_delete=models.DO_NOTHING)  # Field name made lowercase.
    diamonddb_id = models.IntegerField(db_column='DiamondDB_ID', primary_key=True)  # Field name made lowercase.
    diamonddb_version = models.CharField(db_column='DiamondDB_Version', max_length=255, blank=True, null=True)  # Field name made lowercase.
    file_location = models.CharField(db_column='File_Location', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'DiamondDB'

'''
class Users(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    username = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=50)
    role = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'users'
'''
