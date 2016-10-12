/*jslint browser: true*/
/*global $, jQuery*/

/**
 * JQuery Datagrid plugin. Enables AJAX queries, converts JSON to table
 * rows, keeps track of row selection and pagination.
 */
;(function ($) {
    // Enable strict mode for the plugin.
    'use strict';

    // The default options for the plugin.
    var defaults = {
        // The base URL to use for JSON requests.
        url: '',

        // The number of elements to retrieve for a JSON request.
        length: 10,

        // If populate is true, fetch is called after initialing the datagrid.
        populate: true,

        // The function used to generate an Object to pass as the query data
        // when making a JSON request.
        data_callback: function () { return {} },

        // The function to callback after fetching data for the table.
        fetch_callback: function () {},

        // A list of strings representing keys to use when generating the
        // columns and rows of the table.
        format: []
    };

    /**
     * The Datagrid constructor.
     * @param element to initialize on.
     * @param options to override the defaults with.
     * @constructor
     * @return {Object} the public api for the Datagrid.
     */
    function Datagrid (element, options) {
        // Remember the current context.
        var self = this;

        // Remember the DOM element that the Datagrid is bound to
        self.table = $(element);

        // Find the body of the table.
        self.body = self.table.find('tbody');

        // Extend the default options with the use defined options.
        self.options = $.extend({}, defaults, options);

        // Store initial values for private variables
        self.row = -1;
        self.row_element = undefined;
        self.page = 0;
        self.pages = 1;
        self.total = 0;

        // Add a click handler for row selection to the body of the table
        self.body.on('click', 'tr', function () {
            // Get the clicked row
            var element = $(this);

            if (element.hasClass('selected')) {
                // If the row was already selected, deselect it.
                element.removeClass('selected');
                self.row = -1;
                self.row_element = undefined;
            } else {
                // Deselect any row that was previously selected, and mark the
                // current row as selected while storing its id.
                self.table.find('tr.selected').removeClass('selected');
                self.row = element.data('id');
                element.addClass('selected');

                // Store the row element
                (function (element) {
                    self.row_element = element;
                })(element);
            }
        });

        // Append a pagination div after the table, and remember it.
        var $div = $('<div class="text-right"></div>').insertAfter(self.table);
        self.pageInfo = $('<div class="page-info"></div>').appendTo($div);
        self.pageList = $(
            '<ul class="pagination"></ul>').appendTo($div);

        // Render the pagination.
        _render_pagination(self.options['length']);

        // Fetch initial rows if the datagrid needs to be populated.
        if (self.options['populate'] == true) {
            fetch();
        }

        /**
         * Clears the row selection.
         */
        function clear_row() {
            self.table.find('tr.selected').removeClass('selected');
            self.row = -1;
        }

        /**
         * @returns {number} the selected row.
         */
        function get_row() {
            return self.row;
        }

        /**
         * @returns {Object} the selected row's element.
         */
        function get_row_element() {
            return self.row_element;
        }

        /**
         * @returns {Object} the table the datagrid is using.
         */
        function get_table() {
            return self.table;
        }

        /**
         * Fetches JSON data from the server using the Datagrid options, and
         * renders the table.
         */
        function fetch () {
            // Extend the data for the JSON request with the data generated
            // by the user function
            var data = $.extend({
                length: self.options['length'],
                offset: self.page * self.options['length']
            }, self.options['data_callback']());

            // Fetch the JSON from the server.
            $.getJSON(
                self.options['url'], data, function (r) {
                    render_response(r, self.options['length']);

                    // Call the user callback for receiving data from the
                    // table.
                    self.options['fetch_callback']();
                });
        }

        /**
         * Renders response data from the server.
         * @param {Object} r is the response object to render. Contains a
         *                   'data' field for the data to render, and a
         *                   'total' field for the total number of rows in data.
         * @param {number} length is the number of rows to display on the page.
         */
        function render_response(r, length) {
            // Reset the active row.
            self.row = -1;

            // Store total/filtered row amounts.
            self.total = r['total'];

            // Calculate the total number of pages, with a minimum of
            // 1 page.
            self.pages = Math.max(Math.ceil(self.total / length), 1);

            // Render table rows.
            _render_rows(r['data']);

            // Render the pagination.
            _render_pagination(length);
        }

        /**
         * Renders table rows.
         * @param {Object[]} data is the array of Objects to render using the
         *                   options for the Datagrid.
         * @private
         */
        function _render_rows(data) {
            // Empty existing table rows.
            self.body.children().remove();

            // Iterate over elements in the data of the JSON, add them
            // as table rows.
            $.each(data, function (i, row_data) {
                // Iterate over items in the display to generate the
                // columns.
                var cols = [];
                $.each(self.options['format'], function (j, col_key) {
                    cols.push("<td>" + row_data[col_key] + "</td>");
                });

                // Generate the row from the column.
                var $row = $("<tr>" + cols.join("") + "</tr>");

                // Store the row id in the row.
                $row.data('id', row_data['id']);

                // Store all the data on the row.
                $row.data('json', row_data);

                // Append the row to the table body.
                self.body.append($row);
            });
        }

        /**
         * Builds a page control list item for pagination.
         * @param i the index of the page.
         * @param label the label of the page control.
         * @private
         */
        function _build_page_li(i, label) {
            // Create the list element.
            var $li = $('<li><a href="#">' + label + '</a></li>');

            if (i <= -1 || i >= self.pages) {
                // This is either the previous or next button, and the current
                // page is on the boundary. Mark the control as disabled.
                $li.addClass('disabled');
            } else if (i == self.page) {
                // This is a regular page control, and the active one.
                $li.addClass('active');
            }else {
                // This page control needs a click handler, since it's neither
                // active or disabled.
                $li.click(function (evt) {
                    // Prevent the default event.
                    evt.preventDefault();

                    // Set the page to the current index.
                    self.page = i;

                    // Refresh the table.
                    fetch();
                });
            }

            // Append the page to the page list.
            self.pageList.append($li);
        }

        /**
         * Renders the pagination controls for the table.
         * @param {number} length is the number of results to allow on the page.
         * @private
         */
        function _render_pagination(length) {
            // Calculate page information.
            var row_start = Math.min(self.page * length + 1,
                self.total);
            var row_end = Math.min(row_start + length - 1,
                self.total);

            // Set the page info text.
            self.pageInfo.text(row_start + ' to ' + row_end + ' of ' +
                self.total + ' rows.');

            // Remove all elements currently in the page list.
            self.pageList.children().remove();

            // Add the previous button.
            _build_page_li(self.page - 1, '&laquo;');

            // Add the regular page controls, up to a max of 5.
            for (var i = 0; i < Math.min(self.pages, 5); ++i) {
                // Keep the current page in the center past 3.
                if (self.page >= 2) {
                    _build_page_li(i + self.page - 2, i + self.page - 1)
                } else {
                    _build_page_li(i, i + 1);
                }
            }

            // Add the next button.
            _build_page_li(self.page + 1, '&raquo;');
        }

        // Return the public API for the Datagrid.
        var API = {};
        API.clear_row = clear_row;
        API.fetch = fetch;
        API.get_row = get_row;
        API.get_row_element = get_row_element;
        API.get_table = get_table;
        API.render_response = render_response;
        return API;
    }

    /**
     * Initializes the Datagrid on the selected element, with the options
     * given.
     * @param options are the overrides for the default settings.
     * @returns {*} the selectors given.
     * @constructor
     */
    $.fn.Datagrid = function(options) {
        return $(this).each(function () {
            // Prevent the Datagrid from being initialized multiple times.
            if (!$(this).data('Datagrid')) {
                $(this).data('Datagrid', new Datagrid(this, options));
            }
        });
    };
})(jQuery);