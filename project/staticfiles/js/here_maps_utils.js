// Fonction pour initialiser la carte HERE
function initHereMap(containerId, apiKey, places) {
    var platform = new H.service.Platform({
        'apikey': apiKey
    });

    var defaultLayers = platform.createDefaultLayers();

    var map = new H.Map(
        document.getElementById(containerId),
        defaultLayers.vector.normal.map,
        {
            zoom: 10,
            center: { lat: places[0].lat, lng: places[0].lng }
        }
    );

    var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
    var ui = H.ui.UI.createDefault(map, defaultLayers);

    var group = new H.map.Group();
    map.addObject(group);

    places.forEach(function(place) {
        var marker = new H.map.Marker({ lat: place.lat, lng: place.lng });
        marker.setData(place.title);
        group.addObject(marker);
    });

    group.addEventListener('tap', function (evt) {
        var bubble = new H.ui.InfoBubble(evt.target.getGeometry(), {
            content: evt.target.getData()
        });
        ui.addBubble(bubble);
    }, false);

    map.getViewModel().setLookAtData({
        bounds: group.getBoundingBox()
    });
}

// Fonction pour charger les scripts HERE de manière asynchrone
function loadHereMapsScripts(apiKey, callback) {
    var scripts = [
        'https://js.api.here.com/v3/3.1/mapsjs-core.js',
        'https://js.api.here.com/v3/3.1/mapsjs-service.js',
        'https://js.api.here.com/v3/3.1/mapsjs-ui.js',
        'https://js.api.here.com/v3/3.1/mapsjs-mapevents.js'
    ];

    var loadScript = function(index) {
        if (index < scripts.length) {
            var script = document.createElement('script');
            script.src = scripts[index];
            script.onload = function() {
                loadScript(index + 1);
            };
            document.body.appendChild(script);
        } else {
            callback(apiKey);
        }
    };

    loadScript(0);
}