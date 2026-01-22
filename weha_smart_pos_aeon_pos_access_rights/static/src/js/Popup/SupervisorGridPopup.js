odoo.define('weha_smart_pos_aeon_pos_access_rights.SupervisorGridPopup', function(require) {
    'use strict';

    const { useState, onMounted } = owl;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class SupervisorGridPopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            this.state = useState({
                searchQuery: '',
                frequentSupervisorIds: [],
                activeTab: 'frequent', // Default to frequent tab
            });

            onMounted(() => {
                this.loadFrequentSupervisors();
                // If no frequent supervisors, default to all supervisors tab
                if (this.state.frequentSupervisorIds.length === 0) {
                    this.state.activeTab = 'all';
                }
            });
        }

        loadFrequentSupervisors() {
            try {
                const stored = localStorage.getItem('frequentSupervisors');
                if (stored) {
                    this.state.frequentSupervisorIds = JSON.parse(stored);
                }
            } catch (e) {
                console.error('Error loading frequent supervisors:', e);
                this.state.frequentSupervisorIds = [];
            }
        }

        saveFrequentSupervisor(employeeId) {
            try {
                let frequentIds = [...this.state.frequentSupervisorIds];
                
                // Remove if already exists
                frequentIds = frequentIds.filter(id => id !== employeeId);
                
                // Add to beginning
                frequentIds.unshift(employeeId);
                
                // Keep only top 6 frequent supervisors
                frequentIds = frequentIds.slice(0, 6);
                
                this.state.frequentSupervisorIds = frequentIds;
                localStorage.setItem('frequentSupervisors', JSON.stringify(frequentIds));
            } catch (e) {
                console.error('Error saving frequent supervisor:', e);
            }
        }

        get employees() {
            return this.props.employees || [];
        }

        get frequentSupervisors() {
            return this.state.frequentSupervisorIds
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
            this.confirm();
        }

        getPayload() {
            const selected = this.props.employees.find( (item) => this.state.selectedId === item.id);
            return selected && selected.item;
        }
    }

    SupervisorGridPopup.template = 'SupervisorGridPopup';
    SupervisorGridPopup.defaultProps = {
        cancelText: 'Cancel',
    };

    Registries.Component.add(SupervisorGridPopup);

    return SupervisorGridPopup;
});