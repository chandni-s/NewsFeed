/*jslint browser: true*/
/*global $, jQuery, alert*/

/**
 * Switches tabs.
 * @param element is the tab to switch to.
 */
var tabSwitch = function(element) {
    // Remove active from all the tabs.
    $('a[data-toggle="tab"]').parent().removeClass('active');

    // Show the tab.
    element.tab('show');
};


/**
 * Deletes a row with the id given from the database.
 * @param id is the row to delete
 * @param url is the server url to make the request on
 * @param callback is the function that is called when the row was deleted
 */
var deleteRow = function(id, url, callback) {
    // Try deleting the row from the server.
    $.getJSON(url, {'id': id}, function (r) {
        if (r["result"] == false) {
            // Couldn't delete the row.
            toastr.error(r["msg"]);
        } else {
            // Deleted the row, call the callback function.
            callback();
            toastr.success(r["msg"]);
        }
    })
};

/**
 * Clears form input.
 * @param {Object} input are the fields to clear.
 */
var formClear = function(input) {
    $.each(input, function (key, value) {
        value.val('');
    });

    // Need to clear datepicker values separately.
    $('.datepicker').val('').datepicker('update')
};

/**
 * Fills a form with data from the database object associated with the
 * given id. If the form was filled, the callback function is called.
 * @param {number} id is the database object to fill the field values with.
 * @param {Object} input is the list of keys and values to fill.
 * @param {string} url is the server url to make the request on.
 * @param {Function} callback is the function that is called when the
 *                   form was filled successfully.
 */
var formFill = function(id, input, url, callback) {
    // Clear existing values in the form.
    formClear(input);

    // Try getting the data from the server.
    $.getJSON(url, {'id': id}, function (r) {
        if (r["result"] == false) {
            // The id wasn't valid.
            toastr.error(r["msg"]);
        } else {
            // Received JSON data from the server, fill the fields then
            // call the callback function.
            $.each(input, function (key, value) {
                value.val(r['data'][key]);
            });
            callback();
        }
    });
};

/**
 * Sends field date to the server. If the data was saved successfully, the
 * callback function is called.
 * @param {Object} fields is the list of keys and values for the fields.
 * @param {string} url is the server to make the request on.
 * @param {Function} callback is the function that is called when the data
 *                   was saved successfully.
 */
var saveFields = function(fields, url, callback) {
    // Send the modification request to the server.
    $.getJSON(url, fields, function (r) {
        if (r['result']) {
            // The data was modified successfully, call the callback function.
            callback();
            toastr.success(r["msg"]);
        } else {
            // The request wasn't valid.
            toastr.error(r["msg"]);
        }
    });
};

/**
 * Sends form data to the server. If the data was saved successfully, the
 * callback function is called.
 * @param {number} id is the id of the database object to target for the save.
 * @param {Object} input is the list of keys and values for the input fields.
 * @param {string} url is the server to make the request on.
 * @param {Function} callback is the function that is called when the data
 *                   was saved successfully.
 */
var formSave = function(id, input, url, callback) {
    // Generate the JSON data to send from the input fields.
    var data = {};
    $.each(input, function(key, value) {
        data[key] = value.val();
    });

    // Extend the data with the given id.
    data = $.extend({'id': id}, data);

    // Send the modification request to the server.
    saveFields(data, url, callback);
};

/**
 * Returns the string of the selected item in a select control.
 * @param {Object} select is the HTML select element that uses selectize.
 * @returns {string}
 */
var selected_item = function(select) {
    var instance = select[0].selectize;
    return instance.getValue();
};

/**
 * Returns the string of all selected items in a select control.
 * @param {Object} select is the HTML select element that uses selectize.
 * @returns {string}
 */
var selected_items = function(select) {
    var instance = select[0].selectize;
    return instance.getValue().join(" ");
};

/*
 * Executes as the page finishes loading. Sets up interaction between the
 * UI and the backend.
 */
