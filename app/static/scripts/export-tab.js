$(document).ready(function() {
    /*
    * Add tagged locations to dropdown
    *
    */

    var censusTableSuggest = new Bloodhound({
    datumTokenizer: function (data) {
        return data.value['results'];
    },
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    limit: 1500,
    remote: {
            url: '/rest/geotag/suggest/%QUERY',
            filter: function (r) {
                response = r['results'];
                _.map(response, function(item) {
                    if (!!item['topics']) {
                        item['topic_string'] = item['topics'].join(', ');
                    }
                });
                return response;
            }
        }
    });
    
    censusTableSuggest.initialize();
    
    $('#remote-census .typeahead').typeahead({
            minLength: 3,
            }, {
    name: 'censusTableSuggest',
    displayKey: function (x) {return '';},
    source: censusTableSuggest.ttAdapter(),
    templates: {
                suggestion: Handlebars.compile(
                    [
                        '{{#if table_id}}<h5 class="result-type">{{#if column_name}}Column in {{/if}}Table {{table_id}}</h5>{{/if}}',
                        '<p class="result-name">{{simple_table_name}}</p>',
                        '{{#if column_name}}<p class="caption"><strong>Column name:</strong> {{column_name}}</p>{{/if}}',
                        '{{#if topic_string}}<p class="caption"><strong>Table topics:</strong> {{topic_string}}</p>{{/if}}'
                    ].join('')
                )
            }
    });
    
    $('#remote-census .typeahead').on('typeahead:selected typeahead:autocompleted',
            function (e, datum) {
                entry = $('<li class="list-group-item entry"><span class="badge delete">X</span>' + 
                      datum.simple_table_name + 
                  '</li>');
                entry.data('id', datum.table_id);
                $('.tables-list').append(entry);
            });
    

    $('a.submit-census').on('click', function () {
            list = $("ol.tables-list > li");
            ids = list.map(function (li) {
                return $(this).data('id');
            }).get();

            if (ids.length > 0) {
            
                dest = '/geotag/export/?tables=' + ids.join(',')
                window.location.href = dest;
            }
        });

    // list logic
    $('.tables-list').on('click', 'li > span.delete', function() {
        $(this).closest("li").remove();
    });

});
