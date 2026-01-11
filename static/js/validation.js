
/*jshint esversion: 6 */

/**
 * Form Validation & UX Enhancements
 * Quiporder - Equipment Management System
 */
document.addEventListener('DOMContentLoaded', function() {
    
    // =========================================================================
    // FORM VALIDATION FEEDBACK
    // =========================================================================
    
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                this.classList.remove('is-invalid');
            });
        });
    });
    
    /**
     * Validate a single form field
     * @param {HTMLElement} field - The input element to validate
     */
    function validateField(field) {
        if (!field.required) {
            return;
        }
        
        if (field.required && !field.value.trim()) {
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
        
        if (field.type === 'number' && field.min) {
            const value = parseFloat(field.value);
            if (value < parseFloat(field.min)) {
                field.classList.add('is-invalid');
            }
        }
    }
    
    // =========================================================================
    // QUANTITY INPUT - Prevent negative/zero
    // =========================================================================
    
    const quantityInputs = document.querySelectorAll('input[name="quantity"]');
    
    quantityInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            const value = parseInt(this.value);
            if (value < 1 || isNaN(value)) {
                this.value = 1;
                this.classList.add('is-invalid');
            }
        });
    });
});