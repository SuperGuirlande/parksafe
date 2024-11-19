// map_functions.js

const HereMap = (function() {
    const API_KEY = 'sda2UjIJvUAjooPV2AlHuBD2dnQhVKYWCzlgVtqt8hw'; // Replace with your actual HERE API key
    let map, platform, defaultLayers;

    function initMap(containerId, address, lat, lng, zoom = 15) {
        platform = new H.service.Platform({
            'apikey': API_KEY
        });
        defaultLayers = platform.createDefaultLayers();
        
        map = new H.Map(
            document.getElementById(containerId),
            defaultLayers.vector.normal.map,
            {
                zoom: zoom,
                center: { lat: lat, lng: lng }
            }
        );

        // Add window resize listener to adjust the map size
        window.addEventListener('resize', () => map.getViewPort().resize());

        // Enable map interaction (pan, zoom, etc.)
        const behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));

        // Add UI components (zoom, scale, etc.)
        const ui = H.ui.UI.createDefault(map, defaultLayers);

        addMarkerToMap(lat, lng, address);
    }

    function addMarkerToMap(lat, lng, label) {
        const marker = new H.map.Marker({ lat: lat, lng: lng });
        map.addObject(marker);

        // Optionally, add an info bubble to the marker
        const bubble = new H.ui.InfoBubble({ lat: lat, lng: lng }, {
            content: `<div>${label}</div>`
        });
        
        // Add info bubble to the UI
        const ui = H.ui.UI.createDefault(map, defaultLayers);
        ui.addBubble(bubble);
    }

    function geocodeAddress(address) {
        return new Promise((resolve, reject) => {
            const geocoder = platform.getSearchService();
            geocoder.geocode({ q: address }, (result) => {
                if (result.items.length > 0) {
                    resolve(result.items[0].position);
                } else {
                    reject(new Error('Address not found'));
                }
            }, (error) => {
                reject(error);
            });
        });
    }

    return {
        init: async function(containerId, address, lat, lng) {
            try {
                if (!lat || !lng) {
                    const position = await geocodeAddress(address);
                    lat = position.lat;
                    lng = position.lng;
                }
                initMap(containerId, address, lat, lng);
            } catch (error) {
                console.error('Error initializing map:', error);
                document.getElementById(containerId).innerHTML = `<p>Error loading map: ${error.message}</p>`;
            }
        }
    };
})();

// Usage in your HTML file:
// HereMap.init('mapContainer', 'ADDRESS', LATITUDE, LONGITUDE);