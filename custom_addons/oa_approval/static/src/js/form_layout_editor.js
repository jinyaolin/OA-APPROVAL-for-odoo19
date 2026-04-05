odoo.define('oa_approval.form_layout_editor', function (require) {
    "use strict";

    var core = require('web.core');
    var FormController = require('web.FormController');
    var fieldRegistry = require('web.field_registry');
    var FieldOne2Many = require('web.relational_fields').FieldOne2Many;

    var _t = core._t;

    /**
     * Visual Layout Editor Widget
     */
    var LayoutEditorWidget = FieldOne2Many.extend({
        className: 'o_form_field_one2many o_view_manager_content',

        /**
         * Render the layout editor interface
         */
        _render: function () {
            this._super.apply(this, arguments);
            if (this.mode === 'edit') {
                this._renderLayoutEditor();
            }
        },

        /**
         * Render the visual layout editor
         */
        _renderLayoutEditor: function () {
            var self = this;
            var $editor = $('<div>', {
                class: 'oa-layout-editor'
            });

            // Toolbar
            var $toolbar = $('<div>', {
                class: 'oa-layout-toolbar'
            }).append(
                $('<button>', {
                    class: 'btn btn-primary btn-sm',
                    text: _t('Auto Layout'),
                    click: function () { self._autoLayout(); }
                }),
                $('<button>', {
                    class: 'btn btn-secondary btn-sm',
                    text: _t('Reset Layout'),
                    click: function () { self._resetLayout(); }
                }),
                $('<button>', {
                    class: 'btn btn-info btn-sm',
                    text: _t('Preview'),
                    click: function () { self._previewLayout(); }
                }),
                $('<span>', {
                    class: 'ms-3 text-muted',
                    text: _t('Drag fields to reposition, use handles to resize')
                })
            );

            // Grid container
            var $grid = $('<div>', {
                class: 'oa-layout-grid'
            });

            // Render fields
            var fields = this.value.getData();
            this._renderFieldsInGrid($grid, fields);

            $editor.append($toolbar).append($grid);

            // Replace the default view with our custom editor
            this.$el.find('.o_one2many').replaceWith($editor);

            // Initialize drag and drop
            this._initDragAndDrop($grid);
        },

        /**
         * Render fields in the grid based on their layout properties
         */
        _renderFieldsInGrid: function ($grid, fields) {
            var self = this;

            // Sort fields by row and column
            fields.sort(function (a, b) {
                if (a.data.layout_row !== b.data.layout_row) {
                    return a.data.layout_row - b.data.layout_row;
                }
                return a.data.layout_col - b.data.layout_col;
            });

            // Group fields by row
            var rowGroups = {};
            fields.forEach(function (field) {
                var row = field.data.layout_row || 1;
                if (!rowGroups[row]) {
                    rowGroups[row] = [];
                }
                rowGroups[row].push(field);
            });

            // Render each row
            Object.keys(rowGroups).sort().forEach(function (rowNum) {
                var $row = $('<div>', {
                    class: 'oa-layout-row',
                    style: 'display: flex; flex-wrap: wrap; margin-bottom: 10px;'
                });

                rowGroups[rowNum].forEach(function (field) {
                    var width = field.data.layout_width || '6';
                    var $field = self._renderFieldWidget(field, width);
                    $row.append($field);
                });

                $grid.append($row);
            });
        },

        /**
         * Render a single field widget
         */
        _renderFieldWidget: function (field, width) {
            var $field = $('<div>', {
                class: 'oa-layout-field col-' + width,
                'data-field-id': field.data.id,
                draggable: true
            });

            var $label = $('<div>', {
                class: 'field-label',
                text: field.data.label
            });

            var $info = $('<div>', {
                class: 'field-info',
                text: field.data.name + ' (' + field.data.field_type + ')'
            });

            var $actions = $('<div>', {
                class: 'field-actions'
            }).append(
                $('<button>', {
                    class: 'btn btn-sm btn-primary',
                    text: _t('Edit'),
                    click: function (e) {
                        e.stopPropagation();
                        // Open edit dialog
                    }
                })
            );

            $field.append($label).append($info).append($actions);

            // Add drag events
            this._addDragEvents($field);

            return $field;
        },

        /**
         * Add drag events to field widget
         */
        _addDragEvents: function ($field) {
            var self = this;

            $field.on('dragstart', function (e) {
                $(this).addClass('dragging');
                e.originalEvent.dataTransfer.effectAllowed = 'move';
                e.originalEvent.dataTransfer.setData('text/html', $(this).html());
                e.originalEvent.dataTransfer.setData('field-id', $(this).data('field-id'));
            });

            $field.on('dragend', function () {
                $(this).removeClass('dragging');
                $('.oa-layout-field').removeClass('drag-over');
            });

            $field.on('dragover', function (e) {
                e.preventDefault();
                e.originalEvent.dataTransfer.dropEffect = 'move';
                $(this).addClass('drag-over');
            });

            $field.on('dragleave', function () {
                $(this).removeClass('drag-over');
            });

            $field.on('drop', function (e) {
                e.preventDefault();
                var draggedFieldId = e.originalEvent.dataTransfer.getData('field-id');
                var targetFieldId = $(this).data('field-id');

                if (draggedFieldId !== targetFieldId) {
                    self._swapFields(draggedFieldId, targetFieldId);
                }

                $(this).removeClass('drag-over');
            });
        },

        /**
         * Initialize drag and drop functionality
         */
        _initDragAndDrop: function ($grid) {
            var self = this;
            // Already handled in _addDragEvents
        },

        /**
         * Swap two fields positions
         */
        _swapFields: function (fieldId1, fieldId2) {
            var self = this;
            var fields = this.value.getData();

            var field1 = fields.find(function (f) { return f.data.id === fieldId1; });
            var field2 = fields.find(function (f) { return f.data.id === fieldId2; });

            if (field1 && field2) {
                // Swap positions
                var tempRow = field1.data.layout_row;
                var tempCol = field1.data.layout_col;
                field1.data.layout_row = field2.data.layout_row;
                field1.data.layout_col = field2.data.layout_col;
                field2.data.layout_row = tempRow;
                field2.data.layout_col = tempCol;

                // Re-render
                this._renderLayoutEditor();

                // Save changes
                this._saveFieldLayout(field1);
                this._saveFieldLayout(field2);
            }
        },

        /**
         * Auto-layout fields in optimal positions
         */
        _autoLayout: function () {
            var fields = this.value.getData();
            var currentRow = 1;
            var currentCol = 1;

            fields.forEach(function (field) {
                field.data.layout_row = currentRow;
                field.data.layout_col = currentCol;

                currentCol += parseInt(field.data.layout_width || 6);
                if (currentCol > 12) {
                    currentCol = 1;
                    currentRow++;
                }
            });

            this._renderLayoutEditor();
            this._saveAllLayouts();
        },

        /**
         * Reset layout to default
         */
        _resetLayout: function () {
            var fields = this.value.getData();
            fields.forEach(function (field, index) {
                field.data.layout_row = Math.floor(index / 2) + 1;
                field.data.layout_col = (index % 2) * 6 + 1;
                field.data.layout_width = '6';
            });

            this._renderLayoutEditor();
            this._saveAllLayouts();
        },

        /**
         * Preview the layout
         */
        _previewLayout: function () {
            alert(_t('Preview mode - this would show how the form will appear to end users'));
        },

        /**
         * Save field layout
         */
        _saveFieldLayout: function (field) {
            this._rpc({
                model: 'oa.form.template.field',
                method: 'write',
                args: [[field.data.id], {
                    layout_row: field.data.layout_row,
                    layout_col: field.data.layout_col,
                    layout_width: field.data.layout_width
                }]
            });
        },

        /**
         * Save all field layouts
         */
        _saveAllLayouts: function () {
            var self = this;
            var fields = this.value.getData();
            var layouts = {};

            fields.forEach(function (field) {
                layouts[field.data.id] = {
                    layout_row: field.data.layout_row,
                    layout_col: field.data.layout_col,
                    layout_width: field.data.layout_width
                };
            });

            this._rpc({
                model: 'oa.form.template.field',
                method: 'save_layouts',
                args: [layouts]
            });
        }
    });

    // Register the widget
    fieldRegistry.add('layout_editor', LayoutEditorWidget);

    return LayoutEditorWidget;
});
