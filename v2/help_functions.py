def get_diff(last_files_info, current_files_info):
    add = []
    change = []
    remove = []

    for last_info in last_files_info:
        filter_files_info_data = list(filter(lambda x: x['path'] == last_info['path'], current_files_info))
        if len(filter_files_info_data) > 0:
            if last_info['time_modification'] < filter_files_info_data[0]['time_modification']:
                change.append(filter_files_info_data[0])
        else:
            remove.append(last_info)
    for current_info in current_files_info:
        filter_files_info_data = list(filter(lambda x: x['path'] == current_info['path'], last_files_info))
        if len(filter_files_info_data) == 0:
            add.append(current_info)

    return {
        'add': add,
        'change': change,
        'remove': remove
    }