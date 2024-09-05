import os
import csv
import json

with open('sites.tsv', 'r') as file:
    reader = csv.DictReader(file, delimiter='\t')

    cookies_total = dict[tuple, set]
    for row in reader:
        domain = row['domain']

        cookieblock_raw = json.load(open(os.path.join(domain, f'{domain}.accept.cookieblock.json'), 'r'))

        cookieblock_dict = {(cookie_dict['name'], cookie_dict['domain'], cookie_dict['path']): [cookie['timestamp'] for cookie in cookie_dict['variable_data']] for paths in cookieblock_raw.values() for cookies in paths.values() for cookie_dict in cookies.values()}

        filtered_cookies = []
        for cookie, timestamps in cookieblock_dict.items():
            if cookie not in cookies_total:
                cookies_total[cookie] = set(timestamps)
            else:
                # Take the existing timestamps from the dictionary; then, remove all timestamps which also occur in the current file.
                timestamps_filtered = [timestamp for timestamp in timestamps if timestamp not in cookies_total[cookie]]
                # Add the current set of timestamps to our dictionary.
                cookies_total[cookie] = cookies_total[cookie].union(set(timestamps))
                if len(timestamps_filtered) == 0:
                    # We should not include this cookie in the filtered data
                    continue
            # Add the cookie to the set of filtered cookies for this domain.
            filtered_cookies.append(cookie)

        with open(os.path.join(domain, f'{domain}.accept.cookieblock-filtered.json'), 'w') as outfile:
            json.dump(filtered_cookies, outfile)