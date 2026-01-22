line="P000490661   009111080    000000022023101920231203010023590000000000028800.00BUY 2 28,800 A"

data = {
    'mm_type': line[0:1].strip(),
    'promo_no' : line[1:13].strip(),
    'sku_no' : line[13:26].strip(),
    'mm_qty' : line[26:34].strip(),
    'mm_start_date' : line[34:42].strip(),
    'mm_end_date' : line[42:50].strip(),
    'mm_start_time' : line[50:54].strip(),
    'mm_end_time' : line[54:58].strip(),
    'mm_fix_foc_qty' : line[58:60].strip(),
    'promo_price' : line[60:77].strip(),
    'promo_disc_name' : line[77:90].strip(),
    'record_flag': line[90:92].strip(),
    'end_of_record': line[92:94].strip()
}

print(data)