$(document).ready(function () {
    // Toastr options.
    toastr.options = {
        "closeButton": true,
        "debug": false,
        "positionClass": "toast-top-right",
        "onclick": null,
        "showDuration": "300",
        "hideDuration": "300",
        "timeOut": "3000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    };

    // Enable tabbed navigation.
    $('a[data-toggle="tab"]').click(function () {
        tabSwitch($(this));
    });

    // The article input fields.
    var article_fields = {
        title:      $('#article-edit-title'),
        url:        $('#article-edit-url'),
        date:       $('#article-edit-date'),
        author:     $('#article-edit-author'),
        tags:       $('#article-edit-tags')
    };

    // The source input fields.
    var source_fields = {
        url:        $('#source-edit-url')
    };

    // Setup tabs.
    var tabs = {
        watchlist: $('a[href="#view-watchlist"]'),
        articles: $('a[href="#view-articles"]'),
        sources: $('a[href="#view-sources"]'),
        keywords: $('a[href="#view-keywords"]'),
        articleEdit: $('a[href="#view-article-edit"]'),
        articleRef: $('a[href="#view-article-ref"]'),
        sourceEdit: $('a[href="#view-source-edit"]'),
        refSelectArticle: $('a[href="#view-ref-select-article"]'),
        refSelectSource: $('a[href="#view-ref-select-source"]')
    };

    // Enable date picking.
    $('.datepicker').datepicker({
        autoclose: true,
        todayHighlight: true,
        format: "yyyy-mm-dd"
    });

    // Enable the watchlist table.
    var tableWatch = $('#table-watchlist').Datagrid({
        url: '/db/get_watches',
        format: ['url'],
        length: 8,

        // Add filtering.
        data_callback: function () {
            return {
                'url': '%' + $('#search-watchlist').val() + '%'
            };
        }
    }).data('Datagrid');

    // Enable the articles table.
    var tableArticles = $('#table-articles').Datagrid({
        url: '/db/get_articles',
        format: ['title', 'url', 'date', 'author', 'tags'],
        length: 5,

        // Add filtering.
        data_callback: function () {
            return {
                'query': '%' + $('#search-articles').val() + '%'
            };
        },

        // Callback function for receiving rows. Highlights the rows in the
        // the table that are being watched.
        fetch_callback: function () {
            // Replace the articles title with "Articles", in case the user was
            // on the results page after a crawl.
            $('#articles-title').text('Articles');
        }
    }).data('Datagrid');

    // Enable the sources table.
    var tableSources = $('#table-sources').Datagrid({
        url: '/db/get_sources',
        format: ['url'],
        length: 8,

        // Add filtering.
        data_callback: function () {
            return {
                'url': '%' + $('#search-sources').val() + '%'
            };
        }
    }).data('Datagrid');

    // Enable the reference table.
    var tableRef = $('#table-ref').Datagrid({
        url: '/db/get_references',
        format: ['reference', 'parent_title'],
        length: 5,

        // The reference table refers to a specific article, so pass the
        // currently selected articles row to make the query.
        data_callback: function () {
            return {
                'child_id': tableArticles.get_row()
            };
        }
    }).data('Datagrid');

    // Enable the reference article selection table.
    var tableRefArticle = $('#table-ref-article').Datagrid({
        url: '/db/get_articles',
        format: ['title', 'url', 'date', 'author', 'tags'],
        length: 5,

        // Add filtering.
        data_callback: function () {
            return {
                'query': '%' + $('#ref-search-article').val() + '%'
            }
        }

    }).data('Datagrid');

    // Enable the reference source selection table.
    var tableRefSource = $('#table-ref-source').Datagrid({
        url: '/db/get_sources',
        format: ['url'],
        length: 8,

        // Add filtering.
        data_callback: function () {
            return {
                'url': '%' + $('#ref-search-source').val() + '%'
            };
        }
    }).data('Datagrid');

    // Enable the keywords table.
    var tableKeywords = $('#table-keywords').Datagrid({
        url: '/db/get_keywords',
        format: ['name', 'source'],
        length: 8,

        // Add filtering.
        data_callback: function () {
            return {
                'name': '%' + $('#keyword-search').val() + '%'
            };
        }
    }).data('Datagrid');

    // Refresh watchlist while the input is being typed in the filter boxes.
    $('#search-watchlist').on('input', $.debounce(300, function () {
        tableWatch.fetch();
    }));

    // Enable the watchlist add URL button.
    $('#button-watch-add').click(function () {
        saveFields({
            'url': $('#watch-url').val()
        },
        '/db/add_watch',
        function () {
            // Update the table.
            tableWatch.fetch();
        });
    });

    // Enable the watch delete button.
    $('#button-watch-delete').click(function () {
        deleteRow(tableWatch.get_row(), '/db/delete_watch', function () {
            // Update the watch table after the delete.
            tableWatch.fetch();
        });
    });

    // Enable the watch update button.
    $('#button-watch-update').click(function () {
        // Display the modal telling the user to stand by.
        $.getJSON('/web/crawl_watches', {}, function (r) {
            // Results received, dismiss the modal.
            toastr.success(r['msg']);
        });
    });

    // Refresh articles while the input is being typed in the filter boxes.
    $('#search-articles').on('input', $.debounce(300, function () {
        tableArticles.fetch();
    }));

    // Enable the article add manually button.
    $('#button-article-add').click(function () {
        // Clear any currently selected row, and previous values in the article
        // form.
        tableArticles.clear_row();
        formClear(article_fields);
        tabSwitch(tabs['articleEdit']);
    });

    // Enable the article refresh button.
    $('#button-article-refresh').click(function () {
        // Update the table.
        tableArticles.fetch();
    });

    // Enable the article tab.
    tabs['articles'].click(function () {
        // Replace the articles title with "Articles", in case the user was
        // going back from the results page.
        $('#articles-title').text('Articles');

        // Refresh the articles table, and the sources table.
        tableArticles.fetch();
        tableSources.fetch();
    });

    // Enable the article add from URL button.
    $('#button-article-add-url').click(function () {
        // Display the modal telling the user to stand by.
        $('#modal-results-wait').modal('show');

        // Query the server for the results of adding the given URL.
        $.getJSON('/web/crawl_url', {
            'url': encodeURIComponent($('#article-add-url').val()),
            'recursive': $("#article-recursive").prop('checked')
        }, function (r) {
            // Results received, dismiss the modal.
            $('#modal-results-wait').modal('hide');

            if (r['result'] == true) {
                // Replace the articles title with "Results".
                $('#articles-title').text('Results');

                // Fill the articles table up with the given data. Make sure
                // there's enough room to display all results on the page:
                // the server won't be sending this response again!
                tableArticles.render_response(r, 100);

                // Switch back to the articles page, if the user moved away.
                tabSwitch(tabs['articles']);

                // Display the success message.
                toastr.success(r['msg']);
            } else {
                // Tell the user what went wrong.
                toastr.error(r['msg']);
            }
        });
    });

    // Enable the article edit button.
    $('#button-article-edit').click(function () {
        // Try getting the article's data from the server.
        var id = tableArticles.get_row();
        if (id != -1) {
            formFill(
                id,
                article_fields,
                "/db/get_article",
                function () {
                    tabSwitch(tabs['articleEdit']);
                });
        } else {
            toastr.error("No article selected.");
        }
    });

    // Enable the article delete button.
    $('#button-article-delete').click(function () {
        deleteRow(tableArticles.get_row(), '/db/delete_article', function () {
            // Update the article table after the delete.
            tableArticles.fetch();
        });
    });

    // Enable toggling the watch state for an article.
    $('#button-article-watch').click(function () {
        saveFields({
            'id': tableArticles.get_row()
        },
        '/db/toggle_watch',
        function () {
            // Refresh the table after toggling the watch.
            tableArticles.fetch();
        });
    });

    // Enable the article editor cancel button.
    $('.button-article-cancel').click(function () {
        tabSwitch(tabs['articles']);
    });

    // Enable the article editor save button.
    $('#button-article-save').click(function () {
        // Save the form
        formSave(
            tableArticles.get_row(),
            article_fields,
            '/db/modify_article',
            function () {
                // Both article and source tables need to be updated, since
                // sources can be added automatically.
                tableSources.fetch();
                tableArticles.fetch();
                tabSwitch(tabs['articles']);
            });
    });

    // Enable the article reference viewer button.
    $('#button-article-ref').click(function () {
        var id = tableArticles.get_row();
        if (id != -1) {
            // Update the reference table, to fetch for the current article id.
            tableRef.fetch();

            // Change the reference editor's title to match the URL of the given
            // article, to make it clearer what exactly is being edited.

            $('#ref-title').text('Reference Editor (' +
                tableArticles.get_row_element().data('json')["title"] + ')');

            tabSwitch(tabs['articleRef']);
        } else {
            toastr.error("No article selected.");
        }
    });

    // Refresh sources while the input is being typed in the filter box.
    $('#search-sources').on('input', $.debounce(300, function () {
        tableSources.fetch();
    }));

    // Enable the source add button.
    $('#button-source-add').click(function () {
        // Clear any currently selected row, and previous values in the source
        // form.
        tableSources.clear_row();
        formClear(source_fields);
        tabSwitch(tabs['sourceEdit']);
    });

    // Enable the source delete button.
    $('#button-source-delete').click(function () {
        deleteRow(tableSources.get_row(), '/db/delete_source', function () {
            // Deletes can cascade, so update the article table.
            tableArticles.fetch();
            tableSources.fetch();
        });
    });

    // Enable the source refresh button.
    $('#button-source-refresh').click(function () {
        // Update the table.
        tableSources.fetch();
    });

    // Enable the source keywords viewer button.
    $('#button-source-keywords').click(function () {
        var id = tableSources.get_row();
        if (id != -1) {
            // Update the keywords table, to fetch for the current source id.
            tableKeywords.fetch();

            // Change the keyword editor's title to match the URL of the given
            // source, to make it clearer what exactly is being edited.
            $('#keyword-title').text('Keyword Editor (' +
            tableSources.get_row_element().data('json')["url"] + ')');

            // Switch over to the keywords tab.
            tabSwitch(tabs['sourceKeywords']);
        } else {
            toastr.error("No source selected.");
        }
    });


    // Enable the source editor cancel button.
    $('#button-source-cancel').click(function () {
        tabSwitch(tabs['sources']);
    });

    // Enable the source editor save button.
    $('#button-source-save').click(function () {
        // Save the form
        formSave(
            tableSources.get_row(),
            source_fields,
            '/db/modify_source',
            function () {
                tableSources.fetch();
                tabSwitch(tabs['sources']);
            });
    });

    // Enable the reference delete button.
    $('#button-ref-delete').click(function () {
        deleteRow(tableRef.get_row(), '/db/delete_reference', function () {
            // Refresh the table now that the row is gone.
            tableRef.fetch();
        });
    });

    // Enable the reference article selection.
    $('#button-ref-add-article').click(function () {
        // Clear any previously selected row, and switch to the select screen.
        tableRefArticle.clear_row();
        tableRefArticle.fetch();
        tabSwitch(tabs['refSelectArticle']);
    });

    // Enable the reference source selection.
    $('#button-ref-add-source').click(function () {
        // Clear any previously selected row, and switch to the select screen.
        tableRefSource.clear_row();
        tableRefSource.fetch();
        tabSwitch(tabs['refSelectSource']);
    });

    // Enable the reference close button.
    $('#button-ref-close').click(function () {
       tabSwitch(tabs['articles']);
    });

    // Enable the cancel button for reference selection screens.
    $('.button-ref-select-cancel').click(function () {
        // Clear the search fields.
        $('#ref-search-article').val('');
        $('#ref-search-source').val('');

        tabSwitch(tabs['articleRef']);
    });

    // Enable adding an article as a reference.
    $('#button-ref-article-add').click(function () {
        // Add the reference between the two articles to the database.
        saveFields({
            'id': -1,
            'child_id': tableArticles.get_row(),
            'parent_id': tableRefArticle.get_row()
        },
        '/db/add_reference',
        function () {
            // Update the table and switch back to the tab.
            tableRef.fetch();
            tabSwitch(tabs['articleRef']);
        });
    });

    // Refresh article selection while the input is being typed in the filter.
    $('#ref-search-article').on('input', $.debounce(300, function () {
        tableRefArticle.fetch();
    }));

    // Enable adding a source as a reference.
    $('#button-ref-source-add').click(function () {
        // Add the reference between the article and the source to the
        // database.
        saveFields({
                'id': -1,
                'child_id': tableArticles.get_row(),
                'source_id': tableRefSource.get_row()
            },
            '/db/add_reference',
            function () {
                // Update the table and switch back to the tab.
                tableRef.fetch();
                tabSwitch(tabs['articleRef']);
            });
    });

    // Refresh source selection while the input is being typed in the filter.
    $('#ref-search-source').on('input', $.debounce(300, function () {
        tableRefSource.fetch();
    }));

    // Enable the keyword add button.
    $('#button-keyword-add').click(function () {
        // Add the keyword to the database for the selected row.
        saveFields({
            'source_id': selected_item($('#keyword-source')),
            'name': $('#keyword-name').val()
        },
        '/db/add_keyword',
        function () {
            // Update the keywords table.
            tableKeywords.fetch();
        });
    });

    // Enable the keyword delete button.
    $('#button-keyword-delete').click(function () {
        deleteRow(tableKeywords.get_row(), '/db/delete_keyword', function () {
            // Refresh the table now that the row is gone.
            tableKeywords.fetch();
        });
    });

    // Enable the keywords close button.
    $('#button-keyword-close').click(function () {
        // Clear the old keyword add field, and switch back to the sources list.
        $('#keyword-edit-name').val('');
        tabSwitch(tabs['sources']);
    });

    // 2D plot visualization.
    $('#button-viz-plot-line').click(function () {
        // Display the modal telling the user to stand by.
        $('#modal-visual-wait').modal('show');

        // Generate the visualization for the sources listed.
        $.getJSON('/viz/plot_lines', {
            'sources': selected_items($('#viz-plot-line-sources'))
        },  function (r) {
            // Results received, dismiss the modal.
            $('#modal-visual-wait').modal('hide');
            if (r['result'] == true) {
                // Filename received, go to the URL.
                location.href = r['data']['filename'];
            } else {
                // Tell the user what went wrong.
                toastr.error(r['msg']);
            }
        });
    });

    // 2D bar plot visualization.
    $('#button-viz-plot-bar').click(function () {
        // Display the modal telling the user to stand by.
        $('#modal-visual-wait').modal('show');

        // Generate the visualization for the sources listed.
        $.getJSON('/viz/plot_bar', {
         'sources': selected_items($('#viz-plot-bar-sources'))
        },  function (r) {
            // Results received, dismiss the modal.
            $('#modal-visual-wait').modal('hide');
            if (r['result'] == true) {
                // Filename received, go to the URL.
                location.href = r['data']['filename'];
            } else {
                // Tell the user what went wrong.
                toastr.error(r['msg']);
            }
        });
    });

    // Reference in article visualization.
    $('#button-viz-graph-ref-article').click(function () {
        // Display the modal telling the user to stand by.
        $('#modal-visual-wait').modal('show');

        // Generate the visualization for the sources listed.
        $.getJSON('/viz/draw_ref_in_article', {
            'article': selected_item($('#viz-ref-article'))
        },  function (r) {
            // Results received, dismiss the modal.
            $('#modal-visual-wait').modal('hide');
            if (r['result'] == true) {
                // Filename received, go to the URL.
                location.href = r['data']['filename'];
            } else {
                // Tell the user what went wrong.
                toastr.error(r['msg']);
            }
        });
    });

    // Reference to source visualization.
    $('#button-viz-ref-to-source').click(function () {
        // Display the modal telling the user to stand by.
        $('#modal-visual-wait').modal('show');

        // Generate the visualization for the sources listed.
        $.getJSON('/viz/draw_ref_to_source', {
            'source': selected_item($('#viz-ref-to-source'))
        },  function (r) {
            // Results received, dismiss the modal.
            $('#modal-visual-wait').modal('hide');
            if (r['result'] == true) {
                // Filename received, go to the URL.
                location.href = r['data']['filename'];
            } else {
                // Tell the user what went wrong.
                toastr.error(r['msg']);
            }
        });
    });

    // Reference from source visualization.
    $('#button-viz-ref-from-source').click(function () {
        // Display the modal telling the user to stand by.
        $('#modal-visual-wait').modal('show');

        // Generate the visualization for the sources listed.
        $.getJSON('/viz/draw_ref_from_source', {
            'source': selected_item($('#viz-ref-from-source'))
        },  function (r) {
            // Results received, dismiss the modal.
            $('#modal-visual-wait').modal('hide');
            if (r['result'] == true) {
                // Filename received, go to the URL.
                location.href = r['data']['filename'];
            } else {
                // Tell the user what went wrong.
                toastr.error(r['msg']);
            }
        });
    });

    // Selectize single source selection.
    $('.selectize-source').selectize({
        preload: true,
        create: false,
        selectOnTab: true,
        valueField: 'id',
        labelField: 'url',
        searchField: 'url',

        // Get the JSON data from the server
        load: function(query, callback) {
            $.getJSON('/db/get_sources', {
                offset: 0,
                length: 10,
                search: encodeURIComponent(query)
            }, function(r) {
                callback(r["data"]);
            });
        }
    });

    // Selectize multiple source selection.
    $('.selectize-sources').selectize({
        preload: true,
        create: false,
        selectOnTab: true,
        valueField: 'id',
        labelField: 'url',
        searchField: 'url',
        maxItems: 20,

        // Get the JSON data from the server
        load: function(query, callback) {
            $.getJSON('/db/get_sources', {
                offset: 0,
                length: 10,
                search: encodeURIComponent(query)
            }, function(r) {
                callback(r["data"]);
            });
        }
    });

    // Enable select support for articles.
    $('.selectize-article').selectize({
        valueField: 'id',
        labelField: 'title',
        searchField: ['title', 'source', 'url', 'date'],
        create: false,
        preload: true,

        // HTML renderer for the data
        render: {
            option: function(item, escape) {
                return '<div class="article-list">' +
                    '<div class="title">' + escape(item.title) + '</div>' +
                    '<div class="desc">' + escape(item.url) + '</div>' +
                    '</div>';
            }
        },

        // Get the JSON data from the server
        load: function(query, callback) {
            $.getJSON('/db/get_articles', {
                offset: 0,
                length: 10,
                search: encodeURIComponent(query)
            }, function(r) {
                callback(r["data"]);
            });
        }
    });
});