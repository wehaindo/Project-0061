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
            // KPI Data
            revenue: {
                current: 0,
                previous: 0,
                percentage: 0,
                average_order: 0
            },
            orders: {
                current: 0,
                previous: 0,
                percentage: 0
            },
            customers: {
                current: 0,
                previous: 0,
                percentage: 0,
                members: 0,
                member_percentage: 0
            },
            products: {
                total_items_sold: 0,
                unique_products: 0,
                avg_items_per_order: 0
            },
            
            // Chart Data
            dailyChartData: {
                labels: [],
                datasets: [{
                    label: 'Daily Sales',
                    data: [],
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    fill: true
                }]
            },
            storeChartData: {
                labels: [],
                datasets: []
            },
            hourlyChartData: {
                labels: ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', 
                         '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23'],
                datasets: [{
                    label: 'Sales by Hour',
                    data: [],
                    backgroundColor: 'rgba(255, 159, 64, 0.2)',
                    borderColor: 'rgba(255, 159, 64, 1)',
                    borderWidth: 2
                }]
            },
            paymentChartData: {
                labels: [],
                datasets: [{
                    label: 'Payment Methods',
                    data: [],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(153, 102, 255, 0.8)',
                        'rgba(255, 159, 64, 0.8)'
                    ]
                }]
            },
            
            // Tables Data
            topProducts: [],
            topCategories: [],
            cashierPerformance: [],
            storeComparison: [],
            
            // Filters
            period: 7,
            stores: [],
            store: 0,
            
            // Loading state
            isLoading: true
        })
        
        this.orm = useService("orm")
        this.actionService = useService("action")
        
        onWillStart(async () => {
            await this.getStores()
            await this.loadDashboardData()
        })
    }

    async onChangePeriod(){        
        await this.loadDashboardData()
    }

    async onChangeStore(){
        await this.loadDashboardData()
    }
    
    async getStores(){
        try {
            const stores = await this.orm.searchRead("res.branch", [], ["name"])
            this.state.stores = stores
        } catch (error) {
            console.error("Error fetching stores:", error)
        }
    }

    async loadDashboardData(){
        this.state.isLoading = true
        
        try {
            const storeId = this.state.store ? parseInt(this.state.store) : false
            
            // Get comprehensive dashboard data
            const data = await this.orm.call(
                "pos.dashboard",
                "get_dashboard_data",
                [],
                {
                    period: parseInt(this.state.period),
                    store_id: storeId
                }
            )
            
            // Update KPIs
            this.state.revenue = data.revenue
            this.state.orders = data.orders
            this.state.customers = data.customers
            this.state.products = data.products
            
            // Update tables
            this.state.topProducts = data.top_products
            this.state.topCategories = data.top_categories
            this.state.cashierPerformance = data.cashiers
            this.state.storeComparison = data.stores
            
            // Update charts
            await this.loadChartData()
            
        } catch (error) {
            console.error("Error loading dashboard data:", error)
        } finally {
            this.state.isLoading = false
        }
    }
    
    async loadChartData(){
        try {
            const storeId = this.state.store ? parseInt(this.state.store) : false
            
            // Get daily chart data
            const dailyData = await this.orm.call(
                "pos.dashboard",
                "get_daily_chart_data",
                [],
                {
                    period: parseInt(this.state.period),
                    store_id: storeId
                }
            )
            
            this.state.dailyChartData.labels = dailyData.labels
            this.state.dailyChartData.datasets[0].data = dailyData.data
            
            // Get store comparison chart data (only if all stores selected)
            if (!storeId) {
                const storeData = await this.orm.call(
                    "pos.dashboard",
                    "get_store_chart_data",
                    [],
                    {
                        period: parseInt(this.state.period)
                    }
                )
                
                this.state.storeChartData.labels = storeData.labels
                this.state.storeChartData.datasets = storeData.datasets
            }
            
        } catch (error) {
            console.error("Error loading chart data:", error)
        }
    }
    
    formatCurrency(value){
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0
        }).format(value)
    }
    
    formatNumber(value){
        return new Intl.NumberFormat('id-ID').format(value)
    }
}

PosDashboard.template = "weha_smart_pos_aeon_dashboard.PosDashboard"
PosDashboard.components = { ChartTemplate, KpiTemplate }

registry.category("actions").add("weha_smart_pos_aeon_dashboard.pos_dashboard", PosDashboard)