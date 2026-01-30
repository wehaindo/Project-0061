/** @odoo-module */

const { Component } = owl

export class KpiTemplate extends Component {
    
    getPercentageClass(){
        return this.props.percentage >= 0 ? 'text-success' : 'text-danger'
    }
    
    getArrowIcon(){
        return this.props.percentage >= 0 ? 'fa-arrow-up' : 'fa-arrow-down'
    }
    
    formatValue(value){
        if(this.props.isCurrency){
            return new Intl.NumberFormat('id-ID', {
                style: 'currency',
                currency: 'IDR',
                minimumFractionDigits: 0
            }).format(value)
        }
        return new Intl.NumberFormat('id-ID').format(value)
    }
}

KpiTemplate.template = "weha_smart_pos_aeon_dashboard.KpiTemplate"