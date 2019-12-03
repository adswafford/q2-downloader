# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2

from q2_types.per_sample_sequences import \
        SingleLanePerSampleSingleEndFastqDirFmt


def fetch(accession: str, repository: str, only_metagenomics: bool = True,
          only_illumina: bool = True) -> SingleLanePerSampleSingleEndFastqDirFmt:

    # translate the code from the old script
    pass
