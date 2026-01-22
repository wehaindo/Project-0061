import psycopg2

conn = psycopg2.connect(host="10.104.0.3",database="aeondb",user="odoouser",password="pelang123")
cursor = conn.cursor()
strSQL = "select distinct(a.order_id) from pos_order_line a left join pos_order b on a.order_id = b.id left join product_product d on a.product_id = d.id left join product_template e on d.product_tmpl_id = e.id where (price_subtotal - price_subtotal_incl) = 0 and b.date_order > '2023-11-13 00:00:00'"
cursor.execute(strSQL)
pos_orders = cursor.fetchall()

# for pos_order in pos_orders:
#     order  = pos_order[0]
#     print("Order " + str(order))
#     strSQL = "select a.id from pos_order_line a left join account_tax_pos_order_line_rel b on b.pos_order_line_id = a.id where b.pos_order_line_id is null and a.order_id=" + str(order)
#     cursor.execute(strSQL)
#     pos_order_lines = cursor.fetchall()
#     for pos_order_line in pos_order_lines:
#         order_line = pos_order_line[0]
#         print("Order Line " + str(order_line))
        
pos_order = pos_orders[0]
order = pos_order[0]
print("Order " + str(order))
strSQL = "select a.id from pos_order_line a left join account_tax_pos_order_line_rel b on b.pos_order_line_id = a.id where b.pos_order_line_id is null and a.order_id=" + str(order)
cursor.execute(strSQL)
pos_order_lines = cursor.fetchall()
for pos_order_line in pos_order_lines:
    order_line = pos_order_line[0]
    print("Order Line " + str(order_line))
    strSQL = "insert into account_tax_pos_order_line_rel values (" + str(order_line) + ",1)"
    print(strSQL)
    cursor.execute(strSQL)
    #conn.commit()    
    strSQL = "update pos_order_line set price_subtotal=(select (price_subtotal_incl * 100/111) from pos_order_line where id=" + str(order_line) + ") where id=" + str(order_line)
    print(strSQL)
    cursor.execute(strSQL)
    #conn.commit()
strSQL = "update pos_order set amount_tax = (select sum(price_subtotal_incl - price_subtotal) from pos_order_line where order_id = " + str(order) + ") where id=" + str(order)
print(strSQL)
cursor.execute(strSQL)
conn.commit()    

    
