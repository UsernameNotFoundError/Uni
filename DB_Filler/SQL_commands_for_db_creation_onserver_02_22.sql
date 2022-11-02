# Do not forget use database !!!! 

CREATE TABLE Species (
    Species_ID int AUTO_INCREMENT,
	NCBI_ID int NOT NULL UNIQUE,
    Species_Name varchar(100) NOT NULL UNIQUE,
	Species_code varchar(20),
    Alias varchar(40),
	Category varchar(40),
	Commun_name varchar(40),
	taxonomy varchar(1000) UNIQUE,
	Image_path varchar(255),
    PRIMARY KEY(Species_ID)
);

CREATE TABLE Assembly (
	Species int,
    Assembly_ID int NOT NULL,
    Assembly_Version int NOT NULL,
	Assembly_Source varchar(40),
    Addditional_Notes varchar(255),
	Dir_Location varchar(255),
	File_Location varchar(255) NOT NULL,
	CONSTRAINT Assembly_Key PRIMARY KEY (Assembly_ID, Assembly_Version),
    FOREIGN KEY (Species) REFERENCES Species(Species_ID)
);

CREATE TABLE GenomicAnnotation (
	Assembly_ID int NOT NULL,
	Assembly_Version int NOT NULL,
	Annotation_ID int AUTO_INCREMENT,
	Annotation_Version varchar(255),
	File_Location varchar(255) NOT NULL,
    PRIMARY KEY (Annotation_ID),
    CONSTRAINT FK_Assembly_GenomicFeatures FOREIGN KEY (Assembly_ID, Assembly_Version) REFERENCES Assembly(Assembly_ID, Assembly_Version)
);

CREATE TABLE NonCodingRNA (
	Annotation_ID int NOT NULL,
	RNA_ID int AUTO_INCREMENT,
	RNA_Version varchar(55),
	File_Location varchar(255) NOT NULL,
    PRIMARY KEY (RNA_ID),
    FOREIGN KEY (Annotation_ID) REFERENCES GenomicAnnotation(Annotation_ID)
);

CREATE TABLE ProteinSet  (
	Annotation_ID int NOT NULL,
	Protein_ID int AUTO_INCREMENT,
	file_type varchar(50),
	Date_of_the_Data date,
	File_Location varchar(255) NOT NULL,
    PRIMARY KEY (Protein_ID),
    FOREIGN KEY (Annotation_ID) REFERENCES GenomicAnnotation(Annotation_ID)
);

CREATE TABLE BlastDB (
	Protein_ID int,
	Blast_ID int AUTO_INCREMENT,
	Blast_Version varchar(255),
	Dir_Location varchar(255) NOT NULL,
	PRIMARY KEY (Blast_ID),
    FOREIGN KEY (Protein_ID) REFERENCES ProteinSet(Protein_ID)
);

CREATE TABLE FeatureAnnotation (
	Protein_ID int ,
	FeatureAnnotation_ID int AUTO_INCREMENT,
	FeatureAnnotation_Version varchar(255),
    Tool varchar(255),
	Additional_Info varchar(255),
	File_Location varchar(255) NOT NULL,
    PRIMARY KEY (FeatureAnnotation_ID),
    FOREIGN KEY (Protein_ID) REFERENCES ProteinSet(Protein_ID)
);

CREATE TABLE DiamondDB (
	Protein_ID int NOT NULL,
	DiamondDB_ID int NOT NULL,
	DiamondDB_Version varchar(255),
	File_Location varchar(255) NOT NULL,
    PRIMARY KEY (DiamondDB_ID),
    FOREIGN KEY (Protein_ID) REFERENCES ProteinSet(Protein_ID)
);
