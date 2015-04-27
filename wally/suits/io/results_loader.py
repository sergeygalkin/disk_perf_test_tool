import re
import json
import collections


# from wally.utils import ssize_to_b
from wally.statistic import med_dev

PerfInfo = collections.namedtuple('PerfInfo',
                                  ('name',
                                   'bw', 'iops', 'dev',
                                   'lat', 'lat_dev', 'raw',
                                   'meta'))


def split_and_add(data, block_size):
    assert len(data) % block_size == 0
    res = [0] * block_size

    for idx, val in enumerate(data):
        res[idx % block_size] += val

    return res


def process_disk_info(test_output):
    data = {}
    for tp, pre_result in test_output:
        if tp != 'io' or pre_result is None:
            pass

        vm_count = pre_result['__test_meta__']['testnodes_count']
        for name, results in pre_result['res'].items():
            assert len(results['bw']) % vm_count == 0
            block_count = len(results['bw']) // vm_count

            # print
            # print name, block_count
            # print results['bw']
            # print split_and_add(results['bw'], block_count)

            bw, bw_dev = med_dev(split_and_add(results['bw'], block_count))
            iops, iops_dev = med_dev(split_and_add(results['iops'],
                                                   block_count))
            lat, lat_dev = med_dev(results['lat'])
            dev = bw_dev / float(bw)
            data[name] = PerfInfo(name, bw, iops, dev, lat, lat_dev, results,
                                  pre_result['__test_meta__'])
    return data


def parse_output(out_err):
    err_start_patt = r"(?ims)=+\s+ERROR\s+=+"
    err_end_patt = r"(?ims)=+\s+END OF ERROR\s+=+"

    for block in re.split(err_start_patt, out_err)[1:]:
        tb, garbage = re.split(err_end_patt, block)
        msg = "Test fails with error:\n" + tb.strip() + "\n"
        raise OSError(msg)

    start_patt = r"(?ims)=+\s+RESULTS\(format=json\)\s+=+"
    end_patt = r"(?ims)=+\s+END OF RESULTS\s+=+"

    for block in re.split(start_patt, out_err)[1:]:
        data, garbage = re.split(end_patt, block)
        yield json.loads(data.strip())

    start_patt = r"(?ims)=+\s+RESULTS\(format=eval\)\s+=+"
    end_patt = r"(?ims)=+\s+END OF RESULTS\s+=+"

    for block in re.split(start_patt, out_err)[1:]:
        data, garbage = re.split(end_patt, block)
        yield eval(data.strip())


def filter_data(name_prefix, fields_to_select, **filters):
    def closure(data):
        for result in data:
            if name_prefix is not None:
                if not result['jobname'].startswith(name_prefix):
                    continue

            for k, v in filters.items():
                if result.get(k) != v:
                    break
            else:
                yield map(result.get, fields_to_select)
    return closure


def filter_processed_data(name_prefix, fields_to_select, **filters):
    def closure(data):
        for name, result in data.items():
            if name_prefix is not None:
                if not name.startswith(name_prefix):
                    continue

            for k, v in filters.items():
                if result.raw.get(k) != v:
                    break
            else:
                yield map(result.raw.get, fields_to_select)
    return closure


# def load_data(raw_data):
#     data = list(parse_output(raw_data))[0]

#     for key, val in data['res'].items():
#         val['blocksize_b'] = ssize_to_b(val['blocksize'])

#         val['iops_mediana'], val['iops_stddev'] = med_dev(val['iops'])
#         val['bw_mediana'], val['bw_stddev'] = med_dev(val['bw'])
#         val['lat_mediana'], val['lat_stddev'] = med_dev(val['lat'])
#         yield val


# def load_files(*fnames):
#     for fname in fnames:
#         for i in load_data(open(fname).read()):
#             yield i
