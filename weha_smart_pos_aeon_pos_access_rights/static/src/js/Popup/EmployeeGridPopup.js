odoo.define('weha_smart_pos_aeon_pos_access_rights.EmployeeGridPopup', function(require) {
    'use strict';

    const { useState, onMounted } = owl;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class EmployeeGridPopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            this.state = useState({
                searchQuery: '',
                frequentCashierIds: [],
                activeTab: 'frequent', // Default to frequent tab
            });

            onMounted(() => {
                this.loadFrequentCashiers();
                // If no frequent cashiers, default to all employees tab
                if (this.state.frequentCashierIds.length === 0) {
                    this.state.activeTab = 'all';
                }
            });
        }

        loadFrequentCashiers() {
            try {
                const stored = localStorage.getItem('frequentCashiers');
                if (stored) {
                    this.state.frequentCashierIds = JSON.parse(stored);
                }
            } catch (e) {
                console.error('Error loading frequent cashiers:', e);
                this.state.frequentCashierIds = [];
            }
        }

        saveFrequentCashier(employeeId) {
            try {
                let frequentIds = [...this.state.frequentCashierIds];
                
                // Remove if already exists
                frequentIds = frequentIds.filter(id => id !== employeeId);
                
                // Add to beginning
                frequentIds.unshift(employeeId);
                
                // Keep only top 6 frequent cashiers
                frequentIds = frequentIds.slice(0, 6);
                
                this.state.frequentCashierIds = frequentIds;
                localStorage.setItem('frequentCashiers', JSON.stringify(frequentIds));
            } catch (e) {
                console.error('Error saving frequent cashier:', e);
            }
        }

        get employees() {
            return this.props.employees || [];
        }

        get frequentCashiers() {
            return this.state.frequentCashierIds
                .map(id => this.employees.find(emp => emp.id === id))
                .filter(emp => emp !== undefined);
        }

        get filteredEmployees() {
            const query = this.state.searchQuery.toLowerCase().trim();
            if (!query) {
                return this.employees;
            }
            return this.employees.filter(emp => 
                emp.label.toLowerCase().includes(query)
            );
        }

        onSearchInput(ev) {
            this.state.searchQuery = ev.target.value;
        }

        selectItem(itemId) {
            this.state.selectedId = itemId;
            this.saveFrequentCashier(itemId);
            this.confirm();
        }        

        getPayload() {
            const selected = this.props.employees.find( (item) => this.state.selectedId === item.id);
            return selected && selected.item;
        }

    }

    EmployeeGridPopup.template = 'EmployeeGridPopup';
    EmployeeGridPopup.defaultProps = {
        cancelText: 'Cancel',
    };

    Registries.Component.add(EmployeeGridPopup);

    return EmployeeGridPopup;
});