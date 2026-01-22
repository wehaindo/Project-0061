/** @odoo-module **/

import { Order, Orderline, PosGlobalState} from 'point_of_sale.models';
import Registries from 'point_of_sale.Registries';
import session from 'web.session';
import concurrency from 'web.concurrency';
import { Gui } from 'point_of_sale.Gui';
import { round_decimals,round_precision } from 'web.utils';
import core from 'web.core';

const _t = core._t;
const dropPrevious = new concurrency.MutexedDropPrevious(); // Used for queuing reward updates
const mutex = new concurrency.Mutex(); // Used for sequential cache updates

const PosDataGlobalState = (PosGlobalState) => class PosDataGlobalState extends PosGlobalState {
    async load_server_data(){
        const loadedLZStringData = await this.env.services.rpc({
            model: 'pos.session',
            method: 'load_pos_data_speed',
            args: [[odoo.pos_session_id]],
        });
        // const loadedBase64Data = await this.env.services.rpc({
        //     model: 'pos.session',
        //     method: 'load_pos_data_speed',
        //     args: [[odoo.pos_session_id]],
        // });
        console.log('loadedLZStringData');
        console.log(loadedLZStringData);
        const loadedData = LZString.decompressFromBase64(loadedLZStringData);
        // console.log('loadedData');
        // console.log(loadedData);
        // let loadedData = atob(loadedBase64Data)
        await this._processData(JSON.parse(loadedData));
        return this.after_load_server_data();
    }    
};

Registries.Model.extend(PosGlobalState, PosDataGlobalState);


