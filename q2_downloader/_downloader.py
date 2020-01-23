# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2

import pandas
import requests
from lxml import etree
from xmltodict import parse

from q2_types.per_sample_sequences import \
        SingleLanePerSampleSingleEndFastqDirFmt


def fetch(accession: str, repository: str, only_metagenomics: bool = True,
          only_illumina: bool = True) -> SingleLanePerSampleSingleEndFastqDirFmt:

    # translate the code from the old script

    #---- ENA ---#
    if repository == 'ENA':
        related_accessions = get_related_accession_ENA(accession)
        if len(related_accessions) == 0:
            raise Exception(accession + ' is not a valid ID')
        for study_id in related_accessions:
            study_details = fetch_study_details(study_id, repository,
                                                only_metagenomics,
                                                only_illumina)
            fetch_study_info(study_id)

    pass

def get_related_accession_ENA(accession: str):
    response_content, is_valid = check_info_xml_ENA(accession)
    if not is_valid:
        return []
    content_children = etree.fromstring(response_content).getchildren()
    is_study = content_children[0]
    if is_study.tag == 'STUDY':
        return [accession]
    elif is_study.tag == 'PROJECT':
        doc = parse(response_content)
        if 'RELATED_PROJECTS' not in doc['ROOT']['PROJECT']:
            return [doc['ROOT']['PROJECT']['IDENTIFIERS']['SECONDARY_ID']]
        else:
            project_list = doc['ROOT']['PROJECT']['RELATED_PROJECTS']\
                            ['RELATED_PROJECT']
            study_ids = []
            for relative in project_list:
                for key in relative.keys():
                    if key == 'CHILD_PROJECT':
                        study_ids += get_related_accession_ENA(relative[key]['@accession'])
            return study_ids

def check_info_xml_ENA(accession: str):
    """
        Helper function to check if the page of the information of the study
        is supported in ENA.

    Parameters
    ----------
    accession : str
        The accession ID of the study

    """
    host = 'http://www.ebi.ac.uk/ena/data/view/'
    read_type = '&display=xml'
    url = ''.join([host, accession, read_type])

    response = requests.get(url)
    response_content = response.content
    content_children = etree.fromstring(response_content).getchildren()
    if len(content_children) == 0:
        print(accession + " is not a valid ENA study ID")
        return response_content, False
    return response_content, True

def fetch_study_details(accession: str, repository: str,
                        only_metagenomics: bool, only_illumina: bool):
    """
        Returns the details of the study
        The details include all the sample ids, run ids, fastq-file ftps etc.

    Parameters
    ----------
    accession : str
        The accession ID of the study

    repository: str
        The name of the public repository

    only_metagenomics: bool
        Specify only fetching metagenomics studies

    only_illumina: bool
        Specify only fetching illumina studies

    Returns
    -------
    study details: pandas.DataFrame
        The details of the study

    """
    if repository == 'ENA':
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
    elif repository == 'SRA':
        pass
    pass


def details_iterator(accession: str, details: list, repository: str,
                     only_metagenomics: bool, only_illumina: bool):
    """
        Helper function to fetch the details of the study

    Parameters
    ----------
    accession : str
        The accession ID of the study

    repository: str
        The name of the public repository

    only_metagenomics: bool
        Specify only fetching metagenomics studies

    only_illumina: bool
        Specify only fetching illumina studies

    Returns
    -------
    study details: pandas.DataFrame
        The details of the study

    """
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


def fetch_study_info(accession: str):
    """
        Fetch the information of the study.
        The information includes title, abstract and etc.

    Parameters
    ----------
    accession : str
        The accession ID of the study

    """
    response_content, is_valid = check_info_xml(accession)
    if not is_valid:
        return

    content_children = etree.fromstring(response_content).getchildren()
    is_study = content_children[0]
    if is_study.tag != 'STUDY':
        secondary_id = is_study.find('IDENTIFIERS').find('SECONDARY_ID')
        if secondary_id is None:
            raise Exception(accession + " is not a valid ENA study ID")
        else:
            accession = secondary_id.text
            response_content, is_valid = check_info_xml(accession)
            if not is_valid:
                return

    doc = parse(response_content)
    study_title = doc['ROOT']['STUDY']['DESCRIPTOR']['STUDY_TITLE']
    alias = doc['ROOT']['STUDY']['@alias']
    study_abstract = doc['ROOT']['STUDY']['DESCRIPTOR']['STUDY_ABSTRACT'] \
        if 'STUDY_ABSTRACT' in doc['ROOT']['STUDY']['DESCRIPTOR'] else 'None'
    description = doc['ROOT']['STUDY']['DESCRIPTOR']['STUDY_DESCRIPTION'] \
        if 'STUDY_DESCRIPTION' in doc['ROOT']['STUDY']['DESCRIPTOR'] \
        else 'None'
    # Creating default values for PI and env
    PI = 'ENA import'
    env = 'miscellaneous natural or artificial environment'

    file = open(accession + '_study_info.txt', 'w')
    file.write('STUDY_TITLE' + '\t' + 'ALIAS' + '\t' +
               'STUDY_ABSTRACT' + '\t' +
               'STUDY_DESCRIPTION' + '\t' +
               'PRINCIPAL_INVESTIGATOR' + '\t' +
               'ENVIRONMENTAL_PACKAGES' + '\n')
    file.write(study_title + "\t" + alias + "\t" + study_abstract + "\t"
               + description + "\t" + PI + "\t" + env + "\n")
    file.close()



