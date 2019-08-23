"""Download test data and run a test suite."""
import os
import os.path as op
import argparse
import importlib


def fetch(dataset):
    """Fetch the data."""
    from download_test_data import main
    main(dataset)


def sensor():
    """Run sensor pipeline."""
    mod = importlib.import_module('../01-import_and_filter.py')
    mod.main()
    mod = importlib.import_module('../02-apply_maxwell_filter.py')
    mod.main()
    mod = importlib.import_module('../03-extract_events.py')
    mod.main()
    mod = importlib.import_module('../04-make_epochs.py')
    mod.main()
    mod = importlib.import_module('../05a-run_ica.py')
    mod.main()
    mod = importlib.import_module('../05b-run_ssp.py')
    mod.main()
    mod = importlib.import_module('../06a-apply_ica.py')
    mod.main()
    mod = importlib.import_module('../06b-apply_ssp.py')
    mod.main()
    mod = importlib.import_module('../07-make_evoked.py')
    mod.main()
    mod = importlib.import_module('../08-group_average_sensors.py')
    mod.main()
    mod = importlib.import_module('../09-sliding_estimator.py')
    mod.main()
    mod = importlib.import_module('../10-time_frequency.py')
    mod.main()


def source():
    """Run source pipeline."""
    mod = importlib.import_module('../11-make_forward.py')
    mod.main()
    mod = importlib.import_module('../12-make_cov.py')
    mod.main()
    mod = importlib.import_module('../13-make_inverse.py')
    mod.main()
    mod = importlib.import_module('../14-group_average_source.py')
    mod.main()


def report():
    """Run report pipeline."""
    mod = importlib.import_module('../99-make_reports')
    mod.main()


# Where to download the data to
DATA_DIR = op.join(op.expanduser('~'), 'mne_data')

TEST_SUITE = {
    'ds000246': ('config_ds000246', sensor),
    'ds000248': ('config_ds000248', sensor),
    'ds001810': ('config_ds001810', sensor),
    'eeg_matchingpennies': ('config_matchingpennies', sensor),
    'somato': ('config_somato', sensor, source),
}


def run_tests(test_suite):
    """Run a suite of tests.

    Parameters
    ----------
    test_suite : dict
        Each key in the dict is a dataset to be tested. The associated value is
        a tuple with the first element the dataset config, and all remaining
        elements function handles to be called.

    Notes
    -----
    For every entry in the dict, the function `fetch` is called.

    """
    for dataset, test_tuple in test_suite.items():
        # export the environment variables
        os.environ['DATASET'] = dataset
        os.environ['BIDS_ROOT'] = op.join(DATA_DIR, dataset)
        os.environ['MNE_BIDS_STUDY_CONFIG'] = test_tuple[0]

        # Fetch the data
        fetch(dataset)

        # run GNU Make
        for pipeline in test_tuple[1::]:
            pipeline()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('dataset', help=('dataset to test. A key in the '
                                         'TEST_SUITE dictionary. or ALL, '
                                         'to test all datasets.'))
    args = parser.parse_args()

    if args.dataset == 'ALL':
        test_suite = TEST_SUITE
    else:
        test_suite = {args.dataset: TEST_SUITE.get(args.dataset, 'n/a')}

    if 'n/a' in test_suite.values():
        parser.print_help()
        print('\n\n')
        raise KeyError('"{}" is not a valid dataset key in the TEST_SUITE '
                       'dictionary in the run_tests.py module.'
                       .format(args.dataset))
    else:
        # Run the tests
        print('Running the following tests:\n')
        for dataset, test_tuple in test_suite.items():
            print(dataset, test_tuple)
        run_tests(test_suite)