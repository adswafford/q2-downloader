# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


import q2_downloader
from ._downloader import fetch

from qiime2.plugin import Plugin, Str, Bool, Choices

from q2_types.sample_data import SampleData
from q2_types.per_sample_sequences import (SequencesWithQuality,
                                           PairedEndSequencesWithQuality,
                                           JoinedSequencesWithQuality)

plugin = Plugin(
    name='downloader',
    version=q2_downloader.__version__,
    website='http://github.com/biocore/q2-downloader',
    package='q2_downloader',
    description=('This QIIME 2 plugin downloads data from EBI & SRA'),
    short_description='Plugin to download sequence data and sample information'
                      ' from EBI and SRA'
)

plugin.methods.register_function(
    function=fetch,
    inputs={},
    parameters={
        'accession': Str,
        'repository': Str % Choices(['SRA', 'ENA']),
        'only_metagenomics': Bool,
        'only_illumina': Bool
    },
    input_descriptions={},
    outputs=[('sequences', SampleData[SequencesWithQuality |
                                      PairedEndSequencesWithQuality |
                                      JoinedSequencesWithQuality])],
    parameter_descriptions={
        'accession': 'Accession number corresponding to the study.',
        'repository': 'The repository name where to download data from.',
        'only_metagenomics': 'Ignore preparations that are not metagenomic',
        'only_illumina': ('Ignore data that is not associated with an Illumina'
                          ' instrument')
    },
    output_descriptions={
        'sequences': 'Sequence data associated with the study accesion.'
    },
    name='Fetch the sequence data and sample information associated with an '
         'accession number',
    description='Downloads sequence data and sample information for a study'
)
