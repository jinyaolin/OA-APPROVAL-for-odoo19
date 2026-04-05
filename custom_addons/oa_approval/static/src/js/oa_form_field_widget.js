odoo.define('oa_approval.DynamicSelectionWidget', function (require) {
    "use strict";

    var fieldRegistry = require('web.field_registry');
    var FieldChar = require('web.basic_fields').FieldChar;

    var DynamicSelectionWidget = FieldChar.extend({
        events: _.extend({}, FieldChar.prototype.events, {
            'change': '_onSelectionChange',
        }),

        _render: function () {
            this._super.apply(this, arguments);

            var fieldType = this._getFieldType();
            if (this.mode === 'edit' && fieldType === 'selection') {
                var options = this._getSelectionOptions();
                if (options.length > 0) {
                    this._replaceWithDropdown(options);
                }
            }
        },

        _getFieldType: function () {
            if (this.recordData.field_type !== undefined) {
                return this.recordData.field_type;
            }
            var fieldName = this.name;
            var match = fieldName.match(/^field_(\d+)_char$/);
            if (match) {
                var idx = match[1];
                var typeField = 'field_' + idx + '_type';
                return this.recordData[typeField] || '';
            }
            return '';
        },

        _getSelectionOptions: function () {
            var options = [];
            var availableOptions = this._getAvailableOptionsField();

            if (this.recordData[availableOptions]) {
                var optionString = this.recordData[availableOptions];
                options = optionString.split(',').map(function (opt) {
                    return opt.trim();
                }).filter(function (opt) {
                    return opt.length > 0;
                });
            }
            return options;
        },

        _getAvailableOptionsField: function () {
            if (this.recordData.available_options !== undefined) {
                return 'available_options';
            }
            var fieldName = this.name;
            var match = fieldName.match(/^field_(\d+)_char$/);
            if (match) {
                var idx = match[1];
                return 'field_' + idx + '_available_options';
            }
            return 'available_options';
        },

        _replaceWithDropdown: function (options) {
            var self = this;
            var currentValue = this.value || '';

            var $select = $('<select>', {
                class: 'o_input o_form_input',
            });

            $select.append($('<option>', {
                value: '',
                text: '請選擇...',
            }));

            options.forEach(function (option) {
                var $option = $('<option>', {
                    value: option,
                    text: option,
                });
                if (option === currentValue) {
                    $option.prop('selected', true);
                }
                $select.append($option);
            });

            this.$el.replaceWith($select);
            this.setElement($select);

            $select.on('change', function () {
                self._onSelectionChange($(this).val());
            });
        },

        _onSelectionChange: function (value) {
            this._setValue(value);
        },
    });

    fieldRegistry.add('dynamic_selection', DynamicSelectionWidget);

    return DynamicSelectionWidget;
});
