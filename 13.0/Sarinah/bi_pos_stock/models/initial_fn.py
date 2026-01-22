# Yayat
from odoo import api, fields, models, tools


class BiPosStock(models.Model):
    _name = "bi.pos.stock"

    def init(self):
        """
        Contoh Penggunaan:
        SELECT yyt_fn_assign_picking(300, 7);
        SELECT yyt_fn_validate_picking(300, 7);
        """
        # Create function for assign picking in stock picking, just need to validate to complate picking
        query_fn_assign_picking = """
        DROP FUNCTION IF EXISTS yyt_fn_assign_picking(input_picking_id int, input_user_id int);
        CREATE OR REPLACE FUNCTION yyt_fn_assign_picking(input_picking_id int, input_user_id int)
        RETURNS void AS
        $$
        DECLARE
        stpick RECORD;
        stmove RECORD;
        prod RECORD;
        stock_quant_id int;

                                        
        BEGIN
        FOR stpick IN (SELECT * FROM stock_picking WHERE id = input_picking_id)
        LOOP
            FOR stmove IN (SELECT * FROM stock_move WHERE picking_id=input_picking_id)
            LOOP
                FOR prod IN (SELECT * FROM product_product pp LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id WHERE pp.id=stmove.product_id)
                LOOP
                    CASE WHEN prod.owner_id IS NOT NULL THEN
                        -- 1. Ambil stock_quant id
                        SELECT id INTO stock_quant_id
                        FROM stock_quant
                        WHERE company_id = stmove.company_id
                        AND location_id = stmove.location_id 
                        AND product_id = stmove.product_id
                        AND owner_id = prod.owner_id FOR UPDATE; -- LOCK FOR UPDATE
                        
                        -- 2. Update reserved_quantity in stock_quant
                        UPDATE stock_quant SET reserved_quantity = reserved_quantity + stmove.product_uom_qty, write_uid = input_user_id, write_date = (now() at time zone 'UTC') WHERE id=stock_quant_id;
                        
                        -- 3. Insert stock_move_line, untuk lot_id, package_id tidak diinclude karena asumsi barang pos bukan dari production
                        INSERT INTO stock_move_line (id, create_uid, create_date, write_uid, write_date, company_id, date, location_dest_id, location_id, move_id, 
                        owner_id, picking_id, product_id, product_uom_id, product_uom_qty, qty_done, 
                        state, product_qty, reference)
                        VALUES 
                        (nextval('stock_move_line_id_seq'), input_user_id, (now() at time zone 'UTC'), input_user_id, (now() at time zone 'UTC'), stmove.company_id, stpick.date, stmove.location_dest_id, stmove.location_id, stmove.id,
                        prod.owner_id, stpick.id, stmove.product_id, stmove.product_uom, stmove.product_uom_qty, stmove.product_uom_qty,
                        'assigned', stmove.product_uom_qty, stpick.name);
                    
                        -- 4. Update stock_picking
                        UPDATE stock_picking SET state='assigned', write_uid=input_user_id, write_date=(now() at time zone 'UTC') WHERE id=stpick.id;
                        -- 5. Update stock_move
                        UPDATE stock_move SET write_uid=input_user_id, state='assigned', write_date=(now() at time zone 'UTC') WHERE id=stmove.id;
                            
                    ELSE

                        -- 1. Ambil stock_quant id
                        SELECT id INTO stock_quant_id
                        FROM stock_quant
                        WHERE company_id = stmove.company_id
                        AND location_id = stmove.location_id
                        AND product_id = stmove.product_id
                        AND owner_id is Null FOR UPDATE; -- LOCK FOR UPDATE
                        
                        -- 2. Update reserved_quantity in stock_quant
                        UPDATE stock_quant SET reserved_quantity = reserved_quantity + stmove.product_uom_qty, write_uid = input_user_id, write_date = (now() at time zone 'UTC') WHERE id=stock_quant_id;
                        
                        -- 3. Insert stock_move_line, untuk lot_id, package_id tidak diinclude karena asumsi barang pos bukan dari production
                        INSERT INTO stock_move_line (id, create_uid, create_date, write_uid, write_date, company_id, date, location_dest_id, location_id, move_id, 
                        owner_id, picking_id, product_id, product_uom_id, product_uom_qty, qty_done, 
                        state, product_qty, reference)
                        VALUES 
                        (nextval('stock_move_line_id_seq'), input_user_id, (now() at time zone 'UTC'), input_user_id, (now() at time zone 'UTC'), stmove.company_id, stpick.date, stmove.location_dest_id, stmove.location_id, stmove.id,
                        NULL, stpick.id, stmove.product_id, stmove.product_uom, stmove.product_uom_qty, stmove.product_uom_qty,
                        'assigned', stmove.product_uom_qty, stpick.name);
                    
                        -- 4. Update stock_picking
                        UPDATE stock_picking SET state='assigned', write_uid=input_user_id, write_date=(now() at time zone 'UTC') WHERE id=stpick.id;
                        -- 5. Update stock_move
                        UPDATE stock_move SET write_uid=input_user_id, state='assigned', write_date=(now() at time zone 'UTC') WHERE id=stmove.id;
                    END CASE;
                END LOOP;
            END LOOP;
        END LOOP;
        END;
        $$
        LANGUAGE plpgsql;

        """

        query_fn_validate_picking = """
        DROP FUNCTION IF EXISTS yyt_fn_validate_picking(input_picking_id int, input_user_id int);
        CREATE OR REPLACE FUNCTION yyt_fn_validate_picking(input_picking_id int, input_user_id int)
        RETURNS void AS
        $$
        DECLARE
        -- BELOM BISA UNTUK RECEIVE PURCHASE KARENA HPP BELOM DIKALKULASI SAAT RECEIVE
        -- UNTUK SO BELUM DICEK SAMA SEKALI
        stpick RECORD;
        stmove RECORD;
        prod RECORD;
        stock_quant_id_src_loc int;
        stock_quant_id_dst_loc int;
        hpp float;
        pengali_picking_type int;
        depart_id int;
        move_type text; -- internal, incoming, outgoing
        acc_move_id int;

        stjournal_id int; -- coa stock journal
        stvaluation_id int; -- coa stock valuation
        stinput_account_id int; -- coa stock input account
        stoutput_account_id int; -- coa stock output account
        acc_move_seq text; -- for next sequence
        inv_partner_display_name text; 
                                        
        BEGIN
        FOR stpick IN (SELECT * FROM stock_picking WHERE id = input_picking_id)
        LOOP
            FOR stmove IN (SELECT * FROM stock_move WHERE picking_id=input_picking_id)
            LOOP
                FOR prod IN (SELECT * FROM product_product pp LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id WHERE pp.id=stmove.product_id)
                LOOP
                    CASE WHEN prod.owner_id IS NOT NULL THEN
                        -- 1. Ambil stock_quant id
                        -- 1.1 Get stock_quant_id_src_loc
                        SELECT id INTO stock_quant_id_src_loc
                        FROM stock_quant
                        WHERE CASE WHEN (SELECT company_id FROM stock_location WHERE id=stmove.location_id limit 1) IS NULL THEN company_id is null ELSE company_id = (SELECT company_id FROM stock_location WHERE id=stmove.location_id limit 1) END
                        AND location_id = stmove.location_id 
                        AND product_id = stmove.product_id
                        AND owner_id = prod.owner_id FOR UPDATE; -- LOCK FOR UPDATE
                        
                        -- 1.2 Get stock_quant_id_dst_loc
                        SELECT id INTO stock_quant_id_dst_loc
                        FROM stock_quant
                        WHERE CASE WHEN (SELECT company_id FROM stock_location WHERE id=stmove.location_dest_id limit 1) IS NULL THEN company_id is null ELSE company_id = (SELECT company_id FROM stock_location WHERE id=stmove.location_dest_id limit 1) END
                        AND location_id = stmove.location_dest_id 
                        AND product_id = stmove.product_id
                        AND owner_id = prod.owner_id FOR UPDATE; -- LOCK FOR UPDATE
                    ELSE 
                        -- 1. Ambil stock_quant id
                        -- 1.1 Get stock_quant_id_src_loc
                        SELECT id INTO stock_quant_id_src_loc
                        FROM stock_quant
                        WHERE CASE WHEN (SELECT company_id FROM stock_location WHERE id=stmove.location_id limit 1) IS NULL THEN company_id is null ELSE company_id = (SELECT company_id FROM stock_location WHERE id=stmove.location_id limit 1) END
                        AND location_id = stmove.location_id 
                        AND product_id = stmove.product_id
                        AND owner_id IS NULL FOR UPDATE; -- LOCK FOR UPDATE
                        
                        -- 1.2 Get stock_quant_id_dst_loc
                        SELECT id INTO stock_quant_id_dst_loc
                        FROM stock_quant
                        WHERE CASE WHEN (SELECT company_id FROM stock_location WHERE id=stmove.location_dest_id limit 1) IS NULL THEN company_id is null ELSE company_id = (SELECT company_id FROM stock_location WHERE id=stmove.location_dest_id limit 1) END
                        AND location_id = stmove.location_dest_id 
                        AND product_id = stmove.product_id
                        AND owner_id IS NULL FOR UPDATE; -- LOCK FOR UPDATE
                    END CASE;
                            
                    -- 2. Ambil Nilai HPP
                    SELECT p.value_float into hpp
                    FROM ir_property p
                    WHERE p.fields_id= (select id from ir_model_fields where name='standard_price' and model='product.product')
                        AND (p.company_id=1 OR p.company_id IS NULL)
                        AND (p.res_id IN ('product.product,'||prod.id) OR p.res_id IS NULL)
                    ORDER BY p.company_id NULLS FIRST;
                    
                    -- 2.1 CEK HPP, jika barang masuk dari po maka hpp diganti dengan price_unit
                    IF stmove.price_unit is not null then
                        hpp:=stmove.price_unit;
                    END IF;
                        
                    -- 3. Ambil pengali untuk stock_valuation_layer berdasarkan default destination location di stock_picking_type
                    --    dan move_type berdasarkan code
                    SELECT 
                        CASE WHEN code = 'outgoing' THEN
                            CASE WHEN default_location_dest_id = stmove.location_dest_id THEN -1 -- sama menuju customer location
                            ELSE 1
                            END
                        WHEN code = 'incoming' THEN
                            CASE WHEN default_location_dest_id = stmove.location_dest_id THEN 1 -- sama menuju receipt location
                            ELSE -1
                            END
                        ELSE 0 
                        END,
                        code
                        INTO pengali_picking_type, move_type
                    FROM stock_picking_type
                    WHERE id=stmove.picking_type_id;
                        
                    -- 4. Insert stock_valuation_layer jika picking type code bukan internal (0)
                    -- 4.1 Get department_id
                    SELECT department_id into depart_id FROM stock_location WHERE id=stmove.location_id;
                    CASE WHEN move_type <> 'internal' THEN
                        -- 4.2 Insert account_move and account_move_line
                        CASE WHEN prod.is_consignment <> TRUE AND prod.type = 'product' THEN
                            -- 4.2.1 get stock journal id base on product category
                            SELECT r.id INTO stjournal_id
                            FROM ir_property p
                            LEFT JOIN account_journal r ON (string_to_array(p.value_reference, ','))[2]::integer=r.id
                            WHERE p.fields_id=(SELECT id FROM ir_model_fields WHERE model='product.category' AND name='property_stock_journal')
                                AND (p.company_id=1 OR p.company_id IS NULL)
                                AND (p.res_id IN ('product.category,' || prod.categ_id) OR p.res_id IS NULL)
                            ORDER BY p.company_id NULLS FIRST, p.res_id;
                            
                            -- 4.2.2 get account stock valuation
                            SELECT (string_to_array(p.value_reference, ','))[2]::int INTO stvaluation_id
                            FROM ir_property p
                            WHERE p.fields_id=(SELECT id FROM ir_model_fields WHERE model='product.category' AND name='property_stock_valuation_account_id')
                                AND (p.company_id=1 OR p.company_id IS NULL)
                                AND (p.res_id IN ('product.category,' || prod.categ_id) OR p.res_id IS NULL)
                            ORDER BY p.company_id NULLS FIRST, p.res_id;
                            
                            -- 4.2.3 get account stock input
                            SELECT (string_to_array(p.value_reference, ','))[2]::int INTO stinput_account_id
                            FROM ir_property p
                            WHERE p.fields_id=(SELECT id FROM ir_model_fields WHERE model='product.category' AND name='property_stock_account_input_categ_id')
                                AND (p.company_id=1 OR p.company_id IS NULL)
                                AND (p.res_id IN ('product.category,' || prod.categ_id) OR p.res_id IS NULL)
                            ORDER BY p.company_id NULLS FIRST, p.res_id;
                            
                            -- 4.2.4 get account stock output
                            SELECT (string_to_array(p.value_reference, ','))[2]::int INTO stoutput_account_id
                            FROM ir_property p
                            WHERE p.fields_id=(SELECT id FROM ir_model_fields WHERE model='product.category' AND name='property_stock_account_output_categ_id')
                                AND (p.company_id=1 OR p.company_id IS NULL)
                                AND (p.res_id IN ('product.category,' || prod.categ_id) OR p.res_id IS NULL)
                            ORDER BY p.company_id NULLS FIRST, p.res_id;
                            
                            -- 4.2.5 GENERATE NEXT SEQUENCE, FORMAT 'STJ/YEAR/SEQUENCE/RANDOM NUM'
                            -- 4.2.5 GENERATE NEXT SEQUENCE, FORMAT 'STJ/YEAR/SEQUENCE/RANDOM NUM'
                            SELECT SUBSTR(name, 1,11) || (STRING_TO_ARRAY(name, '/'))[3]::int + 1 || '/' || REPLACE(SUBSTR(CURRENT_TIME::TEXT, 7, 5),'.','')
                            INTO acc_move_seq
                            FROM account_move WHERE name like 'STJ/' || SUBSTR(REPLACE(CURRENT_DATE::TEXT,'-',''), 1,6) || '/%/%' ORDER BY ID DESC LIMIT 1; 							
                            CASE WHEN acc_move_seq IS NULL THEN
                                SELECT 'STJ/' || SUBSTR(REPLACE(CURRENT_DATE::TEXT,'-',''), 1,6) || '/1/' || REPLACE(SUBSTR(CURRENT_TIME::TEXT, 7, 5),'.','') INTO acc_move_seq;
                            ELSE
                                SELECT SUBSTR(name, 1,11) || (STRING_TO_ARRAY(name, '/'))[3]::int + 1 || '/' || REPLACE(SUBSTR(CURRENT_TIME::TEXT, 7, 5),'.','')
                                INTO acc_move_seq
                                FROM account_move WHERE name like 'STJ/' || SUBSTR(REPLACE(CURRENT_DATE::TEXT,'-',''), 1,6) || '/%/%' ORDER BY ID DESC LIMIT 1;
                            END CASE;
                            
                            -- 4.2.6 SET invoice_partner_display_name
                            CASE WHEN stmove.purchase_line_id IS NULL THEN
                                SELECT 'Created by: ' || rp.name INTO inv_partner_display_name
                                FROM res_users ru 
                                LEFT JOIN res_partner rp on rp.id=ru.partner_id
                                WHERE ru.id=input_user_id;
                            ELSE
                                SELECT name INTO inv_partner_display_name FROM res_partner WHERE id=(SELECT partner_id FROM purchase_order_line WHERE id=stmove.purchase_line_id);
                            END CASE;
                            
                            IF hpp <> 0 THEN
                                -- 4.2.7 Insert account_move
                                INSERT INTO account_move (id, create_uid, create_date, write_uid, write_date, auto_post, branch_id, currency_id, 
                                date, department_id, extract_remote_id, extract_state, goods_note, invoice_date, invoice_incoterm_id, invoice_sent, invoice_user_id, is_tax_closing, 
                                journal_id, name, pajak, ref, state, stock_move_id, team_id, to_check, type, use_goods_note,
                                company_id, amount_untaxed, amount_tax, amount_total, amount_residual, amount_untaxed_signed, amount_tax_signed, amount_total_signed, amount_residual_signed, invoice_partner_display_name) VALUES 
                                
                                (nextval('account_move_id_seq'), 2, (now() at time zone 'UTC'), 2, (now() at time zone 'UTC'), false, NULL, (SELECT currency_id FROM res_company WHERE id=stmove.company_id LIMIT 1),   
                                CURRENT_DATE, depart_id, -1, 'no_extract_requested', '/', NULL, NULL, false, input_user_id, false, 
                                stjournal_id, acc_move_seq, NULL, stpick.name || ' - ' || prod.name, 'posted', stmove.id, 1, false, 'entry', false,
                                stmove.company_id,'0','0',hpp,'0','0','0',hpp,'0', inv_partner_display_name) RETURNING id INTO acc_move_id;
                                
                                
                                -- 4.2.8 Insert account move line
                                -- 4.2.8.1 account stock valuation
                                INSERT INTO account_move_line (id, create_uid, create_date, write_uid, write_date, account_id, blocked, branch_id, 
                                company_currency_id, reconciled, amount_residual_currency, tax_audit, 
                                credit, debit, 
                                discount, display_type,move_id, name, partner_id, product_id, product_uom_id, 
                                quantity, ref, sequence, tax_exigible, 
                                journal_id, company_id, parent_state, 
                                balance,
                                amount_residual,
                                account_root_id, account_internal_type, 
                                department_id, date, move_name) VALUES 
                                
                                (nextval('account_move_line_id_seq'), input_user_id, (now() at time zone 'UTC'), input_user_id, (now() at time zone 'UTC'), stvaluation_id, false, NULL, 
                                (SELECT currency_id FROM res_company WHERE id=stmove.company_id LIMIT 1), false, 0.0, '',
                                (case when pengali_picking_type < 0 then stmove.product_uom_qty * hpp else 0 end), (case when pengali_picking_type > 0 then stmove.product_uom_qty * hpp else 0 end), 
                                '0.00', NULL, acc_move_id, stpick.name || ' - ' || prod.name, NULL, prod.id, prod.uom_id,
                                pengali_picking_type * stmove.product_uom_qty, stpick.name || ' - ' || prod.name, 10, true,
                                stjournal_id, stmove.company_id, 'posted', 
                                pengali_picking_type * (stmove.product_uom_qty * hpp), -- nilai balace akan negatif jika barang keluar sebaliknya akan positif jika barang masuk (return)
                                '0',  -- nilai amount_residual = 0  untuk account persediaan
                                (select root_id from account_account where id=stvaluation_id), 'other',
                                depart_id, CURRENT_DATE,(select name from account_move where id=acc_move_id));
                                
                                -- 4.2.8.2 account input / output, jika stock_move dari purchase maka yg dipakai adalah account_stock_input
                                -- tandanya adalah stmove.purchase_line_id. jika not null maka move berasal dari purchase order
                                INSERT INTO account_move_line (id, create_uid, create_date, write_uid, write_date, 
                                account_id, blocked, branch_id, reconciled, amount_residual_currency, tax_audit,
                                company_currency_id, 
                                credit, debit, 
                                discount, display_type, move_id, name, partner_id, product_id, product_uom_id, 
                                quantity, ref, sequence, tax_exigible,
                                journal_id, company_id, parent_state, 
                                balance,
                                amount_residual, 
                                account_root_id, account_internal_type, 
                                department_id, date, move_name) VALUES 

                                (nextval('account_move_line_id_seq'), input_user_id, (now() at time zone 'UTC'), input_user_id, (now() at time zone 'UTC'), 
                                (CASE WHEN stmove.purchase_line_id IS NULL THEN stoutput_account_id ELSE stinput_account_id END), false, NULL,false, 0.0, '',
                                (SELECT currency_id FROM res_company WHERE id=stmove.company_id LIMIT 1),
                                (case when pengali_picking_type > 0 then stmove.product_uom_qty * hpp else 0 end), (case when pengali_picking_type < 0 then stmove.product_uom_qty * hpp else 0 end), 
                                '0.00', NULL, acc_move_id, stpick.name || ' - ' || prod.name, NULL, prod.id, prod.uom_id, 
                                pengali_picking_type * stmove.product_uom_qty, stpick.name || ' - ' || prod.name, 10, true,
                                stjournal_id, stmove.company_id, 'posted', 
                                (-1 * pengali_picking_type) * (stmove.product_uom_qty * hpp), --  nilai balance akan positif jika barang keluar sebaliknya akan negatif jika barang masuk (return)
                                '0', -- (-1 * pengali_picking_type) * (stmove.product_uom_qty * hpp), -- nilai amount_residual sama seperti balance untuk account lawan dari persediaan: MASIH RAGU JADI SEMUA RESIDUAL AMOUNT DI 0 IN
                                (select root_id from account_account where id=(CASE WHEN stmove.purchase_line_id IS NULL THEN stoutput_account_id ELSE stinput_account_id END)), 'other', 
                                depart_id, CURRENT_DATE,(select name from account_move where id=acc_move_id));
                            END IF;
                        ELSE NULL;
                        END CASE;
                        
                        -- 4.3 Insert stock_valuation layer -> incoming = 1, outgoing = -1, internal =0
                        -- barang bs dan bks sama-sama dibuat stock_valuation_layer nya cuman klw bks hpp nya pasti 0
                        -- SETIAP BARANG MASUK, FIELD remaining_qty, remaining_value HARUS DIISI
                        INSERT INTO stock_valuation_layer 
                        (id, create_uid, create_date, write_uid, write_date, company_id, description, 
                        product_id, quantity, stock_move_id, unit_cost, value, account_move_id, department_id,
                        remaining_qty, remaining_value) VALUES -- jika return, remaining_qty, remaining_value diisi
                        (nextval('stock_valuation_layer_id_seq'), input_user_id, (now() at time zone 'UTC'), input_user_id, (now() at time zone 'UTC'), stmove.company_id, stpick.name || ' - ' || prod.name, 
                        prod.id,  pengali_picking_type * stmove.product_uom_qty, stmove.id, hpp,  pengali_picking_type * (stmove.product_uom_qty * hpp), acc_move_id, depart_id,
                        
                        CASE WHEN move_type='outgoing' AND pengali_picking_type=1 THEN pengali_picking_type * stmove.product_uom_qty  -- set remaining_qty, operation retrun (barang masuk)
                        WHEN move_type='incoming' AND pengali_picking_type=1 THEN pengali_picking_type * stmove.product_uom_qty ELSE NULL END, -- set remaining_qty, operation receive (barang masuk)
                        
                        CASE WHEN move_type='outgoing' and pengali_picking_type=1 THEN pengali_picking_type * (stmove.product_uom_qty * hpp)  -- set remaining_value, operation retrun (barang masuk)
                        WHEN move_type='incoming' AND pengali_picking_type=1 THEN pengali_picking_type * (stmove.product_uom_qty * hpp) ELSE NULL END); -- set remaining_value, operation receive (barang masuk)
                        
                        -- LAKUKAN PENYESUAIAN COST SAAT BARANG MASUK, MASIH PR
                    ELSE NULL;
                    END CASE;
                        
                    -- 5. Update stock_picking
                    UPDATE stock_picking SET state='done',write_uid=input_user_id,date_done=date_trunc('second',(now() at time zone 'UTC')),write_date=(now() at time zone 'UTC') WHERE id=stpick.id;
                    
                    -- 6. Update stock_move
                    UPDATE stock_move SET write_uid=input_user_id,state='done',date=date_trunc('second',(now() at time zone 'UTC')),write_date=(now() at time zone 'UTC') WHERE id=stmove.id;
                    
                    -- 7. Update stock_move_line
                    UPDATE stock_move_line SET write_uid=input_user_id,product_uom_qty='0.000',date=date_trunc('second',(now() at time zone 'UTC')),product_qty=0.0,state='done',
                    write_date=(now() at time zone 'UTC'), reference=stpick.name
                    WHERE picking_id=stpick.id and move_id=stmove.id and product_id=prod.id;
                    
                    -- 8. Update stock_quant
                    -- 8.1 Pengurangan qty untuk lokasi sumber
                    IF stock_quant_id_src_loc IS NOT NULL THEN
                        UPDATE stock_quant SET write_uid=input_user_id,reserved_quantity=reserved_quantity - stmove.product_uom_qty ,quantity=quantity - stmove.product_uom_qty,write_date=(now() at time zone 'UTC') 
                        WHERE id=stock_quant_id_src_loc;
                    ELSE
                        INSERT INTO stock_quant (create_uid, write_uid, create_date, write_date, product_id, company_id,
                        location_id, owner_id, quantity, reserved_quantity, in_date) VALUES
                        (input_user_id, input_user_id, (now() at time zone 'UTC'), (now() at time zone 'UTC'), stmove.product_id, (SELECT company_id FROM stock_location WHERE id=stmove.location_id limit 1),
                        stmove.location_id, prod.owner_id, 0 - stmove.product_uom_qty, 0, date_trunc('second', (now() at time zone 'UTC')));
                    END IF;
                    -- 8.2 Penambahan qty untuk lokasi tujuan
                    IF stock_quant_id_dst_loc IS NOT NULL THEN
                        UPDATE stock_quant SET write_uid=input_user_id,quantity=quantity + stmove.product_uom_qty,write_date=(now() at time zone 'UTC') WHERE id=stock_quant_id_dst_loc;
                    ELSE
                        INSERT INTO stock_quant (create_uid, write_uid, create_date, write_date, product_id, company_id,
                        location_id, owner_id, quantity, reserved_quantity, in_date) VALUES
                        (input_user_id, input_user_id, (now() at time zone 'UTC'), (now() at time zone 'UTC'), stmove.product_id, (SELECT company_id FROM stock_location WHERE id=stmove.location_dest_id limit 1),
                        stmove.location_dest_id, prod.owner_id, stmove.product_uom_qty, 0, date_trunc('second', (now() at time zone 'UTC')));
                    END IF;
                END LOOP;
            END LOOP;
        END LOOP;
        END;
        $$
        LANGUAGE plpgsql;

        """
        cr = self.env.cr
        # cr.execute(query_fn_assign_picking)
        # cr.execute(query_fn_validate_picking)

