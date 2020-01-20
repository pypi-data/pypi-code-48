import boto3, os, logging
from urllib.parse import urlparse

ACCESS_KEY = 'AKIAQJW2IM3APXAF67UN'
SECRET_KEY = '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'

client = boto3.client('s3', aws_access_key_id=ACCESS_KEY , aws_secret_access_key=SECRET_KEY)


def list_files(bucket_name, path_prefix, dirs_only = False, files_only = False):
    result = client.list_objects(Bucket=bucket_name, Prefix=path_prefix, Delimiter='/')
    result_list = []
    if not files_only:
        for o in result.get('CommonPrefixes'):
            dir=o.get('Prefix')
            if dir[:len(path_prefix)] == path_prefix:
                dir = dir[len(path_prefix):]
            result_list.append(dir)
    if not dirs_only:
        for o in result.get('Contents'):
            file = o.get('Key')
            if file[:len(path_prefix)] == path_prefix:
                file = file[len(path_prefix):]
            if file:
                result_list.append(file)
    return result_list



def download_file(s3_url, save_path):
    '''
    Download and save locally S3 file
    :param s3_url: s3:// url format
    :param save_path: local path to save downloaded file
    :return:
    '''
    parsed_url = urlparse(s3_url)
    bucket_name = parsed_url.netloc
    path = parsed_url.path.lstrip('/')
    file_name = os.path.basename(path)
    if os.path.exists(save_path):
        logging.warning("S3 file already exists: {} -- {}".format(s3_url,save_path))
        return

    logging.info("Downloading bucket_name: '{}'. Path: '{}'".format(bucket_name, path))
    client.download_file(bucket_name,path,save_path)


if __name__ == '__main__':
    import syncvtools.utils.file_tools as ft
    test_list = ft.file_to_list(file_src='/Users/apatsekin/projects/datasets/synapse/mega/v1/1015validation_dates_hs.txt')
    training_list = []
    for threat_type in ['sharps','handguns']:
        files = list_files(bucket_name='synapse-cloudfactory', path_prefix='{}/'.format(threat_type), dirs_only=True)
        #cut last slash
        files = list(map(lambda x: x[:-1], files))
        for file in files:
            training_dir = "{}/{}".format(threat_type, file)
            if training_dir in test_list:
                print("skipped test: {}".format(training_dir))
                continue
            if threat_type == 'handguns' and  not training_dir.endswith('_handguns'):
                print("skipping handgun parts: {}".format(training_dir))
                continue
            training_list.append(training_dir)
    for it in training_list:
        print(it)



