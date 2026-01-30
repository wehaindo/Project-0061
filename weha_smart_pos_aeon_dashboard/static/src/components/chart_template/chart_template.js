/** @odoo-module */

import { registry } from "@web/core/registry"
import { loadJS } from "@web/core/assets"
const { Component, onWillStart, useRef, onMounted, onWillUpdateProps } = owl


export class ChartTemplate extends Component {
    setup(){
        this.chartRef = useRef("chart")
        
        onWillStart(async () => {
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js")
        })
        
        onMounted(() => this.renderChart())
        
        onWillUpdateProps(() => {
            if (this.chart) {
                this.updateChart()
            }
        })
    }

    renderChart(){
        if (!this.chartRef.el) return
        
        const config = {
            type: this.props.type,
            data: this.props.data,
            options: {
                maintainAspectRatio: false,
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: this.props.title,
                        position: 'top',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += new Intl.NumberFormat('id-ID', {
                                        style: 'currency',
                                        currency: 'IDR',
                                        minimumFractionDigits: 0
                                    }).format(context.parsed.y);
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: this.getScales()
            },
        }
        
        this.chart = new Chart(this.chartRef.el, config)
    }
    
    getScales(){
        // Don't use scales for pie/doughnut charts
        if (this.props.type === 'pie' || this.props.type === 'doughnut') {
            return {}
        }
        
        return {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return new Intl.NumberFormat('id-ID', {
                            style: 'currency',
                            currency: 'IDR',
                            minimumFractionDigits: 0,
                            notation: 'compact',
                            compactDisplay: 'short'
                        }).format(value);
                    }
                }
            }
        }
    }

    updateChart(){
        if (!this.chart) return
        
        this.chart.data = this.props.data
        this.chart.update('none') // 'none' for no animation on update
    }
}


ChartTemplate.template = "weha_smart_pos_aeon_dashboard.ChartTemplate"