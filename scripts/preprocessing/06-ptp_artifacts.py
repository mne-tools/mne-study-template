"""
========================================================
06. Remove epochs based on peak-to-peak (PTP) amplitudes
========================================================

Blinks and ECG artifacts are automatically detected and the corresponding SSP
projections components are removed from the data.

"""

import itertools
import logging

import mne
from mne.parallel import parallel_func

from mne_bids import BIDSPath

import config
from config import gen_log_message, on_error, failsafe_run

logger = logging.getLogger('mne-bids-pipeline')


def drop_ptp(subject, session=None):
    bids_path = BIDSPath(subject=subject,
                         session=session,
                         task=config.get_task(),
                         acquisition=config.acq,
                         run=None,
                         recording=config.rec,
                         space=config.space,
                         suffix='epo',
                         extension='.fif',
                         datatype=config.get_datatype(),
                         root=config.deriv_root,
                         check=False)

    infile_processing = None
    if config.use_ica:
        infile_processing = 'ica'
    elif config.use_ssp:
        infile_processing = 'ssp'

    fname_in = bids_path.copy().update(processing=infile_processing)
    fname_out = bids_path.copy().update(processing='clean')

    msg = f'Input: {fname_in}, Output: {fname_out}'
    logger.info(gen_log_message(message=msg, step=6, subject=subject,
                                session=session))

    reject = config.get_reject()
    epochs = mne.read_epochs(fname_in, preload=True)
    epochs.drop_bad(reject=reject)

    msg = 'Saving cleaned eopchs …'
    logger.info(gen_log_message(message=msg, step=6, subject=subject,
                                session=session))
    logger.info(gen_log_message(step=6, message=msg))

    epochs.save(fname_out, overwrite=True)


@failsafe_run(on_error=on_error)
def main():
    """Run epochs."""
    msg = 'Running Step 6: Reject epochs based on peak-to-peak amplitude'
    logger.info(gen_log_message(step=6, message=msg))

    parallel, run_func, _ = parallel_func(drop_ptp,
                                          n_jobs=config.N_JOBS)
    parallel(run_func(subject, session) for subject, session in
             itertools.product(config.get_subjects(), config.get_sessions()))

    msg = 'Completed Step 6: Reject epochs based on peak-to-peak amplitude'
    logger.info(gen_log_message(step=6, message=msg))


if __name__ == '__main__':
    main()