# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2

import requests
import pandas

from q2_types.per_sample_sequences import \
        SingleLanePerSampleSingleEndFastqDirFmt


def fetch(accession: str, repository: str, only_metagenomics: bool = True,
          only_illumina: bool = True) -> SingleLanePerSampleSingleEndFastqDirFmt:

    # translate the code from the old script
    study_details = ena_study_details(accession, repository,
                                      only_metagenomics, only_illumina)
    pass


def ena_study_details(accession: str, repository: str,
                      only_metagenomics: bool, only_illumina: bool):
    """
        Returns the details of the EBI study
        The details include all the sample ids, run ids, fastq-file ftps etc.

    Parameters
    ----------
    accession : str
        The accession ID of the study

    repository: str
        The name of the public repository


    Returns
    -------

    """
    # Grab the details related to the given accession
    host = 'http://www.ebi.ac.uk/ena/data/warehouse/filereport?accession='
    read_type = '&result=read_run&'
    url = ''.join([host, accession, read_type])
    response = requests.get(url)

    # Check for valid accessions
    if not response:
        raise Exception(accession + ' is an invalid ENA study ID')

    details = response.content.split(b'\n')
    return details_iterator(accession, details, repository,
                            only_metagenomics, only_illumina)


def details_iterator(accession: str, details: list, repository: str,
                     only_metagenomics: bool, only_illumina: bool):
    # get header and indices
    if repository == 'ENA':
        header = details[0].split(b'\t')
        lib_source_idx = header.index('library_source')
        inst_platform_idx = header.index('instrument_platform')
        sample_id_idx = header.index('secondary_sample_accession')
    else:
        header = details[0].split(',')
        lib_source_idx = header.index('LibrarySource')
        inst_platform_idx = header.index('Platform')
        sample_id_idx = header.index('Sample')

    # loop through the content
    final_details = []
    for line in details[1:]:
        if len(line) == 0:
            continue
        if repository == 'ENA':
            line = line.split('\t')
        else:
            line = line.split(',')
        # checking parameters
        if only_metagenomics or only_illumina:
            if only_metagenomics and \
               line[lib_source_idx].lower() != 'metagenomic':
                print(line[lib_source_idx])
                print('Library source is not Metagenomic for ' +
                      line[sample_id_idx] + '. Omitting ' +
                      line[sample_id_idx])
                continue
            if only_illumina and line[inst_platform_idx].lower() != 'illumina':
                print(line[inst_platform_idx])
                print('Instrument platform is not Illumina for ' +
                      line[sample_id_idx] + '. Omitting ' +
                      line[sample_id_idx])
                continue
        # check if any field is empty
        for i in range(len(line)):
            if len(line[i]) == 0:
                line[i] = 'unspecified'
        final_details.append(line)

    if len(final_details) == 0:
        if only_metagenomics and only_illumina:
            raise Exception(accession + ' has no samples or runs that ' +
                            ' is from Illumina and metagenomic')
        elif only_metagenomics:
            raise Exception(accession + ' has no samples or runs that ' +
                            ' is metagenomic')
        elif only_illumina:
            raise Exception(accession + ' has no samples or runs that ' +
                            ' is from Illumina')
        else:
            raise Exception(accession + ' has no samples')
    return pandas.DataFrame(final_details, columns=header)
