import os
import numpy as np
import shutil
import subprocess
import time
import random
from pathlib import Path


def execute_astminer(input_data_folder, code2vec_folder, dataset_name):
    cli_path = code2vec_folder + '/cli.jar'

    source = input_data_folder
    destination = code2vec_folder + '/' + dataset_name + '/astminer_output'

    print('# Start astminer cli.jar execution...')
    start_time = time.time()
    subprocess.call(['java', '-jar', cli_path, 'code2vec', '--lang', 'py', '--project', source, '--output', destination])
    print('# End astminer cli.jar execution - Time: {}'.format(time.time() - start_time))


def merging_path_contexts(code2vec_folder, dataset_name, flag_TF=False):
    input_path = code2vec_folder + '/' + dataset_name + '/astminer_output'

    list_of_files = [name for name in os.listdir(input_path) if name.startswith('path_contexts')]
    num_files = len(list_of_files)

    print('# Start merging path_contexts - tot: {}'.format(num_files))
    start_time = time.time()

    output_file_path = code2vec_folder + '/' + dataset_name + '/' + dataset_name + '_all.raw.txt'

    with open(output_file_path, 'w') as outfile:
        for file_name in list_of_files:
            with open(input_path + '/' + file_name) as infile:
                for line in infile:
                    outfile.write(line)

    # Only with TF
    # Generate a txt file with True or False, used together with vectorised representation my c2v models
    if flag_TF:
        TF_file_path = '../../my_code2vec/models_train_stdout/all_files_TF_for_model_y.csv'
        with open(TF_file_path, 'w') as outfile:
            for file_name in list_of_files:
                with open(input_path + '/' + file_name) as infile:
                    for line in infile:
                        if line.split(' ')[0] == 'passed':
                            outfile.write('1\n')
                        else:
                            outfile.write('0\n')

    print('# End merging path_contexts - Time: {}'.format(time.time() - start_time))

    return output_file_path


def split_path_contexts(code2vec_folder, dataset_name, val_ratio=0.1, test_ratio=0.1):
    input_file_path = code2vec_folder + '/' + dataset_name + '/' + dataset_name + '_all.raw.txt'
    output_file_dir = code2vec_folder + '/' + dataset_name

    with open(input_file_path) as f:
        all_path_contexts = f.read().splitlines()

        np.random.shuffle(all_path_contexts)
        train_path_contexts, val_path_contexts, test_path_contexts = np.split(np.array(all_path_contexts),
                                                                              [int(len(all_path_contexts) * (1 - val_ratio - test_ratio)),
                                                                               int(len(all_path_contexts) * (1 - test_ratio))])

        print('Total files: ', len(all_path_contexts))
        print('Training: ', len(train_path_contexts))
        print('Validation: ', len(val_path_contexts))
        print('Testing: ', len(test_path_contexts))

        with open(output_file_dir + '/' + dataset_name + '.training.raw.txt', 'w') as f:
            for line in train_path_contexts:
                f.write('%s\n' % line)

        with open(output_file_dir + '/' + dataset_name + '.validation.raw.txt', 'w') as f:
            for line in val_path_contexts:
                f.write('%s\n' % line)

        with open(output_file_dir + '/' + dataset_name + '.test.raw.txt', 'w') as f:
            for line in test_path_contexts:
                f.write('%s\n' % line)


if __name__ == '__main__':
    input_data_folder = '../../files/all_files_TF'
    code2vec_folder = '../../code2vec_input_data'
    dataset_name = 'all_files_TF'

    # execute_astminer(input_data_folder, code2vec_folder, dataset_name)

    astminer_path_contexts = merging_path_contexts(code2vec_folder, dataset_name, flag_TF=True)

    # split_path_contexts(code2vec_folder, dataset_name)

