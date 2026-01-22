/** @odoo-module */

import { registry } from "@web/core/registry"
import { loadJS } from "@web/core/assets"
import { useService } from "@web/core/utils/hooks"
const { Component, onWillStart, useRef, onMounted, useState } = owl
import { getColor } from "@web/views/graph/colors"
import { browser } from "@web/core/browser/browser"
import { routeToUrl } from "@web/core/browser/router_service"
import { ChartTemplate } from "./chart_template/chart_template"
import { KpiTemplate } from "./kpi_template/kpi_template"

export class PosDashboard extends Component {

    setup(){
        this.state = useState({
            quotations: {
                value:10,
                percentage:6,
            },
            storeData: {
                labels: [
                    '23-03-2024',
                    '24-03-2024',
                ],
                datasets: [
                    {
                        label: '7001',
                        data: [300, 450],
                        hoverOffset: 4
                    },
                    {
                        label: '7002',
                        data: [500, 400],
                        hoverOffset: 4
                    },
                    {
                        label: '7003',
                        data: [250, 350],
                        hoverOffset: 4
                }]
            },
            period:7,
            stores:[],
            store:0,
            storeDatasheet:[]
        })
        this.orm = useService("orm")
        this.actionService = useService("action")


        onWillStart(async ()=>{
            this.getDates()
            await this.getStores();
            // await this.getQuotations()
            await this.getOrders()
        })
    }

    async onChangePeriod(){        
        this.getDates()
        // await this.getQuotations()
        await this.getOrders()
    }

    async onChangeStore(){
        this.getDates()
        // await this.getQuotations()
        await this.getOrders()
    }
    
    getDates(){
        this.state.current_date = moment().subtract(0, 'days').format('YYYY-MM-DD')
        this.state.previous_date = moment().subtract(this.state.period, 'days').format('YYYY-MM-DD')
        console.log(this.state.current_date)
        console.log(this.state.previous_date)
    }

    async getStores(){
        const stores = await this.orm.searchRead("res.branch", [], ["name"])
        console.log("Stores: " + stores)
        this.state.stores = stores
    }

    async getOrders(){        
        console.log('getOrders')        
        var self = this
        var labels = []
        var datasets = []

        let currentMoment = moment().subtract(this.state.period, 'days');
        let endMoment = moment().add(1, 'days');        
        while (currentMoment.isBefore(endMoment, 'day')) {            
            labels.push(currentMoment.format('DD-MM-YYYY'));                                   
            currentMoment.add(1, 'days');        
        }

        this.state.stores.map(async function(store_id){
            console.log(store_id)
            let data = [];
            let currentDate = moment().subtract(self.state.period, 'days');
            let endDate = moment().add(1, 'days');   
            while (currentDate.isBefore(endDate, 'day')) {
                console.log(`Loop at ${currentDate.format('DD-MM-YYYY')}`);
                let nextDate  = moment(currentDate.format('YYYY-MM-DD')).add(1,'days')
                let domain = [
                    ['branch_id','=',store_id.id],
                    ['date_order','>',currentDate.format('YYYY-MM-DD') +  " 00:00:00"],
                    ['date_order','<',nextDate.format('YYYY-MM-DD') + " 00:00:00"],
                    ['state', 'in', ['paid','posted']]
                ]
                console.log(domain)      
                const current_revenue = await self.orm.readGroup("pos.order", domain, ["amount_total:sum"], [])
                console.log(current_revenue[0].amount_total)
                if(current_revenue){
                    if(current_revenue[0].amount_total == null){
                        data.push(0)
                    }else{
                        data.push(current_revenue[0].amount_total)
                    }        
                }else{
                    data.push(0)
                }                                
                currentDate.add(1, 'days');        
            }   
            const vals = {
                label: store_id.name,
                data: data,
                hoverOffset: 4
            }
            datasets.push(vals)         
        })
        this.state.storeData.labels = labels
        this.state.storeData.datasets = datasets
        // console.log(labels)
        // console.log(datasets)
    }
}

PosDashboard.template = "weha_smart_pos_aeon_dashboard.PosDashboard"
PosDashboard.components = { ChartTemplate, KpiTemplate }

registry.category("actions").add("weha_smart_pos_aeon_dashboard.pos_dashboard", PosDashboard)