function get_precipitation_data(date) {

  L.tileLayer('https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/AMSR2_Surface_Precipitation_Rate_Day/default/' + date + '/GoogleMapsCompatible_Level6/{z}/{y}/{x}.png', {
    crossOrigin: 'Anonymous',
    attribution: 'NASA',
  }).addTo(map);
}


function get_giovanni_data(x_min, y_min, x_max, y_max) {

    var imageUrl = '/get_giovanni_precipitation_data/' + x_min+ '/ ' + y_min + '/' + x_max + '/' + y_max,
    imageBounds = [[y_min, x_min], [y_max, x_max]];

    L.imageOverlay(imageUrl, imageBounds).addTo(map);

}


function onEachFeature(feature, layer) {
    
    layer.on({
        click: function(e) {
            console.log(e.target.feature.properties.name);
        }
    });
}

function get_water_by_geom(x_min, y_min, x_max, y_max) {

    $.ajax({
    type: "GET",
    url: "http://localhost:5000/get_water_by_geom/" + x_min+ '/ ' + y_min + '/' + x_max + '/' + y_max,
    dataType: 'json',
    success: function (response) {
        console.log(response);
        geojsonLayer = L.geoJson(response, {
            //style: yourLeafletStyle,
            onEachFeature: onEachFeature
        }).addTo(map);
    },
    error: function() {
        console.log("ERROR");
    }
});

}
