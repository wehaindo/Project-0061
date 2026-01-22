def hextostring(data):
    # print(data)
    result = bytes.fromhex(data).decode('utf-8')
    print(result)

data = "0202000230313030303032373735303030303030303030303030303030303534303931322a2a2a2a2a2a353638342020202a2a2a2a303020202020202030303033313452353434363932303233303732303136313334343030303030353030303031353939394341454f4e3030314e20202020202020202020202020202020202020202020202020202020202020202020202020202020202030303030333530303030313730324e4e4e3030303030303030303030302020202020202020202020204e2020202020202020034f"
data = "0202000230313030303030353730303030303030303030303030303030303532363035312a2a2a2a2a2a313331382020202a2a2a2a3030202020202020303130353038323134393133323032333132303232313439313330303038383530303231323837343852304248323930354e2020202020202020202020202020202020202020202020202f202020202020202020202020202020202030303434343030303030323730304e4e4e3030303030303030303030302020202020202020202020204e20202020202020200331"
data = "0202000230313030303030333935303030303030303030303030303030303435353633332a2a2a2a2a2a343731392020202a2a2a2a303020202020202030303035313930333933363432303235313032383139323231313030303030353030323634383937334332474b363336354e20202020202020202020202020202020202020202020202020202020202020202020202020202020202030303037303330303030323630314e4e4e3030303030303030303030302020202020202020202020204e20202020202020200320"
#print(bytes.fromhex(data).decode('utf-8'))
# hextostring(data[0:8])  
hextostring(data[8:12]) #trans_type
hextostring(data[12:36]) #trans_amount 
hextostring(data[36:60]) #other_amount
hextostring(data[60:98]) #pan
hextostring(data[98:106]) #expired_date
hextostring(data[106:110]) #
hextostring(data[110:134])
hextostring(data[134:146])
hextostring(data[146:162])
hextostring(data[162:174])
hextostring(data[174:204])
hextostring(data[222:278])

          
        #   if (trans_type == "3331" || trans_type == "3332"){
        #     var parsing_data = {
        #       length: jsonData.value.slice(0,8), // 4
        #       trans_type: jsonData.value.slice(8,12), // 2
        #       trans_amount: jsonData.value.slice(12,36), // 12
        #       other_amount: jsonData.value.slice(36,60), // 12
        #       pan: jsonData.value.slice(60,98), // 19 - Benar
        #       expiry_date: jsonData.value.slice(98,106), // 4 
        #       resp_code: jsonData.value.slice(106,110), // 2
        #       rrn: jsonData.value.slice(110,134), // 12
        #       approval_code: jsonData.value.slice(134,146), // 6
        #       date: jsonData.value.slice(146,162), // 8  146 + 16 = 162
        #       time: jsonData.value.slice(162,174), // 6  162 + 12 = 174 
        #       marchant_id: jsonData.value.slice(180,210), // 15 
        #       terminal_id: jsonData.value.slice(210,226), // 8
        #       offline_flag: jsonData.value.slice(226,228), // 1
        #       card_holder_name: jsonData.value.slice(228,280), // 26 228 + 52
        #       pan_cashier_card: jsonData.value.slice(278,310), // 16
        #       invoice_number: jsonData.value.slice(310,322), // 6
        #       batch_number: jsonData.value.slice(322,334), // 6
        #       issuer_id: jsonData.value.slice(334,338), // 2
        #       installment_flag: jsonData.value.slice(338,440), // 1
        #       ddc_flag: jsonData.value.slice(440,442), // 1
        #       redeem_flag: jsonData.value.slice(442,444), // 1
        #       info_amount: jsonData.value.slice(444,468), // 12
        #       dcc_decimal_place: jsonData.value.slice(468,470), // 1
        #       ddc_currency_name: jsonData.value.slice(470,476), // 3
        #       ddc_ex_rate: jsonData.value.slice(476,492), // 8
        #       coupon_flag: jsonData.value.slice(492,494), // 1
        #       filler: jsonData.value.slice(494,510) // 8