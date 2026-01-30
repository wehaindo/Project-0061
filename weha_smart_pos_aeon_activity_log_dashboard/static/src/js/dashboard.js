/** @odoo-module **/

import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

const { DateTime } = luxon;

class PosActivityLogDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.charts = {}; // Store chart instances for cleanup
        
        this.state = useState({
            loading: true,
            stats: {
                total: 0,
                today: 0,
                this_week: 0,
                this_month: 0,
            },
            dashboardData: null,
            dateFrom: DateTime.now().minus({ days: 30 }).toFormat('yyyy-MM-dd'),
            dateTo: DateTime.now().toFormat('yyyy-MM-dd'),
            selectedPosConfigs: [],
            selectedUsers: [],
        });
        
        onWillStart(async () => {
            // Load Chart.js library
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js");
            await this.loadData();
        });
        
        onMounted(() => {
            // Render charts after component is mounted
            if (this.state.dashboardData) {
                this.renderCharts();
            }
        });
    }
    
    async loadData() {
        this.state.loading = true;
        try {
            // Load statistics
            const stats = await this.rpc('/pos_activity_log/stats', {});
            this.state.stats = stats;
            
            // Load dashboard data
            const dashboardData = await this.rpc('/pos_activity_log/dashboard_data', {
                date_from: this.state.dateFrom,
                date_to: this.state.dateTo,
                pos_config_ids: this.state.selectedPosConfigs,
                user_ids: this.state.selectedUsers,
            });
            this.state.dashboardData = dashboardData;
            
            // Render charts after data is loaded (only if component is mounted)
            setTimeout(() => {
                if (document.getElementById('activityTypeChart')) {
                    this.renderCharts();
                }
            }, 100);
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        } finally {
            this.state.loading = false;
        }
    }
    
    renderCharts() {
        // Destroy existing charts to prevent duplicates
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
        
        // Render Activity Type Pie Chart
        if (this.state.dashboardData && this.state.dashboardData.activity_by_type.length > 0) {
            this.renderPieChart(
                'activityTypeChart',
                this.state.dashboardData.activity_by_type.map(item => item.name),
                this.state.dashboardData.activity_by_type.map(item => item.count)
            );
        }
        
        // Render Top Users Bar Chart
        if (this.state.dashboardData && this.state.dashboardData.top_users.length > 0) {
            this.renderBarChart(
                'topUsersChart',
                this.state.dashboardData.top_users.map(item => item.name),
                this.state.dashboardData.top_users.map(item => item.count),
                'Top Users by Activity Count'
            );
        }
        
        // Render Timeline Line Chart
        if (this.state.dashboardData && this.state.dashboardData.timeline.length > 0) {
            this.renderLineChart(
                'timelineChart',
                this.state.dashboardData.timeline.map(item => item.date),
                this.state.dashboardData.timeline.map(item => item.count)
            );
        }
    }
    
    renderPieChart(canvasId, labels, data) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        this.charts[canvasId] = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                        '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
                    ],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                    },
                    title: {
                        display: true,
                        text: 'Activity Distribution by Type'
                    }
                }
            }
        });
    }
    
    renderBarChart(canvasId, labels, data, title) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Activities',
                    data: data,
                    backgroundColor: '#36A2EB',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,
                    },
                    title: {
                        display: true,
                        text: title
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    renderLineChart(canvasId, labels, data) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Daily Activities',
                    data: data,
                    borderColor: '#36A2EB',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    tension: 0.1,
                    fill: true,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,
                    },
                    title: {
                        display: true,
                        text: 'Activity Timeline'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    async onRefresh() {
        await this.loadData();
    }
    
    async onExport() {
        try {
            const data = await this.rpc('/pos_activity_log/export', {
                date_from: this.state.dateFrom,
                date_to: this.state.dateTo,
                pos_config_ids: this.state.selectedPosConfigs,
                user_ids: this.state.selectedUsers,
            });
            
            // Convert to CSV
            if (data && data.length > 0) {
                const headers = Object.keys(data[0]);
                const csv = [
                    headers.join(','),
                    ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
                ].join('\n');
                
                // Download CSV file
                const blob = new Blob([csv], { type: 'text/csv' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `pos_activity_logs_${DateTime.now().toFormat('yyyy-MM-dd')}.csv`;
                a.click();
                window.URL.revokeObjectURL(url);
            }
        } catch (error) {
            console.error('Error exporting data:', error);
        }
    }
    
    onViewAllLogs() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'pos.activity.log',
            views: [[false, 'list'], [false, 'form']],
            context: {
                search_default_today: 1,
            },
        });
    }
}

PosActivityLogDashboard.template = "weha_smart_pos_aeon_activity_log_dashboard.Dashboard";

registry.category("actions").add("pos_activity_log_dashboard", PosActivityLogDashboard);

export default PosActivityLogDashboard;
