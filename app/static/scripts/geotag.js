$(document).ready(function() {
    /*
    * Add tagged locations to dropdown
    *
    */
    var RATIO_THRESHOLD = 1.0;

    var tagged = $('#locdata').data()['tagged'],
        tagged_list = _.pairs(tagged),
        tagged_select = $('#tagged');
    /*
    * Autocomplete code
    *
    */
    var selected_count;

    // hide the autocomplete field on load
    $('#response').hide()

    $('select.geotag-select').change(function() {
            // Save option as selected
            var option = $('option.geotag-option:selected', this);
            
            selectPlace(option.attr('value'));

    });

    var locSuggest = new Bloodhound({
    datumTokenizer: function (data) {
        return data.value['results'];
    },

    queryTokenizer: Bloodhound.tokenizers.whitespace,
    sorter: function (a, b) {

            // sort responses by population/ad count priors
            // TODO: make this a sensible prior; currently sorts by population

            var ratio_a = selected_count/a['population'],
                ratio_b = selected_count/b['population'];

            return (ratio_a > ratio_b)? 1 : -1
    },
    remote: {
            url: '/rest/overview/suggest/%QUERY',
            filter: function (r) {
                return r['results'];
            }
        }
    });
    
    locSuggest.initialize();
    
    $('#remote .typeahead').typeahead({
            minLength: 3,
            }, {
    name: 'locSuggest',
    displayKey: function (d) {
        // Round population display to 4 decimal places
        return d['name'] + ': ' + 
            Math.round(selected_count/d['population']*10000)/10000;
    },
    source: locSuggest.ttAdapter()
    });
    
    $('#remote .typeahead').on('typeahead:selected typeahead:autocompleted',
            function (e, datum) {
            console.log(datum);
            $('#remote .typeahead').data({
                    geo_name: datum['name'],
                    geo_id: datum['full_geoid'],
                    population: datum['population'],
                    longitude: datum['location'][0],
                    latitude: datum['location'][1]
                });
            });
    
    /*
    * Mapping code
    *
    */
    var map = L.map('map').setView([38, -97], 4);
    L.tileLayer("http://{s}.tiles.mapbox.com/v3/sz-giantoak.kfe07odo/{z}/{x}/{y}.png", {
attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
        maxZoom: 18
    }).addTo(map);

    /*
    *
    * Add tagged items to selector and map
    *
    */
    tagged_list = _.sortBy(tagged_list, function (d) {
        return -d[1]['ratio'];
        });
    
    map_keys = {};

    // Iterate through tagged items
    _.each(tagged_list, function(d) {

        // Mark certain locations in red
        var c = d[1]['ratio'] > RATIO_THRESHOLD ? 'dangerous' : '',
            color = c == 'dangerous' ? 'red' : 'green';
        
        tagged_select.append($('<option/>').attr({
                'value': d[1]['id'],
                'class': c + ' ' + 'geotag-option',
                'title': d[0] + ': ' + d[1]['ratio']
                }).data({
                'name': d[0],
                'count': d[1]['count'],
                'ratio': d[1]['ratio'],
                'lng': d[1]['lng'],
                'lat': d[1]['lat']
                }).text(d[0] + ': ' + d[1]['ratio']));
        
        // Add map glyph
        var circle = L.circle([d[1].lat, d[1].lng], 
            Math.min(d[1].ratio*10000, 1),
            {
                            color: color,
                            fillColor: color,
                            fillOpacity: 0.5,
                            name: d[0],
                            id: d[1]['id']
                            });
        circle.addTo(map);
        circle.bindPopup(d[0] + ', Ratio: ' + d[1].ratio + ', Ad Counts: ' + d[1].count);
        // Event handling for glyph clicks
        circle.on('click', function(e) {
            selectPlace(d[1]['id']);
            });

        map_keys[d[1]['id']] = circle;
    });

    /* Select a place from the options and deselect all others */
    function selectPlace(id) {
        $('option.geotag-option').prop('selected', false);
        console.log('selected ' + id);
        var option = $('option.geotag-option[value="' + id + '"]').prop('selected', true),
            option_data = option.data();
        
        $('#remote .typeahead')
            .attr('placeholder', option_data.name)
            .typeahead('val', '');

        selected_count = parseFloat(option_data.count);
        
        try {
            var popup = L.popup()
                .setLatLng([option_data.lat, option_data.lng])
                .setContent(option_data.name + 
                    ', Ratio: ' + option_data.ratio.toPrecision(4) + 
                    ', Ad Counts: ' + option_data.count)
                .openOn(map);
        }
        catch (TypeError) {
            // do nothing
        }

        // show autocomplete box, give it focus
        $('#response').show();
        $('#remote .typeahead').focus();
    }

    /*
    * Event handlers for updating names
    */
    $('#discard_button').click(function (d) {
            var opt = $('option.geotag-option:selected');
            discard(opt);
            $('#response').hide();
            });
    
    $('#remote').submit(function (d) {
            opt = $('option.geotag-option:selected');
            data = $('#remote .typeahead').data();
            accept(opt, data);
            $('#response').hide();
        });

    function discard(opt) {
        // TODO: notify server of removal
        loc_id = opt.attr('value');
        console.log('discarding ' + loc_id + ' : ' + map_keys[loc_id]);

        // remove name from selectors
        $('option[value="' + loc_id + '"][class="geotag-option"]').remove();
        
        // add to trash selector
        $('#trash').prepend(opt);
        
        // remove name from map
        try {
            map.removeLayer(map_keys[name]);
        }
        catch (TypeError) {
            // do nothing
            // all untagged elements go here because they aren't on the map
        }
        
        $.ajax('/geotag/discard/' + loc_id);
    }

    function accept(opt, data) {
        loc_id = opt.attr('value');
        data['loc_id'] = loc_id;
        console.log(loc_id);
        $.post('/geotag/update/', data = data);

        // remove name from selectors
        $('option[value="' + loc_id + '"][class="geotag-option"]').remove();

        // TODO: sync selectors + data (add edited name)
    }

});
