import os
from urllib.parse import urlparse
import click
import requests


def download_m3u8(path):
    res = requests.get(path, verify=False)
    res.raise_for_status()
    path = urlparse(path).path
    out = path[path.rindex('/') + 1:]
    with open(out, 'wb') as f:
        for chunk in res.iter_content(100000):
            f.write(chunk)
    return out


def extract_ts(m3u8_path):
    if m3u8_path.startswith('http://') or m3u8_path.startswith('https://'):
        m3u8_path = download_m3u8(m3u8_path)
    with open(m3u8_path) as fp:
        first = fp.readline().strip()
        if first != '#EXTM3U':
            raise ValueError('Not invalid m3u8 file {}'.format(m3u8_path))
        ts_line = False
        for line in fp:
            if ts_line:
                yield line.strip().lstrip('/')
                ts_line = False
            if line.startswith('#EXTINF'):
                ts_line = True
                continue


def download_ts(path, out, max_retry=5):
    click.echo('Download {}'.format(path))
    success = False
    tries = 1
    res = None
    while not success and tries <= max_retry:
        tries += 1
        try:
            res = requests.get(path, verify=False)
            res.raise_for_status()
            success = True
        except Exception as e:
            click.echo('Download error: {} retrying...'.format(e))
    if not success or not res:
        raise ValueError('Download failed for {}'.format(path))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'wb') as f:
        for chunk in res.iter_content(100000):
            f.write(chunk)
    return out


def merge_ts(ts_list, name, output_dir=None):
    if output_dir:
        out = os.path.join(output_dir, name)
    else:
        out = name
    inputs = '|'.join(ts_list)
    command = 'ffmpeg -i "concat:{}" -acodec copy -vcodec copy -absf aac_adtstoasc {}'.format(inputs, out)
    click.echo('Merge ts list to {}'.format(name))
    os.system(command)


@click.command()
@click.argument('filepath')
@click.argument('url')
@click.option('-o', '--output-dir', help='Output directory')
@click.option('-n', '--merge-name', help='Merged output file name, default m3u8 file name')
@click.option('-c', '--clear', help='Clear ts files after merged', is_flag=True)
@click.option('-s', '--skip', help='Skip number', type=int)
def main(filepath, url, **kwargs):
    """
    Download by m3u8 file.

    :filepath: m3u8 file path or url
    :url: download domain
    """
    ts_list = []
    i = 0
    # extract parts from m3u8 list
    for ts in extract_ts(filepath):
        i += 1
        if kwargs['output_dir']:
            out = os.path.join(kwargs['output_dir'], ts)
        else:
            out = ts
        ts_list.append(out)
        if kwargs['skip'] and kwargs['skip'] >= i:
            continue
        else:
            # download parts
            download_ts('/'.join([url.rstrip('/'), ts]), out)
    # merge parts
    if kwargs['merge_name']:
        name = kwargs['merge_name']
    else:
        name = os.path.splitext(os.path.basename(filepath))[0] + '.mp4'
    merge_ts(ts_list, name, kwargs['output_dir'])
    # clear parts if needed
    if kwargs['clear']:
        for ts in ts_list:
            os.remove(ts)


if __name__ == '__main__':
    main()
