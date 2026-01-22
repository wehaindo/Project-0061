# Open the file in read mode
with open('delete_pos_order_19032025.txt', 'r') as file:
    # Read each line in the file
    row = 0
    for line in file:
        # row = row + 1
        # print(row)
        print('delete from pos_payment where pos_order_id=' + line.replace('\n',';'))
        print('delete from pos_order_line where order_id=' + line.replace('\n',';'))
        print('delete from pos_order where id=' + line.replace('\n',';'))